#!usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import copy
import time
import traceback
from common import base_dir, log_dir, conference_springer, journal_springer, get_html_text, get_html_str, init_dir
from util import get_database_connect, get_random_uniform, get_phantomjs_page

# 保存下载文件的目录
root_dir = base_dir + 'springer/'

# 程序运行日志文件
logfile = log_dir + 'log_springer.txt'


# 处理一级页面
def handle_first_page(url, attrs):
    #获得一级页面
    page_content = get_html_text(url)
    if page_content is None:
        return None
    raw_links = page_content.find_all('a', text='[contents]')
    if (raw_links is not None) and (len(raw_links) > 0):
        links = map(lambda raw_link: raw_link.get('href'), raw_links)   # 会议论文
    else:
        raw_links = page_content.find_all('a', text=re.compile(r'Volume'))   # 期刊
        links = map(lambda raw_link: raw_link.get('href'), raw_links)
    for url in links:
        handle_second_page(url, attrs)
        time.sleep(get_random_uniform(begin=1.0, end=5.0))


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
        print('处理二级页面，没有找到electronic edition链接')
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
                    download_paper_info(raw_ris.get('href'), paper_dict)
        time.sleep(get_random_uniform(begin=1.0, end=10.0))


# 处理三级页面
def handle_third_page(url, attrs):
    soup = get_html_str(get_phantomjs_page(url))
    if soup is None:
        print('soup is None', url)
        return None
    # 获取关于论文的描述信息:标题、作者、发表日期等等
    data_dict = copy.deepcopy(attrs)  # 深拷贝字典
    tmp_list = soup.find_all('li', class_='affiliation')
    affiliation_list = list()
    for tmp in tmp_list:
        affiliation_dict = dict()
        department = tmp.find_next('span', class_='affiliation__department')
        if department is not None:
            affiliation_dict['affiliation_department'] = department.get_text()
        name = tmp.find_next('span', class_='affiliation__name')
        if name is not None:
            affiliation_dict['affiliation_name'] = name.get_text()
        city = tmp.find_next('span', class_='affiliation__city')
        if city is not None:
            affiliation_dict['affiliation_city'] = city.get_text()
        country = tmp.find_next('span', class_='affiliation__country')
        if country is not None:
            affiliation_dict['affiliation_country'] = country.get_text()
        affiliation_list.append(affiliation_dict)
    tmp_list = soup.find_all('span', class_='authors-affiliations__name')
    author_dict = dict()
    for tmp in tmp_list:
        id = tmp.find_next_sibling('ul').find_next('li').get_text()
        author = re.sub(r'\xa0', ' ', tmp.get_text()).strip()
        author = re.sub(r'\.', ' ', author)
        author_dict[author] = affiliation_list[int(id)-1]
    if len(author_dict) != 0:
        data_dict['author'] = author_dict
    return data_dict


# 下载论文描述的ris格式文件保存到本地
def download_paper_info(url, attrs):
    filename = re.split(r'/', url)[-1]
    page_content = get_html_text(url)
    if page_content is None:
        print('出现异常的网址:', url)
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('download_paper_info:' + '出错！' + url)
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
        print('写入数据库出错！', e, filepath)
        print('当前数据字典为：', attrs)
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('write_to_database:' + '写入数据库出错！' + str(e) + filepath)


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
                    attrs['url'] = url
    else:
        print(filepath, '文件不存在！')
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('handle_ris:' + filepath + '文件不存在！' + '\n')


# 爬取springer的论文
def spider_springer(urls, attrs):
    init_dir(root_dir)
    for key, value in urls.items():
        attrs['rank'] = key
        for url in value:
            handle_first_page(url, attrs)


def run_springer():
    with open(logfile, 'a+', encoding='utf-8') as f:
        f.write('acm_spider正常启动:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n')
    try:
        spider_springer(conference_springer, attrs={'category': 'conference'})   # 采集会议论文信息
        spider_springer(journal_springer, attrs={'category': 'journal'})  # 采集期刊论文信息
    except Exception as e:
        with open(logfile, 'a+', encoding='utf-8') as f:
            traceback.print_exc(file=f)
            f.write('acm_spider异常停止:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n\n')
    else:
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('acm_spider正常停止:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n\n')


if __name__ == '__main__':
    run_springer()