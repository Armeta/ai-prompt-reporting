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

def parseBinaryEncoding(bin_enc):
    return [struct.unpack('d', bytearray(bin_enc[i:i+8]))[0] for i in range(0, len(bin_enc), 8)]

def env_Setup():
    
    # Get connection string paramaters
    connectionString = open('src/json/connection_details.json', "r")
    connectionString = json.loads(connectionString.read())
    session          = code_library.snowconnection(connectionString)    

    options_dash  = session.table("\"OptionsDashboard\"")
    options_query = session.table("\"OptionsQuery\"")
    #options_dash_test.show()

    # model selection
    model = SentenceTransformer('all-distilroberta-v1')
    
    #recieve options and their encodings and return
    dash_rows = options_dash.select(['URL', 'ENCODING', 'DESC']).to_pandas().values.tolist()
    query_rows = options_query.select(['RESULT_CACHE', 'ENCODING', 'DESC']).to_pandas().values.tolist()

    dash_opts  = [row[0] for row in dash_rows]
    query_opts = [row[0] for row in query_rows]
    dash_enc   = [parseBinaryEncoding(bytearray(row[1])) for row in dash_rows]
    query_enc  = [parseBinaryEncoding(bytearray(row[1])) for row in query_rows]

    dash_desc  = [row[2] for row in dash_rows]
    query_desc = [row[2] for row in query_rows]

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
        encoding = model.encode(prompt)
    
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

    

    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc = env_Setup()

    totalDash = 0
    countDash = 0
    totalQuery = 0
    countQuery = 0
    totalBoth = 0
    countBoth = 0
    

    ak = open('src/json/answerKey.csv', 'r')
    good = open('src/json/correctQuestions.csv', 'w')
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
            print(ans +'|'+query_answer_desc+'|'+dash_answer_desc)

    print('Dashboards : %02.1f%%' % (countDash*100.0/totalDash))
    print('Queries    : %02.1f%%' % (countQuery*100.0/totalQuery))
    print('Both       : %02.1f%%' % (countBoth*100.0/totalBoth))

if __name__ == '__main__':  
    main()
