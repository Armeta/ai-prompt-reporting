import json
import pyodbc


f = open('src/json/QueryOptions.json','r')
options = json.load(f)
f.close()

cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};server=XPS9310-DZ52693\SQLEXPRESS;database=DEMO;Encrypt=No;Trusted_Connection=yes;TrustServerCertificate = No;')
cursor = cnxn.cursor()

newCities = ['WACO', 'HOUSTON', 'FORT WORTH', 'AUSTIN', 'EL PASO']
newOptions = []

for option in options['options'][493:]:
    for city in newCities:
        newOption = option.copy()
        newOption['query'] = newOption['query'].replace('DALLAS', city).replace('Dallas', city)
        newOption['desc'] = newOption['desc'].replace('DALLAS', city).replace('Dallas', city)
        newOption['result'] = ''
        newOptions.append(newOption)

options['options'] = options['options'] + newOptions

f = open('src/json/QueryOptions2.json','w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()
