#!usr/bin/env python
# -*- coding: utf-8 -*-
import time
import traceback
from elsevier import run_elsevier
from usenix import run_usenix
from isoc import run_isoc
from acm import run_acmdl
from springer import run_springer
from ieee import run_ieee
from multiprocessing import Pool
from common import init_dir, log_dir, base_dir

root_dir = base_dir #保存下载文件的主目录

# 程序运行日志文件
logfile = log_dir + 'log_main.txt'

funcitons = [
    run_isoc,
    run_usenix,
    run_elsevier,
    run_acmdl,
    run_springer,
    run_ieee,
]


def spider_body():
    pool = Pool(processes=4)    # set the processes max number 6
    for function in funcitons:
        pool.apply_async(function)
    pool.close()
    pool.join()


if __name__ == '__main__':
    init_dir(log_dir)
    init_dir(root_dir)
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