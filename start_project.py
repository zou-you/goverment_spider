# -*- coding:utf-8 -*-
import os
import re
from datetime import datetime
import argparse
from pathlib import Path

import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler

from utils import get_date, REGIONS, logger


# 定时任务
def schedule_daily_task(daily_task, task_args=None, hour=17, minute=20):
    # 创建一个调度器对象
    scheduler = BlockingScheduler()

    # 添加每日定时任务，在每天指定小时和分钟执行
    scheduler.add_job(daily_task, 'cron', args=task_args, hour=hour, minute=minute, max_instances=3)

    # 启动调度器
    scheduler.start()


def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--start_date",
        type=str,
        default=None,
        help="The start time of the spider",
    )

    parser.add_argument(
        "--only_start_date",
        action='store_true',
        help="Only the start date is recorded",
    )

    parser.add_argument(
        "--only_save_file",
        action='store_true',
        help="Save only the resulting file",
    )

    parser.add_argument(
        "--timed_task",
        action='store_true',
        help="Timed task",
    )

    return parser.parse_args()

# 写入excel
def data2Excel(now_time_date, year_month, datas, start_date, only_start_date=False):
    # 创建一个ExcelWriter对象
    if now_time_date != start_date:
        if only_start_date:
            # 只取指定日期
            filename = f'政策信息采集_{start_date}.xlsx'
        else:
            # 指定日期范围
            filename = f'政策信息采集_{start_date}_{now_time_date}.xlsx'
    else:
        filename = f'政策信息采集_{now_time_date}.xlsx'
    excel_writer = pd.ExcelWriter(f'./xls_files/{year_month}/{filename}', engine='xlsxwriter')

    # 创建国家、省、市df
    columns = ['部门名称', '类型', '标题', '日期', '链接']
    for region in REGIONS:
        df = pd.DataFrame(datas[region], columns=columns)
        if only_start_date:
            df = df[df['日期'] == start_date]
        df.to_excel(excel_writer, sheet_name=region, index=False)

    # 筛选指定日期
    # df1 = df1[df1["日期"] >= start_date]
    # df2 = df2[df2["日期"] >= start_date]
    # df3 = df3[df3["日期"] >= start_date]
    # df4 = df4[df4["日期"] >= start_date]

    # 保存Excel文件
    excel_writer.close()


# 读取txt文件
def read_txt_file(file_name, data_list=[]):
    data_list = data_list
    try:
        with open(file_name, 'r', encoding='utf-8', newline='') as f:
            lines = f.readlines()
            for j in range(0, len(lines)):
                item = lines[j]
                item = item.replace('\r', '').replace('\n', '').split('\t')
                data_list.append(item)
    except:
        pass
    return data_list


def crate_xlsx_file(now, year_month, start_date, only_start_date=False):
    data_all = {}
    for region in REGIONS:
        data_list = []
        path_list = Path(f"files/{year_month}/{now}/{region}")
        for path in sorted(path_list.iterdir()):
            data_list = read_txt_file(path, data_list=data_list)
        data_all[region] = data_list

    data2Excel(now, year_month, data_all, start_date, only_start_date)


def start(start_date, only_start_date=False, only_save_file=False):
    now, year_month = get_date(yesterday=True)    # 定时任务，这里需要每天计算
    if not start_date:
        start_date = now

    logger.info(f'开始爬取时间 {start_date}')
    code_path = "./codes/"
    file_list = os.listdir(code_path)
    py_file = []

    # 转换成 (数字部分, 原始文件名) 的元组列表
    for item in file_list:
        num = int(re.search(r'\d+', item).group())
        py_file.append((num, item))
    
    # 使用 sorted 进行排序
    py_file = sorted(py_file)

    # 提取排序后的文件名
    py_file_sort = [filename for _, filename in py_file]    

    # 运行爬虫文件
    if not only_save_file:
        logger.info(f'运行文件列表： {py_file_sort}')
        for file in py_file_sort:
            os.system(f'python3 codes/{file} --start_date {start_date}')

    # 采集完成，写入excel
    crate_xlsx_file(now, year_month, start_date, only_start_date)

    logger.info(f'*****爬取完成*****\n\n\n')


if __name__ == "__main__":
    args = get_args()
    if args.timed_task:
        print("定时任务启动")
        schedule_daily_task(start, task_args=(args.start_date, ), hour=1, minute=0)
    else:
        start(args.start_date, args.only_start_date, args.only_save_file)
