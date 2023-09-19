from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
# Visualizations 
import streamlit as st
import time
import toml

# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers    import SentenceTransformer
import matplotlib.pyplot as plt
import seaborn as sns

#data types
import json
import struct

# setup connection with snowflake
def snowconnection():
    f = open('./.streamlit/secrets.toml', 'r')
    connection_config = toml.load(f)
    f.close()
    session = Session.builder.configs(connection_config).create()

    return session

def save_UserCache(i, content):
    # set indice
    name = 'messages' + str(i) 
    st.session_state[name].append({"role": "user", "content": content})

def get_LastPrompt(i):
    name     = 'messages' + str(i) 
    thislist = []
    prompt = ''
    for strings in st.session_state[name]:
        if str(strings).find('user') > 0:
            thislist.append(strings)
    size = len(thislist)
    prompt = str(thislist[size-1]).replace('\'','"')
    prompt = json.loads(prompt)
    return prompt["content"]

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
def write_Audit(session, prompt, FeedbackRating, FeedbackText):
    s=time.gmtime(time.time())
    session_details = session.create_dataframe(
            [
               [
                  session._session_id
                , str(prompt).replace('"','')
                , FeedbackRating
                , str(FeedbackText).replace('"','')
                , time.strftime("%Y-%m-%d %H:%M:%S", s)
                ]
            ]
            , schema=["session_id" , "input", "FeedbackRating", "FeedbackText", "TimeStamp"]
         )
    # This logs write meta data to a table in snowflake
    session_details.write.mode("append").save_as_table("session_messages_feedback")    

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
def get_Model():
    # load largemodel bin file
    model_bin = open('./LocalModel/pytorch_model.bin', 'wb')
    shard = open('./LocalModel/shards/01_shard_pytorch_model.bin', 'rb')
    model_bin.write(shard.read())
    shard.close()
    shard = open('./LocalModel/shards/02_shard_pytorch_model.bin', 'rb')
    model_bin.write(shard.read())
    shard.close()
    shard = open('./LocalModel/shards/03_shard_pytorch_model.bin', 'rb')
    model_bin.write(shard.read())
    shard.close()
    shard = open('./LocalModel/shards/04_shard_pytorch_model.bin', 'rb')
    model_bin.write(shard.read())
    shard.close()
    model_bin.close()
    
    # model selection
    modelName = 'all-distilroberta-v1'
    #modelName = './LocalModel/'
    model = SentenceTransformer(modelName)    
    return model, modelName

@st.cache_resource()
def get_Data(_session, modelName):
    # # Open and collect options
    if(modelName == './LocalModel/'):
        options_dash  = _session.table("\"OptionsDashboardLocal\"") 
        options_query = _session.table("\"OptionsQueryLocal\"")
    else:
        options_dash  = _session.table("\"OptionsDashboardLocal\"") 
        options_query = _session.table("\"OptionsQueryLocal\"")
        
    #recieve options and their encodings and return
    dash_rows  = options_dash.select(['URL', 'ENCODING']).filter(col('URL').isNotNull() & col('ENCODING').isNotNull()).to_pandas().values.tolist()
    query_rows = options_query.select(['RESULT_CACHE', 'ENCODING']).filter(col('RESULT_CACHE').isNotNull() & col('ENCODING').isNotNull()).to_pandas().values.tolist()
    dash_opts  = [row[0] for row in dash_rows]
    query_opts = [row[0] for row in query_rows]
    dash_enc   = [parseBinaryEncoding(bytearray(row[1])) for row in dash_rows]
    query_enc  = [parseBinaryEncoding(bytearray(row[1])) for row in query_rows]

    return dash_enc, dash_opts, query_enc, query_opts

@st.cache_resource()
def get_GraphData(_session, modelName):
    # Open and collect options    
    graph_dash  = _session.table("\"OptionsGraph\"") 
        
    #recieve options and their encodings and return
    graph_Rows = graph_dash.select(['RESULT_CACHE', 'ENCODING']).filter(col('RESULT_CACHE').isNotNull() & col('ENCODING').isNotNull()).to_pandas().values.tolist()
    graph_ops  = [row[0] for row in graph_Rows]
    graph_enc  = [parseBinaryEncoding(bytearray(row[1])) for row in graph_Rows]

    return graph_ops, graph_enc

def env_Setup(_session, Title, Layout, SideBarState, Menu_Items, Title_Image_Path):

    # Bot Avatar Icon
    with open('src/txt/armeta-icon_Base64Source.txt') as f:
        BotAvatar = f.read()
    f.close()

    # User Avatar Icon
    with open('src/txt/usericon_Base64Source.txt') as f:
        UserAvatar = f.read()
    f.close()

    # Page Config
    st.set_page_config(
        page_title            = Title,
        page_icon             = BotAvatar,
        layout                = Layout,
        initial_sidebar_state = SideBarState,
        menu_items            = Menu_Items
    )

    # Page Header/Subheader
    if(len(Title_Image_Path) > 0):
        st.image(Title_Image_Path)

    if(len(Title) > 0):
        st.subheader(Title, divider='rainbow')

    # Open CSS file
    with open('src/css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    f.close()

    model, modelName = get_Model()
    dash_enc, dash_opts, query_enc, query_opts = get_Data(_session, modelName)
    
        # (re)-initialize current chat 
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'number' not in st.session_state:
        st.session_state.number = 0
    if 'FeedbackRating' not in st.session_state:
        st.session_state.FeedbackRating = ''
    if 'FeedbackText' not in st.session_state:
            st.session_state.FeedbackText = ''

    return model, dash_enc, dash_opts, query_enc, query_opts, BotAvatar, UserAvatar

def get_Graph(selected_plot, data):
    if selected_plot == "Bar plot":
        x_axis = st.sidebar.selectbox("Select x-axis", data.columns)
        y_axis = st.sidebar.selectbox("Select y-axis", data.columns)
        st.write("Bar plot:")
        fig, ax = plt.subplots()
        sns.barplot(x=data[x_axis], y=data[y_axis], ax=ax)
        st.pyplot(fig)

    elif selected_plot == "Scatter plot":
        x_axis = st.sidebar.selectbox("Select x-axis", data.columns)
        y_axis = st.sidebar.selectbox("Select y-axis", data.columns)
        st.write("Scatter plot:")
        fig, ax = plt.subplots()
        sns.scatterplot(x=data[x_axis], y=data[y_axis], ax=ax)
        st.pyplot(fig)

    elif selected_plot == "Histogram":
        column = st.sidebar.selectbox("Select a column", data.columns)
        bins = st.sidebar.slider("Number of bins", 5, 100, 20)
        st.write("Histogram:")
        fig, ax = plt.subplots()
        sns.histplot(data[column], bins=bins, ax=ax)
        st.pyplot(fig)

    elif selected_plot == "Box plot":
        column = st.sidebar.selectbox("Select a column", data.columns)
        st.write("Box plot:")
        fig, ax = plt.subplots()
        sns.boxplot(data[column], ax=ax)
        st.pyplot(fig)


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
