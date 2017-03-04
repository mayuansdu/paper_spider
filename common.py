#!usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, time, requests, logging, logging.handlers
from bs4 import BeautifulSoup
from util import get_database_connect

# 存放爬取到的文件的根目录
base_dir = './file/'
# 程序运行日志文件根目录
log_dir = './log/'
logfile = log_dir + 'log_common.log'
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，单位:M。默认最大为50M
# 配置日志: 2个日志文件副本
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('common')

handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate',
           'Connection': 'keep-alive',
           'Cache-Control': 'max-age=0',
}

conference_acm = {
    'a': [
        'http://dblp.uni-trier.de/db/conf/ccs/',
        'http://dblp.uni-trier.de/db/conf/acsac/',
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

ieee_updates_url = {
    'journals': [
        'http://ieeexplore.ieee.org/xpl/mostRecentWeeklyUpdatedPeriodicalsIssues.jsp',
    ],
    'conferences': [
        'http://ieeexplore.ieee.org/xpl/mostRecentWeeklyUpdatedConferencesIssues.jsp',
    ],
    'standards': [
        'http://ieeexplore.ieee.org/xpl/mostRecentWeeklyUpdatedStandardsIssues.jsp',
    ],
    'books': [
        'http://ieeexplore.ieee.org/xpl/bookContentUpdates',
    ],
    'courses': [
        'http://ieeexplore.ieee.org/xpl/courseContentUpdates',
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

# ---------------------------------------------------
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
    for i in range(1, 6):   # 如果连接异常，尝试5次
        try:
            r = requests.get(url, headers=header)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        except Exception as e:
            logger.exception('第%s次 get_html_text出现异常！', i)
            time.sleep(5)
    return None


def get_html_str(str):
    if str is None:
        return None
    soup = BeautifulSoup(str, 'html.parser')
    return soup


# 下载论文描述的ris格式文件保存到本地
def download_paper_info(url, root_dir, attrs):
    filename = re.split(r'/', url)[-1]
    page_content = get_html_text(url)
    if page_content is None:
        logger.error('download_paper_info出错:' + url)
        return None
    data = page_content.get_text()
    if data is not None:
        # 将数据存入本地文件中，方便读取和写入数据库
        filepath = root_dir + filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
            f.flush()
        write_to_database(filepath, attrs)


# 把论文信息写入数据库中
def write_to_database(filepath, attrs):
    attrs['spider_time'] = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())
    try:
        handle_ris(filepath, attrs)
        collection = attrs['category']
        if (collection is not None) and (collection != ''):
            db = get_database_connect()
            if collection == 'conference':
                db.conference.insert(attrs)
            elif collection == 'journal':
                db.journal.insert(attrs)
            else:
                db.others.insert(attrs)
    except Exception as e:
        logger.exception('写入数据库出错！')


# 处理论文RIS文本内容
def handle_ris(filepath, attrs):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:  # 此处不设置为utf-8 因为有特殊符号无法编码
            context = f.readlines()[5:-1]
            for line in context:
                line = line.strip('\n')
                if re.search(r'TI', line) is not None:
                    title = line[6:].strip()
                    attrs['title'] = title
                if re.search(r'BT', line) is not None:
                    booktitle = line[6:].strip()
                    attrs['booktitle'] = booktitle
                if re.search(r'PY', line) is not None:
                    year = line[6:10]
                    attrs['year'] = year
                if re.search(r'DO', line) is not None:
                    doi = line[6:].strip()
                    attrs['doi'] = doi
                if re.search(r'UR', line) is not None:
                    url = line[6:].strip()
                    if 'url' not in attrs.keys():
                        attrs['url'] = url
    else:
        logger.error(filepath + '文件不存在！')