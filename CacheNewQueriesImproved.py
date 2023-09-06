import json
import datetime
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

queryTable = 'OptionsQuery'
#queryTable = 'OptionsQueryLocal'

# add src to system path
sys.path.append('src')

from lib import code_library

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    

options_query = session.table('"%s"' % (queryTable))

stageR = open('toStageQueryResult.csv', 'w')
stageR.write('SK|RESULT_CACHE|RESULT_CACHE_TS\n')

query   = options_query.filter(col('RESULT_CACHE').isNull()).select(['SK', 'QUERY']).to_pandas().values.tolist()
total = len(query)
count = 0
print(str(total) + ' queries to cache')
for row in query:

    result = session.sql(row[1]).collect()

    if(len(result) == 0 or result[0] == None):
        result_str = 'No results'
    elif(len(result[0]) == 0 or result[0][0] == None):
        result_str = 'No results'
    else:
        result_str = result[0][0].replace('\'', '\'\'')

    stageR.write('%d|%s|%s\n' % (row[0], result_str, str(datetime.datetime.now())))
    #session.sql('UPDATE "MODEL"."OptionsQuery" SET RESULT_CACHE=\''+result_str+'\',RESULT_CACHE_TS=CURRENT_TIMESTAMP WHERE SK='+str(row[0])+';').collect()
    
    count += 1
    if(count % 50 == 0):
        print( '%d (%d%%)' % (count, (100.0*count)/total) )


stageR.close()
print('%d queries run' % (count))

print('Clearing Stage...')
session.sql('REMOVE @query_result_stage;').collect()
print('Uploading to Stage...')
session.sql('PUT file://C:/Users/LanceWahlert/source/repos/ai-turkey/ai-prompt-reporting/toStageQueryResult.csv @query_result_stage;').collect()
print('Creating Temp Table...')
session.sql('CREATE TEMPORARY TABLE TempQueryResults (SK INT, RESULT_CACHE VARCHAR(1000), RESULT_CACHE_TS TIMESTAMP);').collect()
print('Copying from Stage...')
session.sql('COPY INTO TempQueryResults (SK, RESULT_CACHE, RESULT_CACHE_TS) FROM @query_result_stage file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');').collect()
print('Updating Query Table')
session.sql('UPDATE MODEL."%s" SET RESUlT_CACHE = B.RESUlT_CACHE , RESULT_CACHE_TS = B.RESULT_CACHE_TS FROM TempQueryResults B WHERE MODEL."%s".SK = B.SK;' % (queryTable, queryTable)).collect()
