"""
采集形如这样的CSV表格
page,id,title,cc,download,like
1,1588,5 Point Lighting Setup,CC-0,1744,4
1,1589,Cocktail Shaker,CC-0,250,3
"""

from utils import *
import time
from bs4 import BeautifulSoup
import pandas as pd

start_page = 0  # 开始采集的页码
end_page = 1400  # 采集结束的页码
wait_time_after_load_page = 3  # 进入一个新的页面之后的等待时间
username = '396839479@qq.com'
password = '20020528lyk'


def perItem(driver, xp, page):
    """
    对于每个物品
    :param driver:
    :return: 物品的各种信息
    """
    elem = xpath(driver, xp)
    html = getInnerHtml(driver, elem)
    soup = BeautifulSoup(html, "html.parser")
    id = int(soup.find('a').get("href").split('/')[-1])
    title = xpath(driver, xp + """/div/div/div[1]""").text
    data = xpath(driver, xp + """/div/div/div[2]""").text
    cc, download, like = data.replace(',', '').replace('"', '').split('\n')  # 去掉逗号和双引号
    res = [page, id, title, cc, download, like, 'no', 'no', 'no']
    print(f"page:{page}", res)
    return res


def perPage(driver, page):
    """
    对于每个页面
    :param driver:
    :param page:
    :return:
    """
    # 从最旧的模型开始采集
    driver.get("https://blendswap.com/blends/{}/oldest".format(page))
    time.sleep(wait_time_after_load_page)
    # driver.execute_script("document.querySelector('.close-button').click();")  # 在等待时间之后停止加载网页
    print("start... page {}".format(page))
    data = []
    itemID = 0
    baseXpath = """/html/body/div/div[2]/div[{}]"""
    allowFailTimes = 2  # 允许采集失败
    failTime = 0
    while True:
        try:
            itemID += 1
            data.append(perItem(driver, baseXpath.format(itemID), page))
        except:
            failTime += 1
            print('fail, page:{}, itemID:{}'.format(page, itemID))
            if failTime > allowFailTimes:
                break
    print(len(data), f"pieces of information have been collected in page {page}.")
    return data


def main():
    driver = driverInit()
    login(driver, username, password)  # 登录
    time.sleep(3)
    try:
        df = pd.read_csv('data.csv')
    except:
        df = pd.read_csv('data.csv', encoding='gbk')
    for page in range(start_page, end_page + 1):
        pageData = perPage(driver, page)
        # 保存数据
        new_df = pd.DataFrame(pageData, columns=df.columns)
        df = pd.concat([df, new_df], ignore_index=True)
        try:
            df.to_csv('data.csv', index=False)
        except:
            print("Error saving file.")


if __name__ == '__main__':
    main()
