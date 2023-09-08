from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from streamlit_extras.stylable_container import stylable_container

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
        st.session_state.NurseName = False    
    if 'requisitions' not in st.session_state:
        st.session_state.requisitions = []

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

        st.session_state.requisitions.append(requisition)

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
        topten_nurses    = sorted_nurses.head(25)
        #remaining_nurses = sorted_nurses.drop(topten_nurses.index) 

        need_tab, nurseList_tab, history_tab = st.tabs(["Requisition Profile", "Recommended Nurses", "Requisition Search History"])
        with need_tab:
            col1, col2 = st.columns(2)

            for index, row in requisition.iterrows():
                with col1:
                    with stylable_container(
                        key="stylizedContainer1",
                        css_styles="""
                            {
                                border: 1px solid rgba(49, 51, 63, 0.2);
                                border-radius: 0.5rem;
                                padding: calc(1em - 1px)
                            }
                            """,
                    ):
                        col11, col12 = st.columns(2)
                        with col11: 
                            st.write(f"**Facility ID:**")
                            st.write(f"**Facility Name:**")
                            st.write(f"**Facility State:**")
                            st.write(f"**Facility City:**")                      
                        with col12:
                        #st.write(f"Requisition ID:  {row['NeedID']}")
                            st.write(f"{row['Need_FacilityID']}")
                            st.write(f"{row['Facility_Name']}")
                            st.write(f"{row['Facility_State']}")
                            st.write(f"{row['Facility_City']}")
                with col2:
                    with stylable_container(
                        key="stylizedContainer2",
                        css_styles="""
                            {
                                border: 1px solid rgba(49, 51, 63, 0.2);
                                border-radius: 0.5rem;
                                padding: calc(1em - 1px)
                            }
                            """,
                    ):
                        col21, col22, col23 = st.columns(3)
                        with col21:
                            st.write(f"**Discipline Name:**")
                            st.write(f"**Discipline ID:**") 
                            st.write(f"**Specialty Name:**")                          
                            st.write(f"**Specialty ID:**")                                 
                        with col22:
                            st.write(f"{row['Discipline_Name']}")
                            st.write(f"{row['Need_DisciplineID']}")  
                            st.write(f"{row['Specialty_Name']}")                         
                            st.write(f"{row['Need_SpecialtyID']}")                                            

            #st.dataframe(requisition.style.format({'NeedID': '{:d}', 'Need_FacilityID': '{:d}'}), hide_index=True)
        with nurseList_tab:
           
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
                
                selected_nurse = None  # Initial value indicating no selection
                for index, row in topten_nurses.iterrows():
                    Ecol1, Ecol2, Ecol3, Ecol4 = st.columns(4)
                    with Ecol1:                                                
                        checkbox_label =  f"{row['Name']}"
                        if st.button("Visit " + checkbox_label + "'s profile", use_container_width=True):
                            selected_nurse = row['Name']
                            print(selected_nurse)
                            st.session_state.navigated = True 
                            st.session_state.ExpanderState = False
                            st.experimental_rerun()
                    with Ecol2:                                            
                        st.markdown(f"{row['Name']}")                
                    with Ecol3:
                        st.markdown(f"{row['NurseID']}")
                    with Ecol4:
                        st.markdown(f"{row['Fit Score']:3.1f}")                
        with history_tab:
           with st.expander("Requisition Search History", expanded = True):
               for req in st.session_state.requisitions:
                    st.write(req)

        # If navigated (i.e., any checkbox was checked), show the new "page"
    if st.session_state.navigated:
        with st.spinner(text="Fetching Profile..."):
            st.write("Nurse Name: "         + str(st.session_state.NurseName))
            st.write("Nurse Profile: "      + str(st.session_state.NurseName))
            st.write("Nurse Work History: " + str(st.session_state.NurseName))
            st.write("Nurse Licenses: "     + str(st.session_state.NurseName))
        if st.button("Return"):
            st.session_state.navigated = False
            st.experimental_rerun()

    
if __name__ == '__main__':
    main()
