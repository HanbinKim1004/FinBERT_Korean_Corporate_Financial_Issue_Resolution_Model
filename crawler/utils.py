import pandas as pd 
import numpy as np
import os 
import datetime
from datetime import datetime as dt
import konlpy
from konlpy.tag import Kkma,Okt 
import re
import string

import konlpy
from konlpy.tag import Kkma,Okt 


from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io


###########################
### preprocessing utils ###
###########################


def remove_stopword(str_):
    stop_words = "아 휴 아이구 아이쿠 아이고 어 나 우리 저희 따라 의해 을 를 에 의 가 으로 로 에게 뿐이다 의거하여 근거하여 입각하여 기준으로 예하면 예를 들면 예를 들자면 저 소인 소생 저희 지말고 하지마 하지마라 다른 물론 또한 그리고 비길수 없다 해서는 안된다 뿐만 아니라 만이 아니다 만은 아니다 막론하고 관계없이 그치지 않다 그러나 그런데 하지만 든간에 논하지 않다 따지지 않다 설사 비록 더라도 아니면 만 못하다 하는 편이 낫다 불문하고 향하여 향해서 향하다 쪽으로 틈타 이용하여 타다 오르다 제외하고 이 외에 이 밖에 하여야 비로소 한다면 몰라도 외에도 이곳 여기 부터 기점으로 따라서 할 생각이다 하려고하다 이리하여 그리하여 그렇게 함으로써 하지만 일때 할때 앞에서 중에서 보는데서 으로써 로써 까지 해야한다 일것이다 반드시 할줄알다 할수있다 할수있어 임에 틀림없다 한다면 등 등등 제 겨우 단지 다만 할뿐 딩동 댕그 대해서 대하여 대하면 훨씬 얼마나 얼마만큼 얼마큼 남짓 여 얼마간 약간 다소 좀 조금 다수 몇 얼마 지만 하물며 또한 그러나 그렇지만 하지만 이외에도 대해 말하자면 뿐이다 다음에 반대로 반대로 말하자면 이와 반대로 바꾸어서 말하면 바꾸어서 한다면 만약 그렇지않으면 까악 툭 딱 삐걱거리다 보드득 비걱거리다 꽈당 응당 해야한다 에 가서 각 각각 여러분 각종 각자 제각기 하도록하다 와 과 그러므로 그래서 고로 한 까닭에 하기 때문에 거니와 이지만 대하여 관하여 관한 과연 실로 아니나다를가 생각한대로 진짜로 한적이있다 하곤하였다 하 하하 허허 아하 거바 와 오 왜 어째서 무엇때문에 어찌 하겠는가 무슨 어디 어느곳 더군다나 하물며 더욱이는 어느때 언제 야 이봐 어이 여보시오 흐흐 흥 휴 헉헉 헐떡헐떡 영차 여차 어기여차 끙끙 아야 앗 아야 콸콸 졸졸 좍좍 뚝뚝 주룩주룩 솨 우르르 그래도 또 그리고 바꾸어말하면 바꾸어말하자면 혹은 혹시 답다 및 그에 따르는 때가 되어 즉 지든지 설령 가령 하더라도 할지라도 일지라도 지든지 몇 거의 하마터면 인젠 이젠 된바에야 된이상 만큼 어찌됏든 그위에 게다가 점에서 보아 비추어 보아 고려하면 하게될것이다 일것이다 비교적 좀 보다더 비하면 시키다 하게하다 할만하다 의해서 연이서 이어서 잇따라 뒤따라 뒤이어 결국 의지하여 기대여 통하여 자마자 더욱더 불구하고 얼마든지 마음대로 주저하지 않고 곧 즉시 바로 당장 하자마자 밖에 안된다 하면된다 그래 그렇지 요컨대 다시 말하자면 바꿔 말하면 즉 구체적으로 말하자면 시작하여 시초에 이상 허 헉 허걱 바와같이 해도좋다 해도된다 게다가 더구나 하물며 와르르 팍 퍽 펄렁 동안 이래 하고있었다 이었다 에서 로부터 까지 예하면 했어요 해요 함께 같이 더불어 마저 마저도 양자 모두 습니다 가까스로 하려고하다 즈음하여 다른 다른 방면으로 해봐요 습니까 했어요 말할것도 없고 무릎쓰고 개의치않고 하는것만 못하다 하는것이 낫다 매 매번 들 모 어느것 어느 로써 갖고말하자면 어디 어느쪽 어느것 어느해 어느 년도 라 해도 언젠가 어떤것 어느것 저기 저쪽 저것 그때 그럼 그러면 요만한걸 그래 그때 저것만큼 그저 이르기까지 할 줄 안다 할 힘이 있다 너 너희 당신 어찌 설마 차라리 할지언정 할지라도 할망정 할지언정 구토하다 게우다 토하다 메쓰겁다 옆사람 퉤 쳇 의거하여 근거하여 의해 따라 힘입어 그 다음 버금 두번째로 기타 첫번째로 나머지는 그중에서 견지에서 형식으로 쓰여 입장에서 위해서 단지 의해되다 하도록시키다 뿐만아니라 반대로 전후 전자 앞의것 잠시 잠깐 하면서 그렇지만 다음에 그러한즉 그런즉 남들 아무거나 어찌하든지 같다 비슷하다 예컨대 이럴정도로 어떻게 만약 만일 위에서 서술한바와같이 인 듯하다 하지 않는다면 만약에 무엇 무슨 어느 어떤 아래윗 조차 한데 그럼에도 불구하고 여전히 심지어 까지도 조차도 하지 않도록 않기 위하여 때 시각 무렵 시간 동안 어때 어떠한 하여금 네 예 우선 누구 누가 알겠는가 아무도 줄은모른다 줄은 몰랏다 하는 김에 겸사겸사 하는바 그런 까닭에 한 이유는 그러니 그러니까 때문에 그 너희 그들 너희들 타인 것 것들 너 위하여 공동으로 동시에 하기 위하여 어찌하여 무엇때문에 붕붕 윙윙 나 우리 엉엉 휘익 윙윙 오호 아하 어쨋든 만 못하다 하기보다는 차라리 하는 편이 낫다 흐흐 놀라다 상대적으로 말하자면 마치 아니라면 쉿 그렇지 않으면 그렇지 않다면 안 그러면 아니었다면 하든지 아니면 이라면 좋아 알았어 하는것도 그만이다 어쩔수 없다 하나 일 일반적으로 일단 한켠으로는 오자마자 이렇게되면 이와같다면 전부 한마디 한항목 근거로 하기에 아울러 하지 않도록 않기 위해서 이르기까지 이 되다 로 인하여 까닭으로 이유만으로 이로 인하여 그래서 이 때문에 그러므로 그런 까닭에 알 수 있다 결론을 낼 수 있다 으로 인하여 있다 어떤것 관계가 있다 관련이 있다 연관되다 어떤것들 에 대해 이리하여 그리하여 여부 하기보다는 하느니 하면 할수록 운운 이러이러하다 하구나 하도다 다시말하면 다음으로 에 있다 에 달려 있다 우리 우리들 오히려 하기는한데 어떻게 어떻해 어찌됏어 어때 어째서 본대로 자 이 이쪽 여기 이것 이번 이렇게말하자면 이런 이러한 이와 같은 요만큼 요만한 것 얼마 안 되는 것 이만큼 이 정도의 이렇게 많은 것 이와 같다 이때 이렇구나 것과 같이 끼익 삐걱 따위 와 같은 사람들 부류의 사람들 왜냐하면 중의하나 오직 오로지 에 한하다 하기만 하면 도착하다 까지 미치다 도달하다 정도에 이르다 할 지경이다 결과에 이르다 관해서는 여러분 하고 있다 한 후 혼자 자기 자기집 자신 우에 종합한것과같이 총적으로 보면 총적으로 말하면 총적으로 대로 하다 으로서 참 그만이다 할 따름이다 쿵 탕탕 쾅쾅 둥둥 봐 봐라 아이야 아니 와아 응 아이 참나 년 월 일 령 영 일 이 삼 사 오 육 륙 칠 팔 구 이천육 이천칠 이천팔 이천구 하나 둘 셋 넷 다섯 여섯 일곱 여덟 아홉 령 영 이 있 하 것 들 그 되 수 이 보 않 없 나 사람 주 아니 등 같 우리 때 년 가 한 지 대하 오 말 일 그렇 위하 때문 그것 두 말하 알 그러나 받 못하 일 그런 또 문제 더 사회 많 그리고 좋 크 따르 중 나오 가지 씨 시키 만들 지금 생각하 그러 속 하나 집 살 모르 적 월 데 자신 안 어떤 내 내 경우 명 생각 시간 그녀 다시 이런 앞 보이 번 나 다른 어떻 여자 개 전 들 사실 이렇 점 싶 말 정도 좀 원 잘 통하 놓".split()
    return ' '.join([ s  for s in str(str_).split(' ') if s not in  stop_words ])

