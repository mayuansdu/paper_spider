#!usr/bin/env python
# -*- coding:utf-8 -*-
import re
import os
import time
import traceback
from common import base_dir, log_dir, ieee_updates_url, get_html_str,\
    init_dir
from util import get_phantomjs_page, get_database_connect, get_random_uniform


# 保存下载文件的目录
root_dir = base_dir + 'updates/ieee/'

# 程序运行日志文件
logfile = log_dir + 'update_ieee.txt'


# 处理1级页面
def handle_first_page(url):
    # 获得一级页面
    page_content = get_html_str(get_phantomjs_page(url))
    if page_content is None:
        print('page is none')
        return None
    options = page_content.find('select', id='updatesDate')
    if options is not None:
        update_date = options.find_next('option')['value']  #IEEE内容更新日期 eg:20170206
        if update_date is None:
            print('没有得到内容更新日期')
        elif update_date <= '20170202':
            print(update_date + '的内容已经更新')
        else:
            print('即将更新' + update_date +'的内容')
            ul = page_content.find('ul', class_='Browsing')
            if ul is not None:
                lis = ul.find_all_next('li', class_='noAbstract')
                urls = list(map(lambda li: 'http://ieeexplore.ieee.org/xpl/' + li.find_next('a').get('href'), lis))
                handle_second_page(urls)
    else:
        print('没有找到updatesDate')


# 处理2级页面
def handle_second_page(urls):
    links = list()
    for url in urls:
        print('2级页面：' + url)
        page_content = get_html_str(get_phantomjs_page(url))
        if page_content is None:
            print('2级页面无法获取')
            return None
        ul = page_content.find('ul', class_='results')
        if ul is not None:
            divs = ul.find_all_next('div', class_='txt')
            for div in divs:
                temp = div.find_next('a', class_='art-abs-url')
                if temp is not None:
                    links.append('http://ieeexplore.ieee.org' + temp.get('href'))
        break
        # time.sleep(get_random_uniform(begin=2, end=15))
    handle_third_page(links)


def handle_third_page(urls):
    print('链接总数为:' + str(len(urls)))
    for url in urls:
        print('3级页面:' + url)
        data_dict = dict()
        page_content = get_html_str(get_phantomjs_page(url))
        if page_content is None:
            print('3级页面无法获取')
            return None
        if page_content.title is not None:
            data_dict['title'] = page_content.title.string
        ul = page_content.find('ul', class_= 'doc-all-keywords-list')
        if ul is None:
            print('无法找到ul')
            return None
        spans = ul.find_all_next('span')
        keywords = list()
        for span in spans:
            temp = span.find_next('a', class_='ng-binding')
            if temp is not None:
                keywords.append(temp.get_text().strip())
        data_dict['keywords'] = keywords
        print(data_dict)


# 采集ieee更新的内容
def update_ieee(urls):
    for key, values in urls.items():
        if key == 'conferences':
            for url in values:
                handle_first_page(url)


def run_iee():
    init_dir(log_dir)
    init_dir(root_dir)
    with open(logfile, 'a+', encoding='utf-8') as f:
        f.write('update_ieee正常启动:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n')
    try:
        update_ieee(ieee_updates_url)
    except Exception as e:
        with open(logfile, 'a+', encoding='utf-8') as f:
            traceback.print_exc(file=f)
            f.write('update_ieee异常停止%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + str(e) + '\n\n')
    else:
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('update_ieee正常停止:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n\n')


if __name__ == '__main__':
    # run_iee()
    handle_third_page(['http://ieeexplore.ieee.org/document/7842913/',])