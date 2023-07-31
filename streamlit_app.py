# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
import time
from sentence_transformers import SentenceTransformer

#data types
import json

# Visualizations 
import streamlit as st
from PIL import Image
import webbrowser

# funny things with simple HTML.
def nav_to(url):
    nav_script = """
        <script type="text/javascript">window.open('%s','_blank');</script>
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)

# load options file and set up model
def env_Setup():
    # Open and collect options
    f       = open('json/Options.json','r')
    options_dash = json.load(f)
    f.close()
    f       = open('json/QueryOptions.json','r')
    options_query = json.load(f)
    f.close()

    model = SentenceTransformer(options_dash['model'])

    #recieve options and their encodings and return
    dash_opts = [option['url'] for option in options_dash['options']]
    dash_enc = [option['encoding'] for option in options_dash['options']]
    #query_opts = [option['query'] for option in options_query['options']]
    query_opts = [option['result'] for option in options_query['options']]
    query_enc = [option['encoding'] for option in options_query['options']]
    return model, dash_enc, dash_opts, query_enc, query_opts

# sets up initial streamlit instance
def page_Setup():
    # tab icon
    #image = Image.open('img/icons/armeta-icon.png')

    # Page Config
    st.set_page_config(
        page_title="AI Turkey",
        #page_icon=image,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "This is a webpage with a user input box where to input natural language and recieve real information along with links to a dashboard to help satisfy your query"
        }
    )

    # Open CSS file
    #with open('css/style.css') as f:
    #   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Page Header/Subheader
    st.title("AI Turkey")

# run the prompt against the AI to recieve an answer
def do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts):   
    #init 
    encoding = None
    
    # Encode prompt based off which model is being used
    encoding = model.encode(prompt)
    
    # pick and return a dashboard answer based off options.json
    sim = cosine_similarity([encoding], dash_enc)
    dash_answer = dash_opts[sim[0].tolist().index(max(sim[0]))]
    # pick and return a query answer
    sim = cosine_similarity([encoding], query_enc)
    query_answer = query_opts[sim[0].tolist().index(max(sim[0]))]
    return dash_answer, query_answer

def main():
    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts = env_Setup()

    # sets up initial streamlit instance
    page_Setup()
 
    # recieve prompt from user and draw a line to seperate results from question
    prompt = st.text_input('What would you like to see?', 'What was the total sales revenue yesterday?')

    # run the prompt against the AI to recieve an answer
    dash_answer, query_answer = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts)

    # shows query results if any
    with st.expander("Query results", expanded=True):  
        with st.spinner(text = "In Progress..."):
            time.sleep(.25)
            if(query_answer != ''):
                #print('Similarity: %f, %s' % (max(sim[0]), answer))            
                st.write(query_answer)
            else:
                st.write("No query results")

    # shows dashboards results if any
    with st.expander("Dashboard results", expanded=True):
        with st.spinner(text = "In Progress..."):
            time.sleep(.25)        
            if(dash_answer != ''):
                #print('Similarity: %f, %s' % (max(sim[0]), answer))              
                if st.button('Open Dashboard'):
                    nav_to(dash_answer)
            else:
                st.write("No dashboard results")

if __name__ == '__main__':        
    main()
