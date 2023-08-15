import json
import struct
import base64
import pyodbc

f = open('src/json/QueryOptions.json','r')
options = json.load(f)
f.close()

keep = ['STORY_SALES_ACCELERATOR', 'STORY_LOCATION_REVIEW', 'STORY_PRODUCT_STORYBOARD']
tableMap = {'STORY_SALES_ACCELERATOR':'sales-opportunity', 'STORY_LOCATION_REVIEW':'location-review', 'STORY_PRODUCT_STORYBOARD':'top-styles'}

db = 'LocalTest'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};server=XPS9310-DZ52693\SQLEXPRESS;database='+db+';Encrypt=No;Trusted_Connection=yes;TrustServerCertificate = No;')
cursor = cnxn.cursor()

count = 0
for option in options['options']: 
    page = None
    for table in keep:
        if(option['query'].find(table) > -1):
            page = tableMap[table]

    if(page != None):
        encoding = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in option['encoding']])
        if(option['desc'] == 'The total dollar value of the current inventory.'):
            option['query'] = 'SELECT CONCAT(\'The total current inventory value is $\', LTRIM(TO_VARCHAR(SUM("INVENTORY_DOLLARS_TY"), \'999,999,999,990\'))) FROM "DASHBOARD"."STORY_SALES_ACCELERATOR";'
        db_query = 'INSERT INTO dbo.OptionsQuery ([DESC], [QUERY], [ENCODING], [DASHBOARD], [RESULT_CACHE], [RESULT_CACHE_TS]) VALUES (\'%s\', \'%s\', 0x%s, \'%s\', \'%s\', %s );' % (option['desc'].replace('\'', '\'\''), option['query'].replace('[','"').replace(']','"').replace('#\')','0\'))').replace('#', '9').replace('FORMAT', 'LTRIM(TO_VARCHAR').replace('\'', '\'\''), encoding, page, option['result'].replace('\'', '\'\''), 'CURRENT_TIMESTAMP')
        #print(db_query)
        try:
            cursor.execute(db_query)
            count += 1
        except Exception as e:
            print('Error: '+ str(e) +' at '+db_query)

cnxn.commit()
print('Inserted '+str(count)+' query options')