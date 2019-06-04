"""
按一二级分类采集，全站采集企鹅风讯的APP数据
"""


# 一级分类，分为游戏和应用两大类
import json
import re

import requests
from lxml import etree

cate = [
    {'maintypename': '应用', 'main_type_id': 2, 'codename': 'a'},
    {'maintypename': '游戏', 'main_type_id': 1, 'codename': 'g'}
]
# 请求URL，获取分类的字母表示 codename 后拼接获取完整的链接
base_url = 'https://fsight.qq.com/AllGames/{}'
# 虽然有应用和游戏两大类别之分，但是请求任意一个就可以获取完整的 platform 和 type 分类
url = "https://fsight.qq.com/AllGames/g"
# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}


def platform_type():
    """
    获取所有的平台分类以及所有的分类
    :return:
    """
    # 用于保存每一个链接的信息
    info = dict()
    # 发起请求
    result = requests.get(url, headers=headers)
    # 获取HTML
    html = parse_response(result)
    print("查看获取的html：", html)
    script = html.xpath('//script/text()')[-1]
    # 将匹配的数据转换成python字典
    data = json.loads(re.findall(r'var g_data = ({.*?});', script)[0], encoding='utf-8')
    # 获取所有的平台
    allplatforms = data.get('allplatforms')
    alltypes = data.get('alltypes')
    for platform in allplatforms:
        pName = platform['pName']
        platformId = platform['platformId']
        for type_ in alltypes.values():
            type_id = type_['type_id']
            type_name = type_['type_name']
            main_type_id = type_['main_type_id']
            if main_type_id == 1:
                info['maintypename'] = cate[-1]['maintypename']
                info['pName'] = pName
                info['platformId'] = platformId
                info['type_id'] = type_id
                info['type_name'] = type_name
            if main_type_id == 2:
                info['maintypename'] = cate[0]['maintypename']
                info['pName'] = pName
                info['platformId'] = platformId
                info['type_id'] = type_id
                info['type_name'] = type_name
            # 将每一条信息写入文件中
            record_result(info)


def record_result(data):
    """
    将结果写入文件
    :param data:
    :return:
    """
    path = r'F:\project\whole_app\wandoujia\wetest.json'
    with open(path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def parse_response(res):
    """
    将获取的响应转换为HTML
    :param res: 响应（text）
    :return: HTML
    """
    try:
        if res.status_code == 200:
            # 测试时使用
            print("查看获取的响应<login-parse_response>：", res.text)
            res.encoding = res.apparent_encoding
            return etree.HTML(res.text, etree.HTMLParser())
        else:
            print("响应的状态码不是200")
            return False
    except Exception as e:
        print(e)


# 测试代码
if __name__ == "__main__":
    platform_type()