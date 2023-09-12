from src.lib import code_library as cl

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_extras.switch_page_button import switch_page


def main() -> None:
    # set up environment 
    cl.env_Setup('FitScore Page', 'collapsed', {}, 'wide', 'src/media/Untitled.jpg')    
    st.markdown("---")
    if 'requisition' in st.session_state and 'topten_nurses' in st.session_state:
        requisition = st.session_state.requisition
        requisition = prettify_requisition(requisition)

        nurse_df = st.session_state.topten_nurses
        nurse_df.index = np.arange(1, len(nurse_df) + 1)
        nurse_df = prettify_nurses(nurse_df)

        st.markdown("## Requisition")
        st.dataframe(requisition, hide_index=True)

        st.markdown(f"## Top {len(nurse_df)} Nurses")
        st.dataframe(nurse_df)

        # Nurse score distribution
        nurse_scores = st.session_state.all_nurse_scores
        st.markdown(f"## Fit Score Distributions")
        st.markdown(f"### Total: {len(nurse_scores)}")
        bin_params = alt.BinParams(extent=[10, 100], step=10)
        st.altair_chart(
            alt.Chart(data=nurse_scores)
               .mark_bar(size=30)
               .encode(alt.X('Fit Score'), y='count()')
               .transform_bin('Fit Score', field='Fit Score', bin=bin_params)
        )
    else:
        st.text('No Requisition Selected')

    if st.button("Return"):
        st.session_state.TabID = '1'
        switch_page('streamlit app')


def prettify_requisition(requisition_df: pd.DataFrame) -> pd.DataFrame:
    location_lambda = lambda row: f"{row['Facility_City']}, {row['Facility_State']}" 
    requisition_df['Location'] = requisition_df.apply(location_lambda, axis=1)

    coordinates_lambda = lambda row: f"{row['Facility_Lat']}, {row['Facility_Long']}"
    requisition_df['Coordinates'] = requisition_df.apply(coordinates_lambda, axis=1)

    columns = {
        'NeedID': 'Need ID',
        'Need_FacilityID': 'Facility ID',
        'Facility_Name': 'Facility Name',
        'Location': 'Facility Location',
        'Coordinates': 'Facility Coordinates',
        'Need_DisciplineID': 'Discipline ID',
        'Discipline_Name': 'Discipline Name',
        'Need_SpecialtyID': 'Specialty ID',
        'Specialty_Name': 'Specialty Name',
    }

    # Rearrange columns
    requisition_df = requisition_df[list(columns.keys())]
    return requisition_df.rename(columns=columns)


def prettify_nurses(nurse_df: pd.DataFrame) -> pd.DataFrame:
    location_lambda = lambda row: f"{row['City']}, {row['State']}" 
    nurse_df['Location'] = nurse_df.apply(location_lambda, axis=1)

    coordinates_lambda = lambda row: f"{row['Lat']}, {row['Long']}"
    nurse_df['Coords'] = nurse_df.apply(coordinates_lambda, axis=1)

    int_cols = ['NurseID', 'YearsOfExperience']
    nurse_df[int_cols] = nurse_df[int_cols].astype(int)

    bool_cols = ['HasDiscipline', 'HasSpecialty']
    bool2str = {True: 'Yes', False: 'No'}
    nurse_df[bool_cols] = nurse_df[bool_cols].replace(bool2str)

    columns={
        'NurseID': 'Nurse ID',
        'Name': 'Name',
        'Fit Score': 'Fit Score',
        'Score_License': 'License Score',
        'Score_Discipline': 'Discipline Score',
        'Score_Specialty': 'Specialty Score',
        'Score_Recency': 'Recency Score',
        'Score_Enddate': 'Contract End Date Score',
        'Score_Experience': 'Experience Score',
        'Score_Proximity': 'Proximity Score',
        'HasDiscipline': 'Has Discipline',
        'HasSpecialty': 'Has Specialty',
        'LastContractEnd_Datetime': 'Contract End Timestamp',
        'YearsOfExperience': 'Years of Experience',
        'Location': 'Location',
        'Coords': 'Location Coordinates',
        'Distance': 'Distance (miles)',
    }

    nurse_df = nurse_df[list(columns.keys())]
    return nurse_df.rename(columns=columns)


if __name__ == '__main__':
    main()
