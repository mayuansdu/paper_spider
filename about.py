#!usr/bin/env python
# -*- coding: utf-8 -*-
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

handler = logging.FileHandler('./log/about.log', encoding='utf-8')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [ %(name)s : %(levelname)s ] %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info('开始本程序')
try:
    with open('./log/info.txt', 'r', encoding='utf-8') as f:
        print(f.readlines())
except (SystemError, KeyboardInterrupt):
    raise
except Exception as e:
    logger.exception('出现异常！')
logger.info('结束本程序.......\n')


# if __name__ == '__main__':
#     print('about Model正在运行...')