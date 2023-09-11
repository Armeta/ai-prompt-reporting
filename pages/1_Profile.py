from src.lib import code_library as cl
import datetime
import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
def main() -> None:
    
    # set up environment 
    cl.env_Setup('Profile Page', 'collapsed', {}, 'wide', '')    

    st.title(str(st.session_state.NurseName))

    # Profile picture and User Info side-by-side
    col1, col2 = st.columns([1,3])  # adjusting the width of the columns
    with col1:
        
        #st.write(f'**{}**')        
        #st.image('data:image/png;base64,' + st.session_state.Profile_Picture, use_column_width=True)
        cl.draw_SmallCard(str(st.session_state.NurseID), str(st.session_state.FitScore), str(st.session_state.State), str(st.session_state.City), 'Nurse ID', 'Fit Score', 'State', 'City')


    with col2:           
        #st.write(f'**{str(st.session_state.NurseName)}**') 
        cl.draw_BigCard(str(st.session_state.Profile_Created_Date), str(st.session_state.Submission_Count), str(st.session_state.Contract_Count), str(st.session_state.YearsOfExperience), str(st.session_state.DaysWorked_Count), str(st.session_state.LastContractEnd_Datetime), str(st.session_state.Termination_Count), str(st.session_state.Distance), str(st.session_state.DISCIPLINES), str(st.session_state.SPECIALTIES) \
                        , 'Profile Created Date'                  , 'Submission Count'                    , 'Contract Count'                    , 'Years Of Experience'                  , 'Total Days Worked'                   , 'Last Contract End'                           , 'Terminations'                         , 'Distance from Facility'          , "Disciplines"                    , "Specialty"                       \
                    )   

        with st.expander("Click to Review Resume", expanded=False):
            st.write(str(st.session_state.Profile_CV))

        if st.button("Return to Recommended Nurses"):
            switch_page('streamlit app')

if __name__ == '__main__':
    main()
