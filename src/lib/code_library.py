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
    req = session.table('NEEDS')
    fac = session.table('FACILITY')

    reqResult = req.filter(col('"NeedID"') == requisition_id)\
    .join(fac,  req.col('"Need_FacilityID"') == fac.col('"FacilityID"'))\
    .select(req.col('"NeedID"'), req.col('"Need_FacilityID"'), req.col('"Need_DisciplineID"'), req.col('"Need_SpecialtyID"'), fac.col('"Facility_Name"'), fac.col('"Facility_State"'))\
    .collect()

    return pd.DataFrame(reqResult)
    return pd.DataFrame(req.join(fac, req.needfacilityid == fac.facilityid)
                           .select(req.needid, req.needdisciplineid, req.needspecialtyid,
                                   fac.facilityid, fac.facilityname, fac.facilitystate)
                           .where(req.needid == requisition_id)
                           .collect())


def get_nurses(session: Session) -> pd.DataFrame:
    return pd.DataFrame(session.table('NURSES').collect())


def get_nurse_specialty(session: Session, requisition: pd.DataFrame) -> pd.DataFrame:
    dis = session.table('DISCIPLINE').filter(col('"DisciplineID"') == requisition['Need_DisciplineID'][0])
    spe = session.table('SPECIALITY').filter(col('"SpecialtyId"') == requisition['Need_SpecialtyID'][0])

    return pd.DataFrame(dis.join(spe, dis.col('"NurseID"') == spe.col('"NurseID"') ).select(dis.col('"NurseID"')).distinct().collect())
    

def _score_licensure(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    eNLC_states = [
        'AL', 'AZ', 'AR', 'CO', 'DE', 'FL', 'GA', 'ID', 'IN', 'IA', 'KS', 'KY',
        'LA', 'ME', 'MD', 'MS', 'MO', 'MT', 'NE', 'NH', 'NJ', 'NM', 'NC', 'ND',
        'OH', 'OK', 'PA', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
        'WI', 'WY'
    ]
    requisition_state = requisition['Facility_State'][0]
    requisition_in_eNLC = requisition_state in eNLC_states

    nurse_df['Score_License'] = nurse_df.apply(lambda row : 1 if (requisition_in_eNLC and row['State'] in eNLC_states) or (row['State'] == requisition_state) else 0, axis=1)

    return nurse_df

def _score_specialty(nurse_df: pd.DataFrame, requisition: pd.DataFrame, nurse_specialty_df: pd.DataFrame) -> pd.DataFrame:
    discipline_id = requisition['Need_DisciplineID'][0]
    specialty_id = requisition['Need_SpecialtyID'][0]

    #nurse_df['Score_Specialty'] = nurse_df.apply(lambda row :

    # Filter out any nurses without the proper discipline
    nurse_df = nurse_df[nurse_df['NURSEDISCIPLINEID'] == discipline_id]

    # TODO: populate nurse's specialty(ies)
    # Score based on the specialty (not discipline)
    # nurse_df['SPECIALTYSCORE'] = (nurse_df['NURSESPECIALTYID'] == specialty_id).astype(int)
    return nurse_df


def score_nurses(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    nurse_df = _score_licensure(nurse_df, requisition)
    #nurse_df = _score_specialty(nurse_df, requisition, nurse_specialty_df)
    #nurse_df = _score_proximity(nurse_df, requisition)
    
    nurse_df['Total_Score'] = nurse_df.apply(lambda row : row['Score_License'], axis=1)

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
