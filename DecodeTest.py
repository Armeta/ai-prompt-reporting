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

def localRead():
    jsonstarttime = datetime.datetime.now()
    f       = open('src/json/Options.json','r')
    options_dash = json.load(f)
    f.close()
    f       = open('src/json/QueryOptions.json','r')
    options_query = json.load(f)
    f.close()

    #recieve options and their encodings and return
    dash_enc = [option['encoding'] for option in options_dash['options']]
    query_enc = [option['encoding'] for option in options_query['options']]
    
    endtime = datetime.datetime.now()
    print('Total JSON encoding load time %d.%06d sec' % ((endtime - jsonstarttime).seconds, (endtime - jsonstarttime).microseconds))
    
    return '%d.%06d' % ((endtime - jsonstarttime).seconds, (endtime - jsonstarttime).microseconds)

def env_Setup():
    snowstarttime = datetime.datetime.now()
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
    dash_opts  = options_dash.select(['url']).to_pandas().values.tolist()
    query_opts = options_query.select(['RESULT_CACHE']).to_pandas().values.tolist()

    binstarttime = datetime.datetime.now()

    dash_bin  = options_dash.select(['encoding']).to_pandas().values.tolist()
    query_bin =options_query.select(['encoding']).to_pandas().values.tolist()
    dash_enc   = [parseBinaryEncoding(bytearray(row[0])) for row in dash_bin]
    query_enc  = [parseBinaryEncoding(bytearray(row[0])) for row in query_bin]

    binendtime = datetime.datetime.now()

    jsonstarttime = datetime.datetime.now()

    dash_json  = options_dash.select(['ENCODING_JSON']).to_pandas().values.tolist()
    query_json = options_query.select(['ENCODING_JSON']).to_pandas().values.tolist()
    dash_enc2   = [parseBinaryEncoding(bytearray(row[0])) for row in dash_bin]
    query_enc2  = [parseBinaryEncoding(bytearray(row[0])) for row in query_bin]

    endtime = datetime.datetime.now()


    snowtime = '%d.%06d' % ((endtime - snowstarttime).seconds, (endtime - snowstarttime).microseconds)
    bintime = '%d.%06d' % ((binendtime - binstarttime).seconds, (binendtime - binstarttime).microseconds)
    jsontime = '%d.%06d' % ((endtime - jsonstarttime).seconds, (endtime - jsonstarttime).microseconds)

    print('Total Snowflake encoding load time %s sec' % (snowtime))
    print('Binary encoding parse time %s sec' % (bintime))
    print('JSON encoding parse time %s sec' % (jsontime))

    return model, dash_enc, dash_opts, query_enc, query_opts, snowtime, bintime, jsontime


# run the prompt against the AI to recieve an answer
def do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts):   
    #init 
    encoding = None
    
    # Encode prompt based off which model is being used
    if(prompt != ''):
        encoding = model.encode(prompt)
    
    # pick and return a dashboard answer based off options.json
    sim = cosine_similarity([encoding], dash_enc)
    dash_answer = dash_opts[sim[0].tolist().index(max(sim[0]))]

    # pick and return a query answer
    sim = cosine_similarity([encoding], query_enc)
    query_answer = query_opts[sim[0].tolist().index(max(sim[0]))]
    return dash_answer, query_answer

def main():

    prompt = 'test'

    # gets mapping file and their encodings as well as meta data for the model being used
    
    localtime = localRead()

    model, dash_enc, dash_opts, query_enc, query_opts, snowtime, binTime, jsontime = env_Setup()

    f = open('DecodeSpeedData.csv', 'a')
    f.write('\n'+snowtime+','+binTime+','+jsontime+','+localtime)
    f.close()


    dash_answer, query_answer = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts)

    print(dash_answer)
    print(query_answer)

if __name__ == '__main__':  
    main()
