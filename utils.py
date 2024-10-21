import re
import time
import random
from datetime import datetime, timedelta
import os
from pathlib import Path

from logger import setup_logger

import signal
import time
from functools import wraps


def timeout(seconds):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError("Function timed out")

        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator


def read_key_words():
    key_list = []
    f = open("key_words.txt", encoding='utf-8')  # 返回一个文件对象
    lines = f.readlines()  # 读取全部内容
    for line in lines:
        # 如果读到空行，就跳过
        if line.isspace():
            continue
        else:
            # 去除文本中的换行等等，可以追加其他操作
            line = line.replace("\n", "")
            line = line.replace("\t", "")
            # 处理完成后的行，追加到列表中
            key_list.append(line)
    f.close()
    return key_list


def write_file(data, date, goverment, region):
    with open(f'files/{year_month}/{date}/{region}/{goverment}.txt', 'w', encoding='utf-8') as f:
        f.write(data)


def get_date(yesterday=False): 
    # 获取当前日期
    date = datetime.now()

    # 计算昨天的日期
    if yesterday:
        date = date - timedelta(days=1)
    
    # 将日期格式化为字符串
    return date.strftime("%Y-%m-%d"), date.strftime("%Y年%m月")


# 请求头集合
MyHeaders = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

# 搜索区域
REGIONS =  ["国家级", "省级", "市级", "南山区"]


# 创建当前日期文件夹
# now = datetime.now().strftime('%Y-%m-%d')
now, year_month = get_date(yesterday=True)
for region in REGIONS:
    os.makedirs(f'files/{year_month}/{now}/{region}', exist_ok=True)
os.makedirs(f'xls_files/{year_month}', exist_ok=True)

# 读取关键词
title_keys = ['通知', '文件', '公告']   # 只匹配以该关键词结尾的标题
add_keys = ['以旧换新', '设备更新']     # 匹配包含该部分关键词的标题
content_keys = read_key_words()         # 内容关键词

# 设置关键词匹配模式
title_pattern = re.compile('(?=（.*?）|$)|'.join(title_keys) + r"(?=（.*?）|$)" + r'|'.join(add_keys))
content_pattern = re.compile('|'.join(content_keys))

# 生成随机睡眠时间
sleep_time = random.uniform(1, 2)

# 设置日志对象
os.makedirs(f'logs', exist_ok=True)
logger = setup_logger(
    log_name='Spider System',
    log_filename=Path('logs/spider.log'),
    log_level='info',
    use_console=False
)