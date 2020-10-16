"""
20200908 ver 2.0
@author: ***
python==3.7.9
selenium==3.141.0
urllib3==1.25.10
requests==2.24.0
beautifulsoup4==4.9.1
"""
import sys, os
import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from urllib import parse
import time
from datetime import datetime
import threading


class NaverComment:
    """
    특정 Naver Cafe에 Target ID의 게시글이 생기는 즉시 댓글을 남기는 프로그램
    """
	
    def __init__(self):
        """
        init 함수
        """
        # https://cafe.naver.com/ArticleList.nhn?search.clubid=29118241&search.menuid=27&search.boardtype=L\
        self.cafe_id = int(input('Naver Cafe ID를 입력해주세요. (ex : 29118241 또는 30020276) : '))
        self.board_id = int(input('Cafe 게시판 ID를 입력해주세요. (ex : 27 또는 2) : ')) 
        # self.cafe_id = 29118241 # https://cafe.naver.com/campingkanㅊ
        self.comment_flag = False

        if  getattr(sys, 'frozen', False): 
            chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
            self.driver = webdriver.Chrome(chromedriver_path)
        else:
            self.driver = webdriver.Chrome()
        login_url = 'https://nid.naver.com/nidlogin.login?mode=form'
        self.driver.get(login_url)
        input('로그인 후 엔터키를 입력해주세요....')
        self.cookies = self.get_cookies_for_requests(self.driver.get_cookies())
        self.url = 'https://cafe.naver.com/ArticleList.nhn?'
        self.url +='search.clubid={}&search.menuid={}&search.boardtype=L'.format(self.cafe_id, self.board_id)
        # https://cafe.naver.com/ArticleList.nhn?search.clubid=30020276&search.menuid=2&search.boardtype=L
        self.driver.get(self.url)
        self.msg = input('댓글 내용을 입력해주세요 : ')
        print('입력하하신 댓글의 내용은 "{}" 입니다.'.format(self.msg))
        limit_thread = int(input('최대로 생성할 Thread의 수를 입력하세요(1 ~ 10) : '))
        self.sem = threading.Semaphore(limit_thread)

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
            cookies_for_requests[key]=value
        return cookies_for_requests
        
    def search_target_article(self, target, mode):
        """
        입력 받은 Target 게시글의 작성자 찾는 함수
        :param author : 찾고자 하는 게시글의 작성자(nick name)
        :return:
        """
        self.sem.acquire()
        if self.comment_flag:
            return
        first_article_author, first_article_id = self.get_first_article()
        if mode == 1:
            print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'),\
                '게시글 작성자가 "{}" 인 게시글 찾고 있습니다...'.format(target))
            if target in first_article_author:
                if self.comment_flag:
                    self.sem.release()
                    return True
                self.write_comment(first_article_id)
                print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '완료', first_article_id)
                self.sem.release()
                return True
            self.sem.release()
        else:
            print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'),\
             '게시글 ID {} 보다 최신 게시글 찾고 있습니다...'.format(target))
            if int(target) < int(first_article_id):
                print(target, first_article_id)
                if self.comment_flag:
                    self.sem.release()
                    return True
                self.write_comment(first_article_id)
                print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '완료', first_article_id)
                self.sem.release()
                return True
            self.sem.release()
    
    def get_first_article(self):
        r = requests.get(
            self.url, 
            cookies = self.cookies,
            )
        soup = bs(r.text, 'html.parser')
        tbodys = soup.find_all('tbody')
        first_article_author = tbodys[1].find_all('td', {'class':'td_name'})[0].text # 작성자 컬럼
        first_article_id = tbodys[1].find_all('div', {'class':'inner_number'})[0].text # ID
        #time.sleep(0.01)
        return first_article_author, first_article_id

    def write_comment(self, article_id):
        """
        게시글에 댓글을 남기는 함수
        :param article_id: 댓글을 남길 게시글 ID
        :prarm msg: 댓글의 내용
        :return:
        """
        if self.comment_flag:
            return True
        self.comment_flag = True
        # idenifier = 'https://apis.naver.com/cafe-home-web/cafe-home/v1/member/identifier'
        comment_post = 'https://apis.naver.com/cafe-web/cafe-mobile/CommentPost.json'
        # requests.get(idenifier, cookies=self.cookies)
        comment_data = {
             'content': self.msg,
             'stickerId': '',
             'cafeId': self.cafe_id,
             'articleId': article_id,
             'requestFrom': 'A'
             }
        _comment = requests.post(
                    comment_post,
                    cookies=self.cookies,
                    data=comment_data
                    )
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'),\
                     '댓글 작성 성공! ({})'.format(self.msg))
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
        url += '?clubid={}&page=1&boardtype=L&articleid={}&referrerAllArticles=false'\
        .format(self.cafe_id, article_id)
        self.driver.get(url)
        
if __name__ == '__main__':
    try:
        test = True
        comment = NaverComment()
        time.sleep(3)
        print("검색 모드 선택\n1. 게시글 작성자 검색\n2. 게시글 ID 검색")
        mode = int(input("(1 또는 2 입력): "))
        if mode == 1: # 게시글 작성 검색
            target = input('Target 게시글의 작성자를 입력해주세요. : ')
            print('작성자가 "{}" 인 게시글을 찾아 "{}" 내용의 댓글을 작성합니다. '.format(target, comment.msg))
        else: # 게시글 ID 검색
            _author, target = comment.get_first_article()
            print('현재 게시판의 최신 글의 ID는 {} 입니다. \n 게시글 ID {} 보다 최신 게시글을 찾습니다.'\
                .format(target, target))
        input('시작 하시려면 엔터키를 입력해주세요....')
        while True:
                t = threading.Thread(target=comment.search_target_article,
                                    args=(target,mode,))
                t.start()
    except:
        pass