import pandas as pd
import streamlit as st
from snowflake.snowpark import Session


# setup connection with snowflake
def snow_session() -> None:
    return Session.builder.configs({
        'account': st.secrets['account'],
        'user': st.secrets['user'], 
        'password': st.secrets['password'],
        'role': st.secrets['role'],
        'warehouse': st.secrets['warehouse'],
        'database': st.secrets['database'],
        'schema': st.secrets['schema']
    }).create()


def get_requisition(session: Session, requisition_id: int) -> pd.DataFrame:
    return pd.DataFrame(session.sql(f"""
        SELECT   NEED.NEEDID
                ,FACL.FACILITYID
                ,FACL.FACILITYNAME
                ,FACL.FACILITYSTATE
                ,NEED.NEEDDISCIPLINEID
                ,NEED.NEEDSPECIALTYID
        FROM NEEDS      NEED
        JOIN FACILITY   FACL ON NEED.NEEDFACILITYID = FACL.FACILITYID
        WHERE NEED.NEEDID = {requisition_id}
        ;
    """).collect())
