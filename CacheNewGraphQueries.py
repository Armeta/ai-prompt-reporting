import json
import datetime
import os
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

#queryTable = 'OptionsQuery'
GraphTable = 'OPTIONS_GRAPH'

# add src to system path
sys.path.append('src')

from lib import code_library

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    

options_Graph = session.table('"%s"' % (GraphTable))

stageR = open('src/outputs/toStageGraphResult.csv', 'w')
stageR.write('SK|RESULT_CACHE|RESULT_CACHE_TS\n')

query   = options_Graph.filter(col('RESULT_CACHE').isNull()).select(['SK', 'QUERY']).to_pandas().values.tolist()
total = len(query)
count = 0
print(str(total) + ' queries to cache')
for row in query:

    result = session.sql(row[1]).collect()
    
    # Initializing an empty result string
    result_str = ''

    if(len(result) == 0 or result[0] == None):
        result_str = 'No results'
    else:
            # Iterating through each row of the result and appending values to result_str
        for r in result:
            # Check if the individual row is non-empty and its first item isn't None
            if len(r) > 0 and r[0] != None:
                result_str += r[0].replace('\'', '\'\'') + "<+>" + str(r[1])

                # Separate values with a comma or any other separator if desired
                result_str += '%@%'

        # Remove trailing comma
        result_str = result_str.rstrip(',')
        if not result_str:
            result_str = 'No results'    

    stageR.write('%d|%s|%s\n' % (row[0], result_str, str(datetime.datetime.now())))
    #session.sql('UPDATE "MODEL"."OptionsQuery" SET RESULT_CACHE=\''+result_str+'\',RESULT_CACHE_TS=CURRENT_TIMESTAMP WHERE SK='+str(row[0])+';').collect()
    
    count += 1
    if(count % 50 == 0):
        print( '%d (%d%%)' % (count, (100.0*count)/total) )


stageR.close()
print('%d queries run' % (count))

print('Clearing Stage...')
session.sql('REMOVE @GRAPH_RESULTS_STAGE;').collect()

print('Uploading to Stage...')
session.sql('PUT file://%s/src/outputs/toStageGraphResult.csv @GRAPH_RESULTS_STAGE;' % (str(os.getcwd()))).collect()

print('Creating Temp Table...')
session.sql('CREATE TEMPORARY TABLE TempQueryResults (SK INT, RESULT_CACHE VARCHAR(16777216), RESULT_CACHE_TS TIMESTAMP);').collect()

print('Copying from Stage...')
session.sql('COPY INTO TempQueryResults (SK, RESULT_CACHE, RESULT_CACHE_TS) FROM @GRAPH_RESULTS_STAGE file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');').collect()

print('Updating Query Table')
session.sql('UPDATE MODEL."%s" SET RESUlT_CACHE = B.RESUlT_CACHE , RESULT_CACHE_TS = B.RESULT_CACHE_TS FROM TempQueryResults B WHERE MODEL."%s".SK = B.SK;' % (GraphTable, GraphTable)).collect()
