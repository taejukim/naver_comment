from concurrent.futures import thread
import os
import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime
from threading import Thread


class NaverComment:
	
    def __init__(self, msg):
        test = True
        if test:
            self.cafe_id = 30631179 # test cafe        
            menu_id = 1
        else: 
            self.cafe_id = 30020276
            menu_id = 2
        self.msg = msg
        view_type = 'W'

        print('Loading chrome..')
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'))
        
        login_url = 'https://nid.naver.com/nidlogin.login?mode=form'
        self.driver.get(login_url)
        input('네이버 로그인 후 엔터키를 입력해주세요....')
    
        self.cookies = self.get_cookies_for_requests(self.driver.get_cookies())
            
        self.url = 'https://cafe.naver.com/ArticleList.nhn?'
        self.url += 'search.clubid={}&search.menuid={}&search.boardtype={}'.format(self.cafe_id, menu_id, view_type)
        print('Move to Naver cafe..')
        self.driver.get(self.url)
        
    def get_cookies_for_requests(self, cookies):
        cookies_for_requests = dict()
        for cookie in cookies:
            key = cookie.get('name')
            value = cookie.get('value')
            cookies_for_requests[key]=value
        return cookies_for_requests

    def search_target_article(self, target_id):
        first_article = self.get_first_article(target_id)
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '게시글 ID {} 보다 최신 게시글 찾고 있습니다...'.format(target_id))
        if int(target_id) < int(first_article):
            return first_article

    def enter_password(self):
        print("get thumbnail image")
        image_url = self.soup.find_all('img', {'alt':'썸네일 이미지'})[0].get('src')
        self.driver.get(image_url)
        password = input('password 입력 : ')
        return password
    
    def get_first_article(self, target_id = None):
        r = requests.get((self.url),
          cookies=(self.cookies))
        self.soup = bs(r.text, 'html.parser')
        article_list = self.soup.find('ul',{'class':'article-movie-sub'})
        li_tag = article_list.find_all('li')[0]
        title_element = li_tag.find_all('a', {'class': 'tit'})[0]
        first_article_href = title_element.get('href')
        pattern = '(articleid\\=)(\\d*?)(?=&)'
        first_article = int(re.search(pattern, first_article_href).group().replace('articleid=',''))
        if target_id:
            if int(target_id) >= int(first_article):
                return first_article
        return first_article
        

    def write_comment(self, article_id, password):
        self.enter_article(article_id)
        content = password + self.msg
        comment_post = 'https://apis.naver.com/cafe-web/cafe-mobile/CommentPost.json'
        comment_data = {
         'content':content,
         'stickerId':'', 
         'cafeId':self.cafe_id, 
         'articleId':article_id, 
         'requestFrom':'A'}
        
        requests.post(comment_post,
          cookies=(self.cookies),
          data=comment_data)
        
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '댓글 작성 성공! ({})'.format(content))
        self.enter_article(article_id)
        
    def enter_article(self, article_id):
        url = 'https://cafe.naver.com/ArticleRead.nhn'
        url += '?clubid={}&page=1&boardtype=L&articleid={}&referrerAllArticles=false'\
        .format(self.cafe_id, article_id)
        self.driver.get(url)
        
if __name__ == '__main__':

    '''
    이근주0813 bluehaaf / skdltm1645@
    송병근 
    윤영미
    변미라1017 sssrrrjjj / 
    강나연0811 comtumi / 
    '''

    print('Start...')
    
    instances = list()
    instance_qty = int(input('네이버 ID 개수 : '))

    for i in range(instance_qty):
        msg = input('이름과 생일을 입력해주세요(홍길동0321) : ')
        instances.append(NaverComment(msg))

    first_article = instances[0].get_first_article()

    print('현재 게시판의 최신 글의 ID는 {} 입니다. \n 게시글 ID {} 보다 최신 게시글을 찾습니다.'.format(first_article, first_article))
    input('시작 하시려면 엔터키를 입력해주세요....')
    while True:
        target_article = instances[0].search_target_article(first_article)
        if target_article:
            break
    
    password = instances[0].enter_password()

    threads = list()
    for instance in instances:
        t = Thread(target=instance.write_comment, args = (target_article, password))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()
        
    input('>>>>>>>>>>>>> 엔터키를 누르면 종료 됩니다.') 
    