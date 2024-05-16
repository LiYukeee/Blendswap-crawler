"""
读取形如这样的CSV表格，并根据其中的id下载数据，在下载完成之后会对该行进行标注。
page,id,title,cc,download,like,download
1,1588,5 Point Lighting Setup,CC-0,1744,4,no
1,1589,Cocktail Shaker,CC-0,250,3,yes
"""
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime
import signal
import fcntl
import queue
import threading

# 下载线程数目
num_thread = 4
# 每条cookie下载多少文件
download_num_per_cookie = 10
# 每个文件的最大允许下载实际按
max_download_time = 600
# 设定会进行下载的最大文件大小单位MB
max_file_size = 99999
# 设定会进行下载的最大文件大小单位MB
min_file_size = 0
csv_file_path = 'data.csv'
# 从csv文件的第几行开始
start_line = 0
# 下载路径
download_path = 'data/'
base_url = 'https://blendswap.com/blend/{}/download'


def timeout_handler(signum, frame):
    raise TimeoutError("timeout....")


def download(id, cookie):
    """
    下载，通过id
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
        if min_file_size <= total_size_MB <= max_file_size:
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


def writeCSV(id, data):
    """
    将数据存入CSV中，加入了文件锁
    """
    with open(csv_file_path, 'r') as file:
        # 对文件进行锁定
        fcntl.flock(file, fcntl.LOCK_EX)  # 应用排他锁

        # 写入文件
        df = pd.read_csv(file)
        line_index = df.loc[df['id'] == id].index[0]
        df.loc[line_index, ['is_download', 'size(MB)', 'path']] = data
        df.to_csv(csv_file_path, index=False)
        fcntl.flock(file, fcntl.LOCK_UN)  # 解锁
    return


def worker(id_queue: queue.Queue, cookie_queue: queue.Queue):
    download_count = 0
    cookie = ''
    if not cookie_queue.empty():
        cookie = cookie_queue.get()
    else:
        return

    while not id_queue.empty():
        id = id_queue.get()
        try:
            print(id, cookie)
            data = download(id, cookie)  # 可能会出错，未知的网络原因，为了不妨碍程序继续运行用try
        except:
            print('network error')
            data = ['no', 'no', 'no']
        # 保存并输出信息
        writeCSV(id, data)
        current_datetime = datetime.now()
        print('time:', current_datetime.date(), current_datetime.time())
        print('id:', id, data)
        download_count += 1
        if download_count >= download_num_per_cookie or data == ['no', 'no', 'no']:  # 下载n次之后或者下载失败需要更换cookie
            download_count = 0
            if not cookie_queue.empty():
                cookie = cookie_queue.get()
                print('----------------------')
                print('update cookie.', cookie)
            else:  # 如果cookie列表空
                return
    return


def main():
    try:
        df = pd.read_csv(csv_file_path)
    except:
        df = pd.read_csv(csv_file_path, encoding='gbk')
    with open('cookie.txt', 'r') as f:  # 从cookie.txt中获取cookie
        cookie = f.read()
    cookieList = cookie.strip().split('\n')

    # 共享列表建立
    id_queue = queue.Queue()
    cookie_queue = queue.Queue()
    for cookie in cookieList:
        cookie_queue.put(cookie)
    for line_index in range(start_line, len(df)):
        if df.iloc[line_index]['is_download'] == 'no':
            id_queue.put(df.iloc[line_index]['id'])

    # 建立线程
    threads = []
    for i in range(num_thread):
        thread = threading.Thread(target=worker, args=(id_queue, cookie_queue,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
