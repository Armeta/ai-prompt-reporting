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
    requisition_id = st.text_input("Requisition ID")

    session = cl.snow_session()

    requisition = cl.get_requisition(session, requisition_id)
    st.write(requisition)


if __name__ == '__main__':
    main()
