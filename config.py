#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
config.py

設定ファイル conf.ini から
各種設定を読み込む
"""
import os
from distutils.sysconfig import get_python_lib
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
filepath = os.path.join(get_python_lib(),'conf.ini')
parser.readfp(open(filepath))

def get_option(section, opt):
    try: 
        return parser.get(section, opt)
    except Exception, err:
        return err
