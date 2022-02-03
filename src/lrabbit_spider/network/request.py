
import lrabbit_spider.network.user_agent as user_agent
import lrabbit_spider.setting as setting
import requests
from lrabbit_spider.utils.
from requests.adapters import HTTPAdapter
class Request(object):

    webdriver_pool:WebD
    __REQUEST_ATTRS__ = {
        # 'method', 'url', 必须传递 不加入**kwargs中
        "params",
        "data",
        "headers",
        "cookies",
        "files",
        "auth",
        "timeout",
        "allow_redirects",
        "proxies",
        "hooks",
        "stream",
        "verify",
        "cert",
        "json",
            }
    def __init__(
        self,
        url="",
        retry_times=0,
        priority=300,
        parser_name=None,
        callback=None,
        filter_repeat=True,
        auto_request=True,
        request_sync=False,
        use_session=None,
        random_user_agent=True,
        download_midware=None,
        is_abandoned=False,
        render=False,
        render_time=0,
        **kwargs,
    ):
        """
        @summary: Request参数
        ---------
        框架参数
        @param url: 待抓取url
        @param retry_times: 当前重试次数
        @param priority: 优先级 越小越优先 默认300
        @param parser_name: 回调函数所在的类名 默认为当前类
        @param callback: 回调函数 可以是函数 也可是函数名（如想跨类回调时，parser_name指定那个类名，callback指定那个类想回调的方法名即可）
        @param filter_repeat: 是否需要去重 (True/False) 当setting中的REQUEST_FILTER_ENABLE设置为True时该参数生效 默认True
        @param auto_request: 是否需要自动请求下载网页 默认是。设置为False时返回的response为空，需要自己去请求网页
        @param request_sync: 是否同步请求下载网页，默认异步。如果该请求url过期时间快，可设置为True，相当于yield的reqeust会立即响应，而不是去排队
        @param use_session: 是否使用session方式
        @param random_user_agent: 是否随机User-Agent (True/False) 当setting中的RANDOM_HEADERS设置为True时该参数生效 默认True
        @param download_midware: 下载中间件。默认为parser中的download_midware
        @param is_abandoned: 当发生异常时是否放弃重试 True/False. 默认False
        @param render: 是否用浏览器渲染
        @param render_time: 渲染时长，即打开网页等待指定时间后再获取源码
        --
        以下参数与requests参数使用方式一致
        @param method: 请求方式，如POST或GET，默认根据data值是否为空来判断
        @param params: 请求参数
        @param data: 请求body
        @param json: 请求json字符串，同 json.dumps(data)
        @param headers:
        @param cookies: 字典 或 CookieJar 对象
        @param files:
        @param auth:
        @param timeout: (浮点或元组)等待服务器数据的超时限制，是一个浮点数，或是一个(connect timeout, read timeout) 元组
        @param allow_redirects : Boolean. True 表示允许跟踪 POST/PUT/DELETE 方法的重定向
        @param proxies: 代理 {"http":"http://xxx", "https":"https://xxx"}
        @param verify: 为 True 时将会验证 SSL 证书
        @param stream: 如果为 False，将会立即下载响应内容
        @param cert:
        --
        @param **kwargs: 其他值: 如 Request(item=item) 则item可直接用 request.item 取出
        ---------
        @result:
        """

        self.url = url
        self.retry_times = retry_times
        self.priority = priority
        self.parser_name = parser_name
        self.callback = callback
        self.filter_repeat = filter_repeat
        self.auto_request = auto_request
        self.request_sync = request_sync
        self.use_session = use_session
        self.random_user_agent = random_user_agent
        self.download_midware = download_midware
        self.is_abandoned = is_abandoned
        self.render = render
        self.render_time = render_time or setting.WEBDRIVER.get("render_time", 0)

        self.requests_kwargs = {}
        for key, value in kwargs.items():
            if key in self.__class__.__REQUEST_ATTRS__:  # 取requests参数
                self.requests_kwargs[key] = value

            self.__dict__[key] = value


    def __repr__(self):
        pass

    def __setattr__(self,key,value):
        self.__dict__[key] = value
        if key in self.__class__.__REQUEST_ATTRS__:
            self.requests_kwargs[key] = value

    def __lt__(self,other):
        return self.priority<other.priority
        pass

    @property
    def _session(self):
        user_session = (
            setting.USE_SESSION if self.user_session is None else self.use_session

        )
        if user_session and not self.__class__.session:
            self.__class__.session = requests.Session()
            http_adapter = HTTPAdapter(pool_connections=1000,pool_maxsize=1000)
            self.__class__.session.mount("http",http_adapter)
    @property
    def _webdriver_pool(self):
        if not self.__class__.web:
        pass

    @property
    def _proxies_pool(slef):
        pass
    @property
    def to_dict():
        pass
    @property
    def callback_name(self):
        pass

    def get_response(self,save_cached=False):
        pass
    def proxy(self):
        pass
    def user_agent(self):
        pass
    @property
    def fingerprint(self):
        pass
    @property
    def _cache_redis_key(self):
        pass
    @property
    def _cache_db(slef):
        pass
    def save_cached(self,response,expire_time=1200):
        pass
    def get_response_from_cached(self,save_cached=True):
        pass
    def del_response_cached(slef):
        pass
    @classmethod
    def from_dict(cls,request_dict):
        pass
    def copy(self):
        pass


