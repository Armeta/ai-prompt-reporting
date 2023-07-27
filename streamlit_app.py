# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
import time
from sentence_transformers import SentenceTransformer

#data types
import json

# AI 
import openai

# Visualizations 
import streamlit as st
from PIL import Image
import webbrowser

# load options file and set up model
def env_Setup():
    # Open and collect options.json
    f       = open('\\json\\Options.json','r')
    options = json.load(f)
    f.close()

    # OpenAI model
    if(options['model'] == 'text-embedding-ada-002'):
        f       = open('\\json\\secrets.json','r')
        secrets = json.load(f)
        f.close()
        openai.organization = secrets['organization']
        openai.api_key      = secrets['api_key']
    else:
        model = SentenceTransformer(options['model'])

    #recieve options and their encodings and return    
    opts    = [option['url'] if option['type'] == 'url' else option['result'] for option in options['options']]
    opt_enc = [option['encoding'] for option in options['options']]
    return options, model, opt_enc, opts

# sets up initial streamlit instance
def page_Setup():
    # tab icon
    image = Image.open('.\\img\\icons\\armeta-icon.png')

    # Page Config
    st.set_page_config(
        page_title="AI Turkey",
        page_icon=image,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "This is a webpage with a user input box where to input natural language and recieve real information along with links to a dashboard to help satisfy your query"
        }
    )

    # Open CSS file
    with open('\\css\\style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Page Header/Subheader
    st.title("AI Turkey")

# run the prompt against the AI to recieve an answer
def do_GET(prompt, options, model, opt_enc, opts):   
    #init 
    encoding = None
    
    # Encode prompt based off which model is being used
    if(options['model'] == 'text-embedding-ada-002'):
        encoding = openai.Embedding.create(input = [prompt], model='text-embedding-ada-002')['data'][0]['embedding']
    else:
        encoding = model.encode(prompt)
    
    # pick and return an answer based off options.json
    sim = cosine_similarity([encoding], opt_enc)
    answer = opts[sim[0].tolist().index(max(sim[0]))]
    return answer, sim

def main():
    # gets mapping file and their encodings as well as meta data for the model being used
    options, model, opt_enc, opts = env_Setup()

    # sets up initial streamlit instance
    page_Setup()
 

    # recieve prompt from user and draw a line to seperate results from question
    prompt = st.text_input('What would you like to see?', 'What was the total sales revenue yesterday?')

    # run the prompt against the AI to recieve an answer
    answer, sim = do_GET(prompt, options, model, opt_enc, opts)

    # shows query results if any
    with st.expander("Query results", expanded=True):  
        with st.spinner(text = "In Progress..."):
            time.sleep(.5)
            if((answer[:5] != 'https') and (answer != '')):
                print('Similarity: %f, %s' % (max(sim[0]), answer))            
                st.write(answer)
            else:
                st.write("No query results")


    # shows dashboards results if any
    with st.expander("Dashboard results", expanded=True):
        with st.spinner(text = "In Progress..."):
            time.sleep(.5)        
            if(answer[:5] == 'https'):
                print('Similarity: %f, %s' % (max(sim[0]), answer))
                url = answer
                if st.button('Open Dashboard'):
                    webbrowser.open_new_tab(url)
            else:
                st.write("No dashboard results")

if __name__ == '__main__':        
    main()
