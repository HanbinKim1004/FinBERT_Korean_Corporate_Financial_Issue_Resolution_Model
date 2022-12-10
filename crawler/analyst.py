import os
import re
from utils import * 
import argparse
from tqdm import tqdm
import konlpy
from konlpy.tag import Kkma,Okt 
import pandas as pd


def crawler(input_dir,company):
    source_dir = f'{input_dir}/{company}'
    result_df = pd.DataFrame(columns=['date','text'])
    for fname in tqdm(os.listdir(source_dir)) : 
        text = pdf_to_txt(f'{source_dir}/{fname}')

        #remove content after 'Compliance Notice' 
        text = text.split('Compliance Notice')[0]

        text = re.sub('\n', repl='', string=''.join(str(text)))
        text = re.sub(pattern= r'[표[0-9]{1}]', repl='',  string = text)
        text = re.sub(pattern= r'[그림[0-9]{1}]', repl='', string =  text)
        
        # get date from text
        date = find_date(text)

        #split in sentences
        text = [ i+'다.' for i in text.split('다.')]

        df = pd.DataFrame(data={'date': date,'text':text})
        result_df = pd.concat([result_df,df])
    
    return result_df


def preprocess(df,company,output_dir) :
    tokenizer = Okt() 

    df['text'] =df['text'].apply(remove_stopword)
    df['text'] =df['text'].apply(remove_symbol)
    df['text'] =df['text'].apply(remove_blank)

    df['pos_tagged'] =df['text'].apply(lambda i : pos_tag(i,tokenizer= tokenizer))
    
    # remove text w/o verb
    df['verb_exist'] = df['pos_tagged'].apply(if_verb_exist)
    df = df[df['verb_exist']==True]

    # remove long number
    df['text'] = df.apply(lambda i : remove_long_number(i['text'],i['pos_tagged']),axis=1)

    # delete unnecessary long data
    df['text'] = df['text'].apply( lambda i : i if len(i) <2000 else '')

    # drop blank data
    df = df[ (df['text']!= '' )  ]

    # drop unnecessary long text 
    

    df = df[['date','text']]

    df.to_csv(f'{output_dir}/analyst_{company}.csv', encoding='utf-8-sig',index=False)
    print(f'{output_dir}/analyst_{company}.csv saved!')
    return None

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir',type=str, default= './pdf_input' )
parser.add_argument('--company',type=str, default= '셀트리온' )
parser.add_argument('--out_dir',type=str, default= './output')


if __name__ == "__main__" :
    args = parser.parse_args() 
    df = crawler(args.input_dir,args.company)
    preprocess(df,args.company,args.out_dir)

    