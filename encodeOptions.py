from sentence_transformers import SentenceTransformer
import json

modelName = 'all-mpnet-base-v2'


def encodeFile(fileName):
    f = open(fileName,'r')
    options = json.load(f)
    f.close()

    options['model'] = modelName

    for option in options['options']:
        option['encoding'] = model.encode(option['desc']).tolist()

    f = open(fileName,'w')
    f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
    f.close()

    print('Encoded '+fileName+' with '+modelName)


model = SentenceTransformer(modelName)
encodeFile('json\\Options.json')
encodeFile('json\\QueryOptions.json')
