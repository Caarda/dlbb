# Takes runs.csv and categories.csv files and generates the full board.csv that gets written to sheets.

import csv, math

def FormatTime(time: float):
    ms, ss = math.modf(time)
    hh, ss = divmod(ss, 3600)
    mm, ss = divmod(ss, 60)

    # Show existing ms up to three decimal places and pad seconds if needed
    padding = "0" if 0 < ss < 10 else "0" if ss == 0 and mm else ""
    ss = f"{padding}{ss + round(ms, 3)}".rstrip("0").rstrip(".")

    if hh:
        return f"{int(hh)}:{int(mm):02d}:{ss}"
    if mm:
        return f"{int(mm)}:{ss}"
    else:
        return f"{ss}"

with open("output/categories.csv", "r", encoding="utf-8") as CategoriesFile:
    with open("output/runs.csv", "r", encoding="utf-8") as RunsFile:
        CategoriesReader = csv.reader(CategoriesFile)
        RunsReader = csv.reader(RunsFile)
        next(CategoriesReader)
        next(RunsReader)

        # We build a dict of dicts that accepts keys [Player][CategoryID] and returns the time of their best run (if it exists), else 0.
        # We also keep track of the World Record in each category for point calculations.
        Players = dict()
        Categories = dict()

        for CategoryID, MaxPoints, _, Game, Category, Subcategory in CategoriesReader:
            Categories[CategoryID] = [0.0, int(MaxPoints), Game.lstrip(" "), Category, Subcategory]

        for run in RunsReader:
            _, _, _, CategoryID, PlayerName, RunTime, _, _, _, _ = run

            if not PlayerName in Players.keys():
                Players[PlayerName] = {"Rank": 0, "Total": 0, "Name": PlayerName}
                for Category in Categories.keys(): Players[PlayerName][Category] = 0

            RunTime = float(RunTime)
            if Players[PlayerName][CategoryID] == 0 or float(RunTime) < Players[PlayerName][CategoryID]:
                Players[PlayerName][CategoryID] = float(RunTime)

            if RunTime < Categories[CategoryID][0] or not Categories[CategoryID][0]:
                Categories[CategoryID][0] = RunTime

        # Times can now be converted into points. Current formula is simply round(MAX_POINTS * (WR / TIME)).
        for Player in Players.keys():

            for Category in Categories.keys():
                if Players[Player][Category]:
                    PlayerScore = round(Categories[Category][1] * (Categories[Category][0] / Players[Player][Category]) ** 2)
                    Players[Player][Category] = f"{FormatTime(Players[Player][Category])} ({PlayerScore})"
                    Players[Player]["Total"] += PlayerScore
                else:
                    Players[Player][Category] = ""

# Now we can sequentially assign ranks in descending score order.
# In the case of ties, players get assigned the same rank and we skip one number forwards.
Previous = 0
Rank = 0
Tie = 0

with open("output/board.csv", "w", newline="", encoding="utf-8") as BoardFile:
    BoardWriter = csv.writer(BoardFile)

    # We need to structure the three top rows column by column for sheet styling to work properly.
    BoardGameHeader = ["Rank", "Points", "Player"]
    BoardCategoryHeader = ["", "", ""]
    BoardSubcategoryHeader = ["", "", ""]

    LastGame = ""
    LastCategory = ""

    for CategoryID in Categories.keys():
        Game, Category, Subcategory = Categories[CategoryID][2], Categories[CategoryID][3], Categories[CategoryID][4]

        if Game != LastGame:
            BoardGameHeader.append(Game)
            LastGame = Game
        else: BoardGameHeader.append("")

        if Category != LastCategory:
            BoardCategoryHeader.append(Category)
            LastCategory = Category
        else: BoardCategoryHeader.append("")

        if Subcategory:
            BoardSubcategoryHeader.append(Subcategory)
        else:
            BoardSubcategoryHeader.append("")

    BoardWriter.writerow(BoardGameHeader)
    BoardWriter.writerow(BoardCategoryHeader)
    BoardWriter.writerow(BoardSubcategoryHeader)

    # Finally, we write player rows in order.
    for Player in sorted(Players, key=lambda player: Players[player]["Total"], reverse=True):
        if Players[Player]["Total"] == Previous:
            Tie += 1
        else:
            Rank += Tie + 1
            Tie = 0

        Players[Player]["Rank"] = Rank
        PlayerRow = list(Players[Player].values())

        BoardWriter.writerow(PlayerRow)
