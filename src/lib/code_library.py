import numpy as np
import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from streamlit_extras.stylable_container import stylable_container

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


@st.cache_data
def get_requisition(_session: Session, requisition_id: int) -> pd.DataFrame:
    req = _session.table('NEEDS')
    fac = _session.table('FACILITY')
    dis = _session.table('DISCIPLINE_LKP')
    spe = _session.table('SPECIALITY_LKP')

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

@st.cache_data
def get_nurses(_session: Session) -> pd.DataFrame:
    nurse_df = _session.table('NURSES')
    
    return pd.DataFrame(nurse_df.collect())

@st.cache_data
def get_nurse_discipline_specialty(_session: Session, requisition: pd.DataFrame) -> [pd.DataFrame, pd.DataFrame]:
    dis = _session.table('DISCIPLINE').filter(col('"DisciplineID"') == int(requisition['Need_DisciplineID'][0])).select(col('"NurseID"').as_('"DisciplineNurseID"')).distinct()
    spe = _session.table('SPECIALITY').filter(col('"SpecialtyId"') == int(requisition['Need_SpecialtyID'][0])).select(col('"NurseID"').as_('"SpecialtyNurseID"')).distinct()

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

def env_Setup():
    # set page details
    st.set_page_config(
        page_title="Nurse AI",
        initial_sidebar_state='collapsed',
        menu_items={},
        layout='wide'
    )
    
    st.image('src/media/Untitled.jpg')

    # Open CSS file
    with open('src/css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    f.close()
    if 'navigated' not in st.session_state:
        st.session_state.navigated = False
    if 'NurseName' not in st.session_state:
        st.session_state.NurseName = ''  
    if 'NurseID' not in st.session_state:
        st.session_state.NurseID = ''
    if 'FitScore' not in st.session_state:
        st.session_state.FitScore = ''
    if 'requisitions' not in st.session_state:
        st.session_state.requisitions = []

def draw_Card(row, col1, col2, col3, col4, dn1, dn2, dn3, dn4):
    with stylable_container(
        key="stylizedContainer",
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
            st.write(f"**{dn1}:**")
            st.write(f"**{dn2}:**")
            st.write(f"**{dn3}:**")
            st.write(f"**{dn4}:**")                      
        with col12:
            st.write(f"{row[col1]}")
            st.write(f"{row[col2]}")
            st.write(f"{row[col3]}")
            st.write(f"{row[col4]}")    

