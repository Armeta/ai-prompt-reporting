from sentence_transformers import SentenceTransformer
import json

jsonFileName = 'Options.json'

model = SentenceTransformer('bert-base-nli-mean-tokens') # try other models

f = open(jsonFileName,'r')
options = json.load(f)
f.close()

for option in options['options']:
    option['encoding'] = model.encode(option['desc']).tolist()

f = open(jsonFileName,'w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()