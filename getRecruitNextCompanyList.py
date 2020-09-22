# coding: utf-8
import math
import pprint
import json
import requests
from bs4 import BeautifulSoup

# リクナビNEXTから企業リストを取得します
# 検索条件は以下の通りです
# 「正社員」「勤務地: 東京」「業種: IT/通信系」「第二新卒歓迎」

# 全体のフロー
# 1. 一覧ページそれぞれにアクセスする
# 2. それぞれの案件のURLから企業ページURLを生成
# 3. 2のURLにアクセスし、情報を取得

MEDIA_KIND = 'リクナビNEXT'

def main():

    # html の取得 => ページ数解析
    nextUrl = "https://next.rikunabi.com/rnc/docs/cp_s00700.jsp?jb_type_long_cd=0500000000&jb_type_long_cd=1200000000&wrk_plc_long_cd=0313100000&indus_long_cd=010000&employ_frm_cd=01&prf_cnd_cd=24"
    htmlContent = requests.get(nextUrl)
    soup = BeautifulSoup(htmlContent.content, "html.parser")

    recruitsCount = soup.find("span", {'class': 'js-resultCount'}).get_text()

    # ページ数取得 => リクナビNEXTは 50 件ずつページネーションしてる
    # またURLパラメータでの指定はページ数ではなく、案件数ごとにcursor指定してるっぽい
    #
    # ex) 2ページ目 => curnum = 51 
    #
    # つまり2ページ目は 51件目から表示している

    pages = math.ceil(int(recruitsCount) / 50) 

    for i in range(pages):

        print(i)

        # 件数出しておく
        curnum = ((i -1) * 50) + 1

        # ページ先の html を取得
        targetUrl = nextUrl + '&curnum=' + str(curnum)
        html = requests.get(targetUrl)
        soup = BeautifulSoup(html.content, "html.parser")

        # 企業詳細ページへのリンク取得
        urls = getDetailUrls(soup)

        # それぞれの会社の情報を取得
        infoList = getInfoList(urls)

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

# 対象の企業詳細ページから企業情報を取得
def getInfo(detailurl):
    print(detailurl)
    html = requests.get(detailurl)
    soup = BeautifulSoup(html.content, "html.parser")
    info = {}
    info['companyName'] = soup.find_all('li', {'typeof': 'v:Breadcrumb'})[3].text.replace("\n","").replace("\r","").replace(" ","")
    info['business'] = soup.select('th:contains("事業内容") + td')[0].text
    if len(soup.select('th:contains("URL") + td')) != 0:
        info['url'] = soup.select('th:contains("URL") + td')[0].a.attrs['href'] 
    if len(soup.select('th:contains("設立") ~ td')) != 0:
        info['foundation'] = soup.select('th:contains("設立") ~ td')[0].text.replace("\n","").replace("\r","").replace(" ","")
    info['mediaKind'] = MEDIA_KIND

    print(info['companyName'])

    return info

# それぞれの企業詳細ページにアクセスし、データのリストを返す
def getInfoList(urls):
    infoList = []
    
    for detailUrl in urls:
        infoList.append(getInfo(detailUrl))
    else:
        return infoList

# 企業詳細ページへのリンク取得 => company/ 配下の「cmi*****」がおそらく企業ID。これを使う
def getDetailUrls(soup):

    pureUrls = soup.find_all('p', {'class': 'js-abScreen__cmpny'})
    urls = []
    for item in pureUrls:
        url = 'https://next.rikunabi.com/' + item.a.attrs['href']
        urls.append(url)
    else:
        return urls

# main 関数の実行
main()



