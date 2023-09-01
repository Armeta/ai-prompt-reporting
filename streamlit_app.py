from src.lib import code_library as cl

import streamlit as st
from snowflake.snowpark.session import Session


def main():
    st.set_page_config(
        page_title="Nurse AI",
        layout='centered',
        initial_sidebar_state='collapsed',
        menu_items={},
    )

    st.header("Nurse AI", divider='rainbow')
    st.text_input("Requisition ID")

    session = cl.snow_session()


if __name__ == '__main__':
    main()
