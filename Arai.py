# Visualizations 
import streamlit as st
from   PIL import Image
from streamlit_extras.switch_page_button import switch_page
#import extra_streamlit_components as stx

# custom functions
from src.lib import code_library
import json

def main():

    # Get connection string paramaters
    session = code_library.snowconnection()   

    # gets mapping file and their encodings as well as meta data for the model being used    
    model, dash_enc, dash_opts, query_enc, query_opts, graph_opts, graph_enc, BotAvatar, UserAvatar  \
    = code_library.env_Setup(session                                          
                             , "Analytics Digital Assistant - Armeta POC"  
                             , "wide"                                         
                             , "expanded"                                     
                             , {'About': "This is a webpage with a user input box where to input natural language and recieve real information along with links to a dashboard to help satisfy your query"} 
                             , './src/media/Title.png' 
                            )

    with st.chat_message("assistant", avatar = BotAvatar):
         st.write("How can I help you?")  

    # sidebar options
    with st.sidebar:
        # caching for chat
        number = code_library.manage_Cache()
        # Give filtering options for AI results
        options = st.radio("What would you like to see?",('Both Dashboard and Query Results', 'Dashboards Only', 'Query Results Only'))

        st.sidebar.header("Visualizations")
        plot_options  = ["Bar plot", "Scatter plot", "Histogram", "Box plot"]
        selected_plot = st.sidebar.selectbox("Choose a plot type", plot_options)

    # load chat history 
    code_library.load_Cache(UserAvatar, BotAvatar)
   
    # recieve prompt from user
    prompt = st.chat_input("Send a Message") 
    if prompt : 

        # Start Chat - user
        with st.chat_message("user", avatar = UserAvatar):
            st.markdown(prompt)
        
        if prompt == 'reload':
            dash_enc, dash_opts, query_enc, query_opts = code_library.get_Data(session)
        else:
            # clean the prompt before the AI recieves it
            clean_prompt = prompt.lower().replace('\'','').replace('-',' ')
            
        # run the prompt against the AI to recieve an answer And Write to session cache for user
        dash_answer, query_answer = \
        code_library.do_Get(clean_prompt, model, dash_enc, dash_opts, query_enc, query_opts)        
        code_library.save_UserCache(number, prompt)  

        #Start chat - assistant
        with st.chat_message("assistant", avatar = BotAvatar):
            # Show query result 
            if(query_answer != '') and (options != 'Dashboards Only'):
                # Write results + session cache for assistant
                query_answer = str(query_answer).replace("$", "\\$")
                st.markdown(query_answer) 
                code_library.save_AssistantCache(number, query_answer)
            elif (options != 'Dashboards Only'):
                # Write results + session cache for assistant 
                st.write("No query results")               
                code_library.save_AssistantCache(number, "No query results")

            # Show dashboard result  
            if(dash_answer != '') and (options != 'Query Results Only'): 
                # Write results + session cache for assistant
                st.markdown("Your query reminds me of this [dashboard.](%s)" % dash_answer)
                st.session_state.number       = number                
                code_library.save_AssistantCache(number, "Your query reminds me of this [dashboard.](%s)" % dash_answer)
        # End chat - assistant

    ChatOptions         = ['Standard Chat', "Draw Graph", 'Give Feedback']
    SelectedChatOption  = st.radio('ChatOptions', ChatOptions, horizontal = True, label_visibility = "hidden")

    if SelectedChatOption == 'Standard Chat':
        ""

    # ask user if reply was helpful
    if SelectedChatOption == 'Give Feedback':
        switch_page('Give Feedback')

    if SelectedChatOption == "Draw Graph": 
        with st.spinner("Drawing: " + selected_plot):
            LastPrompt = code_library.get_LastPrompt(st.session_state.number)
            if LastPrompt:
                graph_answer = code_library.do_GetGraph(LastPrompt, model, graph_opts, graph_enc)
                print(graph_answer)
            else:
                st.write("No prompt")

            # Split the string using the '%@%' delimiter
            graph_ops_str = graph_answer.rstrip('%@%')
            split_ops     = graph_ops_str.split('%@%')
            graph_XY      = [(item.split('<+>')[0], item.split('<+>')[1]) for item in split_ops]
            code_library.get_Graph(selected_plot, graph_XY)

if __name__ == '__main__':  
    main()
