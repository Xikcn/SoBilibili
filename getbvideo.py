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
                "Cookie": "",
                # 切换自己的
                "User-Agent": ""
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