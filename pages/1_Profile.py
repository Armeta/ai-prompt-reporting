from src.lib import code_library as cl
import datetime
import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
def main() -> None:
    
    # set up environment 
    cl.env_Setup('Profile Page', 'collapsed', {}, 'centered', '')    
    st.markdown("---")
    # Profile picture and User Info side-by-side
    col1, col2 = st.columns([1,3])  # adjusting the width of the columns
    with col1:
        if 'NurseName' in st.session_state:
            st.write(f'**{str(st.session_state.NurseName)}**')

        st.image('src/media/ProfilePictures/MicrosoftTeams-image (4).png', use_column_width=True)
        
        st.write('**Nurse ID:**' , str(st.session_state.NurseID))
        st.write('**Fit Score:**', str(st.session_state.FitScore))
        st.write('**State:**'    , str(st.session_state.State))               
        st.write('**City:**'     , str(st.session_state.City))
    with col2:   
        with st.container():
            st.write("")
            st.write("")
            st.write("")
            st.write("")
        st.write('**Profile Created Date:**'   , str(datetime.date.strftime(st.session_state.Profile_Created_Date,"%m/%d/%Y")))     
        st.write('**Submission Count:**'       , str(st.session_state.Submission_Count))  
        st.write('**Contract Count:**'         , str(st.session_state.Contract_Count)) 
        st.write('**Years Of Experience:**'    , str(st.session_state.YearsOfExperience)) 
        st.write('**Total Days Worked:**'      , str(st.session_state.DaysWorked_Count)) 
        st.write('**Last Contract End:**'      , str(datetime.date.strftime(st.session_state.LastContractEnd_Datetime,"%m/%d/%Y"))) 
        st.write('**Terminations:**'           , str(st.session_state.Termination_Count)) 
        st.write('**Distance from Facility:**' , str(st.session_state.Distance)) 

    with st.expander("Resume"):
        st.write("resume")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write("")
    with col2:
        if st.button("Return"):
            switch_page('streamlit app')

if __name__ == '__main__':
    main()
