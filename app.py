import streamlit as st
import json

def provide_raw_data(data: dict) -> None:
    with st.expander(label="Raw Data"):
        st.json(data)

    return


def main():
    st.title("NFL-Predictor")

    with open("data/nfl_data.json", mode="r") as raw_file:
        raw_data = json.load(raw_file)

        st.selectbox(label="Home Team", options=raw_data["teams"], index = 0)
        st.selectbox(label="Away Team", options=raw_data["teams"], index = 1)


        provide_raw_data(data = raw_data)

        return

if __name__ == "__main__":
    main()