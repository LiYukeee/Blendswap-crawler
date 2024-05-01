data = """POST /login HTTP/1.1
Host: blendswap.com
Cookie: session=eyJjc3JmX3Rva2VuIjoiMjU4MTBkMzM2OTgxZTMwOTE3NWE2ZmVhZDI0OWY5YjhiN2EyZjBlOSJ9.ZjG3vQ.KDFoQgK-RVa7tFGp4g-L1nF7TZ0
Content-Length: 162
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
Origin: https://blendswap.com
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://blendswap.com/login
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Priority: u=0, i
Connection: close
"""

if __name__ == '__main__':
    res = ""
    data = data.split('\n')
    for line in data:
        try:
            line = line.split(": ")
            print("'{}': '{}'".format(line[0], line[1]), end=',\n')
        except:
            a = 1
