"""
20200908 ver 2.0
@author: ***
python==3.7.9
selenium==3.141.0
urllib3==1.25.10
requests==2.24.0
beautifulsoup4==4.9.1
"""
import os, io
import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re
import time
from datetime import datetime
from PIL import Image
import pytesseract


class NaverComment:
    """
    특정 Naver Cafe에 Target ID의 게시글이 생기는 즉시 댓글을 남기는 프로그램
    """
	
    def __init__(self):
        """
        init 함수
        """
        self.cafe_id = 30020276
        self.comment_flag = False
        print('Loading chrome..')
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'))
        print('Complete..')
        login_url = 'https://nid.naver.com/nidlogin.login?mode=form'
        self.driver.get(login_url)
        input('네이버 로그인 후 엔터키를 입력해주세요....')
        self.msg = input('이름과 생일을 입력해주세요(홍길동0321) : ')
        print('입력하신 이름과 생일은 "{}" 입니다.'.format(self.msg))
        self.cookies = self.get_cookies_for_requests(self.driver.get_cookies())
        self.url = 'https://cafe.naver.com/ArticleList.nhn?'
        view_type = 'W'
        self.url += 'search.clubid={}&search.menuid=2&search.boardtype={}'.format(self.cafe_id, view_type)
        print('Move to Naver cafe..')
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
            cookies_for_requests[key]=value
        return cookies_for_requests
        
    def get_image_text(self):
        pass

    def search_target_article(self, target_id):
        """
        입력 받은 Target 게시글의 ID를 찾는 함수
        :param target_id: 찾고자 하는 게시글 ID
        :return:
        """
        if self.comment_flag:
            return
        first_article, dongho = self.get_first_article(target_id)
        print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '게시글 ID {} 보다 최신 게시글 찾고 있습니다...'.format(target_id))
        if int(target_id) < int(first_article):
            if self.comment_flag:
                return True
            self.write_comment(first_article, dongho)
            print(datetime.now().strftime('[%y-%m-%d %H:%M:%S.%f]'), '완료', first_article)
            return True
    
    def get_first_article(self, target_id = None):
        r = requests.get((self.url),
          cookies=(self.cookies))
        soup = bs(r.text, 'html.parser')
        article_list = soup.find('ul',{'class':'article-movie-sub'})
        li_tag = article_list.find_all('li')[0]
        title_element = li_tag.find_all('a', {'class': 'tit'})[0]
        first_article_href = title_element.get('href')
        pattern = '(articleid\\=)(\\d*?)(?=&)'
        first_article = int(re.search(pattern, first_article_href).group().replace('articleid=',''))
        if target_id:
            if int(target_id) >= int(first_article):
                return first_article, None
        print("get thumbnail image")
        image_url = li_tag.find_all('img', {'alt':'썸네일 이미지'})[0].get('src')
        image_response = requests.get(image_url, cookies=(self.cookies))
        image_object = Image.open(io.BytesIO(image_response.content))
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        ocr_result = pytesseract.image_to_string(image_object, lang='kor')
        try:
            dong = re.search('\\d*?(?=동)', ocr_result).group().zfill(4)
            ho = re.search('\\d*?(?=호)', ocr_result).group().zfill(4)
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
        self.enter_article(article_id)
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
        url += '?clubid={}&page=1&boardtype=L&articleid={}&referrerAllArticles=false'\
        .format(self.cafe_id, article_id)
        self.driver.get(url)
        
if __name__ == '__main__':
    print('Start...')
    test = True
    comment = NaverComment()
    time.sleep(3)
    first_article, _ = comment.get_first_article()

    print('현재 게시판의 최신 글의 ID는 {} 입니다. \n 게시글 ID {} 보다 최신 게시글을 찾습니다.'.format(first_article, first_article))
    input('시작 하시려면 엔터키를 입력해주세요....')
    while True:
        comment.search_target_article(first_article)
    