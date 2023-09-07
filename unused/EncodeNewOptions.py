from sentence_transformers import SentenceTransformer
import json
import struct
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

options_dash  = session.table("\"OptionsDashboard\"")
options_query = session.table("\"OptionsQuery\"")
#options_dash_test.show()

# model selection
model = SentenceTransformer('all-distilroberta-v1')

# get descriptions, encode, and upload

dash    = options_dash.filter(col('ENCODING' ).isNull()).select(['SK', 'DESC']).to_pandas().values.tolist()
for row in dash:
    enc = model.encode(row[1]).tolist()
    enc_json = '{"encoding": '+str(enc)+'}'
    bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])
    session.sql('UPDATE "MODEL"."OptionsDashboard" SET ENCODING=TO_BINARY(\''+bin+'\'), ENCODING_JSON=\''+enc_json+'\' WHERE SK='+str(row[0])+';').collect()

query   = options_query.filter(col('ENCODING' ).isNull()).select(['SK', 'DESC']).to_pandas().values.tolist()
for row in query:
    enc = model.encode(row[1]).tolist()
    enc_json = '{"encoding": '+str(enc)+'}'
    bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])
    session.sql('UPDATE "MODEL"."OptionsQuery" SET ENCODING=TO_BINARY(\''+bin+'\'), ENCODING_JSON=\''+enc_json+'\' WHERE SK='+str(row[0])+';').collect()
