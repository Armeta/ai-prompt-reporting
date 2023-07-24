from sentence_transformers import SentenceTransformer
import json
import openai

modelName = 'text-embedding-ada-002'
jsonFileName = 'Options.json'

if(modelName == 'text-embedding-ada-002'):
    f = open('secrets.json','r')
    secrets = json.load(f)
    f.close()
    openai.organization = secrets['organization']
    openai.api_key = secrets['api_key']
else:
    model = SentenceTransformer(modelName)

f = open(jsonFileName,'r')
options = json.load(f)
f.close()

options['model'] = modelName

for option in options['options']:
    if(modelName == 'text-embedding-ada-002'):
        option['encoding'] = openai.Embedding.create(input = [option['desc']], model='text-embedding-ada-002')['data'][0]['embedding']
    else:
        option['encoding'] = model.encode(option['desc']).tolist()

f = open(jsonFileName,'w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()