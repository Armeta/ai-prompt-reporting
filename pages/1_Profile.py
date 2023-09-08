from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page

if 'NurseName' in st.session_state:
    st.write("Nurse Name: "         + str(st.session_state.NurseName))
else:
    st.write("Nurse Name: "         + "Your Mom")
if 'NurseID' in st.session_state:
    st.write("Nurse ID: "           + str(st.session_state.NurseID))
else:    
    st.write("Nurse ID: "           + "4266")
if 'FitScore' in st.session_state:
    st.write("Fit Score: "          + str(st.session_state.FitScore))
else:     
    st.write("Fit Score: "          + "Over 9000")

st.write("Nurse Work History: " + "Krust Krab Pizza")
st.write("Nurse Licenses: "     + "Is The Pizza For You And Me")
if st.button("Return"):
    switch_page('streamlit app')