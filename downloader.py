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

max_file_size = 99999  # 设定会进行下载的最大文件大小单位MB
min_file_size = 0  # 设定会进行下载的最大文件大小单位MB
csv_file_path = 'data.csv'
start_line = 0  # 从csv文件的第几行开始
download_path = 'data\\'
base_url = 'https://blendswap.com/blend/{}/download'


def download(id):
    """
    下载，通过id
    :param id:
    :return:
    """
    url = base_url.format(id)
    with open('cookie.txt', 'r') as f:  # 从cookie.txt中获取cookie
        cookie = f.read()
    cookie = {
        'session': cookie
    }
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
    return [is_download, str(total_size_MB), path]


def main():
    try:
        df = pd.read_csv(csv_file_path)
    except:
        df = pd.read_csv(csv_file_path, encoding='gbk')
    for line_index in range(start_line, len(df)):
        line = df.iloc[line_index]
        if line['is_download'] == 'no':  # 如果没有被下载
            id = line['id']
            data = download(id)
            df.loc[line_index, ['is_download', 'size(MB)', 'path']] = data
            df.to_csv(csv_file_path, index=False)
            current_datetime = datetime.now()
            print(current_datetime.date(), current_datetime.time(), 'id:', line['id'], data)


if __name__ == '__main__':
    main()