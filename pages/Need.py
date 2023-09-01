from fns import preprocess_features, drop_features, predict_fit_score

import streamlit as st
import pandas as pd
import pickle

from snowflake.snowpark.session import Session
from streamlit_searchbox import st_searchbox

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
        page_title="Need Matching",
        layout='wide',
        initial_sidebar_state='expanded',
        menu_items={},
    )

    # st.dataframe(pd.DataFrame({
    #     'FITSCORE': [90.1, 85.21, 72.98],
    #     'NURSEID': [231551, 214759, 346128],
    #     'NAME': ["John Manfield", "Jim Shustberg", "Koby Bryant"],
    #     'ADDRESS': ["Manfield, MT 78214", "Boulder, CO 89123", "San Francisco, CA 65212"],
    # }))

    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.markdown("# Need Dashboard")

    searchbox_col, confirm_col = st.columns([0.9, 0.1])

    need_id: int | None = None
    with searchbox_col:
        need_id = st_searchbox(search_need, key='need_search')

    with confirm_col:
        if st.button("Confirm", type='primary'):
            st.session_state['need_id'] = need_id

    if 'need_id' in st.session_state:
        need_id = st.session_state['need_id']

        model = pickle.load(open('../model-files/new_features_model.pkl', 'rb'))

        load_need_profile(need_id)

        st.markdown("## Matching Results")
        df = match_need_to_nurses(need_id)

        # df = df[df['PREDICTEDFITSCORE'] >= 70]

        st.dataframe(df)

        df = drop_features(df, 'need')

        final_df = df.sort_values(by=['PREDICTEDFITSCORE'], ascending=False) \
                     .reset_index() \
                     .drop(['index'], axis=1)

        st.markdown("### Nurses")
        st.dataframe(final_df)


def search_need(need_id: str) -> list[int]:
    print(f"need id: {need_id}")
    query = session.sql(f"""
        SELECT needid
        FROM trsreporting.dev.fact_nsc
        WHERE needid LIKE '{need_id}%'
        LIMIT 10
    """)
    need_df = pd.DataFrame(query.collect())
    return list(need_df['NEEDID'])


def load_need_profile(need_id: int) -> None:
    query = f"""
        SELECT
            FACL.facname,
            FACL."GROUP",
            CONCAT(FACL.faccity, ', ', FACL.facstate, ' ', FACL.faczip) AS address,
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
            FBRS.regulartime
        FROM trsreporting.dev.fact_NSC              AS FNSC
        LEFT JOIN trs.dbo.facilities                AS FACL ON  FNSC.needfacilityid = FACL.facilityid
        LEFT JOIN trs.dbo.needs                     AS NEED ON  FNSC.needid         = NEED.needid
        LEFT JOIN trs.dbo.facilitybillrates         AS FBRS ON  NEED.rateid         = FBRS.rateid
        LEFT JOIN trsreporting.dev.lkp_discipline   AS DISC ON  NEED.disciplineid   = DISC.disciplineid
        LEFT JOIN trsreporting.dev.lkp_specialty    AS SPEC ON  NEED.specialtyid    = SPEC.specialtyid
        WHERE NEED.needid = {need_id}
    """
    df = pd.DataFrame(session.sql(query).collect())

    col1, col2, col3 = st.columns(3)
    col1.metric("Facility Name", df['FACNAME'][0])
    col2.metric("Facility Group", df['GROUP'][0])
    col3.metric("Facility Address", df['ADDRESS'][0])

    col1, col2 = st.columns(2)
    col1.metric("Specialty", df['NEEDSPECIALTY'][0])
    col2.metric("Discipline", df['NEEDDISCIPLINE'][0])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Weekly Gross", f"${df['WEEKLYGROSS'][0]:.2f}")
    col2.metric("Hourly Meals", f"${df['HOURLYMEALS'][0]:.2f}")
    col3.metric("Hourly Lodging", f"${df['HOURLYLODGING'][0]:.2f}")
    col4.metric("Length", f"{df['LENGTH'][0]} Weeks")
    col5.metric("Total Hours", f"{df['TOTALREGHOURS'][0]}")


def match_need_to_nurses(need_id):
    query = f"""
        WITH need
        AS (
            SELECT
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
                FBRS.regulartime
            FROM trsreporting.dev.fact_NSC              AS FNSC
            LEFT JOIN trs.dbo.facilities                AS FACL ON  FNSC.needfacilityid = FACL.facilityid
            LEFT JOIN trs.dbo.needs                     AS NEED ON  FNSC.needid         = NEED.needid
            LEFT JOIN trs.dbo.facilitybillrates         AS FBRS ON  NEED.rateid         = FBRS.rateid
            LEFT JOIN trsreporting.dev.lkp_discipline   AS DISC ON  NEED.disciplineid   = DISC.disciplineid
            LEFT JOIN trsreporting.dev.lkp_specialty    AS SPEC ON  NEED.specialtyid    = SPEC.specialtyid
            WHERE NEED.needid = 598874
        )
        SELECT  
            NPRF.nurseid,
            NEED.faccity,
            NEED.facstate,
            NEED.faczip,
            NEED."GROUP",
            NEED.facilitygrade,
            NEED.numofbeds,
            NEED.needspecialty,
            NEED.needdiscipline,
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
            NEED.regulartime,
            DISC.disciplinename AS nursediscipline,
            NADR.permcity,
            NADR.permstate,
            NADR.permzip
        FROM trs.dbo.nurseprofile                   AS NPRF
        LEFT JOIN trs.dbo.nurseaddresses            AS NADR ON  NPRF.nurseid        = NADR.nurseid
        LEFT JOIN trsreporting.dev.lkp_discipline   AS DISC ON  NPRF.disciplineid   = DISC.disciplineid
        CROSS JOIN need
        ;
    """
    df = pd.DataFrame(session.sql(query).collect())

    df_preprocessed = preprocess_features(df)
    st.dataframe(df_preprocessed)

    beginning_columns = ['PREDICTEDFITSCORE']

    df['PREDICTEDFITSCORE'] = predict_fit_score(df_preprocessed.drop(['NURSEID'], axis=1))
    df = df[beginning_columns + [col for col in df.columns if col not in beginning_columns]]

    return df


if __name__ == '__main__':
    main()
