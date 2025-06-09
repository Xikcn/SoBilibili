import json
import requests
import pandas as pd
import time
import os
import csv
from datetime import datetime


# 初始化CSV文件并写入表头
def init_csv_file(filename):
    if not os.path.exists(filename):
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # 定义CSV表头
            header = [
                "期数", "标题", "描述", "封面图片", "视频链接",
                "UP主昵称", "点赞数", "收藏数", "评论数",
                "分类", "二级分类", "三级分类"
            ]
            writer.writerow(header)


# 追加数据到CSV
def append_to_csv(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            data["期数"],
            data["标题"],
            data["描述"],
            data["封面图片"],
            data["视频链接"],
            data["UP主昵称"],
            data["点赞数"],
            data["收藏数"],
            data["评论数"],
            data["分类"],
            data["二级分类"],
            data["三级分类"]
        ])


# 主程序
if __name__ == "__main__":
    # 生成带日期的文件名
    today = datetime.now().strftime("%Y%m%d")
    csv_filename = f"bilibili_hot_videos_{today}.csv"

    # 初始化CSV文件
    init_csv_file(csv_filename)

    # 循环爬取数据
    for num in range(1, 325):
        try:
            url = f"https://api.bilibili.com/x/web-interface/popular/series/one?number={num}"
            headers = {
                "Cookie": "buvid3=9B6DBB6B-48BB-8AB5-029C-9CF6E337AA2E92177infoc; b_nut=1729610592; _uuid=BF6DDAA6-BF94-7CB3-2A35-C53FD110972D692309infoc; buvid4=26B60AAC-798D-59AC-41E7-8BE9B6D553BE92674-024102215-NDRDuS5Uzfh%2FwAzkIDIAWA%3D%3D; rpdid=|(J~J)J|~|JY0J'u~kmYlJJuk; enable_web_push=DISABLE; LIVE_BUVID=AUTO8517300366292252; CURRENT_BLACKGAP=0; buvid_fp_plain=undefined; hit-dyn-v2=1; enable_feed_channel=ENABLE; fingerprint=8cbe35576255ca5f2344af8553ea204a; buvid_fp=0afb8a5e48595852476c9810e7e297e6; bp_t_offset_513224697=1065224534484844544; CURRENT_QUALITY=116; home_feed_column=5; browser_resolution=1699-911; PVID=1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDk1MjMwNTMsImlhdCI6MTc0OTI2Mzc5MywicGx0IjotMX0.0D0iJYbIWgKI6bTiCfh8qC4ur-0H4-Yv2mRuZgm8rhc; bili_ticket_expires=1749522993; b_lsid=843710AED_1974D4CF583; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; CURRENT_FNVAL=4048; bp_t_offset_3546883695839314=1075952112954769408; header_theme_version=OPEN; SESSDATA=6d738ab9%2C1764905568%2Cb0dd9%2A61CjCwABVXmzCQTf5xC79SNdEV8tuybJWhL0n1EB4FwIneCRv6Am5QCD29fgDk8KZrBJ8SVlhieGpieWFKVVdvLUxhaGFTMEZWNGtPRG5mdU54MHNiX2Z0elVSbkhoRWhlenE0RkZOZi1YOEVuZVhRRjZpMlFCckxOWlRRYTRWTXJCd0d2ZEY0MDNBIIEC; bili_jct=628bc26f97f03cca33e964bab011c507; DedeUserID=3546883695839314; DedeUserID__ckMd5=1c2aadceb4dbe42d; sid=4ips1203",
                # 切换自己的
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
                # 切换自己的
            }

            # 发送请求
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            response_json = response.json()

            # 检查响应状态
            if response_json.get("code") != 0:
                print(f"第{num}期请求失败，错误代码: {response_json.get('code')}")
                continue

            # 保存原始JSON文件
            json_filename = f"bilibili_hot_{num}.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(response_json, f, ensure_ascii=False, indent=2)

            # 提取需要的数据
            weekly_number = response_json["data"]["config"]["number"]
            for item in response_json["data"]["list"]:
                data_row = {
                    "期数": weekly_number,
                    "标题": item["title"],
                    "描述": item["desc"],
                    "封面图片": item["pic"],
                    "视频链接": item["short_link_v2"],
                    "UP主昵称": item["owner"]["name"],
                    "点赞数": item["stat"]["like"],
                    "收藏数": item["stat"]["favorite"],
                    "评论数": item["stat"]["reply"],
                    "分类": item["tname"],
                    "二级分类": item["tnamev2"],
                    "三级分类": item["pid_name_v2"]
                }
                # 立即追加到CSV
                append_to_csv(data_row, csv_filename)

            print(f"第{num}期数据已成功追加到{csv_filename}")

        except Exception as e:
            print(f"第{num}期处理出错: {str(e)}")
            # 即使出错，已处理的数据已保存

        finally:
            time.sleep(3)  # 请求间隔

    print(f"所有数据已保存到{csv_filename}")