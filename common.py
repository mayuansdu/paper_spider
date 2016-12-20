#!usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup

# 存放爬取到的文件的根目录
file_dir = './file/'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate',
           'Connection': 'keep-alive',
           'Cache-Control': 'max-age=0',
}

conference_acm = {
    'a': [
        'http://dblp.uni-trier.de/db/conf/ccs/',
    ],
    'c': [
        'http://dblp.uni-trier.de/db/conf/wisec/',
        'http://dblp.uni-trier.de/db/conf/ih/',
        'http://dblp.uni-trier.de/db/conf/sacmat/',
        'http://dblp.uni-trier.de/db/conf/ccs/',
        'http://dblp.uni-trier.de/db/conf/drm/',
        'http://dblp.uni-trier.de/db/conf/securecomm',
        'http://dblp.uni-trier.de/db/conf/nspw/',
        'http://dblp.uni-trier.de/db/conf/soups/',
    ],
}

journal_acm = {
    'b': [
        'http://dblp.uni-trier.de/db/journals/tissec/',
    ],
}

conference_springer = {
    'a': [
        'http://dblp.uni-trier.de/db/conf/crypto/',
        'http://dblp.uni-trier.de/db/conf/eurocrypt/',
    ],
    'b': [
        'http://dblp.uni-trier.de/db/conf/asiacrypt/',
        'http://dblp.uni-trier.de/db/conf/esorics/',
        'http://dblp.uni-trier.de/db/conf/fse/',
        'http://dblp.uni-trier.de/db/conf/raid/',
        'http://dblp.uni-trier.de/db/conf/pkc/',
        'http://dblp.uni-trier.de/db/conf/tcc/',
        'http://dblp.uni-trier.de/db/conf/ches/',
    ],
    'c': [
        'http://dblp.uni-trier.de/db/conf/acns/',
        'http://dblp.uni-trier.de/db/conf/acisp/',
        'http://dblp.uni-trier.de/db/conf/fc/',
        'http://dblp.uni-trier.de/db/conf/dimva/',
        'http://dblp.uni-trier.de/db/conf/sec/',
        'http://dblp.uni-trier.de/db/conf/isw/',
        'http://dblp.uni-trier.de/db/conf/icics/',
        'http://dblp.uni-trier.de/db/conf/ctrsa/',
        'http://dblp.uni-trier.de/db/conf/sacrypt/',
        'http://dblp.uni-trier.de/db/conf/pam/',
        'http://dblp.uni-trier.de/db/conf/pet/',
        'http://dblp.uni-trier.de/db/conf/icdf2c/',
    ],
}

journal_springer = {
    'a': [
        'http://dblp.uni-trier.de/db/journals/joc/',
    ],
    'b': [
        'http://dblp.uni-trier.de/db/journals/dcc/',
    ],
    'c': [
        'http://dblp.uni-trier.de/db/journals/ejisec/',
    ],
}

conference_ieee = {
    'a': [
        'http://dblp.uni-trier.de/db/conf/sp/',
    ],
    'b': [
        'http://dblp.uni-trier.de/db/conf/acsac/',
        'http://dblp.uni-trier.de/db/conf/csfw/',
        'http://dblp.uni-trier.de/db/conf/dsn/',
        'http://dblp.uni-trier.de/db/conf/srds/',
    ],
    'c': [
        'http://dblp.uni-trier.de/db/conf/trustcom/',
    ],
}

journal_ieee = {
    'a': [
        'http://dblp.uni-trier.de/db/journals/tdsc/',
        'http://dblp.uni-trier.de/db/journals/tifs/',
    ],
}

conference_usenix = {
    'a': [
        'http://dblp.uni-trier.de/db/conf/uss/',
    ],
}

conference_isoc = {
    'b': [
        'http://dblp.uni-trier.de/db/conf/ndss/',
    ],
}

conference_elsevier = {
    'c': [
        'http://dblp.uni-trier.de/db/conf/dfrws/',
    ],
}

journal_elsevier = {
    'b': [
        'http://dblp.uni-trier.de/db/journals/compsec/',
    ],
    'c': [
        'http://www.journals.elsevier.com/computer-law-and-security-review/',
        'http://dblp.uni-trier.de/db/journals/istr/',
    ],
}

journal_ios = {
    'b': [
        'http://dblp.uni-trier.de/db/journals/jcs/',
    ],
}

journal_iet = {
    'c': [
        'http://dblp.uni-trier.de/db/journals/iet-ifs/',
    ],
}

journal_emerald = {
    'c': [
        'http://dblp.uni-trier.de/db/journals/imcs/',
    ],
}

journal_idea = {
    'c': [
        'http://dblp.uni-trier.de/db/journals/ijisp/',
    ],
}

journal_inderscience = {
    'c': [
        'http://dblp.uni-trier.de/db/journals/ijics/',
    ],
}

journal_wiley = {
    'c': [
        'http://dblp.uni-trier.de/db/journals/scn/',
    ],
}


# 初始化目录
def init_dir(path):
    if os.path.exists(path) is False:
        os.makedirs(path)


# 获得解析后的网页文本
def get_html_text(url):
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup