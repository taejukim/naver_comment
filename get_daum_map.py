import requests
import json
import pandas as pd

# 인증은 위한 최소한의 HTTP Response header 와 cookie 정보 정의
headers = {
  'DNT':"1", 
  'Referer':'https://map.kakao.com/', 
  'Sec-Fetch-Mode':'no-cors', 
  'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
  }
cookies = {
  "webid":'d6e743dad4184efab72a025470041072',
  "coachmark:0":"true", 
  "coachmark:2":"true"}
  
def get_daum(x, y): 
    # kakao map 에 그려지는 식당 포인트를 JSON 으로 받아 볼 수 있는 URL
    # 지도의 배율은 L4이고 좌우로 1100, 상하로 1300의 범위를 갖고 있음
    url = 'https://tilesrch.map.daum.net/tmap/msearch/L4/{}/{}.png?output=jsonp&callback=L4_{}_{}&query=%EC%8B%9D%EB%8B%B9&dimg=ns'\
    .format(x,y,x,y)
    r = requests.get(url, headers=headers, cookies=cookies)
    c = 'L4_{}_{}'.format(x, y)
    try:
        # JSON Format만 추출하는 함수
        return get_list(c, r.text)
    except:
        return 

def get_list(c, r):
#     print(r)
    d = r.replace(c, '').replace('(','').replace(')','')
    return json.loads(d)

​lst = []
# x range 0 ~ 1100, y range 0 ~ 1300 (L4)
# X,Y의 모든 범위를 순회하는 이중 For문
for x in range(0, 1100):
    print('x : {}'.format(x))
    for y in range(0, 1300):
        retv = get_daum(x, y)
        if retv:
            lst += retv

# 저장된 Json format을 Pandas dataframe으로 변경 후 Excel 파일로 저장
pd.DataFrame(lst).to_excel('test1.xlsx')