import os
from datetime import datetime

def get_latest_modification_date(folder_path):
    latest_time = 0

    # 遍历文件夹及所有子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            mod_time = os.path.getmtime(file_path)
            if mod_time > latest_time:
                latest_time = mod_time

    if latest_time == 0:
        return None  # 文件夹中没有文件

    # 转换为 年-月-日 格式
    return datetime.fromtimestamp(latest_time).strftime("%Y-%m-%d")

# 示例使用
folder = "E:\\学习\\研究生0\\科研\\写的论文\\ITSC相关\\01.投稿\\代码\\pneuma2\\codes"
latest_mod_date = get_latest_modification_date(folder)
if latest_mod_date:
    print("最近修改日期：", latest_mod_date)
else:
    print("文件夹中没有文件。")
