"""
读取形如这样的CSV表格，并根据其中的id下载数据，在下载完成之后会对该行进行标注。
page,id,title,cc,download,like,is_download
1,1588,5 Point Lighting Setup,CC-0,1744,4,no
1,1589,Cocktail Shaker,CC-0,250,3,yes
"""
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime
import signal
import re

download_num_per_cookie = 10
max_file_size = 100  # 设定会进行下载的最大文件大小单位MB
min_file_size = 0.00018310546875  # 设定会进行下载的最大文件大小单位MB
csv_file_path = 'data.csv'
start_line = 0  # 从csv文件的第几行开始
download_path = 'data/'
base_url = 'https://blendswap.com/blend/{}/download'
max_download_time = 600
# 如果keyword不为空，则会先下载title包含keyword的条目
keyword = ''  # 可以包含多个关键词，用'-'分隔，且不要包含空格，例如   car-desk


def contains1(text, keyword):
    pattern = r'\b{}\b'.format(keyword)  # 这样的匹配策略只会匹配单独的单词，如果是一个单词中包含了关键词匹配失败
    match = re.search(pattern, text)
    if match:
        return True
    else:
        return False

def contains(text, keyword:str):
    if keyword=='':
        return True
    words = keyword.split('-')
    res = False
    for word in words:
        if word != '':
            res = res or contains1(text=text, keyword=word)
    return res
    
    
def timeout_handler(signum, frame):
    raise TimeoutError("timeout....")


def download(id, cookie):
    """
    下载通过id
    :param id:
    :return:
    """
    url = base_url.format(id)
    cookie = {
        'session': cookie
    }
    # 设定最大下载时长
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(max_download_time)
    try:
        response = requests.get(url, cookies=cookie, stream=True)
        total_size = int(response.headers.get("Content-Length", 0))  # 读取文件大小
        total_size_MB = total_size / (1024 * 1024)
        is_download = 'no'
        path = 'no'
        if total_size == 0:
            print('Download quota used up... or cookie invalid...')
            return ['no', 'no', 'no']
        if min_file_size < total_size_MB <= max_file_size:
            # 定义文件名和保存路径
            filename = str(id) + '.blend'
            path = download_path + filename
            # 使用 tqdm 显示下载进度条
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
            with open(path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
            # 下载完成
            progress_bar.close()
            is_download = 'yes'
    except TimeoutError as e:  # 如果运行超时
        print(e)
        return ['no', 'no', 'no']
    return [is_download, str(total_size_MB), path]


def main():
    try:
        df = pd.read_csv(csv_file_path)
    except:
        df = pd.read_csv(csv_file_path, encoding='gbk')
    # 从文件获取cookie
    with open('cookie.txt', 'r') as f:  # 从cookie.txt中获取cookie
        cookie = f.read()
    cookieList = cookie.strip().split('\n')
    cookie = cookieList.pop(0)
    print('--------------------------------------\ncookie:', cookie)
    # # 注册账号生成cookie
    # from getCookie import CookieMaker
    # cookieMaker = CookieMaker(headless=True, implicitlyWait=5)
    # print("-------------------------------")
    # print("create cookie...")
    # cookie = cookieMaker.getCookie()
    # print(cookie)
    download_count = 0
    while True:
        for line_index in range(start_line, len(df)):
            line = df.iloc[line_index]
            if line['is_download'] == 'no':  # 如果没有被下载
                id = line['id']
                title = line['title']
                # title筛选
                if not contains(title, keyword):
                    # 如果不包含关键词则直接开始下一条信息
                    continue

                # 开始下载
                print('start downloading...  id:', id, 'title:',title)
                try:
                    data = download(id, cookie)  # 可能会出错，未知的网络原因，为了不妨碍程序继续运行用try
                except:
                    data = ['no', 'no', 'no']
                # 写入csv
                df.loc[line_index, ['is_download', 'size(MB)', 'path']] = data
                df.to_csv(csv_file_path, index=False)
                # 输出信息
                current_datetime = datetime.now()
                print('time:', current_datetime.date(), current_datetime.time())
                print('id:', line['id'], line['title'], data)
                download_count += 1
                if download_count >= download_num_per_cookie or data == ['no', 'no', 'no']:  # 下载n次之后或者下载失败需要更换cookie
                    download_count = 0
                    print("-------------------------------")
                    print("update cookie...")
                    # # 注册账号并生成cookie
                    # cookie = cookieMaker.getCookie()
                    # 读取cookie列表取出cookie
                    cookie = cookieList.pop()
                    print('--------------------------------------\ncookie:', cookie)
        # 进行多次采集，只有全部都采集完成才会退出循环
        for line_index in range(start_line, len(df)):
            line = df.iloc[line_index]
            if line['is_download'] == 'no':
                continue
        break


if __name__ == '__main__':
    main()
