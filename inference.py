from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from bertopic import BERTopic
import pandas as pd
from torch.utils.data import DataLoader
from dataset import FinanceDataset
from tqdm import tqdm
from bertopic import BERTopic
import pandas as pd
import re
from konlpy.tag import Okt
from utils import stopwords_list
import os

os.environ['KMP_WARNINGS'] = 'off'

def to_words(corpus):
    # corpus = re.sub('^[가-힣]','',corpus)
    words = corpus.split()
    stops = set(stopwords_list)
    meaningful_words = [w for w in words if not w in stops]
    mystring = ''.join(map(str,meaningful_words))
    nouns = okt.nouns(mystring)
    nounstring = ','.join(map(str,nouns))
    return nounstring

device = torch.device('cuda')
tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert")
model = AutoModelForSequenceClassification.from_pretrained("/workspace/KR-FinBert/models/exp3_nofreeze/0.991").to(device)


df = pd.read_csv('/workspace/KR-FinBert/data/comment_2022_Q1_naver.csv')
test_dataset = FinanceDataset(df, mode='test')
test_loader = DataLoader(test_dataset,
                                batch_size=64,
                                num_workers=4,
                                shuffle=False,
                                pin_memory=True,
                                drop_last=False,
                            )


sentence_list = []
pred_list = []
with torch.no_grad():
    model.eval()
    for idx, (sentence) in enumerate(tqdm(test_loader)):
        prep_sentence = tokenizer.batch_encode_plus(sentence, padding=True, return_tensors='pt')

        prep_sentence = prep_sentence.to(device)

        output = model(**prep_sentence)
        preds = torch.argmax(output.logits, dim=-1)
        
        sentence_list.extend(sentence)
        pred_list.extend(preds.tolist())
print("Model Inference Done")        
output = pd.DataFrame(zip(sentence_list, pred_list), columns = ['text', 'sentiment'])
output = output[output['sentiment'] != 1]
output.reset_index(drop=True, inplace=True)

print("Okt tokenizer load ... ", end= '')    
okt = Okt()
print("Done")

print("BERTopic load ... ", end= '')    
topic_model = BERTopic(language="korean", calculate_probabilities=True, verbose=False, nr_topics=10, top_n_words=5)
print("Done")


print("\nPositive Topic Modeling ... ")
pos = output[output['sentiment'] == 2].reset_index(drop=True)
prep_sentence = pos['text'].apply(to_words)
topics, probs = topic_model.fit_transform(prep_sentence)
print("="*50)
print(topic_model.get_topic_info())
print("="*50)


print("\nNegative Topic Modeling ... ")   
neg = output[output['sentiment'] == 0].reset_index(drop=True)
prep_sentence = neg['text'].apply(to_words)
topics, probs = topic_model.fit_transform(prep_sentence)
print("="*50)
print(topic_model.get_topic_info())
print("="*50)