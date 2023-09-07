import json
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')

from lib import code_library

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    

options_query = session.table("\"OptionsQuery\"")

query   = options_query.filter(col('RESULT_CACHE' ).isNull()).select(['SK', 'QUERY']).to_pandas().values.tolist()
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
    session.sql('UPDATE "MODEL"."OptionsQuery" SET RESULT_CACHE=\''+result_str+'\',RESULT_CACHE_TS=CURRENT_TIMESTAMP WHERE SK='+str(row[0])+';').collect()
    count += 1
    if(count % 50 == 0):
        print( '%d (%d%%)' % (count, (100.0*count)/total) )