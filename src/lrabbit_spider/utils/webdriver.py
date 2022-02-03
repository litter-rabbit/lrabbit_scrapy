
from concurrent.futures import thread
import os
import queue
from re import I
import threading
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from lrabbit_spider.utils.log import log
from lrabbit_spider.utils.tools import Singleton
DEFAULT_USERAGENT =  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"

class XhrRequest:
    def __init__(self,url,data,headers);
        self.url = url
        self.data = data
        self.headers = headers

class XhrResponse:
    def __init__(self,request,url,headers,content,status_code):
        self.request = request
        self.url = url
        self.headers = headers
        self.content = content
        self.status_code = status_code




class WebDriver(RemoteWebDriver):
    CHROME = "CHROME"
    def __init__(
        self,
        load_images=True,
        user_agent=None,
        proxy=None,
        headless=False,
        driver_type=CHROME,
        timeout=16,
        window_size=(1024, 800),
        executable_path=None,
        custom_argument=None,
        xhr_url_regexes: list = None,
        **kwargs,
    ):
        """
        webdirver 封装，支持chrome、phantomjs 和 firefox
        Args:
            load_images: 是否加载图片
            user_agent: 字符串 或 无参函数，返回值为user_agent
            proxy: xxx.xxx.xxx.xxx:xxxx 或 无参函数，返回值为代理地址
            headless: 是否启用无头模式
            driver_type: CHROME 或 PHANTOMJS,FIREFOX
            timeout: 请求超时时间
            window_size: # 窗口大小
            executable_path: 浏览器路径，默认为默认路径
            xhr_url_regexes: 拦截xhr接口，支持正则，数组类型
            **kwargs:
        """
        self._load_images = load_images
        self._user_agent = user_agent or DEFAULT_USERAGENT
        self._proxy = proxy
        self._headless = headless
        self._timeout = timeout
        self._window_size = window_size
        self._executable_path = executable_path
        self._custom_argument = custom_argument
        self._xhr_url_regexes = xhr_url_regexes
    
        if self._xhr_url_regexes and driver_type !=WebDriver.CHROME:
            raise Exception("xhr url only support by chrome")
        
        if driver_type == WebDriver.CHROME:
            self.driver= self.chrome_driver()
    
    def _enter__(self):
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        if exc_val:
            log.error(exc_val)
        self.quit()
        return True
    
    def get_driver(self):
        return self.driver
    
    def chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        # docker 里运行需要
        chrome_options.add_argument("--no-sandbox")

        if self._proxy:
            chrome_options.add_argument(
                "--proxy-server={}".format(
                    self._proxy() if callable(self._proxy) else self._proxy
                )
            )

        if self._user_agent:
            chrome_options.add_argument(
                "user-agent={}".format(
                    self._user_agent() if callable(self._user_agent) else self._user_agent
                )
            )
        if self._load_images:
            chrome_options.add_argument(
                "prefs", {"profile.managed_default_content_settings.images": 2}
            ) 
        if not self._headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        if self._window_size:
            chrome_options.add_argument(
                "--window-size={}.{}".format(self._window_size[0],self._window_size[1])
            ) 

        if self._executable_path:
            driver = webdriver.Chrome(options=chrome_options,executable_path=self._executable_path)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        with open(os.path.join(os.path.dirname(__file__),"./js/stealth.min.js"))  as f:
            js = f.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
        
        if self._xhr_url_regexes:
            assert isinstance(self._xhr_url_regexes,list)
            with open(
                os.path.join(os.path.dirname(__file__),"./js/intercept.js") 

            ) as f:
                js = f.read()
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument", {"source": js}
            )
            js = f"window.__urlRegexes = {self._xhr_url_regexes}"
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument", {"source": js}
            )
        return driver



    @property
    def cookies(self):
        cookies_json = {}
        for cookie in self.driver.get_cookies():
            cookie_json[cookie["name"]] = cookie['value']
        return cookies_json

    @cookies.setter
    def cookies(self,val):
        for key,value in val.items():
            self.driver.add_cookie({"name":key,"value":value})
    
        pass

    @property
    def user_agent(self):
        return self.driver.execute_script("return navigator.userAgent;")


    def xhr_response(self,xhr_url_regex):
        data = self.driver.execute_script(
            f'return window.__ajaxData["{xhr_url_regex}"]'
        )
        if not data:
            return None

        request = XhrRequest(**data)["request"]
        response = XhrResponse(request,**data)["response"]
        return response 
    def xhr_text(self,xhr_url_regex):
        response = self.xhr_response(xhr_url_regex)
        if not response:
            return None
        return response.content
        pass

    def xhr_json(self,xhr_url_regex):
        pass

    def __getattr__(self,xhr_url_regex):
        pass



@Singleton
class WebDriverPool:
    def __init__(self,pool_size=5,**kwargs):

        self.queue = queue.Queue(maxsize=pool_size)
        self.kwargs=kwargs
        self.lock = threading.RLock()
        self.driver_count = 0
        pass
    @property
    def is_full(self):
        return self.driver_count >=self.queue.maxsize
        pass

    def get(self,user_agent,proxy):
        if not self.is_full:
            with self.lock:
                kwargs = self.kwargs.copy()
                if user_agent:
                    kwargs["user_agent"] = user_agent
                if proxy:
                    kwargs["proxy"] = proxy
                driver = WebDriver(**kwargs)
                self.queue.put(driver)
                self.driver_count +=1
        driver = self.queue.get()
        return driver
    
    def remove(self,driver):
        driver.quit()
        self.driver_count-=1

    def close(self):
        while not self.queue.empty():
            driver = self.queue.get()
            driver.quit()
            self.driver_count -=1
        


    

    def put(self,driver):
        pass

    def remove(self,driver):
        pass
    def close(self):
        pass





