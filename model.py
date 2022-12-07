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

class Agent:
    def __init__(self, csv_path, model_path, batch_size=64, device=torch.device('cuda')):
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        self.df = pd.read_csv(csv_path)
        self.tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert")
        self.okt = Okt()
        self.topic_model = BERTopic(language="korean", calculate_probabilities=True, verbose=False, nr_topics=10, top_n_words=5)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
        self.dataset = FinanceDataset(self.df, mode='test')
        self.loader = DataLoader(self.dataset,
                                batch_size=batch_size,
                                num_workers=4,
                                shuffle=False,
                                pin_memory=True,
                                drop_last=False,
                            )
        self.device = device
        self.pos_output = {}
        self.neg_output = {}

    def inference(self):
        self.sentiment()
        self.topicmodeling('pos')
        self.topicmodeling('neg')
        return self.pos_output, self.neg_output

    def topicmodeling(self, sent):
        if sent == 'pos':
            pos = self.output[self.output['sentiment'] == 2].reset_index(drop=True)
            prep_sentence = pos['text'].apply(self.to_words)
            self.pos_output['topics'], self.pos_output['probs'] = self.topic_model.fit_transform(prep_sentence)
            self.pos_output['topic_info'] = self.topic_model.get_topic_info()
        elif sent == 'neg':
            pos = self.output[self.output['sentiment'] == 2].reset_index(drop=True)
            prep_sentence = pos['text'].apply(self.to_words)
            self.neg_output['topics'], self.neg_output['probs'] = self.topic_model.fit_transform(prep_sentence)
            self.neg_output['topic_info'] = self.topic_model.get_topic_info()
        else:
            raise NotImplementedError
            
    def sentiment(self):
        sentence_list = []
        pred_list = []
        with torch.no_grad():
            self.model.eval()
            for idx, (sentence) in enumerate(self.loader):
                prep_sentence = self.tokenizer.batch_encode_plus(sentence, padding=True, return_tensors='pt')

                prep_sentence = prep_sentence.to(self.device)

                output = self.model(**prep_sentence)
                preds = torch.argmax(output.logits, dim=-1)
                
                sentence_list.extend(sentence)
                pred_list.extend(preds.tolist())
        self.output = pd.DataFrame(zip(sentence_list, pred_list), columns = ['text', 'sentiment'])
        self.output = self.output[self.output['sentiment'] != 1]
        self.output.reset_index(drop=True, inplace=True)

    def to_words(self, corpus):
        # corpus = re.sub('^[가-힣]','',corpus)
        words = corpus.split()
        stops = set(stopwords_list)
        meaningful_words = [w for w in words if not w in stops]
        mystring = ''.join(map(str,meaningful_words))
        nouns = self.okt.nouns(mystring)
        nounstring = ','.join(map(str,nouns))
        return nounstring
