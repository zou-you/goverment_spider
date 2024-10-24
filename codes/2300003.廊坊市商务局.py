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
import html
import random
import json
import sys 
sys.path.extend(['.', '..'])

from utils import sleep_time, title_pattern, content_pattern, write_file, now, MyHeaders, logger, timeout

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

GOVERMENT = "廊坊市商务局"


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


def get_response(url):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": ".AspNetCore.Antiforgery.hndGADITtl0=CfDJ8PEjZVoteS5Hr_I0C6SOuMhQwd5T-d6-BE2hNTMbbovbjcG-90TtAlIMUcW9i_4OwY54o_Hq7aK5q_cE1O44GCfZTAk19EVdoGIYb8fdHm96_76kpXHIPGcqmkkXwCswrDAkOjQlA3aFTHljguD3Dhk",
        "Host": "zfxxgk.lf.gov.cn",
        "Origin": "https://zfxxgk.lf.gov.cn",
        "Referer": "https://zfxxgk.lf.gov.cn/GKNR/gknr_depart?deptId=39506",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    post_data = {
        "indexPage": 1,
        "pageSize": 15,
        "deptId": 39506,
        "menuId": 0
    }

    # 发送请求
    response = requests.post(url, headers=headers, data=post_data)

    return response


def get_bs(url):
    headers = {'User-Agent': random.choice(MyHeaders)}
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'utf-8'
    bs = BeautifulSoup(response.text, 'html5lib')

    return bs

@timeout(3600)
def get_content(start_date=now):

    url_list, date_list, title_list = [], [], []
    page_turning = True  # 是否需要翻页
    page_num = 1
    while page_turning:
        logger.info(f"当前页：{page_num}")
        # 访问链接
        url_index = f"https://zfxxgk.lf.gov.cn/GKNR/PageData"
        response = get_response(url_index)
        if response.status_code != 200:
            raise ConnectionError("请求失败……") 
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取信息
        results = []
        for li in soup.find_all('li'):
            date = li.find('span').text.strip('[]')  # 提取日期并去除中括号
            if date < start_date:
                if page_num == 1:      # 首页前几条可能不是最新的
                    continue
                page_turning = False
                break

            a_tag = li.find('a')
            title = html.unescape(a_tag['title']).strip().replace("\n", '').replace("\r", '')   # 解码title
            if re.search(title_pattern, title):  # 匹配标签关键字
                logger.info(f"{title}\t{date}")
                href = a_tag['href'].strip()
                if not href.startswith('http'):
                    href = 'https://zfxxgk.lf.gov.cn' + href
                url_list.append(href)
                date_list.append(date)
                title_list.append(title)
            results.append({'href': href, 'title': title, 'date': date})

        # 不进行翻页查找
        break

    result = ''
    # 进入详情页查找关键字
    for index, url_detail in enumerate(url_list):
        bs = get_bs(url_detail)
        text = bs.get_text(strip=True)
        match_res = set(content_pattern.findall(text))
        if match_res:
            result += f"{GOVERMENT}\t{','.join(list(match_res))}\t{title_list[index]}\t{date_list[index]}\t{url_detail}\n"

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