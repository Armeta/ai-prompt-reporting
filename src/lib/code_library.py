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
    dis = session.table('DISCIPLINE_LKP')
    spe = session.table('SPECIALITY_LKP')

    reqResult = req.filter(col('"NeedID"') == requisition_id)\
    .join(fac,  req.col('"Need_FacilityID"') == fac.col('"FacilityID"'))\
    .join(dis,  req.col('"Need_DisciplineID"') == dis.col('"DisciplineID"'))\
    .join(spe,  req.col('"Need_SpecialtyID"') == spe.col('"SpecialtyId"'))\
    .select(req.col('"NeedID"'), req.col('"Need_FacilityID"'), req.col('"Need_DisciplineID"'), req.col('"Need_SpecialtyID"'), fac.col('"Facility_Name"'), fac.col('"Facility_State"'), fac.col('"City"').as_('"Facility_City"'), dis.col('"Discipline_Name"'), spe.col('"Specialty_Name"'))\
    .collect()

    return pd.DataFrame(reqResult)
    return pd.DataFrame(req.join(fac, req.needfacilityid == fac.facilityid)
                           .select(req.needid, req.needdisciplineid, req.needspecialtyid,
                                   fac.facilityid, fac.facilityname, fac.facilitystate)
                           .where(req.needid == requisition_id)
                           .collect())


def get_nurses(session: Session) -> pd.DataFrame:
    nurse_df = session.table('NURSES')
    
    return pd.DataFrame(nurse_df.collect())


def get_nurse_discipline_specialty(session: Session, requisition: pd.DataFrame) -> [pd.DataFrame, pd.DataFrame]:
    dis = session.table('DISCIPLINE').filter(col('"DisciplineID"') == int(requisition['Need_DisciplineID'][0])).select(col('"NurseID"').as_('"DisciplineNurseID"')).distinct()
    spe = session.table('SPECIALITY').filter(col('"SpecialtyId"') == int(requisition['Need_SpecialtyID'][0])).select(col('"NurseID"').as_('"SpecialtyNurseID"')).distinct()

    return pd.DataFrame(dis.collect()), pd.DataFrame(spe.collect())

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

def _score_discipline(nurse_df: pd.DataFrame) -> pd.DataFrame:

    nurse_df['Score_Discipline'] = nurse_df.apply(lambda row : (1 if row['HasDiscipline'] else 0), axis=1)

    return nurse_df
def _score_specialty(nurse_df: pd.DataFrame) -> pd.DataFrame:

    nurse_df['Score_Specialty'] = nurse_df.apply(lambda row : (1 if row['HasSpecialty'] else 0), axis=1)

    return nurse_df

def _score_enddate(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    today = np.datetime64('2023-08-03')

    nurse_df['Score_Enddate'] = nurse_df.apply(lambda row : 1 if pd.isna(row['LastContractEnd_Datetime']) else max(0, 1-max(0, int((row['LastContractEnd_Datetime'] - today)/np.timedelta64(1, 'D')))/35.0), axis=1)

    return nurse_df

def _score_experience(nurse_df: pd.DataFrame) -> pd.DataFrame:

    nurse_df['Score_Experience'] = nurse_df.apply(lambda row : (0 if pd.isna(row['YearsOfExperience']) else min(1, row['YearsOfExperience']/10)), axis=1)

    return nurse_df

def _score_proximity(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    requisition_state = requisition['Facility_State'][0]
    requisition_city = requisition['Facility_City'][0]

    nurse_df['Score_Proximity'] = nurse_df.apply(lambda row : (1 if row['City'] == requisition_city and row['State'] == requisition_state else (0.5 if row['State'] == requisition_state else 0)), axis=1)

    return nurse_df

def score_nurses(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    nurse_df = _score_licensure(nurse_df, requisition)
    nurse_df = _score_discipline(nurse_df)
    nurse_df = _score_specialty(nurse_df)
    nurse_df = _score_enddate(nurse_df, requisition)
    nurse_df = _score_experience(nurse_df)
    nurse_df = _score_proximity(nurse_df, requisition)


    nurse_df['Fit Score'] = nurse_df.apply(lambda row : 
                100 * row['Score_License'] * 
                (row['Score_Discipline'] * 1  +  row['Score_Specialty'] * 1 + row['Score_Enddate'] * 0.5 + row['Score_Experience'] * 0.25 + row['Score_Proximity'] * 0.125)
                / ( 1 + 1 + 0.5 + 0.25 + 0.125)
                , axis=1)
    return nurse_df
