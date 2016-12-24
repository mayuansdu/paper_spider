#!usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import platform
import random
from pymongo import MongoClient
from selenium import webdriver

phantomjs_list =[
    'phantomjs/windows/bin/phantomjs.exe',   # windows环境的phantomjs
    'phantomjs/linux/64/bin/phantomjs',      # 64位linux环境的phantomjs
    'phantomjs/linux/32/bin/phantomjs',      # 32位linux环境的phantomjs
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
        try:
            brower.get(url)
            page = brower.page_source
        except:
            print("Unexpected error:", sys.exc_info()[0])
        else:
            return page
        finally:
            brower.quit()
    else:
        print('无法获得phantomjs')


# 连接到mongodb 默认使用数据库spider
def get_database_connect():
    conn = MongoClient(host='127.0.0.1', port=27017)
    return conn.paper_spider


# 返回生成的随机数,范围是[begin, end]
def get_random_uniform(begin=60, end=300):
    return random.uniform(begin, end)