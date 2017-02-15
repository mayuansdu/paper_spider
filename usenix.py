#!usr/bin/env python
# -*- coding: utf-8 -*-
import re, copy, time, logging, logging.handlers
from common import base_dir, log_dir, conference_usenix, get_html_text,\
    init_dir, download_paper_info
from util import get_random_uniform

# 保存下载文件的目录
root_dir = base_dir + 'usenix/'

# 程序运行日志文件
logfile = log_dir + 'log_usenix.log'
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，默认最大为50M
# 配置日志: 2个日志文件副本
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('usenix')

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
        time.sleep(get_random_uniform(begin=60.0, end=180.0))

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
        paper_dict = handle_third_page(raw_url.get('href'), attrs)
        tmp = raw_url.find_parent('li', class_='drop-down')
        if tmp is not None:
            temp = tmp.find_next_sibling('li', class_='drop-down')
            if temp is not None:
                raw_ris = temp.select_one(
                    'div[class="body"] > ul:nth-of-type(1) > li:nth-of-type(2) > a'
                )
                if raw_ris is not None:
                    download_paper_info(raw_ris.get('href'), root_dir, logfile, paper_dict)
        time.sleep(get_random_uniform(begin=60.0, end=300.0))


# 处理三级页面
def handle_third_page(url, attrs):
    soup = get_html_text(url)
    if soup is None:
        logger.info('soup is None:' + str(url))
        return None
    # 获取关于论文的描述信息:标题、作者、发表日期等等
    data_dict = copy.deepcopy(attrs)  # 深拷贝字典
    tmp = soup.find('div', class_='field-label')
    if tmp is not None:
        tmp = soup.find('div', class_='field-item odd').find_next('p')
        tmp_list = list()
        if tmp is not None:
            i = 0
            for child in tmp.children:
                i += 1
                if (i % 2) != 0:
                    tmp_list.append(child)  # 作者名
                else:
                    child = child.get_text().strip()
                    tmp_list.append(child.strip(';'))   # 机构名称
            authors_dict = dict()
            for n in range(0, len(tmp_list), 2):
                affiliation_dict = dict()
                affiliation_dict['affiliation_name'] = tmp_list[n + 1]
                author_list = re.split(r'(?:and|,)\s*', tmp_list[n])[:-1]
                for author in author_list:
                    if (author != '') and (author != ','):
                        author = re.sub(r'[\.$_]', ' ', author.strip())
                        authors_dict[author] = affiliation_dict
            data_dict['author'] = authors_dict
    return data_dict  # 返回数据字典（类别、等级、作者信息）


# 爬取usenix的论文信息
def spider_usenix(urls, attrs):
    init_dir(log_dir)
    init_dir(root_dir)
    for key, value in urls.items():
        attrs['rank'] = key
        for url in value:
            handle_first_page(url, attrs)


def run_usenix():
    logger.warning('usenix_spider正常启动!')
    try:
        spider_usenix(conference_usenix, attrs={'category': 'conference'})   # 采集会议论文信息
    except Exception as e:
        logger.exception('usenix_spider异常停止!')
    else:
        logger.warning('usenix_spider正常停止!')


if __name__ == '__main__':
    run_usenix()