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
    starttime = datetime.datetime.now()
    
    # Get connection string paramaters
    connectionString = open('src/json/connection_details.json', "r")
    connectionString = json.loads(connectionString.read())
    session          = code_library.snowconnection(connectionString)    

    options_dash  = session.table("\"OptionsDashboard\"")
    options_query = session.table("\"OptionsQuery\"")
    #options_dash_test.show()

    # model selection
    #model = SentenceTransformer('all-distilroberta-v1')
    model = SentenceTransformer('./LocalModel/')
    
    #recieve options and their encodings and return
    dash_rows = options_dash.select(['URL', 'ENCODING', 'DESC']).to_pandas().values.tolist()
    query_rows = options_query.select(['RESULT_CACHE', 'ENCODING', 'DESC']).to_pandas().values.tolist()

    dash_opts  = [row[0] for row in dash_rows]
    query_opts = [row[0] for row in query_rows]
    #dash_enc   = [parseBinaryEncoding(bytearray(row[1])) for row in dash_rows]
    #query_enc  = [parseBinaryEncoding(bytearray(row[1])) for row in query_rows]
    dash_enc   = [model.encode(row[2]) for row in dash_rows]
    query_enc  = [model.encode(row[2]) for row in query_rows]

    dash_desc  = [row[2] for row in dash_rows]
    query_desc = [row[2] for row in query_rows]

    endtime = datetime.datetime.now()

    print('Env Setup in %d sec' % ((endtime-starttime).seconds))

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

    

    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc = env_Setup()


    prompt = 'test'
    while prompt != 'exit':
        print()
        prompt = input('Enter Prompt: ')
        if(prompt == 'exit'):
            break
        dash_answer, query_answer, dash_answer_desc, query_answer_desc = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts, dash_desc, query_desc)
        print(str(dash_answer) + ' ('+str(dash_answer_desc)+')')
        print(str(query_answer) + ' ('+str(query_answer_desc)+')')
    print('Exiting...')

if __name__ == '__main__':  
    main()
