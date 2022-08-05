from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from gspread.exceptions import WorksheetNotFound
from colorama import init, Fore
import requests
import json
import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials as SAC
import time
import os


def codeRun(weburl, i, Sheet):
    init(autoreset=True)

    GetURL = weburl
    # 引用requests套件，透過get()方法(Method)取得網址

    try:
        response = requests.get(GetURL)
        soup = BeautifulSoup(response.content, "html.parser")
        # 抓幣值名稱
        CryptocurrencyName = soup.find_all(
            'span', {'class': 'unit'}, limit=1)
        CryptocurrencyNameText = CryptocurrencyName[0].get_text()
        WorkSheetName = CryptocurrencyNameText+"數據收集"

        print("開始抓取 "+CryptocurrencyNameText+" 幣資料")
        # 抓取幣價
        # 從所有HTML中抓取符合條件的節點 limit限制抓取數量
        try:
            print("抓取幣價中...")
            CurrencyPrices = soup.find_all(
                'span', {'class': 'money-val'}, limit=1)
            # 從CurrencyPrices list中第一個元素中抓取文字
            CurrencyPricesText = CurrencyPrices[0].get_text()
            # 抓取的資料有空格 去除空格
            CurrencyPricesResult = CurrencyPricesText.strip()
        except:
            print(Fore.LIGHTRED_EX+"未抓到幣價...")
            CurrencyPricesResult = ""

        try:
            print("抓取每T收益中...")
            # 抓日理論收益
            TheoreticalBenefit = soup.find_all(
                'span', {'class': 'pl-1 profit-val'}, limit=1)
            TheoreticalBenefitText = TheoreticalBenefit[0].get_text()
            TheoreticalBenefitResult = TheoreticalBenefitText.strip()
        except:
            print(Fore.LIGHTRED_EX+"未抓到每T收益...")
            TheoreticalBenefitResult = ""

        try:
            print("抓取難度中...")
            # 抓當前難度
            # 抓取節點
            Difficulty = soup.find_all(
                'span', {'class': 'format-num'}, limit=1)
            # 從data-origin class中抓取屬性值
            DifficultyNum = float(Difficulty[0].get("data-origin"))

            # 將難度運算後  以字母簡化表示
            DifficultyResult = count(DifficultyNum)

        except:
            print(Fore.LIGHTRED_EX+"未抓到難度...")
            DifficultyResult = ""

        try:
            print("抓取全網算力中...")
            hashingUrl = "https://www.f2pool.com/coins"
            hashingReqs = requests.post(hashingUrl)
            hashingreqsjson = json.loads(hashingReqs.text)
            hashingData = hashingreqsjson['data']['top100']
            for i in range(len(hashingData)):
                if hashingData[i-1]['code'] == CryptocurrencyNameText.lower():
                    HashingResult = hashingData[i-1]['network_hashrate']
                    break
                else:
                    pass
            HashingResult = count(HashingResult)

        except:
            print(Fore.LIGHTRED_EX+"未抓到全網算力...")
            HashingResult = ""

        localTime = time.localtime()  # 取得系統時間
        TimeResult = time.strftime(
            "%Y-%m-%d %H:%M", localTime)  # 時間轉換為想要的格式

        #datas = 資料
        datas = [TimeResult, CurrencyPricesResult, HashingResult,
                 DifficultyResult, TheoreticalBenefitResult]

        try:  # 嘗試直接寫入指定表單
            Sheets = Sheet.worksheet(WorkSheetName)
            Sheets.append_row(datas)
            print(Fore.LIGHTRED_EX+"---------成功新增" +
                  CryptocurrencyNameText+"幣資料---------\n")
        except WorksheetNotFound:  # 如果回報找不到表單的錯誤 執行以下
            print("未檢測到"+CryptocurrencyNameText+"工作表，新增工作表中...")
            Sheet.add_worksheet(title=WorkSheetName, rows=100, cols=20)  # 新增表單
            Sheets = Sheet.worksheet(WorkSheetName)
            print(Fore.LIGHTRED_EX+"成功新增"+CryptocurrencyNameText+"工作表")
            Sheets.append_row([CryptocurrencyNameText+" 挖礦算力分析表"])  # 新增標題
            Sheets.append_row(["日期", "價格", "全網算力", "難度", "每T收益"])  # 新增標示
            Sheets.append_row(datas)
            print(Fore.LIGHTRED_EX+"---------成功新增" +
                  CryptocurrencyNameText+"幣資料---------\n")
    except:
        print(Fore.LIGHTRED_EX + "編號" + str(i+1)+"." +
              weburl+"<--------此網址輸入錯誤！請檢查！！！！！！")


