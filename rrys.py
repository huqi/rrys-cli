#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''人人影视数据库前端'''

import getopt
import json
import logging
import sqlite3
import sys
from enum import IntEnum, unique

logging.basicConfig(level=logging.INFO)

@unique
class INFO(IntEnum):
    ID = 0
    URL = 1
    NAME = 2
    EXPIRE = 3
    EXPIRE_CST = 4
    DATA = 5
    MAX = 6

def get_sql(data):
    sql = ""

    if 'id' in data:
        sql = 'select * from resource where id = %s' % data['id']
    elif 'name' in data:
        sql = 'select * from resource where name like "%{}%"'.format(data['name'])
    else:
        raise AssertionError

    logging.info("sql = %s" % sql)
    return sql

def search(data):
    logging.info("id={}, name={}, format={}, season={}, episode={}, way={}".format(
        data.get('id'),
        data.get('name'),
        data.get('format'),
        data.get('season'),
        data.get('episode'),
        data.get('way')
    ))

    sql = get_sql(data)
    conn = sqlite3.connect('yyets.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    db_value = cursor.fetchall()
    cursor.close()
    conn.close()

    return db_value

def db_value_to_info(value):
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

def join_str_list(header, list):
    str = header

    for i in list:
        str = str + i + ";"

    return str

def show(opt, info_arg):
    for i in info_arg:
        info = i['DATA']['data']['info']
        list = i['DATA']['data']['list']
        print("==================================================")
        print("ID:%s" % i['ID'])
        print("URL:%s" % i['URL'])
        print("片名：%s" % i['CN_NAME'])
        print("原名：%s" % i['EN_NAME'])
        print("别名：%s" % i['ALIAS_NAME'])
        print("类别：%s" % info['channel_cn'])
        print("地区：%s" % info['area'])
        print("--------------------------------------------------")

        if not opt['link_flag']:
            continue

        for l in list:
            formats = opt['format']

            if opt.get('season') and opt['season'] != l['season_num']:
                continue

            print(join_str_list("格式：", l['formats']))
            print('%s' % l['season_cn'])

            if 'ALL' in opt['format']:
                formats = l['formats']

            for o in formats:
                print("--------------------------------------------------")
                print("格式：%s" % o)
                for m in l['items'][o]:
                    if opt.get('episode') and opt['episode'] != m['episode']:
                        continue

                    print("片名：%s" % m['name'])
                    if m['files']:
                        for j in m['files']:
                            print('渠道：%s' % j['way_cn'])
                            print('下载地址：%s' % j['address'])
                    else:
                        print('None')

def print_help():
    print('''
    用法示例：./rrys.py 我的天才女友
    ''')

def get_opt(argv):
    data ={'link_flag':False}

    try:
        opts, args = getopt.getopt(argv, "hlf:i:n:s:e:w:", [
            "help",
            "list"
            "format=",
            "id=",
            "name=",
            "season=",
            "episode=",
            "way="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit()
        if opt in ('-l', '--link'):
            data['link_flag'] = True
        elif opt in ('-f', '--format'):
            data['format'] = arg
        elif opt in ('-i', '--id'):
            data['id'] = arg
        elif opt in ('-n', '--name'):
            data['name'] = arg
        elif opt in ('-s', '--season'):
            data['season'] = arg
        elif opt in ('-e', '--episode'):
            data['episode'] = arg
        elif opt in ('-w', '--way'):
            data['way'] = arg

    return data

def check_opt(opt):
    if not opt:
        return False

    if 'name' not in opt and 'id' not in opt:
        return False

    return True

def opt(argv):
    opt = get_opt(argv)

    if check_opt(opt):
        return opt

def default_opt(opt):
    if not opt.get('format'):
        opt['format'] = ['MP4']

    return opt

def main(argv):
    opt = get_opt(argv)

    if not check_opt(opt):
        print_help()
        sys.exit(3)

    opt = default_opt(opt)
    db_value = search(opt)
    info = db_value_to_info(db_value)
    show(opt, info)

if __name__ == "__main__":
    main(sys.argv[1:])
