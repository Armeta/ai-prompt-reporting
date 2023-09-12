from src.lib import code_library as cl
import datetime
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import extra_streamlit_components as stx
def main() -> None:

    # set up environment 
    cl.env_Setup('Nurse AI', 'collapsed', {}, 'wide', 'src/media/Untitled.jpg')

    # connect to snowflake
    session = cl.snow_session()

    init_requisition_id = None
    requisition_id = None

    first_time = 'requisition_id' not in st.session_state

    if(not first_time):
        init_requisition_id = st.session_state.requisition_id
    else:
        init_requisition_id = 976660

    # Recieve user input
    str_input = st.text_input("Requisition ID Search")
    
    # test user input is valid
    if(str_input.isdigit()):
        requisition_id = int(str_input)
    elif(len(str_input) > 0):
        st.text('Invalid Requisition ID')
        return
    else:
        requisition_id = init_requisition_id

    # display current requisition
    st.text('Requisition ID: '+str(requisition_id))
    
    if first_time or init_requisition_id != requisition_id:
        # Pull requisition details from source
        with st.spinner(text="Searching for Request ID..."):
            requisition = cl.get_requisition(session, requisition_id)
        
        if(len(requisition) < 1):
                st.info('Requisition ID not found', icon="🚨")
                return
        
        # save current requsition to session
        st.session_state.requisition_id = requisition_id
        st.session_state.requisition = requisition

        # # Add requsition to history tab     
        if not requisition.empty and requisition['NeedID'].iloc[0] not in [df['NeedID'].iloc[0] for df in st.session_state.requisitions]:
            st.session_state.requisitions.append(requisition)


    # Pull Nurse dataset from source
        with st.spinner(text="Getting List of Nurses..."):
            nurse_df = cl.get_nurses(session)
            st.toast('Success! Retrieved Nurses.', icon='✅')

        # prepare nurse dataset
        with st.spinner(text="Getting Nurse Details..."):
            nurse_df    = cl.get_nurse_discipline_specialty(session, nurse_df, requisition)
            st.toast('Success! Retrieved Nurse Details.', icon='✅')

        # score nurse dataset
        with st.spinner(text="Scoring Nurses..."):
            scored_nurses                 = cl.score_nurses(nurse_df, requisition)
            valid_nurses                  = scored_nurses[scored_nurses['Fit Score'] > 0]
            sorted_nurses                 = valid_nurses.sort_values(by=['Fit Score'], ascending=False)
            topten_nurses                 = sorted_nurses.head(25)
            st.toast('Success! Scored Nurses.', icon='✅')

        # get nurse profile dataset
        with st.spinner(text="Getting Nurses Profiles..."):
            topten_nurses                 = cl.get_nurse_profile(session, topten_nurses)
            st.toast('Success! Retrieved Nurses Profiles.', icon='✅')

        # save nurse info to session
        st.session_state.topten_nurses = topten_nurses
        
        #remaining_nurses             = sorted_nurses.drop(topten_nurses.index)
         
    else: # requisition and nurses already saved
        requisition = st.session_state.requisition
        topten_nurses = st.session_state.topten_nurses
    
    chosen_id = stx.tab_bar(data=[
          stx.TabBarItemData(id=1, title="Requisition Profile"       , description="")
        , stx.TabBarItemData(id=2, title="Recommended Nurses"        , description="")
        , stx.TabBarItemData(id=3, title="Requisition Search History", description="")
        , stx.TabBarItemData(id=4, title="Give Feedback"             , description="")
    ], default = st.session_state.TabID)

    # sliding tabs for interacting with the different UI's
      # Displays information on the need most recently typed in
    if(chosen_id == '1'):
        with st.spinner(text="Drawing Charts..."):
            for index, row in requisition.iterrows():
                cl.draw_RequisitionCard(row['NeedID'], row['Need_FacilityID'], row['Facility_Name'], row['Facility_State'], row['Facility_City'], row['Discipline_Name'], row['Need_DisciplineID'], row['Specialty_Name'], row['Need_SpecialtyID'], 'Facility ID', 'Facility Name', 'Facility State', 'Facility City', 'Discipline Name', 'Discipline ID', 'Specialty Name', 'Specialty ID')          
            if(first_time):                                     
                st.toast('Welcome to Nurse AI!', icon='👩‍⚕️')
    # Gives a list of recommended nurses after a need has been typed in 
    if(chosen_id == '2'):
        # Writes the header on the Recommended Nurses page
        with st.expander("Top 25 Nurses", expanded = True):
            with st.container():
                Ccol1, Ccol2, Ccol3, Ccol4 = st.columns(4)
                with Ccol1:
                    st.write("<u>**Nurse Profile**</u>", unsafe_allow_html=True)
                with Ccol2:
                    st.write("<u>**Nurse Name**</u>", unsafe_allow_html=True)
                with Ccol3:
                    st.write("<u>**Nurse ID**</u>", unsafe_allow_html=True)
                with Ccol4:
                    st.write("<u>**Fit Score**</u>", unsafe_allow_html=True)  
            # Draws the buttons and writes out the nurse information                       
            with st.spinner(text="Retrieving Top 25 Nurse Profiles..."):              
                for index, row in topten_nurses.iterrows():

                    Ecol1, Ecol2, Ecol3, Ecol4 = st.columns(4)
                    with Ecol1:                                                
                        button_label =  f"{row['Name']}"
                        
                        # If any button is pressed we set conditions to navigate to the profile page
                        if st.button("Visit " + button_label + "'s profile", use_container_width=True):
                            st.session_state.SelectedNurse            = row
                            st.session_state.NurseName                = row['Name']
                            st.session_state.NurseID                  = f"{int(row['NurseID'])}"
                            st.session_state.FitScore                 = f"{row['Fit Score']:3.1f}"
                            st.session_state.State                    = f"{row['State']}"
                            st.session_state.City                     = f"{row['City']}"
                            st.session_state.Profile_Created_Date     = f"{datetime.date.strftime(row['Profile_Created_Date'],'%m/%d/%Y')}"
                            st.session_state.Submission_Count         = f"{int(row['Submission_Count'])}"
                            st.session_state.Contract_Count           = f"{int(row['Contract_Count'])}"
                            st.session_state.YearsOfExperience        = f"{int(row['YearsOfExperience'])}"
                            st.session_state.DaysWorked_Count         = f"{int(row['DaysWorked_Count']):,}"
                            st.session_state.LastContractEnd_Datetime = f"{datetime.date.strftime(row['LastContractEnd_Datetime'],'%m/%d/%Y')}"
                            st.session_state.Termination_Count        = f"{row['Termination_Count']}"
                            st.session_state.Distance                 = f"{int(row['Distance']):,}"
                            st.session_state.Profile_CV               = f"{row['Profile_CV']}"
                            st.session_state.Profile_Picture          = f"{row['Profile_Picture']}"
                            st.session_state.DISCIPLINES              = f"{row['DISCIPLINES']}"
                            st.session_state.SPECIALTIES              = f"{row['SPECIALTIES']}"
                            st.session_state.Email                    = f"{row['Email']}"
                            st.session_state.Phone                    = f"{row['PhoneNumber']}"
                            
                            switch_page('profile')
                    with Ecol2:                                            
                        st.markdown(f"{row['Name']}")                
                    with Ecol3:                     
                        st.markdown(f"{int(row['NurseID'])}")
                    with Ecol4:
                        st.markdown(f"{row['Fit Score']:3.1f}")     
                st.toast('Success! Retrieved Nurse Profiles.', icon='✅')           
    # Gives a running record of all searched requisitions within a user session 
    if(chosen_id == '3'):
        with st.spinner(text="Retrieving Search History..."):
            for req in st.session_state.requisitions:    
                cl.draw_RequisitionCard(req['NeedID'].iloc[0], req['Need_FacilityID'].iloc[0], req['Facility_Name'].iloc[0], req['Facility_State'].iloc[0], req['Facility_City'].iloc[0], req['Discipline_Name'].iloc[0], req['Need_DisciplineID'].iloc[0], req['Specialty_Name'].iloc[0], req['Need_SpecialtyID'].iloc[0], 'Facility ID', 'Facility Name', 'Facility State', 'Facility City', 'Discipline Name', 'Discipline ID', 'Specialty Name', 'Specialty ID')         

    if(chosen_id == '4'):        
        with st.form("Give Feedback: ", clear_on_submit=True):
            st.session_state.FeedbackRating = st.radio("Was this app helpful?", ["✅", "❌"], label_visibility='visible', disabled=False, horizontal=True, index = 0) 
            st.session_state.FeedbackText   = st.text_input("How could this app be improved?", "... ", disabled=False)   
            with st.spinner(text="Sending Feedback..."):                     
                submitted = st.form_submit_button("Submit")
                if submitted:
                    cl.write_Audit(session, st.session_state.FeedbackRating, st.session_state.FeedbackText)
                    st.toast('Success! Your feedback has been recieved. ', icon='✅') 

if __name__ == '__main__':
    main()
