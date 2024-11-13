import csv

newEntries = []

with open('nation.csv', mode='r') as file:
    csvFile = csv.reader(file)
    for line in csvFile:
        x = ''.join(line)
        x_split = x.split('|')
        x_split[-1] = x_split[-1].replace(',', '')
        newEntries.append(','.join(x_split))

with open('nation-new.csv', mode='w', newline='') as outFile:
    writer = csv.writer(outFile)
    for line in newEntries:
        writer.writerow(line.split(','))