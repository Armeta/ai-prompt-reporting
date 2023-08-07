from sentence_transformers import SentenceTransformer
import json
import datetime

modelName = 'all-MiniLM-L12-v2'#'all-mpnet-base-v2'



def encodeFile(fileName):
    
    starttime = datetime.datetime.now()

    f = open(fileName,'r')
    options = json.load(f)
    f.close()

    options['model'] = modelName

    for option in options['options']:
        option['encoding'] = model.encode(option['desc']).tolist()

    f = open(fileName,'w')
    f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
    f.close()

    endtime = datetime.datetime.now()
    print('Encoded %s with %s in %d seconds' % (fileName, modelName, (endtime-starttime).seconds))


model = SentenceTransformer(modelName)
encodeFile('Options.json')
encodeFile('QueryOptions.json')
