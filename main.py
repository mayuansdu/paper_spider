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
logfile_size = 50 * 1024 * 1024  # 日志文件的最大容量，默认最大为50M
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

funcitons = [
    run_acmdl,
    run_springer,
    run_ieee_update,
    run_ieee,
    # run_isoc,
    # run_usenix,
    # run_elsevier,
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
    logger.warning('main_spider正常启动!')
    try:
        spider_body()
    except Exception as e:
        logger.exception('main_spider异常停止!')
    else:
        logger.warning('main_spider正常停止!')