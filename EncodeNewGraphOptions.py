from sentence_transformers import SentenceTransformer
import json
import struct
import os
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')
from lib import code_library

#modelName = 'all-distilroberta-v1'
modelName   = './LocalModel/'
GraphTable  = 'OPTIONS_GRAPH'

if(modelName == './LocalModel/'):
    GraphTable  = 'OPTIONS_GRAPH'

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    

options_graph = session.table(GraphTable) 

# model selection
model = SentenceTransformer(modelName)

outputpath = 'src/outputs/all-distilroberta-v1/'
if(modelName == './LocalModel/'):
    outputpath = 'src/outputs/LocalModel/'

stageQ = open(outputpath + 'toStageGraphEncoding.csv', 'w')
stageQ.write('SK|ENCODING|ENCODING_JSON\n')

# get descriptions, encode, and upload
query_count = 0

query   = options_graph.filter(col('ENCODING' ).isNull()).select(['SK', 'DESC']).to_pandas().values.tolist()
print(str(len(query)) + ' queries to encode')
for row in query:
    enc = model.encode(row[1]).tolist()
    enc_json = '{"encoding": '+str(enc)+'}'
    bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])
    stageQ.write('%d|%s|%s\n' % (row[0], bin, enc_json))
    query_count += 1
stageQ.close()
print(str(query_count) + ' queries encoded')

print('Clearing Stages...')
session.sql('REMOVE @GRAPH_ENCODING_STAGE;').collect()

print('Uploading to Stages...')
session.sql('PUT file://%s/%stoStageGraphEncoding.csv @GRAPH_ENCODING_STAGE;' % (str(os.getcwd()), outputpath)).collect()

print('Creating Temp Tables...')
session.sql('CREATE TEMPORARY TABLE TempQueryEncodings (SK INT, ENCODING BINARY, ENCODING_JSON VARCHAR);').collect()

print('Copying from Stages...')
session.sql('COPY INTO TempQueryEncodings (SK, ENCODING, ENCODING_JSON) FROM @GRAPH_ENCODING_STAGE file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');').collect()

print('Updating Query Table')
session.sql('UPDATE MODEL."%s" SET ENCODING = B.ENCODING , ENCODING_JSON = B.ENCODING_JSON FROM TempQueryEncodings B WHERE MODEL."%s".SK = B.SK;' % (GraphTable, GraphTable)).collect()