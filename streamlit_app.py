from src.lib import code_library as cl

import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session


def main() -> None:
    st.set_page_config(
        page_title="Nurse AI",
        layout='centered',
        initial_sidebar_state='collapsed',
        menu_items={},
    )

    st.header("Nurse AI")

    session = cl.snow_session()

    requisition_id = 976660
    str_input = requisition_id = st.text_input("Requisition ID", value=str(requisition_id))
    if(str_input.isdigit()):
        requisition_id = int(str_input)
    else:
        st.text('Invalid Requisition ID')
        return

    requisition = cl.get_requisition(session, requisition_id)
    print(requisition)
    if(len(requisition) < 1):
        st.text('Requisition ID not found')
        return

    nurse_df = cl.get_nurses(session)

    nurse_dis_df, nurse_spe_df = cl.get_nurse_discipline_specialty(session, requisition)
    nurse_dis_df['HasDiscipline'] = True
    nurse_spe_df['HasSpecialty'] = True
    nurse_df = nurse_df.join(nurse_dis_df.set_index('DisciplineNurseID'), on='NurseID', how='left').join(nurse_spe_df.set_index('SpecialtyNurseID'), on='NurseID', how='left')
    nurse_df['HasDiscipline'] = nurse_df['HasDiscipline'].notna()
    nurse_df['HasSpecialty'] = nurse_df['HasSpecialty'].notna()

    nurse_df = cl.score_nurses(nurse_df, requisition)
    #nurse_df = cl.score_nurses(nurse_df, requisition, nurse_specialty_df)

    st.dataframe(requisition.style.format({'NeedID': '{:d}', 'Need_FacilityID': '{:d}'}), hide_index=True)

    valid_nurses = nurse_df[nurse_df['Fit Score'] > 0]
    info_nurses = valid_nurses[['NurseID', 'Name', 'Fit Score', 'Score_License', 'Score_Discipline', 'Score_Specialty', 'Score_Enddate', 'Score_Experience', 'Score_Proximity']]
    sorted_nurses = info_nurses.sort_values(by=['Fit Score'], ascending=False)
    formatted_nurses = sorted_nurses.style.format({'NurseID': '{:d}', 'Fit Score': '{:3.1f}'})

    st.dataframe(formatted_nurses, hide_index=True)


if __name__ == '__main__':
    main()
