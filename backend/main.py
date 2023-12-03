from fastapi import FastAPI
import json
import pandas as pd

path = "data/nfl_data.json"

app = FastAPI()                 # Öffnet eine Applikation

def FileHandler():
    with open(file=path, mode="r") as raw_file:
        data = json.load(raw_file)
    return data

@app.get("/level-1/data")
async def get_data():           # Ermöglicht asynchrone Kommunikation
    return FileHandler()

@app.get("/level-1/teams")
async def get_teams():
    data = FileHandler()
    return data["teams"]

@app.get("/level-2/stats")
async def get_stats(team_type:str="team"):
    raw_data  = FileHandler()
    raw_data_df = pd.DataFrame(raw_data["games"])

    stats = raw_data_df.groupby(team_type)[
        ["points_scored", "points_allowed"]
    ].mean()
    stats[team_type] = stats.index
    stats.sort_values("points_scored", ascending=False, inplace=True)
    stats.reset_index(drop=True, inplace=True)
    stats.index += 1

    return stats.to_json(orient="index")