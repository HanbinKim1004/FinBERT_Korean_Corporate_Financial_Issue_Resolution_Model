import argparse 
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import sys
import pandas as pd
import numpy as np 
import urllib
from urllib.parse import urlparse
from utils import * 
import konlpy
from konlpy.tag import Kkma,Okt 

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem



def crawler(search_company, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}) :
    
    econ_lst = ['경향신문', '국민일보', '노컷뉴스', '뉴데일리', '뉴스타파', '뉴시스', '데일리안', '동아일보', '디지털타임스', '마이데일리', '매일경제', '머니투데이', '문화일보', '미디어오늘', '블로터', '서울경제', '서울신문', '세계일보', '스포츠동아', '스포츠서울', '스포츠조선', '스포탈코리아', '시사인', '아시아경제', '아이뉴스24', '연합뉴스TV', '오마이뉴스', '이데일리', '일간스포츠', '전자신문', '조선비즈', '조선일보', '중앙데일리', '중앙일보', '지디넷코리아', '지지통신', '코리아헤럴드', '파이낸셜뉴스', '프레시안', '한겨레', '한국경제', '한국경제TV', '한국일보', '헤럴드경제', 'JTBC', 'KBS', 'KBS', 'World', 'MBC', 'MBN', 'OSEN', 'SBS', 'YTN']
    
    url,url_lst,page_num = '', [None],1
    result_df = pd.DataFrame(columns =['date','company','text'])



    while True : 
        # sort = 0  : 관련도순
        # p = 1y : 1년 
        # &de=2022.12.11&ds=2021.12.11 : 기간
        
        # '지면기사'
        #URL = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={company}&sort=0&photo=3&field=0&pd=5&ds=2021.12.1&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:1y,a:all&start={page_num}'
        
        # '전체'. 
        URL =f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search_company}&sort=0&photo=0&field=0&pd=5&cluster_rank=22&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:1y,a:all&start={page_num}'

        # Prevent connection error 
        if np.random.randint(1) == 0 :
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        else :  
            user_agent_rotator = UserAgent()
            headers = user_agent_rotator.get_random_user_agent() # Get Random User Agent String.

        raw = requests.get(URL, headers=headers)
        html = BeautifulSoup(raw.text, "html.parser")
        articles = html.select("div.group_news > ul.list_news > li div.news_area > a")
        url_lst = [ i.attrs['href'] for i in articles ]
        
        if len(url_lst) == 0 : 
            result_df = result_df.drop_duplicates(keep='first',ignore_index=True)
            return result_df
        

        for url in url_lst :
            news = requests.get(url,headers=headers)
            html = BeautifulSoup(news.text,"html.parser")

            # only econ paper
            company,date,title,content  = get_company(html),get_date(html) , get_title(html), get_content(html)
            result = [ re.sub(pattern='<[^>]*>', repl='', string=''.join(str(i))) for i in [date,company,title,content] ]

            # use content and title sperately 
            #df = pd.DataFrame({'date':[result[0]],'company':[result[1]],'title':[result[2]],'content':[result[3]]}) 
            
            # use description and title as text source
            df = pd.DataFrame({'date':result[0],'company':result[1],'text':[result[2],result[3]] }) 
            result_df = pd.concat([result_df,df])

            if len(result_df) % 100 == 0 :
                print(f'{len(result_df)} data is done!')
                if len(result_df) % 500 == 0 :
                    result_df.to_csv(f'news_{len(result_df)}_{search_company}.csv', encoding='utf-8-sig',index=False)

        page_num +=10

    

def preprocess(df, company ,output_dir) :

    # select only econ paper
    # econ_lst = ['경향신문', '국민일보', '노컷뉴스', '뉴데일리', '뉴스타파', '뉴시스', '데일리안', '동아일보', '디지털타임스', '마이데일리', '매일경제', '머니투데이', '문화일보', '미디어오늘', '블로터', '서울경제', '서울신문', '세계일보', '스포츠동아', '스포츠서울', '스포츠조선', '스포탈코리아', '시사인', '아시아경제', '아이뉴스24', '연합뉴스TV', '오마이뉴스', '이데일리', '일간스포츠', '전자신문', '조선비즈', '조선일보', '중앙데일리', '중앙일보', '지디넷코리아', '지지통신', '코리아헤럴드', '파이낸셜뉴스', '프레시안', '한겨레', '한국경제', '한국경제TV', '한국일보', '헤럴드경제', 'JTBC', 'KBS', 'KBS', 'World', 'MBC', 'MBN', 'OSEN', 'SBS', 'YTN']
    # df['if_econ'] = df['company'].apply(lambda i : True if i in econ_lst else False)
    # df = df[df['if_econ']==True]

    df['text'] =df['text'].apply(remove_stopword)
    df['text'] =df['text'].apply(remove_symbol)
    df['text'] =df['text'].apply(remove_blank)

    df = df[['date','text']]
    df.to_csv(f'{output_dir}/news_{company}.csv', encoding='utf-8-sig',index=False)
    print(f'{output_dir}/news_{company}.csv saved!')
    return None


parser = argparse.ArgumentParser()
parser.add_argument('--company',type=str, default= '셀트리온' )
parser.add_argument('--output_dir',type=str, default= './output')


if __name__ == "__main__" :
    args = parser.parse_args() 
    df = crawler(args.company) 
    preprocess(df, args.company ,args.output_dir)

