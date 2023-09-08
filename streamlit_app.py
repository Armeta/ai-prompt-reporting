from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page

def main() -> None:

    # set up environment 
    cl.env_Setup()

    # connect to snowflake
    session = cl.snow_session()

    requisition_id = 976660

    # Recieve user input
    str_input = requisition_id = st.text_input("Requisition ID", value=str(requisition_id))
    
    # test user input is valid
    if(str_input.isdigit()):
        requisition_id = int(str_input)
    else:
        st.text('Invalid Requisition ID')
        return

    # Pull requisition details from source
    requisition = cl.get_requisition(session, requisition_id)
    if(len(requisition) < 1):
        st.text('Requisition ID not found')
        return
    
    # # Add requsition to history tab     
    if not requisition.empty and requisition['NeedID'].iloc[0] not in [df['NeedID'].iloc[0] for df in st.session_state.requisitions]:
        st.session_state.requisitions.append(requisition)


    # Pull Nurse dataset from source
    nurse_df = cl.get_nurses(session)

    # prepare nurse dataset
    nurse_dis_df, nurse_spe_df    = cl.get_nurse_discipline_specialty(session, requisition)
    nurse_dis_df['HasDiscipline'] = True
    nurse_spe_df['HasSpecialty']  = True
    nurse_df                      = nurse_df.join(nurse_dis_df.set_index('DisciplineNurseID'), on='NurseID', how='left').join(nurse_spe_df.set_index('SpecialtyNurseID'), on='NurseID', how='left')
    nurse_df['HasDiscipline']     = nurse_df['HasDiscipline'].notna()
    nurse_df['HasSpecialty']      = nurse_df['HasSpecialty'].notna()
    nurse_df                      = cl.score_nurses(nurse_df, requisition)        
    valid_nurses                  = nurse_df[nurse_df['Fit Score'] > 0]
    info_nurses                   = valid_nurses[['NurseID', 'Name', 'Fit Score']]
    sorted_nurses                 = info_nurses.sort_values(by=['Fit Score'], ascending=False)
    topten_nurses                 = sorted_nurses.head(25)
    #remaining_nurses             = sorted_nurses.drop(topten_nurses.index) 

    # sliding tabs for interacting with the different UI's
    need_tab, nurseList_tab, history_tab = st.tabs(["Requisition Profile", "Recommended Nurses", "Requisition Search History"])
    # Displays information on the need most recently typed in
    with need_tab:
        # Draws the two cards on the title page 
        col1, col2 = st.columns(2)
        for index, row in requisition.iterrows():
            with col1:
                cl.draw_Card(row, 'Need_FacilityID', 'Facility_Name', 'Facility_State', 'Facility_City', 'Facility ID', 'Facility Name', 'Facility State', 'Facility City')
            with col2:
                cl.draw_Card(row, 'Discipline_Name', 'Need_DisciplineID', 'Specialty_Name', 'Need_SpecialtyID', 'Discipline Name', 'Discipline ID', 'Specialty Name', 'Specialty ID')                                        
    # Gives a list of recommended nurses after a need has been typed in 
    with nurseList_tab:
        # Writes the header on the Recommended Nurses page
        with st.expander("Top 25 Nurses", expanded = True):
            with st.container():
                Ccol1, Ccol2, Ccol3, Ccol4 = st.columns(4)
                with Ccol1:
                    st.write("<u>**Nurse Profile**</u>", unsafe_allow_html=True)
                with Ccol2:
                    st.write("<u>**Nurse Name**</u>", unsafe_allow_html=True)
                with Ccol3:
                    st.write("<u>**Nurse ID**</u>", unsafe_allow_html=True)
                with Ccol4:
                    st.write("<u>**Fit Score**</u>", unsafe_allow_html=True)                
            
            # Draws the buttons and writes out the nurse information 
            for index, row in topten_nurses.iterrows():
                Ecol1, Ecol2, Ecol3, Ecol4 = st.columns(4)
                with Ecol1:                                                
                    button_label =  f"{row['Name']}"
                    # If any button is pressed we set conditions to navigate to the profile page
                    if st.button("Visit " + button_label + "'s profile", use_container_width=True):
                        st.session_state.NurseName = row['Name']
                        switch_page('profile')
                with Ecol2:                                            
                    st.markdown(f"{row['Name']}")                
                with Ecol3:
                    st.session_state.NurseID = f"{row['NurseID']}"
                    st.markdown(f"{row['NurseID']}")
                with Ecol4:
                    st.session_state.FitScore = f"{row['Fit Score']:3.1f}"
                    st.markdown(f"{row['Fit Score']:3.1f}")                
    # Gives a running record of all searched requisitions within a user session 
    with history_tab:
        with st.expander("Requisition Search History", expanded = True):
            for req in st.session_state.requisitions:
                st.write(req)

    
if __name__ == '__main__':
    main()
