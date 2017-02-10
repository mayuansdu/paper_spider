#!usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import platform
import random
import time
from pymongo import MongoClient
from selenium import webdriver

phantomjs_list =[
    './phantomjs/windows/bin/phantomjs.exe',   # windows环境的phantomjs
    './phantomjs/linux/64/bin/phantomjs',      # 64位linux环境的phantomjs
    './phantomjs/linux/32/bin/phantomjs',      # 32位linux环境的phantomjs
]


# 根据运行平台,调用不同的phantomjs
def get_phantomjs():
    bits, os = platform.architecture()
    if (os == 'WindowsPE'): #Windows系统
        phantomjs = phantomjs_list[0]
    elif (os == 'ELF'): # Linux系统
        if (bits == '64bit'):
            phantomjs = phantomjs_list[1]
        else:
            phantomjs = phantomjs_list[2]
    else:
        print('没有%s%s的phantomJS' % (os, bits))
    return phantomjs


# 返回phantomjs渲染后的页面,类型为str
def get_phantomjs_page(url):
    phantomjs = get_phantomjs()
    if (phantomjs is not None):
        brower = webdriver.PhantomJS(executable_path=phantomjs)
        brower.set_page_load_timeout(120)  # seconds 设置页面完全加载时间，超时则抛出异常
        for i in range(1, 6):   # 如果连接异常，尝试5次
            try:
                print('第' + str(i) + '次尝试请求页面' + url)
                brower.get(url)
                page = brower.page_source
                get_page = True # 已经获得完整页面数据
            except:
                print('phantomjs出现错误:', sys.exc_info()[0])
                get_page = False
            finally:
                if get_page:    # 获得完整页面数据 则返回
                    brower.quit()
                    return page
                elif 5 == i:    # 最后一次请求也未得到完整页面数据，则退出phantomjs 返回None
                    brower.quit()
                    return None
                else:           # 未获得完整页面数据，则随机休眠一段时间，再次发送请求
                    time.sleep(get_random_uniform(begin=5.0, end=10.0))
    else:
        print('无法获得phantomjs')


# 连接到mongodb 默认使用数据库spider
def get_database_connect():
    conn = MongoClient(host='127.0.0.1', port=27017)
    db = conn.paper_spider
    # db.authenticate('ps', 'ps*sp!')
    return db


# 返回生成的随机数,范围是[begin, end]
def get_random_uniform(begin=60, end=300):
    return random.uniform(begin, end)