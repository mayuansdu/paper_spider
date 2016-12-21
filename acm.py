#!usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import copy
import time
import requests
from common import header, base_dir, conference_acm, journal_acm, get_html_text, init_dir, get_html_str
from util import get_database_connect, get_random_uniform, get_phantomjs_page

# 保存下载文件的目录
root_dir = base_dir + 'acm/'


# 处理一级页面
def handle_first_page(url, attrs):
    #获得一级页面
    raw_links = get_html_text(url).find_all('a', text='[contents]')
    if ((raw_links is not None) and (len(raw_links)) > 0):
        links = map(lambda raw_link: raw_link.get('href'), raw_links)   # 会议论文
    else:
        raw_links = get_html_text(url).find_all('a', text=re.compile(r'Volume'))   # 期刊
        links = map(lambda raw_link: raw_link.get('href'), raw_links)
    for url in links:
        handle_second_page(url, attrs)
        time.sleep(get_random_uniform(begin=5.0, end=20.0))


# 处理二级页面
def handle_second_page(url, attrs):
    # 获得二级页面
    soup = get_html_text(url)
    # 优先使用DOI链接
    raw_links = soup.find_all(text=re.compile(r'electronic edition via DOI'))
    if len(raw_links) == 0:
        # 没有找到DOI链接，就选择使用通过 @ 找到的链接
        raw_links = get_html_text(url).find_all(text=re.compile(r'electronic edition @'))
    links = map(lambda tmp: tmp.find_parent('a'), raw_links)
    for raw_url in links:
        tmp = raw_url.find_parent('li', class_='drop-down')
        if tmp is not None:
            temp = tmp.find_next_sibling('li', class_='drop-down')
            if temp is not None:
                raw_ris = temp.select_one(
                    'div[class="body"] > ul:nth-of-type(1) > li:nth-of-type(2) > a'
                )
                if raw_ris is not None:
                    ris = raw_ris.get('href')   # 论文信息RIS文件链接
        print('论文:', raw_url.get('href'))
        print('ris:', ris)
        # handle_third_page(raw_url.get('href'), attrs)
        # time.sleep(get_random_uniform(begin=5.0, end=20.0))
    if links is None:
        print('处理二级页面，没有找到electronic edition链接')


# 处理三级页面
def handle_third_page(url, attrs):
    soup = get_html_text(url)
    # 获取关于论文的描述信息:标题、作者、发表日期等等
    # data_dict = copy.deepcopy(attrs)  # 深拷贝字典
    # authors = soup.find_all('a', attrs={'title': 'Author Profile Page'})
    # if (authors is not None) and (authors != ''):
    #     authors_dict = {}
    #     for tmp in authors:
    #         temp = tmp.find_next('a', attrs={'title': 'Institutional Profile Page'})
    #         if (temp is not None) and (temp != ''):
    #             institute = temp.find_next('small')
    #             if (institute is not None) and (institute != ''):
    #                 authors_dict[tmp.get_text().strip()] = institute.get_text().strip()
    #     data_dict['author'] = authors_dict
    # else:
    #     print('三级页面没有找到论文描述信息{0}:'.format(url))
    # 获取论文的EndNote格式信息并保存到本地
    tmp = soup.find('a', text='EndNote')
    if (tmp is not None):
        raw_link = tmp.get('href')
        endnote = 'http://dl.acm.org/' + re.split(r"'", raw_link)[3]
        print(endnote)
        download_paper_info(raw_link)
    else:
        print('没有找到此链接的EndNote:%s' % (url))


# 下载论文描述的ris格式文件保存到本地
def download_paper_info(url):
    filename = re.split(r'/', url)[-1]
    print('name:', filename, url)
    data = get_html_text(url).get_text()
    if data is not None:
        # 将数据存入本地文件中，方便读取和写入数据库
        filepath = root_dir + filename
        with open(filepath, 'w') as f:
            f.write(data)
            f.flush()
        write_to_database(filepath)


# 把论文信息写入数据库中
def write_to_database(filepath):
    pass


# 爬取ACMDL的论文
def spider_acm_dl(urls, attrs):
    init_dir(root_dir)
    for key, value in urls.items():
        attrs['rank'] = key
        for url in value:
            handle_first_page(url, attrs)


def run_acmdl():
    spider_acm_dl(conference_acm, attrs={'category': 'conference'})   # 采集会议论文信息
    spider_acm_dl(journal_acm, attrs={'category': 'journal'})  # 采集期刊论文信息


if __name__ == '__main__':
    run_acmdl()