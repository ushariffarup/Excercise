file='csv'
if file == 'csv':
    print("The file is a CSV file.")
elif file == 'json':
    print("The file is a JSON file.")
elif file == 'xml':
    print("The file is an XML file.")
else:
    print("The file is not supported.")

match file:
    case 'csv':
        print("The file is a CSV file.")
    case 'json':
        print("The file is a JSON file.")
    case 'xml':
        print("The file is an XML file.")
    case _:
        print("The file is not supported.")

count=0
if(file=='csv' or file=='xlxs') and(count>50):
    print("The file is either CSV or XLXS and the count is greater than 50.")
    