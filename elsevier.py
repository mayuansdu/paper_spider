#!usr/bin/env python
# -*- coding: utf-8 -*-
import re, os, copy, time, logging, logging.handlers
from common import base_dir, log_dir, conference_elsevier, journal_elsevier, get_html_text,\
    init_dir
from util import get_random_uniform, get_database_connect

# 保存下载文件的目录
root_dir = base_dir + 'elsevier/'

# 程序运行日志文件
logfile = log_dir + 'log_elsevier.log'
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，默认最大为50M
# 配置日志: 2个日志文件副本
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('elsevier')

handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


# 处理一级页面
def handle_first_page(url, attrs):
    # 获得一级页面
    page_content = get_html_text(url)
    if page_content is None:
        logger.info('1级页面无法获取：' + str(url))
        return None
    raw_links = page_content.find_all('a', text='[contents]')
    if (raw_links is not None) and (len(raw_links) > 0):
        links = map(lambda raw_link: raw_link.get('href'), raw_links)   # 会议论文
    else:
        raw_links = page_content.find_all('a', text=re.compile(r'Volume'))   # 期刊
        links = map(lambda raw_link: raw_link.get('href'), raw_links)
    for url in links:
        handle_second_page(url, attrs)
        time.sleep(get_random_uniform(begin=2.0, end=60.0))


def handle_second_page(url, attrs):
    # 获得二级页面
    soup = get_html_text(url)
    if soup is None:
        return None
    # 优先使用DOI链接
    raw_links = soup.find_all(text=re.compile(r'electronic edition via DOI'))
    if len(raw_links) == 0:
        # 没有找到DOI链接，就选择使用通过 @ 找到的链接
        raw_links = soup.find_all(text=re.compile(r'electronic edition @'))
    links = map(lambda tmp: tmp.find_parent('a'), raw_links)
    if links is None:
        logger.info('处理二级页面，没有找到electronic edition链接' + str(url))
    for raw_url in links:
        tmp = raw_url.find_parent('li', class_='drop-down')
        if tmp is not None:
            temp = tmp.find_next_sibling('li', class_='drop-down')
            if temp is not None:
                raw_ris = temp.select_one(
                    'div[class="body"] > ul:nth-of-type(1) > li:nth-of-type(2) > a'
                )
                if raw_ris is not None:
                    download_paper_info(raw_ris.get('href'), root_dir, attrs)
        time.sleep(get_random_uniform(begin=2.0, end=60.0))


# 下载论文描述的ris格式文件保存到本地
def download_paper_info(url, root_dir, attrs):
    filename = re.split(r'/', url)[-1]
    page_content = get_html_text(url)
    if page_content is None:
        logger.error('download_paper_info出错！' + str(url))
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
    data_dict = copy.deepcopy(attrs)
    data_dict['spider_time'] = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())
    try:
        handle_ris(filepath, data_dict)
        collection = data_dict['category']
        if (collection is not None) and (collection != ''):
            db = get_database_connect()
            if collection == 'conference':
                db.conference.insert(data_dict)
            elif collection == 'journal':
                db.journal.insert(data_dict)
            else:
                db.others.insert(data_dict)
    except Exception:
        logger.exception('写入数据库出错！')


# 处理论文RIS文本内容
def handle_ris(filepath, attrs):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:  # 此处不设置为utf-8 因为有特殊符号无法编码
            context = f.readlines()[5:-1]
            author_dict = dict()
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
                if re.search(r'AU', line) is not None:
                    author = line[6:].strip()
                    author = re.sub(r'[\._$]', ' ', author)
                    author_dict[author] = dict()
            attrs['author'] = author_dict
    else:
        logger.info('文件不存在！' + str(filepath))


# 爬取elsevier的论文信息
def spider_elsevier(urls, attrs):
    init_dir(log_dir)
    init_dir(root_dir)
    for key, value in urls.items():
        attrs['rank'] = key
        for url in value:
            handle_first_page(url, attrs)


def run_elsevier():
    logger.warning('elsevier_spider正常启动!')
    try:
        spider_elsevier(conference_elsevier, attrs={'category': 'conference'})   # 采集会议论文信息
        # spider_elsevier(journal_elsevier, attrs={'category': 'conference'}) # 采集期刊信息
    except Exception as e:
        logger.exception('elsevier_spider异常停止!')
    else:
        logger.warning('elsevier_spider正常停止!')


if __name__ == '__main__':
    run_elsevier()