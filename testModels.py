from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import datetime
import openai

modelsToTest = ['bert-base-nli-mean-tokens', 'all-mpnet-base-v2', 'all-distilroberta-v1', 'all-MiniLM-L12-v2', 'multi-qa-distilbert-cos-v1', 'all-MiniLM-L6-v2', 'multi-qa-MiniLM-L6-cos-v1', 'paraphrase-albert-small-v2', 'paraphrase-MiniLM-L3-v2']

openaiToTest = 'text-embedding-ada-002'
if(openaiToTest):
    f = open('secrets.json','r')
    secrets = json.load(f)
    f.close()
    openai.organization = secrets['organization']
    openai.api_key = secrets['api_key']
    #print(openai.Embedding.create(input = ['What was the total sales revenue yesterday?'], model=openaiToTest)['data'][0]['embedding'])


f = open('Options.json','r')
options = json.load(f)
f.close()
f = open('AnswerKey.json','r')
answers = json.load(f)
f.close()

results = {}

opt_url = [option['url'] for option in options['options']]
opt_desc = [option['desc'] for option in options['options']]
tst_prompt = [answer['prompt'] for answer in answers['pairs']]
tst_url = [answer['url'] for answer in answers['pairs']]

for modelName in modelsToTest:
    model = SentenceTransformer(modelName)
    results[modelName] = {'score': 0.0, 'time': None, 'results':[]}
    starttime = datetime.datetime.now()

    optEncodings = model.encode(opt_desc)
    for prompt, url in zip(tst_prompt, tst_url):
        promptEncoding = model.encode(prompt)
        sim = cosine_similarity([promptEncoding], optEncodings)
        guess_url = opt_url[sim[0].tolist().index(max(sim[0]))]
        if(guess_url == url):
            results[modelName]['score'] += 1
        results[modelName]['results'].append([guess_url == url, prompt, guess_url])
    results[modelName]['score'] /= len(tst_prompt)
    endtime = datetime.datetime.now()
    results[modelName]['time'] = (endtime-starttime).seconds
    print('%2.0f%% %s' % (results[modelName]['score']*100, modelName))

try:
    if(openaiToTest):
        modelName = openaiToTest
        results[modelName] = {'score': 0.0, 'time': None, 'results':[]}
        starttime = datetime.datetime.now()
        optEncodings = [data['embedding'] for data in openai.Embedding.create(input = opt_desc, model=openaiToTest)['data']]

        for prompt, url in zip(tst_prompt, tst_url):
            promptEncoding = openai.Embedding.create(input = [prompt], model=openaiToTest)['data'][0]['embedding']
            sim = cosine_similarity([promptEncoding], optEncodings)
            guess_url = opt_url[sim[0].tolist().index(max(sim[0]))]
            if(guess_url == url):
                results[modelName]['score'] += 1
            results[modelName]['results'].append([guess_url == url, prompt, guess_url])
        results[modelName]['score'] /= len(tst_prompt)
        endtime = datetime.datetime.now()
        results[modelName]['time'] = (endtime-starttime).seconds
        print('%2.0f%% %s' % (results[modelName]['score']*100, modelName))
except:
    print('openAI failed')

f = open('TestResults.json','w')
f.write(json.dumps(results, indent=4))
f.close()