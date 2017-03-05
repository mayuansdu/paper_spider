#!usr/bin/env python
# -*- coding: utf-8 -*-
import re, time, logging, logging.handlers, copy
from common import base_dir, log_dir, journal_elsevier, get_html_text,\
    get_html_str, init_dir
from util import get_random_uniform, get_database_connect, get_phantomjs_page

# 保存下载文件的目录
root_dir = base_dir + 'elsevier/journals/'

# 程序运行日志文件
logfile = log_dir + 'log_science_direct.log'
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，默认最大为50M
# 配置日志: 2个日志文件副本
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('science')

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
    raw_links = list()
    li_list = page_content.select('a[href^="http://dblp.uni-trier.de/db/journals/"]')
    for li in li_list:
        temp = li.get('href')
        if 'http://dblp.uni-trier.de/db/journals/' != temp:
            raw_links.append(temp)
    for url in raw_links:
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
    links = map(lambda tmp: tmp.find_parent('a').get('href'), raw_links)
    if links is None:
        logger.info('处理二级页面，没有找到electronic edition链接' + str(url))
    handle_third_page(list(links), attrs)


def handle_third_page(urls, attrs):
    for url in urls:
        soup = get_html_str(get_phantomjs_page(url))
        if soup is None:
            logger.info('3级页面无法获取:' + str(url))
            return None
        else:
            link = soup.find('link', attrs={'rel': 'canonical'})
            if link:
                link = link.get('href')
            else:
                logger.info('handle_third_page没有找到跳转链接link:' + str(url))
                return None
        soup = get_html_str(get_phantomjs_page(link))
        # 获取关于论文的描述信息:标题、作者、发表日期等等
        data_dict = copy.deepcopy(attrs)  # 深拷贝字典
        data_dict['url'] = link     # 保存论文的正真链接地址
        h1 = soup.find('h1', class_='svTitle')
        if h1:
            data_dict['title'] = h1.get_text().strip()
        ul = soup.find('ul', class_='authorGroup noCollab svAuthor')
        if ul:
            a_list = ul.find_all_next('a', class_='authorName svAuthor')
            authors_dict = dict()
            for a in a_list:
                affiliation_dict = dict()
                affiliation_dict['affiliation'] = ''
                affiliation_dict['affiliation_name'] = ''
                affiliation_dict['affiliation_country'] = ''
                author_name = a.get_text().strip()
                author_name = re.sub(r'[\._$]', ' ', author_name)
                authors_dict[author_name] = affiliation_dict
            data_dict['author'] = authors_dict
        h2 = soup.find('h2', text=re.compile(r'Abstract'))
        if h2:
            p = h2.find_next_sibling('p')
            data_dict['abstract'] = p.get_text()
        h2 = soup.find('h2', text=re.compile(r'Keywords'))
        if h2:
            ul = h2.find_next_sibling('ul')
            keywords_list = ul.find_all_next('li', class_='svKeywords')
            keywords = list()
            for keyword in keywords_list:
                keywords.append(keyword.get_text().strip())
            data_dict['keywords'] = keywords
        h2 = soup.find('h2', text=re.compile(r'References'))
        if h2:
            li_list = h2.find_all_next('li', class_='title')
            references = list()
            for li in li_list:
                references.append(li.get_text().strip())
            data_dict['reference'] = references
        write_to_database(data_dict)
        time.sleep(get_random_uniform(begin=2.0, end=60.0))


# 把论文信息写入数据库中
def write_to_database(attrs):
    data_dict = copy.deepcopy(attrs)
    data_dict['spider_time'] = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())
    try:
        collection = data_dict['category']
        if collection and (collection != ''):
            db = get_database_connect()
            if collection == 'journal':
                db.conference.insert(data_dict)
            elif collection == 'conference':
                db.journal.insert(data_dict)
            else:
                db.others.insert(data_dict)
    except Exception:
        logger.exception('写入数据库出错！')


def spider_science_direct(urls, attrs):
    init_dir(log_dir)
    init_dir(root_dir)
    for key, value in urls.items():
        attrs['rank'] = key
        for url in value:
            handle_first_page(url, attrs)


def run_science_direct():
    logger.warning('science_direct_spider正常启动!')
    try:
        spider_science_direct(journal_elsevier, attrs={'category': 'journal'})   # 采集期刊信息
    except Exception as e:
        logger.exception('science_direct_spider异常停止!')
    else:
        logger.warning('science_direct_spider正常停止!')


if __name__ == '__main__':
    run_science_direct()
    # handle_third_page(['http://dx.doi.org/10.1016/j.cose.2016.10.001',], {})