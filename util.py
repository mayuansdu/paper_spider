#!usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import platform
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By

phantomjs_list =[
    'phantomjs/windows/bin/phantomjs.exe',   # windows环境的phantomjs
    'phantomjs/linux/64/bin/phantomjs',      # 64位linux环境的phantomjs
    'phantomjs/linux/32/bin/phantomjs',      # 32位linux环境的phantomjs
]