def settingCoinUrl():  # 設定菜單
    while True:
        setCoin = np.load("data.npz", allow_pickle=True)['coinUrl'].tolist()
        googleUrlList = np.load("data.npz", allow_pickle=True)[
            'googleUrl'].tolist()
        print("\n新增/刪除目前設定")
        print("1.新增")
        print("2.刪除")
        print("3.顯示目前資料")
        print("4.回目錄\n")
        addDele = input("請輸入執行動作：").strip()
        if addDele == "1":
            print("\n新增")
            addName = input("請輸入名稱：")
            addUrl = input("請輸入網址：")
            setCoin.append([addName, addUrl])
            np.savez("data", coinUrl=setCoin, googleUrl=googleUrlList)
            print(Fore.LIGHTRED_EX+"新增　" + addName + " : " + addUrl + " 成功！")
        elif addDele == "2":
            try:  # 嘗試刪除
                print("\n刪除")
                delNum = int(input("請輸入要刪除的項目編號："))
                delName = str(setCoin[delNum-1][0])
                delURL = str(setCoin[delNum-1][1])
                del setCoin[delNum-1]  # 刪除資料
                print(Fore.LIGHTRED_EX+"成功刪除：名稱: " + delName+"  網址: "+delURL)
                np.savez("data", coinUrl=setCoin, googleUrl=googleUrlList)
            except:  # 發生錯誤
                print(Fore.LIGHTRED_EX+"\n編號輸入錯誤!")
        elif addDele == "3":
            print("\n目前已設定抓取資料為以下:")
            print("---------------------------")
            if setCoin == [] or setCoin == [None]:
                print(Fore.LIGHTRED_EX+"目前無資料")
            else:
                for i in range(len(setCoin)):
                    print(str(i+1)+". 名稱: " +
                          setCoin[i][0]+"  網址: "+setCoin[i][1])
            print("---------------------------")
        elif addDele == "4":
            break
        else:
            print(Fore.LIGHTRED_EX+"\n--------請輸入數字來執行動作！--------\n")


def settingGoogle():  # google設定菜單
    while True:
        googleUrlList = np.load("data.npz", allow_pickle=True)[
            'googleUrl'].tolist()
        setCoin = np.load("data.npz", allow_pickle=True)['coinUrl'].tolist()
        print("\n設定google試算表資料")
        print("1.設定google金鑰")
        print("2.設定google試算表網址")
        print("3.顯示目前設定")
        print("4.回目錄\n")
        googleSettingMenu = input("請輸入執行動作：").strip()
        if googleSettingMenu == "1":
            print("\n設定google金鑰")
            googleGoldKey = input("請輸入'完整'金鑰檔案名稱(需包含.json) : ")
            googleUrlList[0][0] = googleGoldKey
            np.savez("data", coinUrl=setCoin, googleUrl=googleUrlList)
            print(Fore.LIGHTRED_EX+"設定金鑰成功！")
        elif googleSettingMenu == "2":
            print("\n設定google表單網址")
            googleUrl = input("請輸入試算表'完整'網址：")
            # 整理網址出要用的部分
            googleUrl = googleUrl[googleUrl.rfind(
                "spreadsheets/d/")+15:googleUrl.rfind("edit")-1]
            googleUrlList[0][1] = googleUrl
            np.savez("data", coinUrl=setCoin, googleUrl=googleUrlList)
            print(Fore.LIGHTRED_EX+"設定試算表網址成功！")
        elif googleSettingMenu == "3":
            print("\n目前googole試算表設定如下:")
            print("---------------------------")
            if googleUrlList[0][0] == "":
                print(Fore.LIGHTRED_EX+"尚未設定金鑰")
            else:
                print("金鑰檔名: "+googleUrlList[0][0])

            if googleUrlList[0][1] == "":
                print(Fore.LIGHTRED_EX+"尚未設定試算表網址")
            else:
                print("試算表網址: "+googleUrlList[0][1])
            print("---------------------------")
        elif googleSettingMenu == "4":
            break
        else:
            print(Fore.LIGHTRED_EX+"\n--------請輸入數字來執行動作！--------\n")


# 簡化數字計算
def count(number):
    if number >= 1e18:
        number = str(round(number/1e18, 2))+"E"
    elif number >= 1e15:
        number = str(round(number/1e15, 2))+"P"
    elif number >= 1e12:
        number = str(round(number/1e12, 2))+"T"
    elif number >= 1e9:
        number = str(round(number/1e9, 2))+"G"
    elif number >= 1e6:
        number = str(round(number/1e6, 2))+"M"
    elif number >= 1e3:
        number = str(round(number/1e3, 2))+"K"
    else:
        number = round(number, 2)
    return number
