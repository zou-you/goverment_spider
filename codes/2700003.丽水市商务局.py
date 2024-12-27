# -*- coding:utf-8 -*-
import requests
import datetime
import time
import sys
import os
import io
import re
import argparse
from bs4 import BeautifulSoup
import random
import sys 
sys.path.extend(['.', '..'])

from utils import sleep_time, title_pattern, content_pattern, write_file, now, MyHeaders, logger, timeout

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

GOVERMENT = "丽水市商务局"


def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--start_date",
        type=str,
        default=now,
        help="The start time of the spider",
    )

    return parser.parse_args()


def get_bs(url):
    headers = {'User-Agent': random.choice(MyHeaders)}
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, 'html5lib')

    return bs, response

# 定义函数将日期格式转换为 YYYY-MM-DD
def format_date(date_str):
    # 移除中文字符并转换为日期格式
    date_obj = datetime.datetime.strptime(date_str, '%Y年%m月%d日')
    # 返回格式化后的日期
    return date_obj.strftime('%Y-%m-%d')

@timeout(3600)
def get_content(start_date=now):
    url_index = "http://sswj.lishui.gov.cn/col/col1229219464/index.html"

    url_list, date_list, title_list = [], [], []
    page_turning = True  # 是否需要翻页
    page_num, news_num = 1, 0

    # 定义正则表达式
    record_pattern = re.compile(r'</a><a href="(.*?)" target="_blank".*?\[(\d{4}-\d{2}-\d{2})\]')

    while page_turning:
        logger.info(f"当前页：{page_num}")

        # 访问链接
        bs, response = get_bs(url_index)
        html_content = response.text
        
        # 使用正则表达式进行匹配
        records = record_pattern.findall(html_content)

        # 找出符合要求的时间以及标题
        for record in records:
            news_num += 1
            href, date = record
     
            if date < start_date:
                if news_num <= 10:      # 首页前几条可能不是最新的
                    continue
                page_turning = False
                break
            if not href.startswith('http'):
                href = 'http://sswj.lishui.gov.cn' + href
            url_list.append(href)
            date_list.append(date)

        # 不进行翻页查找
        break

    result = ''
    # 进入详情页查找关键字
    for index, url_detail in enumerate(url_list):
        bs, _ = get_bs(url_detail)
        title = bs.find(class_='t_news').get_text(strip=True).replace('·', '').replace('\n', '')
        if title_pattern.search(title):  # 匹配标签关键字
            logger.info(f"{title}\t{date_list[index]}")
            text = bs.get_text(strip=True)
            match_res = set(content_pattern.findall(text))
            if match_res:
                result += f"{GOVERMENT}\t{','.join(list(match_res))}\t{title}\t{date_list[index]}\t{url_detail}\n" 
            # 随机睡眠
            time.sleep(sleep_time)

        # 随机睡眠
        time.sleep(sleep_time)

    # 写入文件
    write_file(result, now, GOVERMENT, "市级")


if __name__ == "__main__":
    args = get_args()
    
    # 获取当前文件路径
    current_file_path = __file__
    # 使用 os.path.basename() 函数获取文件名，然后使用 os.path.splitext() 函数分割文件名和后缀
    current_file_name = os.path.splitext(os.path.basename(current_file_path))[0]

    # 记录最大尝试次数
    attempts, max_attempts = 0, 3

    # 开始抓取
    logger.info(f"{'-'*20}{current_file_name} 开始抓取{'-'*20}")
    while attempts < max_attempts:
        try:
            get_content(args.start_date)
            break  # 如果代码成功执行，跳出循环
        except Exception as e:
            attempts += 1  # 增加尝试次数
            logger.error(f"{e}")
            time.sleep(2)
            if attempts == max_attempts:
                logger.error("已达到最大尝试次数，程序终止。")
            else:
                logger.info(f"当前重试次数{attempts}...")
    logger.info(f"{'-'*20}{current_file_name} 抓取完成{'-'*20}\n\n")