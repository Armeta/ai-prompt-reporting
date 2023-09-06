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

    #requisition_id = st.text_input("Requisition ID")
    requisition_id = 976660
    requisition = cl.get_requisition(session, requisition_id)

    #print(requisition)
    if(len(requisition) < 1):
        return

    nurse_df = cl.get_nurses(session)
    #nurse_specialty_df = cl.get_nurse_specialty(session, requisition)
    nurse_df = cl.score_nurses(nurse_df, requisition)
    #nurse_df = cl.score_nurses(nurse_df, requisition, nurse_specialty_df)

    st.dataframe(requisition, hide_index=True)

    st.dataframe(nurse_df[nurse_df['Total_Score'] > 0][['NurseID', 'Name', 'Total_Score']].sort_values(by=['Total_Score'], ascending=False), hide_index=True)


if __name__ == '__main__':
    main()
