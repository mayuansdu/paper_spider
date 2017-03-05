#!usr/bin/env python
# -*- coding: utf-8 -*-
import platform, random, time, logging, logging.handlers
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# 记录程序运行的日志文件设定
logfile = './log/log_util.log'
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，单位:M。默认最大为50M
# 配置日志: 2个日志文件副本
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('util')

handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

phantomjs_list =[
    './phantomjs/windows/bin/phantomjs.exe',   # windows环境的phantomjs
    './phantomjs/linux/32/bin/phantomjs',      # 32位linux环境的phantomjs
    './phantomjs/linux/64/bin/phantomjs',      # 64位linux环境的phantomjs
]


# 根据运行平台,调用不同的phantomjs
def get_phantomjs():
    phantomjs = phantomjs_list[1]	# 默认使用Linux 32bit
    bits, os = platform.architecture()
    if (os == 'WindowsPE'): #Windows系统
        phantomjs = phantomjs_list[0]
    elif (bits == '64bit'): # Linux系统
        phantomjs = phantomjs_list[2]
    else:
        logger.info('没有适合{os}{bits}的phantomjs!'.format(os=os, bits=bits))
    return phantomjs


# 返回phantomjs渲染后的页面,类型为str
def get_phantomjs_page(url):
    phantomjs = get_phantomjs()
    if phantomjs:
        caps = DesiredCapabilities.PHANTOMJS
        caps["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) " \
                                                    "Gecko/20100101 Firefox/51.0"
        brower = webdriver.PhantomJS(executable_path=phantomjs, desired_capabilities=caps)
        brower.set_page_load_timeout(180)  # seconds 设置页面完全加载时间，超时则抛出异常
        for i in range(1, 6):   # 如果连接异常，尝试5次
            try:
                brower.get(url)
                page = brower.page_source
                get_page = True # 已经获得完整页面数据
            except:
                logger.exception('第%s次请求页面,phantomjs出现错误:', i)
                get_page = False
            finally:
                if get_page:    # 获得完整页面数据 则返回
                    brower.quit()
                    return page
                elif 5 == i:    # 最后一次请求也未得到完整页面数据，则退出phantomjs 返回None
                    brower.quit()
                    logger.error('无法获得此链接的数据:' + str(url))
                    return None
                else:           # 未获得完整页面数据，则随机休眠一段时间，再次发送请求
                    time.sleep(get_random_uniform(begin=5.0, end=20.0))
    else:
        logger.error('无法获得phantomjs')


# 连接到mongodb 默认使用数据库paper_spider
def get_database_connect():
    conn = MongoClient(host='127.0.0.1', port=27617)
    db = conn.paper_spider
    db.authenticate('ps', 'ps*sp!')
    return db


# 返回生成的随机数,范围是[begin, end]
def get_random_uniform(begin=60, end=300):
    return random.uniform(begin, end)


if __name__ == '__main__':
    print(get_phantomjs_page('https://httpbin.org/get?show_env=1')) # 可以显示报文头部信息的网址