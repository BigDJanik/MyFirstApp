import requests
from io import StringIO
import streamlit as st
import json
import pandas as pd

# Fürs containern ändern:
#URL = "http://172.17.0.1:8000"
URL = "http://127.0.0.1:8000"

ENDPOINT_DATA = URL + "/level-1/data"
ENDPOINT_TEAMS = URL + "/level-1/teams"
ENDPOINT_STATS = URL + "/level-2/stats"
ENDPOINT_WINS = URL + "/level-3/wins"
ENDPOINT_INFO = URL + "/level-3/info_notes"
ENDPOINT_SCORING = URL + "/level-4/scoring"
ENDPOINT_PREDICTION = URL + "/level-5/prediction"


def provide_raw_data():
    
    response = requests.get(url=ENDPOINT_DATA)
    raw_data = response.json()

    with st.expander(label="Raw Data"):
        st.json(raw_data)
    return

def provide_derived_data():
    with st.expander(label="Insights"):
        
        team_types = ["team", "opponent"]
        for team_type in team_types:
            if team_type == "team":
                label = "Home"
            else:
                label = "Away"
        
            st.subheader(f"{label} Insights")
        
            response = requests.get(url=ENDPOINT_STATS, params={"team_type": team_type})
            raw_data = response.json()
            df = pd.read_json(StringIO(raw_data), orient="index")
            st.write(df)
    return

def provide_algorithm():
    with st.expander("Algorithm for Home Advantage"):
        st.markdown(
            # info_notes
            requests.get(url=ENDPOINT_INFO).text        # Abrufen der Info Notes
        )

        data = requests.get(url=ENDPOINT_WINS).json()
        prepared_data = pd.read_json(StringIO(data), orient="index")

        st.write(prepared_data)
    return

def provide_decision_support(home_team, away_team):
    
    response = requests.get(ENDPOINT_SCORING, params=({"home_team": home_team, "away_team": away_team}))
    scoring_means = response.json()
    
    with st.expander("Metrics for Decision"):
        first_col, second_col = st.columns(2)

        first_col.metric(label="Home scoring mean", value=scoring_means["home_scoring_mean"])
        second_col.metric(label="Away scoring mean", value=scoring_means["away_scoring_mean"])
        first_col.metric(label="Home allowed mean", value=scoring_means["home_allowed_mean"])
        second_col.metric(label="Away allowed mean", value=scoring_means["away_allowed_mean"])
    return

def provide_automated_decision(
    home_team,
    away_team,
):
    response = requests.get(ENDPOINT_PREDICTION, params=({"home_team": home_team, "away_team": away_team}))
    response = response.json()
    
    winner = response["winner"]
    spread_pred = response["spread_pred"]
    
    with st.expander("Prediction"):

        st.success(f"{winner} wins with a handicap of {spread_pred} points.")
        
    return


def main():
    st.title("NFL-Predictor")

    response = requests.get(url = ENDPOINT_TEAMS)
    teams = response.json()
    home_team = st.selectbox(label="Home", options=teams, index=0)
    away_team = st.selectbox(label="Away", options=teams, index=1)

    # Level 1
    provide_raw_data()

    # Level 2
    provide_derived_data()

    # Level 3
    provide_algorithm()

    # Level 4
    provide_decision_support(home_team, away_team)

    # Level 5
    provide_automated_decision(
        home_team,
        away_team,
    )   
    return


if __name__ == "__main__":
    main()