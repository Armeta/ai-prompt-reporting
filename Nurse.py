from fns import preprocess_features, drop_features, get_values_and_labels, predict_fit_score
from typing import Tuple, List

import pickle
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
import numpy as np

from streamlit_searchbox import st_searchbox
from snowflake.snowpark.session import Session

from typing import Union
session = Session.builder.configs({
    'account': st.secrets['account'],
    'user': st.secrets['user'], 
    'password': st.secrets['password'],
    'role': st.secrets['role'],
    'warehouse': st.secrets['warehouse'],
    'database': st.secrets['database'],
    'schema': st.secrets['schema']
}).create()


def main():
    st.set_page_config(
        page_title="Nurse Matching",
        layout='wide',
        initial_sidebar_state='collapsed',
        menu_items={},
    )

    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.markdown("# Nurse Matching")

    searchbox_col, confirm_col = st.columns([0.9, 0.1])

    nurse_id: Union[int, None] = None
    with searchbox_col:
        nurse_id = st_searchbox(search_nurse, key='nurse_search')

    with confirm_col:
        if st.button("Confirm", type='primary'):
            st.session_state['nurse_id'] = nurse_id

    if 'nurse_id' in st.session_state and st.session_state['nurse_id'] == nurse_id:
        nurse_id = st.session_state['nurse_id']

        model = pickle.load(open('../model-files/new_features_model.pkl', 'rb'))

        load_nurse_profile(nurse_id)

        if 'nurse_matched_df' not in st.session_state:
            st.session_state['nurse_matched_df'] = match_nurse_to_needs(nurse_id)

        st.markdown("## Matching Results")
        df = st.session_state['nurse_matched_df']

        df = df[df['PREDICTEDFITSCORE'] >= 70]

        group_col, specialty_col = st.columns(2)

        values, labels = get_values_and_labels(df, 'FACSTATE')
        source = pd.DataFrame({
            'State': labels,
            '# Of Needs': values,
        })

        group_col.markdown("### State of Facility")
        group_col.altair_chart(alt.Chart(source).mark_arc(innerRadius=50).encode(
            theta='# Of Needs',
            color='State:N',
        ))


        df = drop_features(df, 'nurse')
        
        final_df = df.sort_values(by=['PREDICTEDFITSCORE'], ascending=False) \
                     .reset_index() \
                     .drop(['index'], axis=1)

        st.markdown("### Needs")
        st.dataframe(final_df)


def search_nurse(nurse_id: str) -> List[int]:
    query = session.sql(f"""
        SELECT nurseid
        FROM trs.dbo.nurseprofile
        WHERE nurseid LIKE '{nurse_id}%'
        LIMIT 10
    """)
    nurse_df = pd.DataFrame(query.collect())
    return List(nurse_df['NURSEID'])


def load_nurse_profile(nurse_id: int) -> None:
    if 'nurse_df' not in st.session_state:
        query = f"""
            SELECT  CONCAT(NPRF.fname, ' ', NPRF.lname)                             AS fullname,
                    NPRF.status,
                    DISC.disciplinename                                             AS discipline,
                    NPRF.grade,
                    CONCAT(NADR.permcity, ', ', NADR.permstate, ' ', NADR.permzip)  AS address
            FROM trs.dbo.nurseprofile                   NPRF
            LEFT JOIN trsreporting.dev.lkp_discipline   DISC ON NPRF.disciplineid   = DISC.disciplineid
            LEFT JOIN trs.dbo.nurseaddresses            NADR ON NPRF.nurseid        = NADR.nurseid
            WHERE   NPRF.nurseid        = {nurse_id}
                AND NADR.ismostcurrent  = TRUE
        """
        st.session_state['nurse_df'] = pd.DataFrame(session.sql(query).collect())

    nurse_df = st.session_state['nurse_df']

    name_col, discipline_col, address_col = st.columns(3)
    name_col.metric("Full Name", nurse_df['FULLNAME'][0])
    discipline_col.metric("Discipline", nurse_df['DISCIPLINE'][0])
    address_col.metric("Permanent Address", nurse_df['ADDRESS'][0])

    status_col, grade_col = st.columns(2)
    status_col.metric("Status", nurse_df['STATUS'][0])
    grade_col.metric("Grade", nurse_df['GRADE'][0])


def match_nurse_to_needs(nurse_id: int) -> pd.DataFrame:
    print("nurse id: ", nurse_id)
    features = session.sql(f"""
        WITH nurse
        AS (
            SELECT  DISC.disciplinename AS nursediscipline,
                    NADR.permcity,
                    NADR.permstate,
                    NADR.permzip
            FROM trs.dbo.nurseprofile                   AS NPRF
            LEFT JOIN trs.dbo.nurseaddresses            AS NADR ON  NPRF.nurseid        = NADR.nurseid
            LEFT JOIN trsreporting.dev.lkp_discipline   AS DISC ON  NPRF.disciplineid   = DISC.disciplineid
            WHERE   NPRF.nurseid         = {nurse_id}
                AND NADR.ismostcurrent   = TRUE
        )
        SELECT
            NEED.needid,
            FACL.faccity,
            FACL.facstate,
            FACL.faczip,
            FACL."GROUP",
            FACL.facilitygrade,
            FACL.numofbeds,
            SPEC.specialtyname  AS needspecialty,
            DISC.disciplinename AS needdiscipline,
            NEED.weeklygross,
            NEED.hourlymeals,
            NEED.hourlylodging,
            NEED.taxedhourly,
            NEED.jobgrade,
            NEED."LENGTH",
            NEED.totalreghours,
            NEED.totalpremhours,
            NEED.totalothours,
            NEED.totalhourly,
            FBRS.regulartime,
            NURS.nursediscipline,
            NURS.permcity,
            NURS.permstate,
            NURS.permzip
        FROM trsreporting.dev.fact_NSC              AS FNSC
        LEFT JOIN trs.dbo.facilities                AS FACL ON  FNSC.needfacilityid = FACL.facilityid
        LEFT JOIN trs.dbo.needs                     AS NEED ON  FNSC.needid         = NEED.needid
        LEFT JOIN trs.dbo.facilitybillrates         AS FBRS ON  NEED.rateid         = FBRS.rateid
        LEFT JOIN trsreporting.dev.lkp_discipline   AS DISC ON  NEED.disciplineid   = DISC.disciplineid
        LEFT JOIN trsreporting.dev.lkp_specialty    AS SPEC ON  NEED.specialtyid    = SPEC.specialtyid
        CROSS JOIN nurse NURS
        ;
    """)
    df = pd.DataFrame(features.collect())
    df_preprocessed = preprocess_features(df)

    beginning_columns = ['PREDICTEDFITSCORE']

    df['PREDICTEDFITSCORE'] = predict_fit_score(df_preprocessed.drop(['NEEDID'], axis=1))
    df = df[beginning_columns + [col for col in df.columns if col not in beginning_columns]]

    return df


if __name__ == '__main__':
    main()
