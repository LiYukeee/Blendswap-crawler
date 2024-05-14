"""
每个账号每天的下载次数是有限制的，但BlenderSwap网站注册流程简单（不需要邮箱验证码，甚至不需要是一个正确的邮箱）
因此当cookie失效的时候我们可以直接重新创建一个账号获取崭新的cookie
"""
from utils import *
from datetime import datetime


class CookieMaker:
    def __init__(self, headless, implicitlyWait):
        self.headless = headless
        self.implicitlyWait = implicitlyWait
        # self.driver = driverInit(headless=headless, implicitlyWait=implicitlyWait)
        self.register_url = "https://blendswap.com/register"

    def register(self, username, email, password):
        self.driver.get(self.register_url)
        username_xpath = """//*[@id="username"]"""
        email_xpath = """//*[@id="email"]"""
        password_xpath = """//*[@id="password"]"""
        confirm_xpath = """//*[@id="password_confirm"]"""
        xpath(self.driver, username_xpath).clear()
        xpath(self.driver, username_xpath).send_keys(username)
        xpath(self.driver, email_xpath).clear()
        xpath(self.driver, email_xpath).send_keys(email)
        xpath(self.driver, password_xpath).clear()
        xpath(self.driver, password_xpath).send_keys(password)
        xpath(self.driver, confirm_xpath).clear()
        xpath(self.driver, confirm_xpath).send_keys(password)
        register_btn_xpath = """/html/body/div/div/div/div/div/form/button"""
        xpath(self.driver, register_btn_xpath).click()

    def getEmail(self):
        """根据当前时间生成一个email地址"""
        current_datetime = datetime.now()
        email = (str(current_datetime.date()).replace('-', '')
                 + str(current_datetime.time()).replace(':', '').replace('.', '')
                 + '@123.com')
        return email

    def logout(self):
        self.driver.get("https://blendswap.com/logout")

    def getCookie(self):
        # email是随机生成的
        username = 'downloader'
        password = '123456789'
        # print('logout...')
        # self.logout()
        self.driver = driverInit(headless=self.headless, implicitlyWait=self.implicitlyWait)
        email = self.getEmail()
        print('Email:', email)
        print('Register...')
        self.register(username=username, email=email, password=password)
        print('getCookie...')
        cookie = self.driver.get_cookies()[0]
        return cookie['value']


if __name__ == '__main__':
    # 自动注册账号并生成cookie，存储到cookie.txt
    cookieMaker = CookieMaker(headless=True, implicitlyWait=1)
    cookieList = []
    for i in range(1000):
        cookie = cookieMaker.getCookie()
        print(cookie)
        cookieList.append(cookie)
        with open('cookie.txt', 'a') as file:
            file.write(cookie)
            file.write('\n')

