# Fetches runs from every category in the series using the speedrun.com api and writes them to runs.csv

import requests, csv, pathlib, time

API = "https://www.speedrun.com/api/v1/"
SERIES_ID = "5nk5epn9"

def RequestAPI(request):
    while True:
        Response = requests.get(request)
        if Response.status_code == 420:
            print(f"Rate Limited! Waiting 15 seconds...")
            time.sleep(15)
            continue
        break
    return Response.json()["data"]

def FetchRuns(seriesID: str):
    pathlib.Path("output").mkdir(exist_ok=True)

    with open(f"output/runs.csv", "w", newline="", encoding="utf-8") as RunsFile:
        RunsWriter = csv.writer(RunsFile)
        RunsWriter.writerow(["game","category","subcategory","category_id","player","time","date","platform","emulator","run_id"])

        # Get the list of games from the series endpoint.
        SeriesData = RequestAPI(API + "/series/" + seriesID + "/games")
        Games = [x["id"] for x in sorted(SeriesData, key=lambda x: (x["release-date"])) if x["id"] != "m1mprj12"]   # Orders by release date with Category Extensions last

        # For each game...
        for GameID in Games:
            GameData = RequestAPI(API + "/games/" + GameID + "?embed=platforms,variables,categories")
            GameName = GameData["names"]["international"]
            GamePlatforms = {x["id"]: x["name"] for x in GameData["platforms"]["data"]}
            GameCategories = [x for x in GameData["categories"]["data"]]
            GameVariables = dict()

            print(f"Fetching runs from {GameName} [{GameID}]...")

            # Get variable data
            for VariableData in GameData["variables"]["data"]:
                Variables = VariableData["values"]["values"]
                VariableObsoletes = VariableData["obsoletes"]
                VariableIsSubcategory = VariableData["is-subcategory"]
                for VariableID in Variables.keys():
                    Variable = Variables[VariableID]
                    VariableName = Variable["label"]
                    if VariableIsSubcategory:
                        VariableRules = Variable["rules"]
                        VariableIsArchived = (VariableRules.split("\n")[0] == "(ARCHIVED)") if VariableRules is not None else False
                        VariableIsMisc = (Variable["flags"]["miscellaneous"] == True)
                    else:
                        VariableIsArchived = False
                        VariableIsMisc = False
                    GameVariables[VariableID] = [VariableID, VariableName, VariableObsoletes, VariableIsSubcategory, VariableIsArchived, VariableIsMisc]

            # For each category...
            for CategoryData in GameCategories:
                CategoryID = CategoryData["id"]
                CategoryName = CategoryData["name"]
                CategoryType = CategoryData["type"]
                CategoryIsMisc = CategoryData["miscellaneous"]

                if CategoryType == "per-level" or CategoryIsMisc: continue

                # Get the leaderboard
                CategoryLeaderboard = RequestAPI(API + "/leaderboards/" + GameID +  "/category/" + CategoryID + "?embed=players")

                # Get usernames from non-guests
                CategoryPlayers = dict()
                for Player in CategoryLeaderboard["players"]["data"]:
                    if Player["rel"] == "user": CategoryPlayers[Player["id"]] = Player["names"]["international"]

                # Get all runs and write them to runs.csv
                CategoryRuns = CategoryLeaderboard["runs"]

                for RunData in CategoryRuns:
                    CategoryDisplayName = f"{GameID}{CategoryID}"

                    if RunData["run"]["players"][0]["rel"] == "user":
                        RunPlayer = CategoryPlayers[RunData["run"]["players"][0]["id"]]
                    elif RunData["run"]["players"][0]["rel"] == "guest":
                        RunPlayer = RunData["run"]["players"][0]["name"]
                    RunID = RunData["run"]["id"]
                    RunTime = RunData["run"]["times"]["primary_t"]
                    RunDate = RunData["run"]["date"]
                    RunPlatform = GamePlatforms[RunData["run"]["system"]["platform"]]
                    RunIsEmulated = RunData["run"]["system"]["emulated"]
                    RunVariables = list(RunData["run"]["values"].values())

                    if RunVariables:
                        RunVariable = RunVariables[0]
                        [VariableID, VariableName, VariableObsoletes, VariableIsSubcategory, VariableIsArchived, VariableIsMisc] = GameVariables[RunVariable]

                        if VariableIsArchived or VariableIsMisc: continue
                        if VariableObsoletes and not VariableIsSubcategory: SubcategoryName = ""    # We need to handle obsoleting runs in generate_board.py
                        else:
                            SubcategoryName = VariableName
                            CategoryDisplayName = f"{GameID}{CategoryID}{VariableID}"
                    else: 
                        SubcategoryName = ""
                        
                    RunsWriter.writerow([GameName, CategoryName, SubcategoryName, CategoryDisplayName, RunPlayer, RunTime, RunDate, RunPlatform, RunIsEmulated, RunID])

FetchRuns(SERIES_ID)
