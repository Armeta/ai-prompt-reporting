from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader
import json

baseModelName  = 'all-MiniLM-L12-v2'

f = open('json/Options.json','r')
options = json.load(f)
f.close()
f = open('json/AnswerKey.json','r')
answers = json.load(f)
f.close()

opts = [option['url'] if option['type'] == 'url' else option['query'] for option in options['options']]
opt_desc = [option['desc'] for option in options['options']]

pairs = []

for pair in answers['pairs']:
    if(pair['ans'] in opts):
        pairs.append({'prompt': pair['prompt'], 'ans': opt_desc[opts.index(pair['ans'])]})

baseModel = SentenceTransformer(baseModelName)
train_examples = [InputExample(texts=[pair['prompt'], pair['ans']]) for pair in pairs]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model=baseModel)

baseModel.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3, output_path='./LocalModel/')