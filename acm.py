#!usr/bin/env python
# -*- coding: utf-8 -*-
import re, copy, time, logging, logging.handlers
from common import base_dir, log_dir, conference_acm, journal_acm, get_html_text,\
    init_dir, download_paper_info
from util import get_random_uniform

# 保存下载文件的目录
root_dir = base_dir + 'acm/'
# 程序运行日志文件
logfile = log_dir + 'log_acm.log'
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，默认最大为50M
# 配置日志: 2个日志文件副本
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('acm')

handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


# 处理一级页面
def handle_first_page(url, attrs):
    #获得一级页面
    page_content = get_html_text(url)
    if page_content is None:
        logger.info('1级页面无法获取：' + str(url))
        return None
    raw_links = page_content.find_all('a', text='[contents]')
    if ((raw_links is not None) and (len(raw_links)) > 0):
        links = map(lambda raw_link: raw_link.get('href'), raw_links)   # 会议论文
    else:
        raw_links = page_content.find_all('a', text=re.compile(r'Volume'))   # 期刊
        links = map(lambda raw_link: raw_link.get('href'), raw_links)
    for url in links:
        handle_second_page(url, attrs)
        time.sleep(get_random_uniform(begin=60.0, end=180.0))


# 处理二级页面
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
                    download_paper_info(raw_ris.get('href'), root_dir, paper_dict)
        time.sleep(get_random_uniform(begin=60.0, end=300.0))
    if links is None:
        logger.info('处理二级页面，没有找到electronic edition链接' + str(url))


# 处理三级页面
def handle_third_page(url, attrs):
    soup = get_html_text(url)
    if soup is None:
        logger.info('soup is None:' + str(url))
        return None
    # 获取关于论文的描述信息:标题、作者、发表日期等等
    data_dict = copy.deepcopy(attrs)  # 深拷贝字典
    # 获取论文PDF的下载地址
    pdf_url = soup.find('a', attrs={'name': 'FullTextPDF'})
    if pdf_url is not None:
        pdf_url = 'http://dl.acm.org/' + pdf_url.get('href').strip()
        data_dict['pdf_url'] = pdf_url
    authors = soup.find_all('a', attrs={'title': 'Author Profile Page'})
    if (authors is not None) and (authors != ''):
        authors_dict = {}
        for tmp in authors:
            temp = tmp.find_next('a', attrs={'title': 'Institutional Profile Page'})
            if (temp is not None) and (temp != ''):
                institute = temp.find_next('small')
                if (institute is not None) and (institute != ''):
                    affiliation_dict = dict()
                    # mongodb中带有"."号，"_"号和"$"号前缀的Key被保留
                    author_name = re.sub(r'[\._$]', ' ', tmp.get_text().strip())
                    institute = institute.get_text().strip()
                    data_list = re.split(r',', institute)
                    affiliation_dict['affiliation'] = institute
                    affiliation_dict['affiliation_name'] = data_list[0]
                    if len(data_list) != 1:
                        affiliation_dict['affiliation_country'] = data_list[-1]
                    authors_dict[author_name] = affiliation_dict
        data_dict['author'] = authors_dict
        return data_dict    #返回数据字典（类别、等级、作者信息）
    else:
        logger.info('三级页面没有找到论文描述信息' + str(url))


# 爬取ACMDL的论文
def spider_acm_dl(urls, attrs):
    init_dir(log_dir)
    init_dir(root_dir)
    for key, value in urls.items():
        attrs['rank'] = key
        for url in value:
            handle_first_page(url, attrs)


def run_acmdl():
    logger.warning('acm_spider正常启动!')
    try:
        spider_acm_dl(conference_acm, attrs={'category': 'conference'})   # 采集会议论文信息
        spider_acm_dl(journal_acm, attrs={'category': 'journal'})  # 采集期刊论文信息
    except Exception as e:
        logger.exception('acm_spider异常停止!')
    else:
        logger.info('acm_spider正常停止!')


if __name__ == '__main__':
    # run_acmdl()
    handle_third_page('http://dl.acm.org/citation.cfm?doid=2976749.2978341', attrs={'category': 'conference'})