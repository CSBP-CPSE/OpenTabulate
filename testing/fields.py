import csv

csvfile = open('fields.csv', 'r', newline='')
reader = csv.reader(csvfile)

for row in reader:
   for entry in row:
     print(entry)

