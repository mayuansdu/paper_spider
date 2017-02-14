#!usr/bin/env python
# -*- coding: utf-8 -*-
import time, traceback, logging, logging.handlers
from elsevier import run_elsevier
from usenix import run_usenix
from isoc import run_isoc
from acm import run_acmdl
from springer import run_springer
from ieee import run_ieee
from ieee_update import run_ieee_update
from multiprocessing import Pool
from common import init_dir, log_dir, base_dir

root_dir = base_dir #保存下载文件的主目录
# 记录程序运行的日志文件设定
logfile = log_dir + 'log_main.log'
logfile_size = 100 * 1024 * 1024  # 日志文件的最大容量，单位 M。默认最大为100M
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')


funcitons = [
    # run_isoc,
    # run_usenix,
    # run_elsevier,
    run_acmdl,
    run_springer,
    run_ieee_update,
    run_ieee,
]


def spider_body():
    pool = Pool(processes=4)    # set the processes max number 6
    for function in funcitons:
        pool.apply_async(function)
    pool.close()
    pool.join()


def init():
    init_dir(log_dir)
    init_dir(root_dir)


if __name__ == '__main__':
    init()
    with open(logfile, 'a+', encoding='utf-8') as f:
        print('main_spider正常启动:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')))
        f.write('main_spider正常启动:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n')
    try:
        spider_body()
    except Exception as e:
        print('出现错误:', str(e))
        print('main_spider异常停止:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')))
        with open(logfile, 'a+', encoding='utf-8') as f:
            traceback.print_exc(file=f)
            f.write('main_spider异常停止:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n'+ str(e) +'\n\n')
    else:
        print('main_spider正常停止:%s' % (time.strftime('%Y%m%d-%H:%M:%S')))
        with open(logfile, 'a+', encoding='utf-8') as f:
            f.write('main_spider正常停止:%s' % (time.strftime('%Y.%m.%d %H:%M:%S')) + '\n\n')