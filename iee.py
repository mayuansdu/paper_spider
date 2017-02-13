#!usr/bin/env python
# -*- coding:utf-8 -*-
import re
import time
import traceback
from common import base_dir, log_dir, ieee_updates_url, get_html_str,\
    init_dir
from util import get_phantomjs_page, get_database_connect, get_random_uniform


# 保存下载文件的目录
root_dir = base_dir + 'updates/ieee/'

# 程序运行日志文件
logfile = log_dir + 'update_ieee.txt'

# 程序在START_HOUR ~ END_HOUR 之间运行
START_HOUR = 7
END_HOUR = 22


# 处理1级页面
def handle_first_page(url):
    # 获得一级页面
    page_content = get_html_str(get_phantomjs_page(url))
    if page_content is None:
        print('page is none')
        return None
    options = page_content.find('select', id='updatesDate')
    if options is not None:
        update_time = options.find_next('option')['value']  #获得IEEE内容更新日期，例如:20170206
        # 从数据库中读取上次更新的时间
        db = get_database_connect()
        collection = db.update_conf
        setting_dict = collection.find_one({'name':'setting'})
        if setting_dict:
            last_update_time = setting_dict['last_update_time']
        else:
            last_update_time = '20170101'
            collection.insert(dict({'name':'setting','last_update_time':last_update_time,'this_update_time':last_update_time}))
        if update_time > last_update_time:  # IEEE内容已更新，但是本地尚未采集此次数据
            collection.update_one({'name':'setting'}, {'$set': {'this_update_time': update_time, 'status': 'unfinished'}})
            ul = page_content.find('ul', class_='Browsing')
            if ul is not None:
                lis = ul.find_all_next('li', class_='noAbstract')
                urls = list(map(lambda li: 'http://ieeexplore.ieee.org/xpl/' + li.find_next('a').get('href'), lis))
                handle_second_page(urls)
                # 本次采集数据完成，将本次更新日期保存到数据库
                collection.update_one({'name': 'setting'},{'$set': {'last_update_time': update_time, 'status': 'finished'}})


# 处理2级页面
def handle_second_page(urls):
    links = list()
    for url in urls:
        page_content = get_html_str(get_phantomjs_page(url))
        if page_content is None:
            print('2级页面' + url + '无法获取')
            return None
        ul = page_content.find('ul', class_='results')
        if ul is not None:
            divs = ul.find_all_next('div', class_='txt')
            for div in divs:
                temp = div.find_next('a', class_='art-abs-url')
                if temp is not None:
                    links.append('http://ieeexplore.ieee.org' + temp.get('href'))
        # 找到分页代码，获得分页总数，并向分页链接请求页面内容
        pagination = page_content.find('div', class_='pagination')
        if pagination is not None:
            a_list = pagination.select('a[aria-label^="Pagination Page"]')
            if a_list:
                pageNumber = a_list[-1].get_text().strip()
                if pageNumber is not None:
                    pageNumber = int(pageNumber)
                    url_list = list()
                    for number in range(2, pageNumber+1):
                        url_list.append(url + '&pageNumber=' + str(number))
                    for tmp_url in url_list:
                        page_content = get_html_str(get_phantomjs_page(tmp_url))
                        if page_content is None:
                            print('2级页面' + url + '无法获取')
                            return None
                        ul = page_content.find('ul', class_='results')
                        if ul is not None:
                            divs = ul.find_all_next('div', class_='txt')
                            for div in divs:
                                temp = div.find_next('a', class_='art-abs-url')
                                if temp is not None:
                                    links.append('http://ieeexplore.ieee.org' + temp.get('href'))
        else:
            print('没有找到分页代码' + url)
        time.sleep(get_random_uniform(begin=1.0, end=10.0))
    handle_third_page(links)    # 进一步处理已采集到的当前页面上的所有3级页面的链接


