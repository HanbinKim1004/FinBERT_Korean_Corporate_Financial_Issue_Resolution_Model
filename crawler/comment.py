# REFERENCE : https://codingspooning.tistory.com/entry/파이썬-네이버-종목토론방-크롤링

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



def crawler(codes, page, headers  = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}):
    result_df = pd.DataFrame([])
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
                title = tb[i].select('td.title > a')[0]['title']
                views = tb[i].select('td > span')[1].text
                pos = tb[i].select('td > strong')[0].text
                neg = tb[i].select('td > strong')[1].text
                table = pd.DataFrame({'날짜': [date], '제목': [title], '조회': [views], '공감': [pos], '비공감': [neg]})
                result_df = pd.concat([result_df, table])

    return result_df


def preprocess(df,startdate,company,output_dir) :
    tokenizer = Okt() 

    # str-to-time 
    df['날짜'] = df['날짜'].apply(lambda i : str_to_time(i,'%Y.%m.%d %H:%M'))
    start_date= dt.strptime(startdate, "%Y%m%d")
    df = df[ start_date < df['날짜'] ]

    df.rename(columns={'제목':'text'},inplace=True)
    df.rename(columns={'날짜':'date'},inplace=True)

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
parser.add_argument('--page',type=int, default= 1000)
parser.add_argument('--ticker',type=str, default= '068270' )
parser.add_argument('--company',type=str, default= '셀트리온' )
parser.add_argument('--output_dir',type=str, default= './output')
parser.add_argument('--startdate',type=str, default= '20220101')


if __name__ == "__main__" :
    args = parser.parse_args() 
    df = crawler(args.ticker,args.page)
    preprocess(df,startdate = args.startdate,company=args.company, output_dir=args.output_dir)

