import pandas as pd
import cv2
import os
from glob import glob
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from torchmetrics import F1Score
from dataset import FinanceDataset

os.environ["TOKENIZERS_PARALLELISM"] = "false"

EXP_NAME = 'exp3_nofreeze'
BATCH_SIZE = 32
NUM_EPOCHS = 50
LEARNING_RATE = 2e-3

class Averager:
    def __init__(self):
        self.current_total = 0.0
        self.count = 0

    def update(self, value, batch_size):
        self.current_total += value * batch_size
        self.count += batch_size
    
    def acc_update(self, value, batch_size):
        self.current_total += value
        self.count += batch_size
    @property
    def value(self):
        if self.count == 0:
            return 0
        else:
            return 1.0 * self.current_total / self.count

    def reset(self):
        self.current_total = 0.0
        self.count = 0

df = pd.read_csv('/workspace/KR-FinBert/finance_data.csv')
df_train, df_valid = train_test_split(df, test_size=0.2, random_state=42, stratify=df['labels'])

dataset_train = FinanceDataset(df_train, mode='train')
dataset_valid = FinanceDataset(df_train, mode='val')

train_loader = DataLoader(dataset_train,
                                batch_size=BATCH_SIZE,
                                num_workers=4,
                                shuffle=True,
                                pin_memory=True,
                                drop_last=False,
                                # collate_fn=collate
                            )
                            
valid_loader = DataLoader(dataset_valid,
                                batch_size=BATCH_SIZE,
                                num_workers=4,
                                shuffle=False,
                                pin_memory=True,
                                drop_last=False,
                                # collate_fn=collate
                            )


device = torch.device('cuda')
model = AutoModelForSequenceClassification.from_pretrained("snunlp/KR-FinBert", num_labels=3).to(device)
new_params = list(model.classifier.parameters()) + list(model.bert.pooler.dense.parameters())
optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9)
nSamples = [604, 2879, 1363]
normedWeights = [1 - (x / sum(nSamples)) for x in nSamples]
normedWeights = torch.FloatTensor(normedWeights).to(device)
criterion = torch.nn.CrossEntropyLoss(normedWeights)
# criterion = torch.nn.CrossEntropyLoss()
tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert")
best_val_acc = 0
f1 = F1Score(average='macro', num_classes=3)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer,step_size=10, gamma=0.3, verbose=True)

for epoch in range(NUM_EPOCHS):
    train_loss_hist = Averager()
    train_acc_hist = Averager()
    model.train()
    for idx, (sentence, label) in enumerate(train_loader):
        optimizer.zero_grad()
        sentence = tokenizer.batch_encode_plus(sentence, padding=True, return_tensors='pt')

        sentence = sentence.to(device)
        label = label.to(device)

        output = model(**sentence)
        preds = torch.argmax(output.logits, dim=-1)
        loss = criterion(output.logits, label)
            
        loss_value = loss.item()
        matches = (preds == label).sum().item()

        train_loss_hist.update(loss_value, BATCH_SIZE)
        train_acc_hist.acc_update(matches, BATCH_SIZE)
        
        loss.backward()
        optimizer.step()

    print(
                    f"Epoch[{epoch+1}/{NUM_EPOCHS}]({idx + 1}/{len(train_loader)}) || "
                    f"training loss {train_loss_hist.value:4.4} || training accuracy {train_acc_hist.value:4.2%}"
                )
    train_loss_hist.reset()
    train_acc_hist.reset()
    
    ## VAL
    val_loss_hist = Averager()
    val_acc_hist = Averager()
    target_list = []
    pred_list = []
    
    with torch.no_grad():
        model.eval()
        for idx, (sentence, label) in enumerate(valid_loader):
            sentence = tokenizer.batch_encode_plus(sentence, padding=True, return_tensors='pt')

            sentence = sentence.to(device)
            label = label.to(device)

            output = model(**sentence)
            preds = torch.argmax(output.logits, dim=-1)
            
            target_list.extend(label.tolist())
            pred_list.extend(preds.tolist())

            loss_item = criterion(output.logits, label).detach().item()
            acc_item = (label == preds).sum().item()

            val_loss_hist.update(loss_item, BATCH_SIZE)
            val_acc_hist.acc_update(acc_item, BATCH_SIZE)
    if val_acc_hist.value > best_val_acc:
        best_val_acc = val_acc_hist.value
        model.save_pretrained(os.path.join(*['models', EXP_NAME, f'{best_val_acc:.3f}']))
    print(f"[Val] Acc : {val_acc_hist.value:4.2%}, Loss: {val_loss_hist.value:4.2}, F1: {f1(torch.tensor(pred_list), torch.tensor(target_list)):4.2}")
    scheduler.step()