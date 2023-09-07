from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session


def main() -> None:
    # set page details
    st.set_page_config(
        page_title="Nurse AI",
        initial_sidebar_state='collapsed',
        menu_items={},
        layout='wide'
    )

    st.image('src/media/Untitled.jpg')
    
    # set up environment 
    cl.env_Setup()
    #st.header("Nurse AI")

    # connect to snowflake
    session = cl.snow_session()
    
    if 'navigated' not in st.session_state:
        st.session_state.navigated = False
    
    if 'NurseName' not in st.session_state:
        st.session_state.NurseName = ''
        
    # If not navigated yet, show checkboxes
    if not st.session_state.navigated:  

        requisition_id = 976660
        str_input = requisition_id = st.text_input("Requisition ID", value=str(requisition_id))
        if(str_input.isdigit()):
            requisition_id = int(str_input)
        else:
            st.text('Invalid Requisition ID')
            return

        requisition = cl.get_requisition(session, requisition_id)
        # print(requisition)
        if(len(requisition) < 1):
            st.text('Requisition ID not found')
            return

        nurse_df = cl.get_nurses(session)

        nurse_dis_df, nurse_spe_df    = cl.get_nurse_discipline_specialty(session, requisition)
        nurse_dis_df['HasDiscipline'] = True
        nurse_spe_df['HasSpecialty']  = True
        nurse_df                      = nurse_df.join(nurse_dis_df.set_index('DisciplineNurseID'), on='NurseID', how='left').join(nurse_spe_df.set_index('SpecialtyNurseID'), on='NurseID', how='left')
        nurse_df['HasDiscipline']     = nurse_df['HasDiscipline'].notna()
        nurse_df['HasSpecialty']      = nurse_df['HasSpecialty'].notna()
        nurse_df                      = cl.score_nurses(nurse_df, requisition)
        
        valid_nurses     = nurse_df[nurse_df['Fit Score'] > 0]
        info_nurses      = valid_nurses[['NurseID', 'Name', 'Fit Score']]
        sorted_nurses    = info_nurses.sort_values(by=['Fit Score'], ascending=False)
        topten_nurses    = sorted_nurses.head(10)
        #remaining_nurses = sorted_nurses.drop(topten_nurses.index) 

        need_tab, nurseList_tab, history_tab = st.tabs(["Current Need", "Recommended Nurses", "Need Search History"])
        with need_tab:
            st.dataframe(requisition.style.format({'NeedID': '{:d}', 'Need_FacilityID': '{:d}'}), hide_index=True)

        with nurseList_tab:
            with st.expander("Top Ten Nurses", expanded = True):
                st.write(" NurseID, Nurse Name, FitScore")
                st.session_state.NurseName = cl.show_checkboxes_and_return_selection(topten_nurses)

            # with st.expander("All Nurses"):

        with history_tab:
            st.write("History Goes Here")

        # If navigated (i.e., any checkbox was checked), show the new "page"
    if st.session_state.navigated:
        st.write("Nurse Name: "         + str(st.session_state.NurseName))
        st.write("Nurse Profile: "      + str(st.session_state.NurseName))
        st.write("Nurse Work History: " + str(st.session_state.NurseName))
        st.write("Nurse Licenses: "     + str(st.session_state.NurseName))
        if st.button("Return"):
            st.session_state.navigated = False
            st.experimental_rerun()

    
if __name__ == '__main__':
    main()
