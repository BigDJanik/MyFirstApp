from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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