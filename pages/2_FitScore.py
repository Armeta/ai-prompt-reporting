from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
def main() -> None:
    # set up environment 
    cl.env_Setup('FitScore Page', 'collapsed', {}, 'wide', 'src/media/Untitled.jpg')    
    st.markdown("---")
    if 'requisition' in st.session_state and 'topten_nurses' in st.session_state:
        
        requisition = st.session_state.requisition

        nurse_df = st.session_state.topten_nurses
        nurse_df['Location'] = nurse_df.apply(lambda row : row['City'] + ', ' + row['State'], axis=1)
        nurse_df['Coords'] = nurse_df.apply(lambda row : str(row['Lat']) + ', ' + str(row['Long']), axis=1)
        nurse_df = nurse_df[['NurseID', 'Name', 'Fit Score', 'Score_License', 'Score_Discipline', 'Score_Specialty', 'Score_Recency', 'Score_Enddate', 'Score_Experience', 'Score_Proximity', 'State', 'HasDiscipline', 'HasSpecialty', 'LastContractEnd_Datetime', 'YearsOfExperience', 'Location', 'Coords', 'Distance']]
        formatted_nurses = nurse_df.style.format({'NurseID': '{:d}', 'Fit Score': '{:3.1f}'})

        st.dataframe(requisition.style.format({'NeedID': '{:d}', 'Need_FacilityID': '{:d}'}), hide_index=True)
        st.dataframe(formatted_nurses, hide_index=True)

                        
    else:
        st.text('No Requisition Selected')

    if st.button("Return"):
        switch_page('streamlit app')

if __name__ == '__main__':
    main()
