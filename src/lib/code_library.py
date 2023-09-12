import numpy as np
import pandas as pd
import math
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from streamlit_extras.stylable_container import stylable_container

import extra_streamlit_components as stx
# setup connection with snowflake\
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

@st.cache_data(show_spinner = False, persist = "disk")
def get_requisition(_session: Session, requisition_id: int) -> pd.DataFrame:
    req = _session.table('NEEDS')
    fac = _session.table('FACILITY')
    dis = _session.table('DISCIPLINE_LKP')
    spe = _session.table('SPECIALITY_LKP')

    reqResult = req.filter(col('"NeedID"') == requisition_id)\
    .join(fac,  req.col('"Need_FacilityID"') == fac.col('"FacilityID"'))\
    .join(dis,  req.col('"Need_DisciplineID"') == dis.col('"DisciplineID"'))\
    .join(spe,  req.col('"Need_SpecialtyID"') == spe.col('"SpecialtyId"'))\
    .select(req.col('"NeedID"'), req.col('"Need_FacilityID"'), req.col('"Need_DisciplineID"'), req.col('"Need_SpecialtyID"'), fac.col('"Facility_Name"'), fac.col('"Lat"').as_('"Facility_Lat"'), fac.col('"Long"').as_('"Facility_Long"'), fac.col('"Facility_State"'), fac.col('"City"').as_('"Facility_City"'), dis.col('"Discipline_Name"'), spe.col('"Specialty_Name"'))\
    .collect()

    return pd.DataFrame(reqResult)
    return pd.DataFrame(req.join(fac, req.needfacilityid == fac.facilityid)
                           .select(req.needid, req.needdisciplineid, req.needspecialtyid,
                                   fac.facilityid, fac.facilityname, fac.facilitystate)
                           .where(req.needid == requisition_id)
                           .collect())

@st.cache_data(show_spinner = False, persist = "disk")
def get_nurses(_session: Session) -> pd.DataFrame:
    nurse_df_unfiltered = _session.table('NURSES')
    print(nurse_df_unfiltered)
    nurse_df = nurse_df_unfiltered.filter(
    (nurse_df_unfiltered['DISCIPLINES'].isNotNull()) &
    (nurse_df_unfiltered['SPECIALTIES'].isNotNull()) &
    (nurse_df_unfiltered['"YearsOfExperience"'].isNotNull()) &
    (nurse_df_unfiltered['"Contract_Count"'].isNotNull()) &
    (nurse_df_unfiltered['"DaysWorked_Count"'].isNotNull()) &
    (nurse_df_unfiltered['"LastContractEnd_Datetime"'].isNotNull())
    ).select(['"NurseID"', '"State"', '"Working_Status"', '"Submission_Count"', '"Contract_Count"', '"YearsOfExperience"', '"DaysWorked_Count"', '"LastContractEnd_Datetime"', '"Termination_Count"', '"Name"', '"City"', '"Lat"', '"Long"', '"DISCIPLINES"', '"SPECIALTIES"'])

    nurse_df = pd.DataFrame(nurse_df.collect())

    print(str(nurse_df.shape[0]) + ' nurses loaded')
    return nurse_df

