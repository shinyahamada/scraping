# coding: utf-8
import math
import pprint
import json
import requests
from bs4 import BeautifulSoup

# GASではシートの書き出しのみやってもらうようにするから、
# GASでいう所の info オブジェクトまでは python で用意するようにする
# info {
#   companyName: ****,
#   url: *******,
#   business: ********,
#   foundation: ********,
#   mediaKind: ********,
# }

MEDIA_KIND = 'DODA'

def main():

    # print('Hello Python!!')

    # html の取得 -> ページ数解析
    dodaUrl = "https://doda.jp/DodaFront/View/JobSearchList.action?op=17%2C70%2C71%2C76&pic=1&preBtn=3&ds=1&oc=03L&so=50&tp=1"
    htmlContent = requests.get(dodaUrl)
    soup = BeautifulSoup(htmlContent.content, "html.parser")

    recruitsCount = soup.find("span", {'class': 'number'}).get_text()

    pages = math.ceil(int(recruitsCount) / 50)



    for i in range(pages):

        # ページ先の html を取得
        targetUrl = dodaUrl + '&page=' + str(i+1)
        html = requests.get(targetUrl)
        soup = BeautifulSoup(html.content, "html.parser")

        # 詳細ページへのリンク取得
        urls = getDetailUrls(soup)

        # それぞれの会社の情報を取得
        infoList = getInfoList(urls)

        print(infoList[0])

        # GAS に POST 
        postToGas(infoList)


# それぞれの詳細ページにアクセスし、データ(info)のリストを返す
def getInfoList(urls):
    infoList = []

    # for test in range(2):
    #     infoList.append(getInfo(urls[test]))

    for detailUrl in urls:
        infoList.append(getInfo(detailUrl))
    else:
        return infoList


def getInfo(detailUrl):
    html = requests.get(detailUrl)
    soup = BeautifulSoup(html.content, "html.parser")
    info = {}
    info['companyName'] = soup.find('h1').text.replace("\n","").replace("\r","").replace(" ","")
    info['business'] = soup.select('th:contains("事業概要") + td')[0].text
    if len(soup.select('th:contains("企業URL") + td')) != 0:
        info['url'] = soup.select('th:contains("企業URL") + td')[0].a.attrs['href'] 
    if len(soup.select('th:contains("設立") ~ td')) != 0:
        info['foundation'] = soup.select('th:contains("設立") ~ td')[0].text.replace("\n","").replace("\r","").replace(" ","")
    info['mediaKind'] = MEDIA_KIND

    print(info['companyName']);

    return info


def postToGas(infoList):

    # html を解析のためにGASへ送る
    response = requests.post(
        'https://script.google.com/macros/s/AKfycbyCIAMv2kxUUR6Wt_q1GXmY-PduxWsLzQMaE7yt6Axvr2APhqno/exec',
        data = json.dumps(infoList)
    )

    print(response.json)


# URL整形
def getDetailUrls(soup):
    pureUrls = soup.find_all('h2', {'class': 'title'})
    urls= []
    for item in pureUrls:
        pureUrl = item.a.attrs['href']
        containUrl = pureUrl.split('JobSearchDetail/')[1]
        jobId = containUrl.split('/')[0]
        url = "https://doda.jp/DodaFront/View/JobSearchDetail/" + jobId + "/-tab__jd/-fm__jobdetail/-mpsc_sid__10/-tp__1/"
        urls.append(url)
    else:
        return urls

# メイン関数の実行
main()


# def test():
#     infoList = []
#     info = {}
#     info['companyName'] =  'fdfafda'
#     info['url'] = 'fdafadfa'
#     info['business'] = 'fdafa'
#     info['foundation'] = 'faldfjad'
#     info['mediaKind'] = 'DODA'

#     infoo = {}
#     infoo['companyName'] = 'aaaa'
#     infoo['url'] = 'fdfafadfa'
#     infoo['business'] = 'alalalal'
#     infoo['foundation'] = 'foundation'
#     infoo['mediaKind'] = 'DODA'

#     infoList.append(info)
#     infoList.append(infoo)
#     infoList.append(info) # 重複チェック用

#     postToGas(json.dumps(infoList))

# test()

