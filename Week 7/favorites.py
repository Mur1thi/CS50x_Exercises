import csv

with open("favorites.csv", "r") as file:
    # Do something with file
    reader = csv.DictReader(file)
    for row in reader:
        favorite = row["language"]
        print(favorite)
