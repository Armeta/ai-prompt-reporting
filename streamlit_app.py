# data manipulation 
from sklearn.metrics.pairwise import cosine_similarity
import time
from sentence_transformers import SentenceTransformer
import time
import random

#data types
import json

# Visualizations 
import streamlit as st
from PIL import Image
from streamlit.components.v1 import html


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

def randomGreeting():
        message_placeholder = st.empty()

        full_response = ""
        assistant_response = random.choice(
            [
        "Hello there! How can I assist you today?",
        "Hi, human! Is there anything I can help you with?",
        "Do you need help?",
        "Greetings and salutations!",
        "Good day, my esteemed friend.",
        "Hello, how do you fare today?",
        "Warmest salutations to you.",
        "A pleasant morning/evening to you.",
        "Hi, it's wonderful to see you again.",
        "Welcome back, my dear companion.",
        "How have you been, my good fellow?",
        "Hello, I hope your day is off to a splendid start.",
        "Good day to you, kind soul.",
        "Hi there, I trust everything is going well.",
        "What a pleasure it is to encounter you today.",
        "Greetings, noble sir/madam.",
        "Good morning/afternoon, may it be delightful.",
        "Hello, I am most delighted to engage with you.",
        "Salutations, my valued acquaintance.",
        "Hey there, I hope you're having a wonderful day.",
        "How are you doing on this fine occasion?",
        "A warm welcome to you, my esteemed associate.",
        "Hi, it's great to be in your company again.",
        "Hello, I hope your endeavors are prosperous.",
        "Good to see you, my esteemed compatriot.",
        "How have you been keeping, my friend?",
        "Greetings, may your day be filled with joy.",
        "Hello, I trust you are in high spirits.",
        "It's a pleasure to reconnect with you.",
        "Hi, I hope life has been treating you kindly.",
        "What brings you here, my good fellow?",
        "Salutations, may your day be filled with success.",
        "Good day, it's a pleasure to interact with you.",
        "Hello, I hope you're in good health and spirits.",
        "A warm welcome to you, my respected friend.",
        "Hi there, I trust you're enjoying your day.",
        "How are things in your world today?",
        "Greetings, I hope this message finds you well.",
        "Hello, I'm delighted to be in touch with you.",
        "Good morning/afternoon, may fortune favor you.",
        "It's a pleasure to see you again, my dear companion.",
        "Hi, I hope you're savoring life's joys.",
        "How have you been, my esteemed colleague?",
        "Salutations, may your path be guided by success.",
        "Hello, it's an honor to communicate with you.",
        "Welcome back, my esteemed ally.",
        "Hi there, I hope your day has been gratifying.",
        "What a delightful surprise to encounter you.",
        "Greetings, I trust your aspirations are thriving.",
        "Good day to you, may it be filled with triumphs.",
        "Hello, I hope your journey is full of wonder.",
        "A warm welcome to you, my cherished associate.",
        "Hi, I trust you're finding inspiration each day.",
        "How have you been keeping, my fine friend?",
        "Salutations, may your efforts be fruitful.",
        "Hello, it's a privilege to converse with you.",
        "Good to see you, my esteemed confidant.",
        "How's life treating you on this fine day?",
        "Greetings, I hope your path is paved with success.",
        "Hi, I hope you're experiencing joy in abundance.",
        "What brings you here, my distinguished colleague?",
        "A pleasant morning/afternoon to you, dear friend.",
        "Hello, I trust life's blessings find you well.",
        "It's a pleasure to reconnect with you, my esteemed companion.",
        "Salutations, may your endeavors be met with triumph.",
        "Good day, it's an honor to engage with you.",
        "Hello, I hope you're basking in happiness.",
        "Hi there, I trust you're embracing life's wonders.",
        "How are things in your world, my esteemed confidant?",
        "Greetings, may your day be filled with contentment.",
        "Welcome back, my distinguished friend.",
        "Hi, I hope you're surrounded by prosperity.",
        "How have you been, my esteemed interlocutor?",
        "Salutations, may serenity be your constant companion.",
        "Hello, it's a privilege to connect with you again.",
        "Good to see you, my dear compatriot.",
        "How's life treating you lately, my valued associate?",
        "Greetings, may your dreams know no bounds.",
        "Hi, I trust your pursuits are met with success.",
        "What brings you here, my esteemed conversationalist?",
        "A warm welcome to you, my cherished friend.",
        "Hello, I hope you're savoring life's pleasures.",
        "It's a pleasure to engage with you, my esteemed compatriot.",
        "Salutations, may your path be illuminated with wisdom.",
        "Good day, it's wonderful to reconnect with you.",
        "Hello, I trust you're surrounded by positivity.",
        "Hi there, I hope your endeavors are thriving.",
        "How are things in your world, my esteemed associate?",
        "Greetings, may your days be filled with fulfillment.",
        "Welcome back, my dear companion.",
        "Hi, I hope you're embarking on exciting ventures.",
        "How have you been, my esteemed friend?",
        "Salutations, may your aspirations be met with triumph.",
        "Hello, it's a pleasure to communicate with you.",
        "Good to see you, my esteemed colleague.",
        "How's life treating you on this fine occasion?",
        "Greetings, I hope your journey is filled with joy.",
        "Hi, I trust you're pursuing your passions.",
        "What brings you here, my cherished associate?",
        "A warm welcome to you, my distinguished friend.",
        "Hello, I hope you're surrounded by inspiration.",
        "It's a pleasure to engage with you, my esteemed ally.",
        "Salutations, may your path be lined with prosperity."

            ]
        )

        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
    
        return message_placeholder, full_response

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
    # gets mapping file and their encodings as well as meta data for the model being used
    model, dash_enc, dash_opts, query_enc, query_opts = env_Setup()

    # sets up initial streamlit instance
    page_Setup()
    prompt = st.chat_input("Send a Message")

    # initiiate new session cache
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # load old session cache
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
             st.markdown(message["content"])

    # recieve prompt from user                       
    if prompt : 
        # run the prompt against the AI to recieve an answer
        dash_answer, query_answer = do_GET(prompt, model, dash_enc, dash_opts, query_enc, query_opts)

        # Start Chat - user
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Write to session cache for user
        st.session_state.messages.append({"role": "user", "content": prompt})
        # End chat - user

        query_answer = ''
        #Start chat - assistant
        with st.chat_message("assistant"):

            # random greeting
            message_placeholder, full_response = randomGreeting() 
            message_placeholder.markdown(full_response)
            
            # Write session cache for assistant 
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # check to make sure query was a question
            if prompt.find("?") != -1:
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
                    st.markdown("Your query reminds me of this dashboard: [here](%s)" % url)

                    # Write session cache for assistant 
                    st.session_state.messages.append({"role": "assistant", "content": "Your query reminds me of this dashboard: [here](%s)" % url})                        
        # End chat - assistant



if __name__ == '__main__':  
    main()
