# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

#data types
import json
import struct

# Visualizations 
import streamlit as st
from   PIL import Image
from   streamlit.components.v1 import html
from   streamlit_option_menu import option_menu
import streamlit as st
import   sys

# add src to system path
sys.path.append('src')

from lib import code_library

# tab icon
image = Image.open('src/media/armeta-icon.png')

# Page Config
st.set_page_config(
    page_title="Retail Analytics Digital Assistant",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "This is a webpage with a user input box where to input natural language and recieve real information along with links to a dashboard to help satisfy your query"
    }
)

def parseBinaryEncoding(bin_enc):
    return [struct.unpack('d', bytearray(bin_enc[i:i+8]))[0] for i in range(0, len(bin_enc), 8)]

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
    session          = code_library.snowconnection(connectionString)    

    # # Open and collect options
    options_dash  = session.table("\"OptionsDashboard\"") 
    options_query = session.table("\"OptionsQuery\"")

    # model selection
    model = SentenceTransformer('all-distilroberta-v1')
    
    #recieve options and their encodings and return
    dash_rows = options_dash.select(['URL', 'ENCODING']).to_pandas().values.tolist()
    query_rows = options_query.select(['RESULT_CACHE', 'ENCODING']).to_pandas().values.tolist()

    dash_opts  = [row[0] for row in dash_rows]
    query_opts = [row[0] for row in query_rows]
    dash_enc   = [parseBinaryEncoding(bytearray(row[1])) for row in dash_rows]
    query_enc  = [parseBinaryEncoding(bytearray(row[1])) for row in query_rows]

    # Page Header/Subheader
    st.title("💬 arai") 
    with st.chat_message("assistant", avatar = BotAvatar):
        st.write("How can I help you?")    

    return model, dash_enc, dash_opts, query_enc, query_opts, BotAvatar, UserAvatar

# run the prompt against the AI to recieve an answer
def do_GET(prompt, _model, dash_enc, dash_opts, query_enc, query_opts):   
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

def main():

    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts, BotAvatar, UserAvatar = env_Setup()
    
    # (re)-initialize current chat 
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # sidebar options
    with st.sidebar:
            # caching for chats  
            number = st.number_input('Insert chat index number', min_value=0, max_value=None, value=0, step=1)
            # create new cache
            name = 'messages' + str(number) 
            
            # initialize session cache    
            if name not in st.session_state:
                st.session_state[name] = []

                # remove data from current session cache 
                del st.session_state['messages']
                
                # reinitialize current session cache
                st.session_state['messages'] = []                
            else:                
                # if the name exists then we just swap out the cache
                st.session_state['messages'] = st.session_state[name]
            
            # Give filtering options for AI results
            options = st.radio("What would you like to see?",('Both Dashboard and Query Results', 'Dashboards Only', 'Query Results Only'))

    load_Cache(UserAvatar, BotAvatar)

    # recieve prompt from user
    prompt = st.chat_input("Send a Message")                     
    if prompt : 
        # Start Chat - user
        with st.chat_message("user", avatar = UserAvatar):
            st.markdown(prompt)
        # run the prompt against the AI to recieve an answer And Write to session cache for user
        dash_answer, query_answer = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts)        
        save_UserCache(number, prompt)               
        
        #Start chat - assistant
        with st.chat_message("assistant", avatar = BotAvatar):
            # Show query result 
            if(query_answer != '') and (options != 'Dashboards Only'):
                # Write results + session cache for assistant
                query_answer = str(query_answer).replace("$", "\\$")
                st.markdown(query_answer) 
                save_AssistantCache(number, query_answer)

            elif (options != 'Dashboards Only'):
                # Write results + session cache for assistant 
                st.write("No query results")               
                save_AssistantCache(number, "No query results")

            # Show dashboard result  
            if(dash_answer != '') and (options != 'Query Results Only'): 
                # Write results + session cache for assistant
                st.markdown("Your query reminds me of this [dashboard.](%s)" % dash_answer)                
                save_AssistantCache(number, "Your query reminds me of this [dashboard.](%s)" % dash_answer)
    # End chat - assistant
image.close()

if __name__ == '__main__':  
    main()