@st.cache_data(show_spinner = False, persist = "disk")
def get_nurse_discipline_specialty(_session: Session, nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    dis = _session.table('DISCIPLINE').filter(col('"DisciplineID"') == int(requisition['Need_DisciplineID'][0])).select(col('"NurseID"').as_('"DisciplineNurseID"')).distinct()
    spe = _session.table('SPECIALITY').filter(col('"SpecialtyId"') == int(requisition['Need_SpecialtyID'][0])).select(col('"NurseID"').as_('"SpecialtyNurseID"')).distinct()

    nurse_dis_df = pd.DataFrame(dis.collect())
    nurse_spe_df = pd.DataFrame(spe.collect())

    nurse_dis_df['HasDiscipline'] = True
    nurse_spe_df['HasSpecialty']  = True
    nurse_df                      = nurse_df.join(nurse_dis_df.set_index('DisciplineNurseID'), on='NurseID', how='left').join(nurse_spe_df.set_index('SpecialtyNurseID'), on='NurseID', how='left')
    nurse_df['HasDiscipline']     = nurse_df['HasDiscipline'].notna()
    nurse_df['HasSpecialty']      = nurse_df['HasSpecialty'].notna()

    return nurse_df

@st.cache_data(show_spinner = False, persist = "disk")
def get_nurse_profile(_session: Session, nurse_df: pd.DataFrame) -> pd.DataFrame:
    profile = _session.table('NURSEPROFILE')
    needed_nurses = _session.create_dataframe(nurse_df['NurseID'].to_frame('NurseID'))

    nurses_with_profile = profile.join(needed_nurses, on='"NurseID"', how='inner')

    nurses_with_profile = pd.DataFrame(nurses_with_profile.collect())

    nurses_with_profile = nurses_with_profile.join(nurse_df.set_index('NurseID'), on='NurseID', how='inner')

    return nurses_with_profile.sort_values(by=['Fit Score'], ascending=False)

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

def _score_recency(nurse_df: pd.DataFrame) -> pd.DataFrame:
    today = np.datetime64('2023-08-03')

    nurse_df['Score_Recency'] = nurse_df.apply(lambda row : 0 if pd.isna(row['LastContractEnd_Datetime']) else max(0, 1-max(0, int((today - row['LastContractEnd_Datetime'])/np.timedelta64(1, 'D')))/365.0), axis=1)
    return nurse_df

def _score_enddate(nurse_df: pd.DataFrame) -> pd.DataFrame:
    today = np.datetime64('2023-08-03')

    nurse_df['Score_Enddate'] = nurse_df.apply(lambda row : 1 if pd.isna(row['LastContractEnd_Datetime']) else max(0, 1-max(0, int((row['LastContractEnd_Datetime'] - today)/np.timedelta64(1, 'D')))/35.0), axis=1)
    return nurse_df

def _score_experience(nurse_df: pd.DataFrame) -> pd.DataFrame:

    nurse_df['Score_Experience'] = nurse_df.apply(lambda row : (0 if pd.isna(row['YearsOfExperience']) else min(1, max(0, row['YearsOfExperience']-2)/8)), axis=1)
    return nurse_df
    
def distance(lat1, lat2, lon1, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
 
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return(c * r)

def _score_proximity(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    requisition_lat= requisition['Facility_Lat'][0]
    requisition_long = requisition['Facility_Long'][0]

    nurse_df['Distance'] = nurse_df.apply(lambda row : -1 if pd.isna(distance(requisition_lat, row['Lat'], requisition_long, row['Long'])) else int(distance(requisition_lat, row['Lat'], requisition_long, row['Long'])), axis=1)
    nurse_df['Score_Proximity'] = nurse_df.apply(lambda row : max(0, 1 - distance(requisition_lat, row['Lat'], requisition_long, row['Long'])/500.0), axis=1)
    return nurse_df
    #requisition_state = requisition['Facility_State'][0]
    #requisition_city = requisition['Facility_City'][0]
    #nurse_df['Score_Proximity'] = nurse_df.apply(lambda row : (1 if row['City'] == requisition_city and row['State'] == requisition_state else (0.5 if row['State'] == requisition_state else 0)), axis=1)

def score_nurses(nurse_df: pd.DataFrame, requisition: pd.DataFrame) -> pd.DataFrame:
    nurse_df = _score_licensure(nurse_df, requisition)
    nurse_df = _score_discipline(nurse_df)
    nurse_df = _score_specialty(nurse_df)
    nurse_df = _score_recency(nurse_df)
    nurse_df = _score_enddate(nurse_df)
    nurse_df = _score_experience(nurse_df)
    nurse_df = _score_proximity(nurse_df, requisition)


    nurse_df['Fit Score'] = nurse_df.apply(lambda row : 
                100 * row['Score_License'] * 
                (   row['Score_Discipline'] * 1
                  + row['Score_Specialty'] * 1
                  + row['Score_Recency'] * 0.75 
                  + row['Score_Enddate'] * 0.5 
                  + row['Score_Experience'] * 0.25 
                  + row['Score_Proximity'] * 0.125)
                / ( 1 + 1 + 0.75 + 0.5 + 0.25 + 0.125)
                , axis=1)
    return nurse_df

def env_Setup(Page_Title, Side_Bar_State, Menu_Items, Layout, Title_Image_Path):

    # set page details
    st.set_page_config(
          page_title            = Page_Title
        , initial_sidebar_state = Side_Bar_State
        , menu_items            = Menu_Items
        , layout                = Layout
    )

    if(len(Title_Image_Path) > 0):
        st.image(Title_Image_Path)

    # Open CSS file
    with open('src/css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    f.close()  

    if 'TabID' not in st.session_state:
        st.session_state.TabID = '1'
    if 'NurseName' not in st.session_state:
        st.session_state.NurseName = ''  
    if 'NurseID' not in st.session_state:
        st.session_state.NurseID = ''
    if 'FitScore' not in st.session_state:
        st.session_state.FitScore = ''
    if 'requisitions' not in st.session_state:
        st.session_state.requisitions = []
    if 'State' not in st.session_state:
        st.session_state.State = ''
    if 'ProfileCreatedDate' not in st.session_state:
        st.session_state.ProfileCreatedDate = ''
    if 'City' not in st.session_state:
        st.session_state.City = ''
    if 'Profile_Created_Date' not in st.session_state:
        st.session_state.Profile_Created_Date = ''
    if 'Submission_Count' not in st.session_state:
        st.session_state.Submission_Count = ''
    if 'Contract_Count' not in st.session_state:
        st.session_state.Contract_Count = ''
    if 'YearsOfExperience' not in st.session_state:
        st.session_state.YearsOfExperience = ''
    if 'DaysWorked_Count' not in st.session_state:
        st.session_state.DaysWorked_Count = ''
    if 'LastContractEnd_Datetime' not in st.session_state:
        st.session_state.LastContractEnd_Datetime = ''
    if 'Termination_Count' not in st.session_state:
        st.session_state.Termination_Count = ''
    if 'Distance' not in st.session_state:
        st.session_state.Distance = ''
    if 'Profile_CV' not in st.session_state:
        st.session_state.Profile_CV = ''    
    if 'Profile_Picture' not in st.session_state:
        st.session_state.Profile_Picture = ''    
    if 'DISCIPLINES' not in st.session_state:
        st.session_state.DISCIPLINES = ''    
    if 'SPECIALTIES' not in st.session_state:
        st.session_state.SPECIALTIES = ''        

def draw_SmallCard(col1, col2, col3, col4, dn1, dn2, dn3, dn4):
    with stylable_container(
        key="stylizedContainer1",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-color: #002e5d;
                border-radius: 0.5rem;
                padding: calc(1em - 1px)
            }
            """,
    ):
        col11, col12 = st.columns([1,2])
        with col11: 
            st.write(f"**{dn1}:**")
            st.write(f"**{dn2}:**")
            st.write(f"**{dn3}:**")
            st.write(f"**{dn4}:**")                      
        with col12:
            st.write(f"{col1}")
            st.write(f"{col2}")
            st.write(f"{col3}")
            st.write(f"{col4}")    

def draw_MediumCard(col1, col2, col3, col4, dn1, dn2, dn3, dn4):
    with stylable_container(
        key="stylizedContainer2",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-color: #002e5d;
                border-radius: 0.5rem;
                padding: calc(1em - 1px)
            }
            """,
    ):
        col11, col12 = st.columns([1,3])
        with col11: 
            st.write(f"**{dn1}:**")
            st.write(f"**{dn2}:**")
            st.write(f"**{dn3}:**")
            st.write(f"**{dn4}:**")                      
        with col12:
            st.write(f"{col1}")
            st.write(f"{col2}")
            st.write(f"{col3}")
            st.write(f"{col4}")    

def draw_BigCard(col1, col2, col3, col4, col5, col6, col7, col8, col9, dn1, dn2, dn3, dn4, dn5, dn6, dn7, dn8, dn9):
    with stylable_container(
        key="stylizedContainer3",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                border-color: #002e5d;
                padding: calc(1em - 1px);
                height: 500px
            }
            """,
    ):
        col11, col12 = st.columns([1,3])
        with col11: 
            st.write(f"**{dn1}:**")
            st.write(f"**{dn2}:**")
            st.write(f"**{dn3}:**")
            st.write(f"**{dn4}:**") 
            st.write(f"**{dn5}:**")
            st.write(f"**{dn6}:**")
            st.write(f"**{dn7}:**")
            st.write(f"**{dn8}:**")
            st.write(f"**{dn9}:**")
                                              
        with col12:
            st.write(f"{col1}")
            st.write(f"{col2}")
            st.write(f"{col3}")
            st.write(f"{col4}")  
            st.write(f"{col5}")
            st.write(f"{col6}")
            st.write(f"{col7}")
            st.write(f"{col8}")
            st.write(f"{col9}")
            