def remove_symbol(str_):
    return re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", str_)

def remove_single_word(lst):
    if len(lst) < 2 : 
        return None 
    else :
        return lst 

def remove_blank(str_):
    return str_.strip()

def remove_blank(str_):
    return str_.strip()


def tokenize(str,tokenizer) :
    return tokenizer.morphs(str)

def pos_tag(str,tokenizer) :
    return tokenizer.pos(str)

def str_to_time(str_,form):
    if '오전' in str_ or '오후' in str_ :
        str_ = str_.replace('오전','')
        str_ = str_.replace('오후','')
        time = dt.strptime(str_ ,'%Y.%m.%d.  %H:%M') 
    else : 
        time = dt.strptime(str_ ,form)  if type(str_) == str  else str_ 
    return time


def change_format(news) :
    for row in news.iloc : 
        text = row['summary '] if len(str(row['summary '])) > len(str(row['content'])) else row['content']
        new_row = pd.DataFrame(data={'date':[row['date']],'title':[text]})
        news = pd.concat([news,new_row])
    news.rename(columns={'title':'text'},inplace=True)
    return news[['date','text']].sort_values('date')


def if_verb_exist(lst):
    lst = [1 for i in lst if i[1] == 'Verb']
    if sum(lst) > 0 :
        return True
    else : 
        return False

