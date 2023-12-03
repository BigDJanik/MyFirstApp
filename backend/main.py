from fastapi import FastAPI
import json

path = "data/nfl_data.json"


app = FastAPI()                 # Öffnet eine Applikation

@app.get("/data")
async def get_data():           # Ermöglicht asynchrone Kommunikation
    with open(file=path, mode="r") as raw_file:
        data = json.load(raw_file)
    return data

@app.get("/teams")
async def get_teams():
    with open(file=path, mode="r") as raw_file:
        data = json.load(raw_file)
    return data["teams"]