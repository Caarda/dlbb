# Calculates category point values based on the number of runs and writes them to categories.csv.

import csv, math

# Count the number of runs in each category.
with open("output/runs.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)

    RunnerCounts = dict()

    for run in reader:
        GameName, CategoryName, SubcategoryName, CategoryID, PlayerName, RunTime, RunDate, Platform, RunID = run

        # Add unseen categories.
        if CategoryID not in RunnerCounts:
            RunnerCounts[CategoryID] = [1, GameName, CategoryName, SubcategoryName]
        else:
            RunnerCounts[CategoryID][0] += 1

# Calculate values and write to file.
with open("output/categories.csv", "w", newline="", encoding="utf-8") as f:
    f.write("category_id,points,display_name,game,category,subcategory\n")

    # The most runners in a single category.
    HighestRunnerCount = max(x[0] for x in RunnerCounts.values())

    # Max points for each category based on the number of runners. Current formula is [20 + round(80 * log(RUNNERS, HIGHEST_RUNNERS))].
    for CategoryID in RunnerCounts:
        PlayerCount, GameName, CategoryName, SubcategoryName = RunnerCounts[CategoryID]
        ReadableCategoryName = f"{GameName} - {CategoryName} ({SubcategoryName})" if SubcategoryName else f"{GameName} - {CategoryName}"

        PointValue = 20 + round(80 * math.log(PlayerCount, HighestRunnerCount))

        f.write(f"{f'{CategoryID},':<27}{f'{PointValue},':<6}{f' | {ReadableCategoryName},':<80}{f'{GameName},'}{f'{CategoryName},'}{f'{SubcategoryName}'}\n")
