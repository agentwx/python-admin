#!/usr/bin/env python
# -*- coding:UTF-8 -*-
'''
@Description: 
@Author: Zpp
@Date: 2019-09-05 16:07:19
@LastEditTime: 2020-03-31 09:47:09
@LastEditors: Zpp
'''
from flask import Flask
from conf.setting import server_info
import models
import routes
import services
import logs
import logging


def create_app():
    app = Flask(__name__)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)
    return app


logs.init_app()
# 初始化
logging.info(u'-----初始化项目-----')
app = create_app()
logging.info('--------------------')

try:
    logging.info(u'------启动成功------')
    app.run(port=server_info['port'], host=server_info['host'])
except Exception as e:
    print e
    logging.error(u'------启动失败------')
