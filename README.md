# BlendSwap Downloader

blendswap的爬虫

自动从[blendswap](https://blendswap.com/)网站下载模型

使用selenium Webdriver获取`data.csv`，其中包含页面、ID、标题、抄送、下载次数、点赞次数等信息。截至2024年5月1日，共有25196条信息。

此信息存储在`data.csv`中

# main.py

您可以跳过这一段，因为25196条信息的`data.csv`已在文件列表中。

基于selenium构建`data.csv`的脚本。

导入包后，您可以更改：

```python
start_page = 0 # Starting page for crawling
end_page = 1400 # Ending page for crawling
wait_time_after_load_page = 3 # Waiting time after loading a new page
username = ''
password = ''
```



# downloader.py

从`data.csv`中读取数据并下载。

导入包后，您可以更改：

```python
max_file_size = 99999  # Maximum file size in MB for downloading
min_file_size = 0  # Minimum file size in MB for downloading
csv_file_path = 'data.csv'
start_line = 0  # Starting line in the CSV file
download_path = 'data/'
base_url = 'https://blendswap.com/blend/{}/download'
```

如果您的cookie无效或您的帐户的每日下载限制已用完，将提示此消息：Download quota used up... or cookie invalid...

在Blendswap中创建帐户不需要验证。因此，您可以轻松创建帐户，脚本已经包含了自动注册的流程，因此你可以直接使用它，但是创建账号的过程需要一些时间。或者你可以订阅它，然后你可以无限制地下载。

![image-20240514155530979](README.assets/image-20240514155530979.png)

正在运行...

# Use you own cookie

如何获取cookie？

在浏览器中打开blendswap并登录到您的帐户。按F12，选择应用程序Cookie-https://blendswap.com，复制“session”键的“Cookie Value”，粘贴到“Cookie.txt”中并保存。如果你要使用自定的cookie需要对`downloader.py`进行一些改动，或者直接退回上一个版本。

![image-20240501145100026](README.assets/image-20240501145100026.png)