# -*- coding:utf-8 -*-
import requests
import datetime
import time
import sys
import io
import re
import argparse
from bs4 import BeautifulSoup
import random
import json
import sys 
sys.path.extend(['.', '..'])

from utils import sleep_time, title_pattern, content_pattern, write_file, now, MyHeaders, logger, timeout

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

GOVERMENT = "国家工信部"


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
    headers = {'User-Agent': random.choice(MyHeaders)}
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'utf-8'
    
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
    continue_count = 0
    while page_turning:
        logger.info(f"当前页：{page_num}")

        # 访问链接
        url_index = f"https://www.miit.gov.cn/search-front-server/api/search/info?websiteid=110000000000000&scope=basic" \
            f"&q=&pg=10&cateid=57&pos=title_text%2Cinfocontent%2Ctitlepy&_cus_eq_typename=%E9%80%9A%E7%9F%A5" \
            f"&dateField=deploytime&level=6&p={page_num}"
        try:
            response = get_response(url_index)

            # 解析json
            json_data = json.loads(response.text)
            data_results = json_data['data']['searchResult']['dataResults']
            if data_results is None and continue_count < 3:
                continue_count += 1
                continue
        except TypeError:
            time.sleep(2)
            if continue_count < 3:
                continue_count += 1
                continue

        for data in data_results:
            data_ = data['data']

            # 找出符合要求的时间以及标题
            date = data_.get("jsearch_date", "").strip().replace("\n", '')
            if date < start_date:
                if page_num == 1:      # 首页前几条可能不是最新的
                    continue
                page_turning = False
                break
            title = data_.get("title", "").strip().replace("\n", '')
            if re.search(title_pattern, title):  # 匹配标签关键字
                logger.info(f"{title}\t{date}")
                url_list.append('https://www.miit.gov.cn' + data_.get('url'))      # 需要拼接url
                date_list.append(date)
                title_list.append(title)

        # 进行翻页查找
        if data_results:
            page_num += 1
            # 随机睡眠
            time.sleep(sleep_time)
        else:
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
    write_file(result, now, GOVERMENT, "国家级")


if __name__ == "__main__":
    args = get_args()
    
    logger.info(f"{'-'*20}{GOVERMENT}开始抓取{'-'*20}")
    try:
        get_content(args.start_date)
    except Exception as e:
        logger.error(f"{e}")
    logger.info(f"{'-'*20}{GOVERMENT}抓取完成{'-'*20}\n\n")