def handle_third_page(urls):
    for url in urls:
        data_dict = dict()
        page_content = get_html_str(get_phantomjs_page(url))
        if page_content is None:
            continue
        # 论文URL地址
        data_dict['url'] = url
        # 论文类型
        data_dict['category'] = 'conference'
        # IEEE更新论文日期
        data_dict['update_time'] = time.strftime('%Y%m%d', time.localtime())
        # 论文采集时间
        data_dict['spider_time'] = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())
        # 采集论文名
        if page_content.title is not None:
            data_dict['title'] = page_content.title.string[:-22].strip()
        # 采集论文关键词信息
        ul = page_content.find('ul', class_= 'doc-all-keywords-list')
        if ul is not None:
            spans = ul.find_all_next('span')
            keywords = list()
            for span in spans:
                temp = span.find_next('a', class_='ng-binding')
                if temp is not None:
                    keywords.append(temp.get_text().strip())
            data_dict['keywords'] = keywords
        # 采集论文作者信息
        h2 = page_content.find('h2', text='Authors')
        if h2 is not None:
            div = h2.find_next_sibling('div', class_='ng-scope')
            if div is not None:
                temp = div.select('a[href^="/search/searchresult.jsp?searchWithin="]')
                if temp is not None:
                    authors_dict = dict()    # 保存多个作者信息到字典
                    for a in temp:
                        affiliation_dict = dict()
                        span = a.find_next('span', class_='ng-binding')
                        if span is not None:
                            author_name = span.get_text().strip()
                            author_name = re.sub(r'[._$]', ' ', author_name)
                            tmp = a.parent.find_next_sibling('div', class_='ng-binding')
                            if tmp is not None:
                                affiliation = tmp.get_text().strip()
                                data_list = re.split(r',', affiliation)
                                affiliation_dict['affiliation'] = affiliation
                                if data_list is not None:
                                    affiliation_dict['affiliation_country'] = data_list[-1]
                            authors_dict[author_name] = affiliation_dict
                    data_dict['author'] = authors_dict
        # 获取论文参考信息
        page_content = get_html_str(get_phantomjs_page(url + 'references?ctx=references'))
        if page_content is not None:
            h2 = page_content.find('h2', text='References')
            if h2 is not None:
                divs = h2.find_next_siblings('div', class_='reference-container ng-scope')
                references = list()
                for div in divs:
                    div_temp = div.find_next('div', class_='description ng-binding')
                    if div_temp:
                        references.append(div_temp.get_text().strip())
                data_dict['references'] = references
        # 获取论文被引用信息
        page_content = get_html_str(get_phantomjs_page(url + 'citations?anchor=anchor-paper-citations-ieee&ctx=citations'))
        if page_content is not None:
            # Cited in Papers - IEEE
            h2 = page_content.find('h2', text=re.compile(r'Cited in Papers - IEEE'))
            citations = list()
            if h2 is not None:
                divs = h2.find_next_siblings('div', class_='ng-scope')
                for div in divs:
                    div_temp = div.find_next('div', class_='description ng-binding')
                    if div_temp:
                        citations.append(div_temp.get_text().strip())
            # Cited in Papers - Other Publishers
            h2 = page_content.find('h2', text=re.compile(r'Cited in Papers - Other Publishers'))
            if h2 is not None:
                divs = h2.find_next_siblings('div', class_='ng-scope')
                for div in divs:
                    div_temp = div.find_next('div', class_='description ng-binding')
                    if div_temp:
                        citations.append(div_temp.get_text().strip())
            data_dict['citations'] = citations
        write_to_database(data_dict)
        time.sleep(get_random_uniform(begin=1.0, end=10.0))


def write_to_database(data):
    try:
        db = get_database_connect()
        db.update_ieee.insert(data)
    except Exception as e:
        print('当前数据字典为：', data)
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('update_ieee:' + '写入数据库出错！' + str(e) + '\n')


# 采集ieee更新的内容
def update_ieee(urls):
    for key, values in urls.items():
        if key == 'conferences':
            for url in values:
                handle_first_page(url)


def run_iee():
    while True: # 每天运行一次
        hour = int(time.strftime('%H'))
        if START_HOUR <= hour <= END_HOUR:
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
        else:   # 休眠1小时
            time.sleep(1*60*60)


if __name__ == '__main__':
    run_iee()