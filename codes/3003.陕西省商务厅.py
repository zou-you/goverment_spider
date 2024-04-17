# -*- coding:utf-8 -*-
import requests
import datetime
import time
import sys
import io
import re
import random
import argparse
from bs4 import BeautifulSoup

sys.path.extend(['.', '..'])

from utils import sleep_time, title_pattern, content_pattern, write_file, now, MyHeaders, logger, timeout

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

GOVERMENT = "陕西省商务厅"


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
    response.encoding = 'gbk'
    bs = BeautifulSoup(response.text, 'html5lib')

    return bs

@timeout(3600)
def get_content(start_date=now):

    url_index = "http://sxdofcom.shaanxi.gov.cn/newstyle/pub_newschannel.asp?chid=100258"

    url_list, date_list, title_list = [], [], []
    page_turning = True  # 是否需要翻页
    page_num = 1
    while page_turning:
        logger.info(f"当前页：{page_num}")

        # 访问链接
        bs = get_bs(url_index)
        text_list = bs.select(".morelmr div ul li a")
        time_list = bs.select('.morelmr [style="float:right"]')

        # 找出符合要求的时间以及标题
        for text, tim in zip(text_list, time_list):
            date = tim.get_text(strip=True).split(' ')[0]
            if date < start_date:
                if page_num == 1:      # 首页前几条可能不是最新的
                    continue
                page_turning = False
                break

            url_list.append("http://sxdofcom.shaanxi.gov.cn/" + text['href'])
            date_list.append(date)

        # 进行翻页查找
        if page_num != 5:
            page_num += 1
            url_index = f"http://sxdofcom.shaanxi.gov.cn/newstyle/pub_newschannel.asp?Page={page_num}&chid=100258"
            # 随机睡眠
            time.sleep(sleep_time)
        else:
            break

    result = ''
    # 进入详情页查找关键字
    for index, url_detail in enumerate(url_list):
        bs = get_bs(url_detail)
        title = bs.find('div', class_='zbt').get_text(strip=True).strip().replace('·', '').replace('\n', '')
        if title_pattern.search(title):  # 匹配标签关键字
            logger.info(f"{title}\t{date_list[index]}")
            text = bs.get_text(strip=True)
            match_res = set(content_pattern.findall(text))
            if match_res:
                result += f"{GOVERMENT}\t{','.join(list(match_res))}\t{title}\t{date_list[index]}\t{url_detail}\n" 
            # 随机睡眠
            time.sleep(sleep_time)

    # 写入文件
    write_file(result, now, GOVERMENT, "省级")



if __name__ == "__main__":
    args = get_args()
    
    logger.info(f"{'-'*20}{GOVERMENT}开始抓取{'-'*20}")
    try:
        get_content(args.start_date)
    except Exception as e:
        logger.error(f"{e}")
    logger.info(f"{'-'*20}{GOVERMENT}抓取完成{'-'*20}\n\n")