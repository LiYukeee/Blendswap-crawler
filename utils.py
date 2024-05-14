import selenium.webdriver.remote.webelement
from selenium import webdriver
from selenium.webdriver.common.by import By

implicitlyWait = 10  # 隐式等待时间


def xpath(dr, val) -> selenium.webdriver.remote.webelement.WebElement:
    """
    driver.find_element_by_xpath 便捷方法
    """
    return dr.find_element(by=By.XPATH, value=val)


def driverInit(path='.\\', headless=False, implicitlyWait=5):  # 浏览器初始化
    """
    driver初始化
    :return: driver
    """
    # 打开谷歌浏览器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--enable-print-browser')
    if headless:
        chrome_options.add_argument('--headless')  # headless模式下，浏览器窗口不可见，应当可提高效率
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
    prefs = {
        'download.default_directory': r'{}'.format(path)  # 此处填写你希望文件下载的路径,可填写your file path默认下载地址
    }
    chrome_options.add_argument('--kiosk-printing')  # 静默打印，无需用户点击打印页面的确定按钮
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            })
                          """})  # 防止某些网站通过检测 navigator.webdriver 属性来识别这是一个自动化浏览器实例
    driver.implicitly_wait(implicitlyWait)
    driver.set_window_size(900, 720)  # 设定窗口大小
    return driver


def login(dr, userName, password):
    """登录blendswap"""
    dr.get("https://blendswap.com/login")  # 登录界面
    xpath(dr, """//*[@id="email"]""").clear()
    xpath(dr, """//*[@id="email"]""").send_keys(userName)
    xpath(dr, """//*[@id="password"]""").clear()
    xpath(dr, """//*[@id="password"]""").send_keys(password)
    xpath(dr, """/html/body/div/div/div/div[2]/div/form/button""").click()


def getInnerHtml(dr, element):
    """
    获取元素的HTML
    :param dr:
    :param element:
    :return:
    """
    return dr.execute_script("return arguments[0].innerHTML;", element)
