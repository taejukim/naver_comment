"""
20200908 ver 2.0
@author: ***
python==3.7.9
selenium==3.141.0
urllib3==1.25.10
requests==2.24.0
beautifulsoup4==4.9.1
"""
import sys, os, requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from urllib import parse
import time
from datetime import datetime
import threading, re

class NaverComment:
    '''특정 Naver Cafe에 Target ID의 게시글이 생기는 즉시 댓글을 남기는 프로그램'''

    def __init__(self):
        """
        init 함수
        """
        self.cafe_id = 30020276
        self.comment_flag = False
        if getattr(sys, 'frozen', False):
            chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe')
            self.driver = webdriver.Chrome(chromedriver_path)
        else:
            self.driver = webdriver.Chrome()
        login_url = 'https://nid.naver.com/nidlogin.login?mode=form'
        self.driver.get(login_url)
        input('네이버 로그인 후 엔터키를 입력해주세요....')
        self.msg = input('이름과 생일을 입력해주세요(홍길동0321) : ')
        print('입력하하신 이름과 생일의 내용은 "{}" 입니다.'.format(self.msg))
        self.cookies = self.get_cookies_for_requests(self.driver.get_cookies())
        self.url = 'https://cafe.naver.com/ArticleList.nhn?'
        self.url += 'search.clubid={}&search.menuid=2&search.boardtype=L'.format(self.cafe_id)
        self.driver.get(self.url)

    def get_cookies_for_requests(self, cookies):
        """
        Selenium으로 접속한 Browser cookie를 requests 모듈에 적용할 수 있도록 변환하여 반환
        :param cookies: 
        :return:
        """
        cookies_for_requests = dict()
        for cookie in cookies:
            key = cookie.get('name')
            value = cookie.get('value')
            cookies_for_requests[key] = value
        else:
            return cookies_for_requests

    def search_target_article(self, target_id):
        """
        입력 받은 Target 게시글의 ID를 찾는 함수
        :param target_id: 찾고자 하는 게시글 ID
        :return:
        """
        if self.comment_flag:
            return
        first_article, dongho = self.get_first_article()
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '게시글 ID {} 보다 최신 게시글 찾고 있습니다...'.format(target_id))
        if int(target_id) < int(first_article):
            if self.comment_flag:
                return True
            self.write_comment(first_article, dongho)
            print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '완료', first_article)
            return True

    def get_first_article(self):
        r = requests.get((self.url),
          cookies=(self.cookies))
        soup = bs(r.text, 'html.parser')
        tbodys = soup.find_all('tbody')
        first_article = tbodys[1].find_all('div', {'class': 'inner_number'})[0].text
        title = tbodys[1].find_all('div', {'class': 'inner_list'})[0].text.strip()
        try:
            dong = re.search('\\d*?(?=동)', title).group().zfill(4)
            ho = re.search('\\d*?(?=호)', title).group().zfill(4)
        except:
            return (
             first_article, None)
        else:
            return (
             first_article, dong + ho)

    def write_comment(self, article_id, dongho):
        """
        게시글에 댓글을 남기는 함수
        :param article_id: 댓글을 남길 게시글 ID
        :prarm msg: 댓글의 내용
        :return:
        """
        if self.comment_flag:
            return True
        self.comment_flag = True
        comment_post = 'https://apis.naver.com/cafe-web/cafe-mobile/CommentPost.json'
        if dongho:
            msg = dongho + self.msg
        else:
            msg = self.msg
        comment_data = {'content':dongho + self.msg,  'stickerId':'', 
         'cafeId':self.cafe_id, 
         'articleId':article_id, 
         'requestFrom':'A'}
        comment = requests.post(comment_post,
          cookies=(self.cookies),
          data=comment_data)
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '댓글 작성 성공! ({})'.format(self.msg))
        self.enter_article(article_id)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>> Ctrl + C 를 누르면 종료 됩니다.')
        return article_id

    def enter_article(self, article_id):
        """
        댓글을 남긴 게시글에 진입하는 함수(Selenium)
        :param article_id: 댓글을 남긴 게시글 ID
        :return:
        """
        url = 'https://cafe.naver.com/ArticleRead.nhn'
        url += '?clubid={}&page=1&boardtype=L&articleid={}&referrerAllArticles=false'.format(self.cafe_id, article_id)
        self.driver.get(url)


if __name__ == '__main__':
    test = True
    comment = NaverComment()
    time.sleep(3)
    first_article, _ = comment.get_first_article()
    print('현재 게시판의 최신 글의 ID는 {} 입니다. \n 게시글 ID {} 보다 최신 게시글을 찾습니다.'.format(first_article, first_article))
    input('시작 하시려면 엔터키를 입력해주세요....')
    while True:
        comment.search_target_article(first_article)
