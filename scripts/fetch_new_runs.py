# Fetches runs from every category in the series using the speedrun.com api and writes them to runs.csv

import requests, csv, pathlib, time

API = "https://www.speedrun.com/api/v1/"
SERIES_ID = "5nk5epn9"

def GetRawRuns(seriesID: str):
    pathlib.Path("cache").mkdir(exist_ok=True)
    pathlib.Path("output").mkdir(exist_ok=True)

    with open(f"output/runs.csv", "w", newline="", encoding="utf-8") as categoryFile:
        writer = csv.writer(categoryFile)
        writer.writerow(["game","category","subcategory","category_id","player_id","time","date","platform","run_id"])

        # Read cached API info
        try:
            with open("cache/players.csv", "r", newline="", encoding="utf-8") as players:
                CACHED_PLAYERS = dict(csv.reader(players))
        except:
            print("No cached player data present.")
            CACHED_PLAYERS = dict()
        try:
            with open("cache/platforms.csv", "r", newline="", encoding="utf-8") as platforms:
                CACHED_PLATFORMS = dict(csv.reader(platforms))
        except:
            print("No cached platform data present.")
            CACHED_PLATFORMS = dict()

        # Get each game in the series
        response = requests.get(API + "/series/" + seriesID + "/games")
        data = response.json()
        games = [x["id"] for x in data["data"]]
        
        for gameID in games:
            while True:
                response = requests.get(API + "/games/" + gameID)
                if response.status_code == 420:
                    waitTime = int(response.headers.get("Retry-After", 5))
                    print(f"Rate Limited! Waiting {waitTime} seconds...")
                    time.sleep(waitTime)
                    continue
                break
            data = response.json()
            gameInfo = data["data"]
            gameName = gameInfo["names"]["international"]

            print(f"Fetching runs from {gameName} [{gameID}]...")

            # Add missing platforms to cache.
            for platform in gameInfo["platforms"]:
                if platform not in CACHED_PLATFORMS:
                    response = requests.get(API + "/platforms/" + platform)
                    data = response.json()
                    CACHED_PLATFORMS[platform] = data["data"]["name"]

            # Create a dict to resolve subcategory values
            while True:
                response = requests.get(API + "/games/" + gameID + "/variables")
                if response.status_code == 420:
                    waitTime = int(response.headers.get("Retry-After", 15))
                    print(f"Rate Limited! Waiting {waitTime} seconds...")
                    time.sleep(waitTime)
                    continue
                break
            data = response.json()
            variables = data["data"]
            subcategories = {
                key: value
                for variable in variables
                for key, value in variable["values"]["choices"].items()
            }

            # Get each category in the game
            while True:
                response = requests.get(API + "/games/" + gameID + "/categories")
                if response.status_code == 420:
                    waitTime = int(response.headers.get("Retry-After", 5))
                    print(f"Rate Limited! Waiting {waitTime} seconds...")
                    time.sleep(waitTime)
                    continue
                break
            data = response.json()
            categories = data["data"]

            for categoryInfo in categories:
                categoryID = categoryInfo["id"]
                categoryName = categoryInfo["name"].replace("\"", "")   # Duck Life Treasure Hunt - "Furry%"
                categoryType = categoryInfo["type"]
                if categoryType == "per-level": continue

                # Get each run in the category
                while True:
                    response = requests.get(API + "/leaderboards/" + gameID +  "/category/" + categoryID)
                    if response.status_code == 420:
                        waitTime = int(response.headers.get("Retry-After", 5))
                        print(f"Rate Limited! Waiting {waitTime} seconds...")
                        time.sleep(waitTime)
                        continue
                    break
                data = response.json()
                leaderboard = data["data"]
                runs = leaderboard["runs"]

                for runInfo in runs:
                    runID = runInfo["run"]["id"]
                    runDate = runInfo["run"]["date"]
                    runTime = runInfo["run"]["times"]["primary_t"]
                    runPlatform = CACHED_PLATFORMS[runInfo["run"]["system"]["platform"]]
                    runIsEmu = runInfo["run"]["system"]["emulated"]
                    subcategoryID = "" if not runInfo["run"]["values"].values() else next(iter(runInfo["run"]["values"].values()))
                    subcategoryName = "" if not subcategoryID else subcategories[subcategoryID]

                    # Unregistered player data is different
                    runPlayerType = runInfo["run"]["players"][0]["rel"]

                    if runPlayerType == "user":
                        runPlayerID = runInfo["run"]["players"][0]["id"]
                        if runPlayerID not in CACHED_PLAYERS:
                            while True:
                                response = requests.get(API + "/users/" + runPlayerID)
                                if response.status_code == 420:
                                    waitTime = int(response.headers.get("Retry-After", 5))
                                    print(f"Rate Limited! Waiting {waitTime} seconds...")
                                    time.sleep(waitTime)
                                    continue
                                break
                            data = response.json()
                            CACHED_PLAYERS[runPlayerID] = data["data"]["names"]["international"]
                        runPlayerName = CACHED_PLAYERS[runPlayerID]             

                    elif runPlayerType == "guest":
                        runPlayerID = None
                        runPlayerName = runInfo["run"]["players"][0]["name"]

                    # Write each run to the file
                    writer.writerow([gameName, categoryName, subcategoryName, gameID + categoryID + subcategoryID, runPlayerName, runTime, runDate, runPlatform, runID])

    # Update cached API info
    with open("cache/players.csv", "w", newline="", encoding="utf-8") as players:
        writer = csv.writer(players)
        writer.writerows(CACHED_PLAYERS.items())
    with open("cache/platforms.csv", "w", newline="", encoding="utf-8") as platforms:
        writer = csv.writer(platforms)
        writer.writerows(CACHED_PLATFORMS.items())

GetRawRuns(SERIES_ID)
