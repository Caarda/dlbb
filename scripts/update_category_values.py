# Calculates category point values based on the number of runs and writes them to categories.csv

import csv, math

# Count the number of runs in each category
with open("output/runs.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)

    RunnerCounts = dict()

    for run in reader:
        GameName, CategoryName, SubcategoryName, CategoryID, PlayerName, RunTime, RunDate, Platform, RunID = run

        # Add unseen categories
        if CategoryID not in RunnerCounts:
            ReadableCategoryName = f"{GameName} - {CategoryName} ({SubcategoryName})" if SubcategoryName else f"{GameName} - {CategoryName}"
            RunnerCounts[CategoryID] = [ReadableCategoryName, 1]
        else:
            RunnerCounts[CategoryID][1] += 1

# Calculate values and write to file
with open("output/categories.csv", "w", newline="", encoding="utf-8") as f:
    f.write("category_id,points,cateogry_name\n")
    MaxRunnerCount = max(x[1] for x in RunnerCounts.values())

    for CategoryID in RunnerCounts:
        ReadableCategoryName, PlayerCount = RunnerCounts[CategoryID]
        PointValue = 20 + round(80 * math.log(PlayerCount, MaxRunnerCount))
        f.write(f"{f'{CategoryID},':<27}{f'{PointValue},':<6}// {ReadableCategoryName}\n")