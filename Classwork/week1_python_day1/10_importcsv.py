import csv
import decimal

with open('C:\\Users\\Umar.Shariff\\OneDrive - Arup\\Desktop\\FDE\\Week1_Oct3Oct4\\homework_invoices.csv', mode='r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        try:
            if float(row['amount']) > 900000.00:
                print(f"Invoice amount is greater than 1000: {row['amount']}")
        except ValueError:
            print(f"Invalid value for amount: {row['amount']}")