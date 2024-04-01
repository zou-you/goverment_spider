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

GOVERMENT = "南山区企业服务综合平台"


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
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Authorization": "YmVhcmVyRGlzcGVuc2U=",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "69",
        "Content-Type": "application/json",
        "Cookie": "_gscu_1535588677=10838278ixkynv15; _gscbrs_1535588677=1; _gscs_1535588677=10838278crcvud15|pv:9",
        "Host": "www.inanshan.org.cn",
        "Origin": "https://www.inanshan.org.cn",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "token": "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVkIjoxNzEwODM4MzEzMjYwLCJleHAiOjE3MTE0NDMxMTMsImluZm8iOnsiaWQiOjE3NTUyNzMsImNyZWRpdENvZGUiOiI5MTQ0MDMwMDYxODgxNTU3ODMiLCJ1c2VyQ29kZSI6Ijg0MjA5ZDQ1LTQzMmEtNDc3OS1hZGY1LWM0NGNjNGFhOGQ5YiIsInR5cGUiOjEsImFnZW50IjoxLCJlbnRlcnByaXNlTmFtZSI6IuW6t-S9s-mbhuWbouiCoeS7veaciemZkOWFrOWPuCIsImZsYWciOiJmZWF0dXJlOnRva2VuOjExOTE0NDAzMDA2MTg4MTU1NzgzMTg0MjA5ZDQ1LTQzMmEtNDc3OS1hZGY1LWM0NGNjNGFhOGQ5YiIsImxvZ2luVHlwZSI6MSwiYWNjb3VudCI6bnVsbCwicm9sZXMiOm51bGx9fQ.XC6M-rZScQRu932d4cEAgy27o3rYt2IyZ08Ct2Oau-4"
        }
    post_data = {"typeId": "17", "sortType": 0, "searchKey": "", "pageNum": 1, "pageSize": 100}
    response = requests.post(url, headers=headers, data=json.dumps(post_data))
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

    content_list, date_list, title_list, id_list = [], [], [], []
    page_turning = True  # 是否需要翻页
    page_num = 1
    while page_turning:
        logger.info(f"当前页：{page_num}")
        # 访问链接
        url_index = f"https://www.inanshan.org.cn/inanshan-govpolicy/affiche-information/getInformationPage"
        response = get_response(url_index)
        if response.status_code != 200:
            raise ConnectionError("请求失败……") 
        # 解析json
        json_data = json.loads(response.text)
        records = json_data.get("data")['records']
        for record in records:
            
            # 找出符合要求的时间以及标题
            date = record.get('releaseData', '')
            if date < start_date:
                if page_num == 1:      # 首页前几条可能不是最新的
                    continue
                page_turning = False
                break
            title = record.get('title', '').strip().replace("\n", '')
            if re.search(title_pattern, title):  # 匹配标签关键字
                logger.info(f"{title}\t{date}")
                content_list.append(record.get("content", ""))      
                date_list.append(date)
                title_list.append(title)
                id_list.append(record.get("id", ""))

        # 不进行翻页查找
        break

    result = ''
    # 进入详情页查找关键字
    for index, content in enumerate(content_list):
        match_res = set(content_pattern.findall(content))
        if match_res:
            url_detail = f"https://www.inanshan.org.cn/zjsbtzgg/detail?id={id_list[index]}&parentId=enRmdy16Y2Z3LXpqc2I%3D&typeName=详情页&typeId=17"
            result += f"{GOVERMENT}\t{','.join(list(match_res))}\t{title_list[index]}\t{date_list[index]}\t{url_detail}\n"

        # 随机睡眠
        # time.sleep(sleep_time)

    # 写入文件
    write_file(result, now, GOVERMENT, "南山区")


if __name__ == "__main__":
    args = get_args()
    
    logger.info(f"{'-'*20}{GOVERMENT}开始抓取{'-'*20}")
    try:
        get_content(args.start_date)
    except Exception as e:
        logger.error(f"{e}")
    logger.info(f"{'-'*20}{GOVERMENT}抓取完成{'-'*20}\n\n")
