# This is only useful when someone wants their displayed username updated or if speedrun.com decides to change platform IDs for some reason.
# Making one request for each player takes forever and I couldn't get requesting player info to be embedded in runs to work, which is the whole reason for caching usernames in the first place.

import requests, time, csv

API = "https://www.speedrun.com/api/v1/"

def UpdateCachedPlayers():
    newPlayers = set()

    with open("cached/players.csv", "r", newline="", encoding="utf-8") as playersFile:
        playersReader = csv.reader(playersFile)
        oldPlayers = set(tuple(row) for row in playersReader if len(row) == 2)

    for player in oldPlayers:
        while True:
            response = requests.get(API + "/users/" + player[0])
            if response.status_code == 420:
                waitTime = int(response.headers.get("Retry-After", 15))
                print(f"Rate Limited! Waiting {waitTime} seconds...")
                time.sleep(waitTime)
                continue
            break
        data = response.json()
        player = tuple([player[0], data["data"]["names"]["international"]])
        newPlayers.add(player)
        print("Updated ", player)
        time.sleep(0.5)

    with open("cached/players.csv", "w", newline="", encoding="utf-8") as playersFile:
        playersWriter = csv.writer(playersFile)
        playersWriter.writerows(newPlayers)

def UpdateCachedPlatforms():
    newPlatforms = set()

    with open("cached/platforms.csv", "r", encoding="utf-8") as platformsFile:
        platformsReader = csv.reader(platformsFile)
        oldPlatforms = set(tuple(row) for row in platformsReader if len(row) == 2)

    for platform in oldPlatforms:
        while True:
            response = requests.get(API + "/platforms/" + platform[0])
            if response.status_code == 420:
                waitTime = int(response.headers.get("Retry-After", 15))
                print(f"Rate Limited! Waiting {waitTime} seconds...")
                time.sleep(waitTime)
                continue
            break
        data = response.json()
        platform = tuple([platform[0], data["data"]["name"]])
        newPlatforms.add(platform)
        print("Updated ", platform)
        time.sleep(0.5)

    with open("cached/platforms.csv", "w", newline="", encoding="utf-8") as platformsFile:
        platformsWriter = csv.writer(platformsFile)
        platformsWriter.writerows(newPlatforms)

UpdateCachedPlayers()
UpdateCachedPlatforms()