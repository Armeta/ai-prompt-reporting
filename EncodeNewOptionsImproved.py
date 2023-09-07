from sentence_transformers import SentenceTransformer
import json
import struct
import os
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType


#modelName = 'all-distilroberta-v1'
modelName = './LocalModel/'
queryTable = 'OptionsQuery'
dashTable = 'OptionsDashboard'

if(modelName == './LocalModel/'):
    queryTable = 'OptionsQueryLocal'
    dashTable = 'OptionsDashboardLocal'


# add src to system path
sys.path.append('src')

from lib import code_library

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    

options_dash  = session.table("\""+dashTable+"\"")
options_query = session.table("\""+queryTable+"\"")
#options_dash_test.show()

# model selection
model = SentenceTransformer(modelName)

outputpath = 'src/outputs/all-distilroberta-v1/'
if(modelName == './LocalModel/'):
    outputpath = 'src/outputs/LocalModel/'

stageD = open(outputpath+'toStageDashboardEncoding.csv', 'w')
stageD.write('SK|ENCODING|ENCODING_JSON\n')
stageQ = open(outputpath+'toStageQueryEncoding.csv', 'w')
stageQ.write('SK|ENCODING|ENCODING_JSON\n')

# get descriptions, encode, and upload
dash_count = 0
query_count = 0

dash    = options_dash.filter(col('ENCODING' ).isNull()).select(['SK', 'DESC']).to_pandas().values.tolist()
print(str(len(dash)) + ' dashboards to encode')
for row in dash:
    enc = model.encode(row[1]).tolist()
    enc_json = '{"encoding": '+str(enc)+'}'
    bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])
    stageD.write('%d|%s|%s\n' % (row[0], bin, enc_json))
    #session.sql('UPDATE "MODEL"."OptionsDashboard" SET ENCODING=TO_BINARY(\''+bin+'\'), ENCODING_JSON=\''+enc_json+'\' WHERE SK='+str(row[0])+';').collect()
    dash_count += 1
stageD.close()
print(str(dash_count) + ' dashboards encoded')

query   = options_query.filter(col('ENCODING' ).isNull()).select(['SK', 'DESC']).to_pandas().values.tolist()
print(str(len(query)) + ' queries to encode')
for row in query:
    enc = model.encode(row[1]).tolist()
    enc_json = '{"encoding": '+str(enc)+'}'
    bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])
    stageQ.write('%d|%s|%s\n' % (row[0], bin, enc_json))
    #session.sql('UPDATE "MODEL"."OptionsQuery" SET ENCODING=TO_BINARY(\''+bin+'\'), ENCODING_JSON=\''+enc_json+'\' WHERE SK='+str(row[0])+';').collect()
    query_count += 1
stageQ.close()
print(str(query_count) + ' queries encoded')

print('Clearing Stages...')
session.sql('REMOVE @dashboard_encoding_stage;').collect()
session.sql('REMOVE @query_encoding_stage;').collect()
print('Uploading to Stages...')
session.sql('PUT file://%s/%stoStageDashboardEncoding.csv @dashboard_encoding_stage;' % (str(os.getcwd()), outputpath)).collect()
session.sql('PUT file://%s/%stoStageQueryEncoding.csv @query_encoding_stage;' % (str(os.getcwd()), outputpath)).collect()
print('Creating Temp Tables...')
session.sql('CREATE TEMPORARY TABLE TempDashboardEncodings (SK INT, ENCODING BINARY, ENCODING_JSON VARCHAR);').collect()
session.sql('CREATE TEMPORARY TABLE TempQueryEncodings (SK INT, ENCODING BINARY, ENCODING_JSON VARCHAR);').collect()
print('Copying from Stages...')
session.sql('COPY INTO TempDashboardEncodings (SK, ENCODING, ENCODING_JSON) FROM @dashboard_encoding_stage file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');').collect()
session.sql('COPY INTO TempQueryEncodings (SK, ENCODING, ENCODING_JSON) FROM @query_encoding_stage file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');').collect()
print('Updating Dashboard Table')
session.sql('UPDATE MODEL."%s" SET ENCODING = B.ENCODING , ENCODING_JSON = B.ENCODING_JSON FROM TempDashboardEncodings B WHERE MODEL."%s".SK = B.SK;' % (dashTable, dashTable)).collect()
print('Updating Query Table')
session.sql('UPDATE MODEL."%s" SET ENCODING = B.ENCODING , ENCODING_JSON = B.ENCODING_JSON FROM TempQueryEncodings B WHERE MODEL."%s".SK = B.SK;' % (queryTable, queryTable)).collect()



