import json
import pyodbc


f = open('json\\QueryOptions.json','r')
options = json.load(f)
f.close()

cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};server=XPS9310-DZ52693\SQLEXPRESS;database=DEMO;Encrypt=No;Trusted_Connection=yes;TrustServerCertificate = No;')
cursor = cnxn.cursor()
limit = 100

for option in options['options']:
    if option['result'] == None or option['result'] == '':
        limit -= 1
        if limit == 0:
            break
        try:
            cursor.execute(option['query'])
            row = cursor.fetchone()
            if row:
                option['result'] = row[0]
            else:
                option['result'] = 'No data matches the query'
        except:
            print('Error on '+option['query'])

f = open('json\\QueryOptions.json','w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()
