from sentence_transformers import SentenceTransformer
import json

modelName = 'all-MiniLM-L12-v2'
# openAI 'text-embedding-ada-002'
jsonFileName = 'json\\Options.json'

model = SentenceTransformer(modelName)

f = open(jsonFileName,'r')
options = json.load(f)
f.close()

options['model'] = modelName

for option in options['options']:
    option['encoding'] = model.encode(option['desc']).tolist()

f = open(jsonFileName,'w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()
