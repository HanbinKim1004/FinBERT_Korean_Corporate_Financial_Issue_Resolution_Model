# REFERENCE :  https://github.com/FinanceData/OpenDartReader

import OpenDartReader
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import pandas as pd
import argparse
from utils import *
import konlpy
from konlpy.tag import Kkma,Okt 


def crawler(ticker, start_date, api_key) : 
    dart = OpenDartReader(api_key)  

    df = dart.list(ticker, start=start_date, kind='A', final=False)
    df['true_date'] = df['report_nm'].apply(lambda x : True if '기재정정' not in x else False)
    df = df[df['true_date']==True]
    
    file_dict =df[['report_nm','rcept_no']].to_dict()
    
    result_df =pd.DataFrame(columns = ['date','text'])

    for i in tqdm(file_dict['report_nm'].keys()) :
        name, num = file_dict['report_nm'][i], file_dict['rcept_no'][i]
        date = re.findall('\(([^)]+)', name)[0]

        xml_text = dart.document(num)
        xml_text=re.sub(pattern='<[^>]*>', repl='', string=''.join(str(xml_text)))
        xml_text=re.sub('crcc||cr||\n', repl='', string=''.join(str(xml_text)))
        xml_text = [ i+'다.' for i in xml_text.split('다.')]
        
        df = pd.DataFrame({'date': date, 'text' : xml_text})
        result_df = pd.concat([result_df,df])
    
    return result_df


def preprocess(df, company ,output_dir) :
    tokenizer = Okt()

    df['date'] = df['date'].apply(lambda x : x.split('(')[-1][:-1])

    df['text'] =df['text'].apply(remove_stopword)
    df['text'] =df['text'].apply(remove_symbol)
    df['text'] =df['text'].apply(remove_blank)
    
    df['pos_tagged'] =df['text'].apply(lambda i : pos_tag(i,tokenizer= tokenizer))
    
    # remove first page
    df = df.iloc[8:]

    # remove text w/o verb
    df['verb_exist'] = df['pos_tagged'].apply(if_verb_exist)
    df = df[df['verb_exist']==True]

    #delete long number
    df['text'] = df.apply(lambda i : remove_long_number(i['text'],i['pos_tagged']),axis=1)
    
    # drop blank data
    df = df[ df['text'] != '']

    # delete unnecessary long data
    df['text'] = df['text'].apply( lambda i : i if len(i) <2000 else '')

    
    df = df[['date','text']]
    df.to_csv(f'{output_dir}/dart_{company}.csv', encoding='utf-8-sig',index=False)
    print(f'{output_dir}/dart_{company}.csv saved!')
    return None


parser = argparse.ArgumentParser()
parser.add_argument('--company',type=str, default= '셀트리온' )
parser.add_argument('--ticker',type=str, default= '068270' )
parser.add_argument('--output_dir',type=str, default= './output')
parser.add_argument('--startdate',type=str, default= '2022-01-01')
parser.add_argument('--api_key',type=str, default = 'aa939ad957cd4a3c260d0f3c3cdc95862100c39f')

if __name__ == "__main__" :
    args = parser.parse_args() 
    df = crawler(args.ticker, args.startdate, args.api_key) 
    preprocess(df, args.company ,args.output_dir)


