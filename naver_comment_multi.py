from concurrent.futures import thread
import os
import requests
import time
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime
from threading import Thread

import info

class NaverComment:
	
    def __init__(self, id, password, msg, test=False):
        if test:
            self.cafe_id = 30631179 # test cafe        
            menu_id = 1
        else: 
            self.cafe_id = 30020276
            menu_id = 2
        self.msg = msg
        view_type = 'W'

        print('브라우저 로딩...')
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'))
        
        if not self.login(id, password):
            input('Login 후 엔터를 눌러주세요')
    
        self.cookies = self.get_cookies_for_requests(self.driver.get_cookies())
            
        self.url = 'https://cafe.naver.com/ArticleList.nhn?'
        self.url += 'search.clubid={}&search.menuid={}&search.boardtype={}'.format(self.cafe_id, menu_id, view_type)
        print('네이버 카페로 이동...')
        self.driver.get(self.url)
        
    def get_cookies_for_requests(self, cookies):
        cookies_for_requests = dict()
        for cookie in cookies:
            key = cookie.get('name')
            value = cookie.get('value')
            cookies_for_requests[key]=value
        return cookies_for_requests

    def login(self, id, password):
        login_url = 'https://nid.naver.com/nidlogin.login?mode=form'
        self.driver.get(login_url)
        time.sleep(1)
        input_js = ' \
        document.getElementById("id").value = "{}"; \
        document.getElementById("pw").value = "{}"; \
        '.format(id, password)
        self.driver.execute_script(input_js)
        time.sleep(1)
        self.driver.find_element_by_id('log.login').click()
        time.sleep(2)
        if self.driver.find_element_by_id('query'):
            return True
        return False

    def search_target_article(self, target_id):
        first_article = self.get_first_article(target_id)
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '게시글 ID {} 보다 최신 게시글 찾고 있습니다...'.format(target_id))
        if int(target_id) < int(first_article):
            return first_article

    def enter_password(self):
        image_url = self.soup.find_all('img', {'alt':'썸네일 이미지'})[0].get('src')
        self.driver.get(image_url)
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '썸네일 이미지 추출 완료')
        password = input(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f] Password 입력 : '))
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


    print('시작...')

    is_test = input("Test 인가요? [y/n] ")
    while True:
        if is_test == 'y' or is_test == 'n':
            break
        is_test = input("다시 입력해주세요. Test 인가요? [y/n] ")
    ids = info.info
    if is_test:
        ids = info.test_info


    instances = list()
    for i in ids:
        msg = i.get('msg')
        id = i.get('id')
        password = i.get('pass')
        print(msg, id, password)
        if is_test == 'y':
            args = (id, password, msg, True)
        else:
            args = (id, password, msg)
        instances.append(NaverComment(*args))

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
    