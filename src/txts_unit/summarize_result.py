import csv
import sys

if len(sys.argv) != 2:
    print("Please specify file name")
    exit(1)

filename = sys.argv[1]


with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    header = next(reader)
    for row in reader:
        print(row)



