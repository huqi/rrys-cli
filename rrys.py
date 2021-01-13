#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''人人影视数据库前端'''

import sys
import json
import logging
import sqlite3
from enum import IntEnum, unique

@unique
class INFO(IntEnum):
    ID = 0
    URL = 1
    NAME = 2
    EXPIRE = 3
    EXPIRE_CST = 4
    DATA = 5
    MAX = 6

def search(name):
    logging.info("search name = %s" % name)
    sql = 'select * from resource where name like "%{}%"'.format(name)
    logging.info("sql = %s", sql)

    conn = sqlite3.connect('yyets.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    value = cursor.fetchall()
    cursor.close()
    conn.close()
    return value

def refresh_data(value):
    list = []
    count = len(value)
    logging.info("result count = %d" % count)

    for d in value:
        data = {}
        data['ID'] = d[INFO.ID]
        data['URL'] = d[INFO.URL]
        name = d[INFO.NAME].split('\n')
        data['CN_NAME'] = name[0]
        data['EN_NAME'] = name[1]
        data['ALIAS_NAME'] = name[2]
        data['EXPIRE'] = d[INFO.ID]
        data['EXPIRE_CST'] = d[INFO.EXPIRE_CST]
        data['DATA'] = json.loads(d[INFO.DATA])
        list.append(data)

    return list
    #print(list)

    # print(value[0])
    #with open('result.txt', 'w') as f:
    #    f.write(value)
    # info = json.loads(value)
    # print(type(info))

def print_result(list):
    if not list:
        print("没有找到该影片！")

    for i in list:
        info = i['DATA']['data']['info']
        season_list = i['DATA']['data']['list']
        print("==========")
        print("中文片名：%s" % i['CN_NAME'])
        print("英文片名：%s" % i['EN_NAME'])
        print("别名：%s"% i['ALIAS_NAME'])
        print("频道：%s" % info['channel_cn'])
        for j in season_list:
            print("%s：" % j['season_cn'])
            print("----------")
            if 'MP4' in j['formats']:
                logging.info("MP4 Founded!")
                mp4_set = j['items']['MP4']
                for k in mp4_set:
                    files = k['files']
                    print(k['name'])
                    print(files[0]['address'])
                    print("----------")
            else:
                print("没有找到MP4格式文件！")
            print("==========")

def print_help():
    print('''
    用法示例：./rrys.py 我的天才女友
    ''')

def main():
    logging.basicConfig(level=logging.ERROR)

    if len(sys.argv) < 2:
       print_help()
       exit(-1)

    value = search(sys.argv[1])
    list = refresh_data(value)
    print_result(list)

if __name__ == "__main__":
    main()