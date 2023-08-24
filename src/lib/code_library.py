from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
# Visualizations 
import streamlit as st

# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

#data types
import json
import struct

# setup connection with snowflake
def snowconnection(connection_config):
    session = Session.builder.configs(connection_config).create()
    #session_details = session.create_dataframe([[session._session_id,session.sql("select current_user();").collect()[0][0],str(session.get_current_warehouse()).replace('"',''),str(session.get_current_role()).replace('"','')]], schema=["session_id","user_name","warehouse","role"])
    
    # This logs write meta data to a table in snowflake
    #session_details.write.mode("append").save_as_table("session_audit")
    
    return session

def save_UserCache(i, content):
    # set indice
    name = 'messages' + str(i) 
    st.session_state[name].append({"role": "user", "content": content})

def save_AssistantCache(i, content):
    # set indice
    name = 'messages' + str(i) 
    st.session_state[name].append({"role": "assistant", "content": content})

def load_Cache(UserAvatar, BotAvatar):
    # load session cache or reset if none
    for message in st.session_state.messages:
        if(message["role"] == "user"):
            with st.chat_message("user", avatar = UserAvatar):
                st.markdown(message["content"])
        else:       
            with st.chat_message("assistant", avatar = BotAvatar):
                st.markdown(message["content"])

def parseBinaryEncoding(bin_enc):
    return [struct.unpack('d', bytearray(bin_enc[i:i+8]))[0] for i in range(0, len(bin_enc), 8)]

# write session meta data
def write_Audit(session, prompt):
    session_details = session.create_dataframe(
            [
               [
                  session._session_id
                , str(prompt).replace('"','')
                ]
            ]
            , schema=["session_id" , "input"]
         )

    # This logs write meta data to a table in snowflake
    session_details.write.mode("append").save_as_table("session_message_audit")    

# caching for chats  
def manage_Cache():
    # caching for chats  
    number = st.number_input('Insert chat index number', min_value=0, max_value=None, value=0, step=1)
    # create new cache
    name = 'messages' + str(number) 
    
    # initialize session cache    
    if name not in st.session_state:
        st.session_state[name] = []

        # remove data from current session cache # reinitialize current session cache
        del st.session_state['messages']                          
        st.session_state['messages'] = []                
    else:                
        # if the name exists then we just swap out the cache
        st.session_state['messages'] = st.session_state[name]    
    
    return number

# load options file and set up model
@st.cache_resource()
def env_Setup():
    # Bot Avatar Icon
    with open('src/txt/armeta-icon_Base64Source.txt') as f:
        BotAvatar = f.read()
    f.close()

    # User Avatar Icon
    with open('src/txt/usericon_Base64Source.txt') as f:
        UserAvatar = f.read()
    f.close()

    # Open CSS file
    with open('src/css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    f.close()

    # Get connection string paramaters
    connectionString = open('src/json/connection_details.json', "r")
    connectionString = json.loads(connectionString.read())
    session          = snowconnection(connectionString)    

    # # Open and collect options
    options_dash  = session.table("\"OptionsDashboard\"") 
    options_query = session.table("\"OptionsQuery\"")

    # model selection
    model = SentenceTransformer('all-distilroberta-v1')
    
    #recieve options and their encodings and return
    dash_rows  = options_dash.select(['URL', 'ENCODING']).filter(col('URL').isNotNull() & col('ENCODING').isNotNull()).to_pandas().values.tolist()
    query_rows = options_query.select(['RESULT_CACHE', 'ENCODING']).filter(col('RESULT_CACHE').isNotNull() & col('ENCODING').isNotNull()).to_pandas().values.tolist()

    dash_opts  = [row[0] for row in dash_rows]
    query_opts = [row[0] for row in query_rows]
    dash_enc   = [parseBinaryEncoding(bytearray(row[1])) for row in dash_rows]
    query_enc  = [parseBinaryEncoding(bytearray(row[1])) for row in query_rows]

    # Page Header/Subheader
    st.title("💬 arai") 
    with st.chat_message("assistant", avatar = BotAvatar):
        st.write("How can I help you?")    

    return model, dash_enc, dash_opts, query_enc, query_opts, BotAvatar, UserAvatar, session

# run the prompt against the AI to recieve an answer
def do_Get(prompt, _model, dash_enc, dash_opts, query_enc, query_opts):   
    #init 
    encoding = None
    
    # Encode prompt based off which model is being used
    if(prompt != ''):
        encoding = _model.encode(prompt)
    
    # pick and return a dashboard answer based off options.json
    sim = cosine_similarity([encoding], dash_enc)
    dash_answer = dash_opts[sim[0].tolist().index(max(sim[0]))]

    # pick and return a query answer
    sim = cosine_similarity([encoding], query_enc)
    query_answer = query_opts[sim[0].tolist().index(max(sim[0]))]
    return dash_answer, query_answer
