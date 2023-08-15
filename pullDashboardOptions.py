import json
import struct
import base64
import pyodbc

f = open('src/json/Options.json','r')
options = json.load(f)
f.close()

keep = ['sales-opportunity', 'location-review', 'top-styles']
db = 'LocalTest'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};server=XPS9310-DZ52693\SQLEXPRESS;database='+db+';Encrypt=No;Trusted_Connection=yes;TrustServerCertificate = No;')
cursor = cnxn.cursor()

count = 0
for option in options['options']: 
    page = ''
    filter = None
    query = None
    pos = option['url'].find('?')
    if(pos > 0):
        page = option['url'][37:pos]
        #print(option['url'][37:])
        for q in option['url'][pos+1:].replace('%3D', '=').split('&'):
            if(q[:5] == 'query'):
                query = q[5+1:]
            if(q[:6] == 'filter'):
                filter = q[6+1:]
    else:
        page = option['url'][37:]

    if(page in keep):
        encoding = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in option['encoding']])
        db_query = 'INSERT INTO dbo.OptionsDashboard ([DESC], [URL], [ENCODING], DASHBOARD, [FILTER], [QUERY], [FILTER_B64], [QUERY_B64]) VALUES (\'%s\', \'%s\', 0x%s, \'%s\', %s, %s, %s, %s );' % (option['desc'].replace('\'', '\'\''), option['url'].replace('demo','snowflake'), encoding, page, 'NULL' if filter == None else str(base64.b64decode(filter))[1:], 'NULL' if query == None else str(base64.b64decode(query))[1:], 'NULL' if filter == None else '\''+filter+'\'', 'NULL' if query == None else '\''+query+'\'')
        try:
            cursor.execute(db_query)
            count += 1
        except Exception as e:
            print('Error: '+ str(e) +' at '+db_query)

cnxn.commit()
print('Inserted '+str(count)+' dashboard options')