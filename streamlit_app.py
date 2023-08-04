# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

#data types
import json

# Visualizations 
import streamlit as st
from PIL import Image
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu

import streamlit as st

# load options file and set up model
def env_Setup():
    # Open and collect options
    f       = open('src\\json\\Options.json','r')
    options_dash = json.load(f)
    f.close()
    f       = open('src\\json\\QueryOptions.json','r')
    options_query = json.load(f)
    f.close()

    model = SentenceTransformer(options_dash['model'])

    #recieve options and their encodings and return
    dash_opts = [option['url'] for option in options_dash['options']]
    dash_enc = [option['encoding'] for option in options_dash['options']]
    query_opts = [option['result'] for option in options_query['options']]
    query_enc = [option['encoding'] for option in options_query['options']]
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

# tab icon
image = Image.open('src\\media\\armeta-icon.jpeg')

# Page Config
st.set_page_config(
    page_title="Retail Analytics Digital Assistant",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This is a webpage with a user input box where to input natural language and recieve real information along with links to a dashboard to help satisfy your query"
    }
)
# Open CSS file
with open('src\\css\\style.css') as f:
   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
   f.close()
   
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Page Header/Subheader
st.title("💬 rvai") 
with st.chat_message("assistant", avatar=image):
    st.write("How can I help you?")

def main():
    # tab icon
    image = Image.open('src\\media\\armeta-icon.jpeg')
    imageuser = Image.open('src\\media\\usericon.jpeg') 

    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts = env_Setup()
  
    # load old session cache
    for message in st.session_state.messages:
        if(message["role"] == "user"):
            with st.chat_message("user", avatar=imageuser):
                st.markdown(message["content"])
        else:       
            with st.chat_message("assistant", avatar=image):
                st.markdown(message["content"])

    prompt = st.chat_input("Send a Message")

    # recieve prompt from user                       
    if prompt : 
        # Start Chat - user
        with st.chat_message("user", avatar=imageuser):
            st.markdown(prompt)

        query_answer = ''

        # run the prompt against the AI to recieve an answer
        dash_answer, query_answer = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts)        
                   
        # Write to session cache for user
        st.session_state.messages.append({"role": "user", "content": prompt})
        # End chat - user
        
        #Start chat - assistant
        with st.chat_message("assistant", avatar=image):
            # Show query result 
            if(query_answer != ''):
                st.write(query_answer)

                # Write session cache for assistant 
                st.session_state.messages.append({"role": "assistant", "content": query_answer})                   
            else:
                st.write("No query results")

                # Write session cache for assistant 
                st.session_state.messages.append({"role": "assistant", "content": "No query results"})  

            # Show dashboard result  
            if(dash_answer != ''):                  
                url = dash_answer
                st.markdown("Your query reminds me of this [dashboard.](%s)" % url)

                # Write session cache for assistant 
                st.session_state.messages.append({"role": "assistant", "content": "Your query reminds me of this dashboard: [here](%s)" % url})                        
    # End chat - assistant
    image.close()
    imageuser.close()
image.close()

if __name__ == '__main__':  
    main()
