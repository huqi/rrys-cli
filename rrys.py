#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''人人影视数据库前端'''

import getopt
import json
import logging
import sqlite3
import sys
from enum import IntEnum, unique

import pyperclip

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

@unique
class TEXT_COLOR(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    EXT_RED = 35
    EXT_BLUE = 36
    WHITE = 37

def print_highlight_text(str, color):
    print('\033[1;{}m {} \033[0m'.format(color, str))

def print_text_yellow(str):
    print_highlight_text(str, TEXT_COLOR.YELLOW)

def print_text_red(str):
    print_highlight_text(str, TEXT_COLOR.RED)

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

def show_info(i):
    info = i['DATA']['data']['info']
    print_text_yellow("==================================================")
    print_text_yellow("ID:%s" % i['ID'])
    print_text_yellow("URL:%s" % i['URL'])
    print_text_yellow("片名：%s" % i['CN_NAME'])
    print_text_yellow("原名：%s" % i['EN_NAME'])
    print_text_yellow("别名：%s" % i['ALIAS_NAME'])
    print_text_yellow("类别：%s" % info['channel_cn'])
    print_text_yellow("地区：%s" % info['area'])
    print_text_yellow("--------------------------------------------------")

def copy_to_clipboard(flag, addr):
    if not flag:
        return
    
    num = input("选择渠道：")
    pyperclip.copy(addr[int(num)])

def show(opt, info_arg):
    for i in info_arg:
        list = i['DATA']['data']['list']

        show_info(i)

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
                print_highlight_text("格式：%s" % o, TEXT_COLOR.GREEN)
                print_highlight_text("-------------", TEXT_COLOR.GREEN)
                for m in l['items'][o]:
                    if opt.get('episode') and opt['episode'] != m['episode']:
                        continue

                    print_text_red("片名：%s" % m['name'])
                    if m['files']:
                        addr = []
                        for k, j in enumerate(m['files']):
                            print_highlight_text('[%s]渠道：%s' % (k, j['way_cn']), TEXT_COLOR.BLUE)
                            print('下载地址：%s' % j['address'])
                            addr.append(j['address'])
                        copy_to_clipboard(opt.get('copy_flag'), addr)
                    else:
                        print('None')
                    print("\n")

                print("--------------------------------------------------\n\n")

def print_help():
    print('''
    用法示例：./rrys.py -n 我的天才女友 -l
             -l             显示下载链接
             -c             拷贝下载链接到剪切板
             -i             用影片id查询
             -f             指定格式
             -w             指定下载渠道
    ''')

def get_opt(argv):
    data ={'link_flag':False}

    try:
        opts, args = getopt.getopt(argv, "hlcf:i:n:s:e:w:", [
            "help",
            "list",
            "copy",
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
        elif opt in ('-c', '--copy'):
            data['copy_flag'] = True
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
