import numpy as np
import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col


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


def get_nurses(session: Session) -> pd.DataFrame:
    return pd.DataFrame(session.table('NURSES')
                               .sort(col('NURSEID'))
                               .collect())


def score_nurses(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    # nurse_df = _score_licensure(nurse_df, requisition)
    nurse_df = _score_specialty(nurse_df, requisition)
    nurse_df = _score_proximity(nurse_df, requisition)
    return nurse_df


def _score_licensure(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    eNLC_states = [
        'AL', 'AZ', 'AR', 'CO', 'DE', 'FL', 'GA', 'ID', 'IN', 'IA', 'KS', 'KY',
        'LA', 'ME', 'MD', 'MS', 'MO', 'MT', 'NE', 'NH', 'NJ', 'NM', 'NC', 'ND',
        'OH', 'OK', 'PA', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
        'WI', 'WY'
    ]
    requisition_state = requisition['FACILITYSTATE'][0]

    # TODO: Finish implementing


def _score_specialty(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    discipline_id = requisition['NEEDDISCIPLINEID'][0]
    specialty_id = requisition['NEEDSPECIALTYID'][0]

    # Filter out any nurses without the proper discipline
    nurse_df = nurse_df[nurse_df['NURSEDISCIPLINEID'] == discipline_id]

    # TODO: populate nurse's specialty(ies)
    # Score based on the specialty (not discipline)
    # nurse_df['SPECIALTYSCORE'] = (nurse_df['NURSESPECIALTYID'] == specialty_id).astype(int)
    return nurse_df


def _score_proximity(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    req_state = requisition['FACILITYSTATE'][0]
    # TODO: populate facility's city
    # req_city = requisition['FACILITYCITY'][0]
    req_city = 'Kansas City'

    # TODO: replace these artificial nurse columns with real columns
    nurse_df['NURSESTATE'] = 'TX'
    nurse_df['NURSECITY'] = 'Dallas'

    conditions = [
        (nurse_df['NURSESTATE'] == req_state) & (nurse_df['NURSECITY'] == req_city),
        (nurse_df['NURSESTATE'] == req_state),
        (nurse_df['NURSESTATE'] != req_state),
    ]

    choices = [1, 0.5, 0]

    nurse_df['PROXIMITYSCORE'] = np.select(conditions, choices)

    return nurse_df
