from torch.utils.data import Dataset


class FinanceDataset(Dataset):
    def __init__(self, df, mode='train'):
        self.df = df
        self.mode = mode
        self.label2key = {'positive' : 2, 'neutral' : 1, 'negative' : 0}
    def __len__(self):
        len_dataset = len(self.df)
        return len_dataset

    def __getitem__(self, idx):
        sentence = self.df.iloc[idx]['text']
        
        if self.mode == 'test':
            return sentence
        else:
            label = self.df.iloc[idx]['labels']
            return sentence, self.label2key[label]