def remove_long_number(text,pos):
    if len(pos) > 0:
        lst = [i[0] for i in pos if (i[1] == 'Number') and (len(i[0])>4) ]
        #lst+= [i[0] for i in pos if (i[1] == 'Alpha') & (len(i[0])>10) ]
        text = re.sub('||'.join(lst), repl='', string=text)
    return text


def remove_num_alpha_only (text,pos):
    if len(pos)==1 :
        if pos[0][1] in ['Number','Alpha'] :
            text =''
    return text

############################
### analyst report crawl ###
############################

def find_date(text):
    if re.findall(r'2022년 [0-9]{2}월 [0-9]{2}일',text) !=[]:
        date = re.findall(r'2022년 [0-9]{2}월 [0-9]{2}일',text)[-1]
    elif re.findall(r'22/[0-9]{2}/[0-9]{2}',text) !=[]:
        date = re.findall(r'22/[0-9]{2}/[0-9]{2}',text)[-1]
    elif re.findall(r'2022/[0-9]{2}/[0-9]{2}',text) != [] :
        date = re.findall(r'22/[0-9]{2}/[0-9]{2}',text)[-1]
    elif re.findall(r'22-[0-9]{2}-[0-9]{2}',text)!= [] :
        date = re.findall(r'22-[0-9]{2}-[0-9]{2}',text)[-1]
    elif re.findall(r'2022-[0-9]{2}-[0-9]{2}',text)!= [] :
        date = re.findall(r'2022-[0-9]{2}-[0-9]{2}',text)[-1]
    elif re.findall(r'현재 주가([0-9]{1}/[0-9]{2})',text)!= [] :
        date = re.findall(r'현재 주가([0-9]{1}/[0-9]{2})',text)
        date = date.split('주가')[-1]
    elif re.findall(r'현재 주가([0-9]{2}/[0-9]{2})',text)!= [] :
        date = re.findall(r'현재 주가([0-9]{1}/[0-9]{2})',text)
        date = date.split('주가')[-1]
    else :
        date = None
    return date

def get_month(date):
    if '/' in date : 
        month = date.split('/')[-2]
    elif '-' in date : 
        month = date.split('-')[-2]
    elif '월' in date : 
        month = date.split('월')[0][-2:]
    return month



def pdf_to_txt (fname):
    
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(fname, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                    caching=True,
                                    check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()
    # close open handles
    converter.close()
    fake_file_handle.close()

    return text

############################
###   naver news crawl   ###
############################

def get_title(news_html) : 
    if news_html.find("meta",property= "og:title") :
        title = news_html.find("meta",property= "og:title").attrs['content']
    elif news_html.select_one("#content > div.end_ct > div > h2"):
        title = news_html.select_one("#content > div.end_ct > div > h2")
    else :
        title = ''
    title = re.sub(pattern='<[^>]*>', repl='', string=''.join(str(title))) 
    return title




def get_company(news_html) : 
    if news_html.find("meta",property= "og:site_name") :
        company = news_html.find("meta",property= "og:site_name").attrs['content']

    elif news_html.find("meta",property='dd:publisher') :
        company = news_html.find("meta",property='dd:publisher').attrs['content']

    elif news_html.find("meta",property="og:article:author") :
        company = news_html.find("meta",property="og:article:author").attrs['content'].split('|')[0]

    elif news_html.find("meta",property="og:url") : 
        if 'khan' in news_html.find("meta",property="og:url").attrs['content'] :
            company = '경향신문'
        elif 'chosun' in news_html.find("meta",property="og:url").attrs['content'] :
            company = '조선일보'
        # elif 'joseilbo' in news_html.find("meta",property="og:url").attrs['content'] :
        #     company = '조세일보'
        elif 'wowtv' in news_html.find("meta",property="og:url").attrs['content'] :
            company = '한국경제TV'
        elif 'koreadaily' in news_html.find("meta",property="og:url").attrs['content'] :
            company = '중앙일보'
        elif 'yonhapnewstv' in news_html.find("meta",property="og:url").attrs['content'] :
            company = '연합뉴스TV'

        else :
            company = ''

    else :
            company = ''

    company=re.sub(pattern='<[^>]*>', repl='', string=''.join(str(company))) 

    return company



def get_content(news_html) : 
    if news_html.find("meta",property='og:description') :
        content= news_html.find("meta",property='og:description').attrs['content']
        content = re.sub('[||]||\n', repl='', string=content)
        content=re.sub(pattern='<[^>]*>', repl='', string=''.join(str(content))) 
    else : 
        content =''
    return content


def get_date(news_html) : 
    if news_html.find("meta",property="article:published_time"):
        date = news_html.find("meta",property="article:published_time").attrs['content']
        date = date[:10]
    elif news_html.find("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span"):
        date = news_html.select_one("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span").attrs['data-date-time']
    elif news_html.find("#content > div.end_ct > div > div.article_info > span > em") :
        date =news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
    else:
        date =''

    date = re.sub(pattern='<[^>]*>', repl='', string=''.join(str(date))) 
    return date