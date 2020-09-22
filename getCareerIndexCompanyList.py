# coding: utf-8
import math
import pprint
import json
import requests
from bs4 import BeautifulSoup

# type 掲載企業がGraspyにかなりフィットしてそうだったが
# 掲載企業のURL

MEDIA_KIND = 'CareerIndex'

def main():
    # html の取得 => ページ数解析
    nextUrl = "https://careerindex.jp/job_offers?utf8=%E2%9C%93&s%5Boccupation%5D%5B%5D=01&s%5Boccupation%5D%5B%5D=05&s%5Bprefecture%5D%5B%5D=13&s%5Bword_search_type%5D=all&s%5Bword%5D=&s%5Bemployment%5D%5B%5D=03001&s%5Bannual_income%5D=&s%5Bindustry%5D%5B%5D=02&s%5Bfeature%5D%5B%5D=19002"
    htmlContent = requests.get(nextUrl)
    soup = BeautifulSoup(htmlContent.content, "html.parser")

    recruitsCountStr = soup.find("strong").get_text()
    recruitsCountStr = recruitsCountStr.replace(",", "")
    recruitsCount = recruitsCountStr.replace("件", "")

    # ページ数取得 => CareerIndex は 20 件ずつページネーションしてる
    # またURLパラメータでの指定はページ数になっている

    pages = math.ceil(int(recruitsCount) / 20)

    for i in range(pages):

        print(i)

        # ページ先の html を取得
        targetUrl = nextUrl + '&pages=' + str(i)
        html = requests.get(targetUrl)
        soup = BeautifulSoup(html.content, "html.parser")

        # 企業詳細ページへのリンク取得
        urls = getDetailUrls(soup)

        # それぞれの会社の情報を取得
        infoList = getInfoList(urls)

        print(infoList[0])

        # GAS に POST
        postToGas(infoList)

# GAS に POST
def postToGas(infoList):

    #html を解析のためにGASへ送る
    response = requests.post(
        'https://script.google.com/macros/s/AKfycbyCIAMv2kxUUR6Wt_q1GXmY-PduxWsLzQMaE7yt6Axvr2APhqno/exec',
        data = json.dumps(infoList)
    )

    print(response.json)

# それぞれの企業詳細ページにアクセスし、データのリストを返す
def getInfoList(urls):
    infoList = []

    for detailUrl in urls:
        infoList.append(getInfo(detailUrl))
    else:
        return infoList

# 企業詳細ページへのリンク取得 => 
def getInfo(detailUrl):
    html = requests.get(detailUrl)
    soup = BeautifulSoup(html.content, "html.parser")
    info = {}
    info['companyName'] = soup.find('p', {'class': 'head_wrap__company_name'}).get_text()
    print(info['companyName'])
    info['business'] = soup.select('div:contains("事業内容") + div')[0].text.replace("\n","").replace("\r","").replace(" ","")
    if len(soup.select("div:contains('URL') ~ div")) != 0:
        info['url'] = soup.select("div:contains('URL') ~ div")[0].text.replace("\n","").replace("\r","").replace(" ","")
    if len(soup.select('div:contains("設立日")')) != 0:
        info['foundation'] = soup.select('div:contains("設立日") ~ div')[0].text.replace("\n","").replace("\r","").replace(" ","")
        info['mediaKind'] = MEDIA_KIND

    print(info['companyName'])

    return info

# URL整形
def getDetailUrls(soup):
    pureUrls = soup.find_all('li', {'class': 'job_offers_list__to_detail'})
    urls = []
    for item in pureUrls:
        url = "https://careerindex.jp/" + item.a.attrs['href']
        urls.append(url)
    else:
        return urls

# main 関数の実行
main()