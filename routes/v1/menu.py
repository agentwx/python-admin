#!/usr/bin/env python
# -*- coding:UTF-8 -*-
'''
@Description: 菜单API
@Author: Zpp
@Date: 2019-09-10 16:16:54
@LastEditTime: 2020-05-07 09:52:22
@LastEditors: Zpp
'''
from flask import Blueprint, request
from collection.v1.menu import MenuModel
from ..token_auth import auth, validate_current_access
from libs.code import ResultDeal

route_menu = Blueprint('Menu', __name__, url_prefix='/v1/Menu')


@route_menu.route('/CreateMenu', methods=['POST'])
@auth.login_required
@validate_current_access
def CreateMenu():
    params = {
        'pid': request.form.get('pid', '0'),
        'title': request.form.get('title'),
        'path': request.form.get('path'),
        'icon': request.form.get('icon'),
        'mark': request.form.get('mark'),
        'sort': request.form.get('sort'),
        'component': request.form.get('component'),
        'componentPath': request.form.get('componentPath'),
        'name': request.form.get('name'),
        'cache': True if request.form.get('cache') == 'true' else False,
        'is_disabled': True if request.form.get('is_disabled') == 'true' else False
    }

    result = MenuModel().CreateMenuRequest(params)

    if type(result).__name__ == 'str':
        return ResultDeal(msg=result, code=-1)

    return ResultDeal(data=result)


@route_menu.route('/DelMenu', methods=['POST'])
@auth.login_required
@validate_current_access
def DelMenu():
    result = MenuModel().DelMenuRequest(menu_id=request.form.get('menu_id'))
    
    if type(result).__name__ == 'str':
        return ResultDeal(msg=result, code=-1)
        
    return ResultDeal(data=result)


@route_menu.route('/GetMenuToInterface', methods=['GET'])
@auth.login_required
@validate_current_access
def GetMenuToInterface():
    result = MenuModel().GetMenuToInterfaceRequest(menu_id=request.args.get('menu_id'))

    if type(result).__name__ == 'str':
        return ResultDeal(msg=result, code=-1)

    return ResultDeal(data=result)


@route_menu.route('/ModifyMenu', methods=['POST'])
@auth.login_required
@validate_current_access
def ModifyMenu():
    params = {
        'pid': request.form.get('pid', '0'),
        'title': request.form.get('title'),
        'path': request.form.get('path'),
        'icon': request.form.get('icon'),
        'mark': request.form.get('mark'),
        'sort': request.form.get('sort'),
        'component': request.form.get('component'),
        'componentPath': request.form.get('componentPath'),
        'name': request.form.get('name'),
        'cache': True if request.form.get('cache') == 'true' else False,
        'is_disabled': True if request.form.get('is_disabled') == 'true' else False
    }

    result = MenuModel().ModifyMenuRequest(menu_id=request.form.get('menu_id'), params=params)

    if type(result).__name__ == 'str':
        return ResultDeal(msg=result, code=-1)

    return ResultDeal(data=result)


@route_menu.route('/QueryMenuByParam', methods=['POST'])
@auth.login_required
@validate_current_access
def QueryMenuByParam():
    params = {}
    if request.form.get('is_disabled'):
        params['is_disabled'] = True if request.form.get('is_disabled') == 'true' else False
    if request.form.get('role_id'):
        params['role_id'] = request.form.get('role_id')
            
    result = MenuModel().QueryMenuByParamRequest(
        params=params, 
        is_interface=True if request.form.get('is_interface') == 'true' else False
    )

    if type(result).__name__ == 'str':
        return ResultDeal(msg=result, code=-1)

    return ResultDeal(data=result)
