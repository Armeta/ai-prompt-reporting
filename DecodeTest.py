# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

#data types
import json

#snowpark
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')

from lib import code_library

def env_Setup():
    # Get connection string paramaters
    connectionString = open('src/json/connection_details.json', "r")
    connectionString = json.loads(connectionString.read())
    session          = code_library.snowconnection(connectionString)    

    # # Open and collect options
    # f            = open('src/json/Options.json','r')
    # options_dash = json.load(f)
    # f.close()
    # f             = open('src/json/QueryOptions.json','r')
    # options_query = json.load(f)
    # f.close()

    options_dash  = session.table("\"OptionsDashboard\"")
    options_query = session.table("\"OptionsQuery\"")
    #options_dash_test.show()

    model = SentenceTransformer('all-MiniLM-L12-v2')

    #recieve options and their encodings and return
    dash_opts  = [option['url']      for option in options_dash['options']]
    dash_enc   = [option['encoding'] for option in options_dash['options']]
    query_opts = [option['result']   for option in options_query['options']]
    query_enc  = [option['encoding'] for option in options_query['options']]
    return model, dash_enc, dash_opts, query_enc, query_opts

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
    model, dash_enc, dash_opts, query_enc, query_opts = env_Setup()
    
    dash_answer, query_answer = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts)

    print(dash_answer)
    print(query_answer)

if __name__ == '__main__':  
    main()
