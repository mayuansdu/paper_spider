#!usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.handlers


# 记录程序运行的日志文件设定
logfile = './log/about.log'
logfile_size = 1 * 1024 * 1024  # 日志文件的最大容量，单位 M。默认最大为100M
# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

handler = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=logfile_size, backupCount=2, encoding='utf-8')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def run_about():
    logger.info('开始aaaaaaaa程序')
    i = 100
    while i > 0:
        try:
            with open('./log/info.txt', 'r', encoding='utf-8') as f:
                print(f.readlines())
        except (SystemError, KeyboardInterrupt):
            raise
        except Exception as e:
            logger.exception('第%s次出现异常！', i)
            i -= 1
    logger.info('结束aaaaaaaa程序.......\n')


if __name__ == '__main__':
    run_about()