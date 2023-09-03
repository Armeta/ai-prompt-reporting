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

    st.header("Nurse AI", divider='rainbow')

    session = cl.snow_session()

    requisition_id = st.text_input("Requisition ID")
    requisition = cl.get_requisition(session, requisition_id)
    st.write(requisition)

    st.markdown("### Nurse Table")
    if 'nurse_df' not in st.session_state:
        st.session_state['nurse_df'] = cl.get_nurses(session)
    nurse_df = pd.DataFrame(st.session_state['nurse_df'])
    nurse_df['NURSESTATE'] = 'TX'
    st.dataframe(nurse_df)


if __name__ == '__main__':
    main()
