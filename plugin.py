# -*- coding: utf-8 -*-
#########################################################
# 고정영역
#########################################################
# python
import os
import sys
import traceback
import json
import re

# third-party
import requests
from flask import Blueprint, request, Response, render_template, redirect, jsonify, url_for, send_from_directory
from flask_login import login_required
from flask_socketio import SocketIO, emit, send

# sjva 공용
from framework.logger import get_logger
from framework import app, db, scheduler, socketio, path_app_root
from framework.util import Util, AlchemyEncoder
from system.logic import SystemLogic
            
# 패키지
package_name = __name__.split('.')[0]
logger = get_logger(package_name)
from .logic import Logic
from .model import ModelSetting



blueprint = Blueprint(package_name, package_name, url_prefix='/%s' %  package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

def plugin_load():
    Logic.plugin_load()

def plugin_unload():
    Logic.plugin_unload()

plugin_info = {
    'version' : '0.1.0.2',
    'name' : u'torrssen2',
    'category_name' : 'launcher',
    'icon' : '',
    'developer' : 'soju6jan',
    'description' : u'torrssen2 런처<br><a href="https://github.com/tarpha/torrssen2" target="_blank">torrssen2 Git</a><br><br>나스당 TRPE님이 개발하신 torrssen2를 설치 & 실행하는 런처입니다.<br>도커 이외의 환경에서는 JAVA 실행환경을 따로 설치해야합니다.',
    'home' : 'https://github.com/soju6jan/launcher_torrssen2',
    'more' : '',
}
#########################################################

# 메뉴 구성.
menu = {
    'main' : [package_name, u'torrssen2'],
    'sub' : [
        ['setting', u'설정'], ['log', u'로그']
    ], 
    'category' : 'launcher',
}  

#########################################################
# WEB Menu
#########################################################
@blueprint.route('/')
def home():
    return redirect('/%s/setting' % package_name)


@blueprint.route('/<sub>')
@login_required
def detail(sub): 
    if sub == 'setting':
        setting_list = db.session.query(ModelSetting).all()
        arg = Util.db_list_to_dict(setting_list)
        arg['status'] = str(Logic.current_process is not None)
        arg['is_installed'] = 'Installed' if Logic.is_installed() else 'Not Installed'
        return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    elif sub == 'log':
        return render_template('log.html', package=package_name)
    return render_template('sample.html', title='%s - %s' % (package_name, sub))


@blueprint.route('/ajax/<sub>', methods=['GET', 'POST'])
@login_required
def ajax(sub):
    logger.debug('AJAX %s %s', package_name, sub)
    if sub == 'setting_save':
        try:
            ret = Logic.setting_save(request)
            return jsonify(ret)
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    elif sub == 'status':
        try:
            todo = request.form['todo']
            if todo == 'true':
                if Logic.current_process is None:
                    Logic.scheduler_start()
                    ret = 'execute'
                else:
                    ret =  'already_execute'
            else:
                if Logic.current_process is None:
                    ret =  'already_stop'
                else:
                    Logic.scheduler_stop()
                    ret =  'stop'
            return jsonify(ret)
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    elif sub == 'install':
        try:
            Logic.install()
            ret = {}
            return jsonify({})
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


