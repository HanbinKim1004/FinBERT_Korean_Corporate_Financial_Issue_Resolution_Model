# REFERENCE : https://codingspooning.tistory.com/entry/파이썬-네이버-종목토론방-크롤링

from bs4 import BeautifulSoup
import requests
import re
import datetime as dt
from tqdm import tqdm
import pandas as pd
import argparse
from utils import *
import konlpy
from konlpy.tag import Kkma,Okt 



def crawler(codes, page,startdate, headers  = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}):
    result_df = pd.DataFrame([])
    start_date= dt.strptime(startdate, "%Y-%m-%d")

    n_ = 0
    for page in tqdm(range(1, page)):
        n_ += 1
        
        url = "https://finance.naver.com/item/board.naver?code=%s&page=%s" % (codes, str(page))
        html = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html.decode('euc-kr', 'replace'), 'html.parser')
        table = soup.find('table', {'class': 'type2'})
        tb = table.select('tbody > tr')

        for i in range(2, len(tb)):
            if len(tb[i].select('td > span')) > 0:
                date = tb[i].select('td > span')[0].text
                start_date= dt.strptime(startdate, "%Y-%m-%d")
                date= str_to_time(date,'%Y.%m.%d %H:%M')

                if start_date > date : 
                    print(f' comment from {date} done!')
                    return result_df

                text = tb[i].select('td.title > a')[0]['title']
                table = pd.DataFrame({'date': [date], 'text': [text]})
                result_df = pd.concat([result_df, table])

    return result_df


def preprocess(df,company,output_dir) :
    tokenizer = Okt() 

    df['text'] =df['text'].apply(remove_stopword)
    df['text'] =df['text'].apply(remove_symbol)
    df['text'] =df['text'].apply(remove_blank)

    #df['tokenized'] =df['text'].apply(lambda i : tokenize(i,tokenizer= tokenizer))
    df['pos_tagged'] =df['text'].apply(lambda i : pos_tag(i,tokenizer= tokenizer))
    
    #remove data with only number or only alpha
    df['text'] = df.apply(lambda i : remove_num_alpha_only(i['text'],i['pos_tagged']), axis=1)

    #delete long number
    df['text'] = df.apply(lambda i : remove_long_number(i['text'],i['pos_tagged']),axis=1)
    

    # remove blank data
    df = df[( df['text'] !='' ) & (df['pos_tagged'] != None) ]

    result= df[['date','text']]
    result.to_csv(f'{output_dir}/comment_{company}.csv', encoding='utf-8-sig',index=False)

    print(f'{output_dir}/comment_{company}.csv saved!')

    return None

parser = argparse.ArgumentParser()
parser.add_argument('--max_page',type=int, default= 1500)
parser.add_argument('--ticker',type=str, default= '068270' )
parser.add_argument('--company',type=str, default= '셀트리온' )
parser.add_argument('--output_dir',type=str, default= './output')
parser.add_argument('--startdate',type=str, default= '2022-01-01')


if __name__ == "__main__" :
    args = parser.parse_args() 
    df = crawler(args.ticker,args.max_page, args.startdate)
    preprocess(df,company=args.company, output_dir=args.output_dir)

