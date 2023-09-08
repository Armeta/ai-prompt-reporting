from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
def main() -> None:
    # set up environment 
    cl.env_Setup()    
    st.markdown("---")
    if 'NurseName' in st.session_state:
        row12 = "Nurse Name: "         
        row11 = str(st.session_state.NurseName)
    else:
        row12 = "Nurse Name: "          
        row11 = "Your Mom"
    if 'NurseID' in st.session_state:
        row22 = "Nurse ID: "           
        row21 = str(st.session_state.NurseID)
    else:    
        row22 = "Nurse ID: "            
        row21 = "4266"
    if 'FitScore' in st.session_state:
        row32 = "Fit Score: "          
        row31 = str(st.session_state.FitScore)
    else:     
        row32 = "Fit Score: "          
        row31 = "Over 9000"

    col1, col2 = st.columns(2)
    with col1:
        cl.draw_Card(row11, row21, row31, "Krust Krab Pizza", row12, row22, row32, "Fav Food")
    with col2:
        cl.draw_Card("Fired for Disorderly Conduct", "Aries", "Dogs", "Alaska", "Work History", "Sign", "Cats/Dogs", "Fav state")

    if st.button("Return"):
        switch_page('streamlit app')

if __name__ == '__main__':
    main()
