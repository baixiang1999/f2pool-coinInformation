from oauth2client.service_account import ServiceAccountCredentials as SAC
import os
import numpy as np
from scrapercode import *
from colorama import init, Fore


init(autoreset=True)
while True:
    try:
        setCoin = np.load("data.npz", allow_pickle=True)['coinUrl'].tolist()
        print("執行目錄:")
        print("1.執行儲存資料")
        print("2.設定抓取資料")
        print("3.設定google試算表位置")
        print("4.退出")
        anwser = input("\n請輸入執行動作：").strip()
        if anwser == "1":  # 執行抓取資料
            try:
                googleUrlList = np.load("data.npz", allow_pickle=True)[
                    'googleUrl'].tolist()
                Json = googleUrlList[0][0]  # Json  表單金鑰
                Url = ["https://spreadsheets.google.com/feeds"]
                Connect = SAC.from_json_keyfile_name(Json, Url)
                GoogleSheets = gspread.authorize(Connect)
                try:
                    Sheet = GoogleSheets.open_by_key(
                        googleUrlList[0][1])  # 試算表代號
                    if setCoin == []:
                        print(Fore.LIGHTRED_EX+"\n未抓到資料!請再確認是否已設定網址!\n")
                    else:
                        for i in range(len(setCoin)):
                            print("編號" + str(i+1) + ".資料開始執行")
                            codeRun(setCoin[i][1], i, Sheet)
                        print(Fore.LIGHTRED_EX+"\n---------執行完成！---------")
                except:
                    print(Fore.LIGHTRED_EX + "\n試算表網址尚未輸入或輸入錯誤!\n")
            except:
                print(Fore.LIGHTRED_EX + "\n未找到對應金鑰:"+googleUrlList[0][0]+"\n")
        elif anwser == "2":  # 設定菜單
            settingCoinUrl()
        elif anwser == "3":  # 設定菜單
            settingGoogle()
        elif anwser == "4":
            print("\n---------退出...---------")
            os.system("pause")
            break

        else:
            print(Fore.LIGHTRED_EX+"\n--------請輸入數字來執行動作！--------\n")
    except FileNotFoundError:
        coinUrl = []
        googleUrl = [["", ""]]
        np.savez("data", coinUrl=coinUrl, googleUrl=googleUrl)
        print("創建data.npz檔案")
