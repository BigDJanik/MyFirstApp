from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import pandas as pd
from io import StringIO

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

@app.get("/level-3/wins")
async def get_info():
    raw_data = FileHandler()
    raw_data_df = pd.DataFrame(raw_data["games"])

    condition_1 = raw_data_df["points_scored"] - raw_data_df["points_allowed"] > 3
    condition_2 = raw_data_df["points_scored"] - raw_data_df["points_allowed"] < 0

    prepared_data_df = raw_data_df.copy()
    prepared_data_df["true wins"] = condition_1 | condition_2

    return prepared_data_df.to_json(orient="index")

@app.get("/level-3/info_notes")
async def get_info():
    info_notes = """
                    **Heimvorteil sind +3 Punkte im Handicap**  
                    *(Modellierte Annahme)*
                    
                    ---

                    Erklärung:
            
                    Die Schätzung des Heimvorteils in der NFL auf ungefähr 2,5 bis 3 Punkte pro Spiel basiert auf einer Kombination von historischen Daten, Studien und Erfahrungen von Sportanalysten. Es ist wichtig zu beachten, dass dies eine allgemeine Schätzung ist und keine exakte wissenschaftliche Berechnung darstellt. Hier sind einige der Quellen und Grundlagen, auf denen diese Schätzung basiert:

                    - **Historische Daten:** Durch die Analyse von jahrzehntelangen NFL-Spielprotokollen können Sportanalysten Muster erkennen, die darauf hinweisen, dass Teams, die zu Hause spielen, tendenziell bessere Ergebnisse erzielen als bei Auswärtsspielen. Dies kann als Ausgangspunkt für die Schätzung des Heimvorteils dienen.

                    - **Akademische Studien:** Es gibt einige akademische Studien und wissenschaftliche Arbeiten, die den Heimvorteil im Sport, einschließlich der NFL, untersuchen. Diese Studien nutzen statistische Methoden, um den Heimvorteil zu quantifizieren. Obwohl die Ergebnisse variieren können, zeigen viele dieser Studien einen Heimvorteil von etwa 2,5 bis 3 Punkten pro Spiel.

                    - **Erfahrung von Sportanalysten:** Sportexperten und Analysten, die die NFL und andere Sportligen abdecken, bringen ihre Erfahrung und Einsichten in die Schätzung des Heimvorteils ein. Dies kann auf beobachteten Mustern und ihrer Kenntnis der Dynamik von Heim- und Auswärtsspielen basieren.
                    """

    return HTMLResponse(content=info_notes)

@app.get("/level-4/scoring")
async def get_scoring_means(home_team, away_team):
    
    home_stats = await get_stats(team_type="team")
    away_stats = await get_stats(team_type="opponent")
    
    home_stats = pd.read_json(StringIO(home_stats), orient="index")
    away_stats = pd.read_json(StringIO(away_stats), orient="index")
    
    scoring_means = {}
    
    home_scoring_mean = home_stats[home_stats["team"] == home_team][
            "points_scored"
        ].values[0]
    scoring_means["home_scoring_mean"] = home_scoring_mean
    
    away_scoring_mean = away_stats[away_stats["opponent"] == away_team][
            "points_scored"
        ].values[0]
    scoring_means["away_scoring_mean"] = away_scoring_mean
    
    home_allowed_mean = home_stats[home_stats["team"] == home_team][
            "points_allowed"
        ].values[0]
    scoring_means["home_allowed_mean"] = home_allowed_mean
    
    away_allowed_mean = away_stats[away_stats["opponent"] == away_team][
            "points_allowed"
        ].values[0]
    scoring_means["away_allowed_mean"] = away_allowed_mean
    
    return scoring_means

@app.get("/level-5/prediction")
async def predict(home_team, away_team):
    scoring_means = await get_scoring_means(home_team=home_team, away_team=away_team)
    home_pred = (scoring_means["home_scoring_mean"] + scoring_means["away_allowed_mean"]) / 2
    away_pred = (scoring_means["away_scoring_mean"] + scoring_means["home_allowed_mean"]) / 2

    spread_pred = home_pred - away_pred

    if spread_pred > 0:
        winner = home_team
        spread_pred *= -1

    else:
        winner = away_team
        spread_pred = spread_pred
    
    return {"winner": winner, "spread_pred": spread_pred}
