# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

#data types
import json
import struct
import datetime

#snowpark
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')

from lib import code_library

#modelname = 'all-distilroberta-v1'
modelname = './LocalModel/'

def parseBinaryEncoding(bin_enc):
    return [struct.unpack('d', bytearray(bin_enc[i:i+8]))[0] for i in range(0, len(bin_enc), 8)]

def env_Setup():

    starttime = datetime.datetime.now()
    
    opsFile = open('src/outputs/GeneratedOptions.txt', 'r')
    
    ops = [line.replace('\n', '') for line in opsFile]
    ops = list(set(ops)) # removes duplicates


    # model selection
    model = SentenceTransformer(modelname)
    
    # # Get connection string paramaters
    # connectionString = open('src/json/connection_details.json', "r")
    # connectionString = json.loads(connectionString.read())
    # session          = code_library.snowconnection(connectionString)    

    # if(modelname == './LocalModel/'):
    #     options_dash  = session.table("\"OptionsDashboardLocal\"")
    #     options_query = session.table("\"OptionsQueryLocal\"")
    # else:
    #     options_dash  = session.table("\"OptionsDashboard\"")
    #     options_query = session.table("\"OptionsQuery\"")
    # #options_dash_test.show()

    # #recieve options and their encodings and return
    # dash_rows = options_dash.select(['URL', 'ENCODING', 'DESC']).to_pandas().values.tolist()
    # query_rows = options_query.select(['RESULT_CACHE', 'ENCODING', 'DESC']).to_pandas().values.tolist()

    dash_opts  = [desc for desc in ops]
    query_opts = [desc for desc in ops]
    dash_enc   = [model.encode(desc) for desc in ops]
    query_enc  = [model.encode(desc) for desc in ops]

    dash_desc  = [desc for desc in ops]
    query_desc = [desc for desc in ops]

    return model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc


# run the prompt against the AI to recieve an answer
def do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc):   
    #init 
    encoding = None
    dash_answer = ''
    query_answer = ''
    dash_answer_desc = ''
    query_answer_desc = ''

    # Encode prompt based off which model is being used
    if(prompt != ''):
        clean_prompt = prompt.replace('\'', '').replace('-', '')
        encoding = model.encode(clean_prompt)
    
        # pick and return a dashboard answer based off options.json
        sim = cosine_similarity([encoding], dash_enc)
        dash_answer = dash_opts[sim[0].tolist().index(max(sim[0]))]
        dash_answer_desc = dash_desc[sim[0].tolist().index(max(sim[0]))]

        # pick and return a query answer
        sim = cosine_similarity([encoding], query_enc)
        query_answer = query_opts[sim[0].tolist().index(max(sim[0]))]
        query_answer_desc = query_desc[sim[0].tolist().index(max(sim[0]))]
    
    return dash_answer, query_answer, dash_answer_desc, query_answer_desc

def main():

    starttime = datetime.datetime.now()

    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc = env_Setup()

    print('Env setup (options encoded) in %d secs' % ((datetime.datetime.now() - starttime).seconds))

    totalDash = 0
    countDash = 0
    totalQuery = 0
    countQuery = 0
    totalBoth = 0
    countBoth = 0

    total = -1
    ak = open('src/outputs/answerKey.csv', 'r')
    for line in ak:
        total += 1
    ak.close()

    ak = open('src/outputs/answerKey.csv', 'r')
    ak_timestamp = ak.readline().replace('\n', '').replace('\r', '')

    outputpath = 'src/outputs/all-distilroberta-v1/'
    if(modelname == './LocalModel/'):
        outputpath = 'src/outputs/LocalModel/'
    good = open(outputpath+'Questions_good.csv', 'w')
    bad = open(outputpath+'Questions_bad.csv', 'w')
    bad_debug = open(outputpath+'Questions_bad_debug.csv', 'w')
    bad_debug.write('Question | Wrong Answer | Expected Answer')

    currentCount = 0
    starttime = datetime.datetime.now()
    for line in ak.readlines():
        if(line == ''):
            continue
        split = line.split('|')
        prompt = split[0]
        ans = split[1].replace('\n', '').replace('\r', '')

        dash_answer, query_answer, dash_answer_desc, query_answer_desc = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc)

        totalDash += 1
        totalQuery += 1
        totalBoth += 1
        if(dash_answer_desc == ans):
            countDash += 1
        if(query_answer_desc == ans):
            countQuery += 1
        if(dash_answer_desc == ans and query_answer_desc == ans):
            good.write(prompt+'\n')
            countBoth += 1
        if(dash_answer_desc != ans and query_answer_desc != ans):
            bad.write(prompt+'\n')
            bad_debug.write(prompt + ' | ' + query_answer_desc + ' | ' + ans + '\n')

        currentCount += 1
        if(currentCount % 100 == 0):
            endtime = datetime.datetime.now()
            dur_s = (endtime - starttime).seconds
            left_s = int(dur_s/currentCount * (total-currentCount))
            dur_m = int(dur_s / 60)
            dur_s = dur_s % 60
            left_m = int(left_s / 60)
            left_s = left_s % 60
            print('Evaluated %5d entries (%d%%) in %2dm %02ds. Estimated time remaining: %2dm %02ds' % (currentCount, currentCount*100.0/total, dur_m, dur_s, left_m, left_s))

    endtime = datetime.datetime.now()
    dur_s = (endtime - starttime).seconds
    dur_m = int(dur_s / 60)
    dur_s = dur_s % 60
    print('Evaluated %5d total entries in %2dm %02ds.' % (currentCount, dur_m, dur_s))
    print( '%s model on %d entries from answerKey %s' % ('Tuned' if modelname == './LocalModel/' else 'Base' , currentCount, ak_timestamp) )
    print('Dashboards : %02.1f%%' % (countDash*100.0/totalDash))
    print('Queries    : %02.1f%%' % (countQuery*100.0/totalQuery))
    print('Both       : %02.1f%%' % (countBoth*100.0/totalBoth))

    good.close()
    bad.close()
    bad_debug.close()

if __name__ == '__main__':  
    main()
