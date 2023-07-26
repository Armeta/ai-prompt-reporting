from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import html
import openai
import streamlit as st

# Page Config
st.set_page_config(
    page_title="AI Turkey",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This page supplies a prompt where a user can input queries and recieve links to a dashboard that helps them solve their query"
    }
 )

# Page Header/Subheader
st.title("AI Turkey")


hostName = 'localhost'
serverPort = 8080


f = open('Options.json','r')
options = json.load(f)
f.close()


# OpenAI model
if(options['model'] == 'text-embedding-ada-002'):
    f = open('secrets.json','r')
    secrets = json.load(f)
    f.close()
    openai.organization = secrets['organization']
    openai.api_key = secrets['api_key']
else:
    model = SentenceTransformer(options['model'])

opts = [option['url'] if option['type'] == 'url' else option['result'] for option in options['options']]
opt_enc = [option['encoding'] for option in options['options']]


def do_GET(prompt):
    print(prompt)
    if(prompt != ''): # prompt is supplied, show result
        encoding = None
        # prompt implementation
        if(options['model'] == 'text-embedding-ada-002'):
            encoding = openai.Embedding.create(input = [prompt], model='text-embedding-ada-002')['data'][0]['embedding']
        else:
            encoding = model.encode(prompt)
        
        sim = cosine_similarity([encoding], opt_enc)
        answer = opts[sim[0].tolist().index(max(sim[0]))]
        st.write('Similarity: %f, %s' % (max(sim[0]), answer))


if __name__ == '__main__':        
    prompt = st.text_input('Prompt', 'What was the total sales revenue yesterday?')
    
    do_GET(prompt)

