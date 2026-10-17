import csv

DATA_SET = "diabetic_data.csv"
with open(DATA_SET, mode="r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    first_row = next(reader)        #print(first_row)
    print(first_row)