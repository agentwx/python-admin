#!/usr/bin/env python
# -*- coding:UTF-8 -*-
'''
@Description:
@Author: Zpp
@Date: 2019-09-09 10:02:39
@LastEditTime: 2020-04-29 14:50:08
@LastEditors: Zpp
'''
from flask import request
from models import db
from models.system import Admin, Role, Menu, LoginLock, Interface
from conf.setting import Config, base_info, default
import uuid
import datetime
import copy


class AdminModel():
    def QueryAdminByParamRequest(self, params, page=1, page_size=20, order_by='id'):
        '''
        管理员列表
        '''
        s = db.session()
        try:
            data = {}
            for i in ['role_id', 'is_disabled']:
                if params.has_key(i):
                    data[i] = params[i]

            result = Admin.query.filter_by(**data).order_by(order_by).paginate(page, page_size, error_out=False)

            return {'data': [value.to_json() for value in result.items], 'total': result.total}
        except Exception as e:
            print e
            return str(e.message)

    def CreateAdminRequest(self, params):
        '''
        新建管理员
        '''
        s = db.session()
        try:
            role = s.query(Role).filter(Role.role_id == params['role_id']).first()

            if not role:
                return str('角色不存在')

            if role.mark == default['role_mark']:
                return str('不能设为为超级管理员')

            admin = s.query(Admin).filter(Admin.username == params['username']).first()

            if admin:
                return str('管理员已存在')

            item = Admin(
                admin_id=uuid.uuid4(),
                username=params['username'],
                password=Config().get_md5(params['password']),
                sex=int(params['sex']),
                email=params['email'],
                nickname=params['nickname'],
                avatarUrl=params['avatarUrl'],
                role_id=params['role_id'],
                is_disabled=params['is_disabled']
            )
            s.add(item)
            role.admins.append(item)
            s.commit()
            return True
        except Exception as e:
            s.rollback()
            print e
            return str(e.message)

    def GetAdminRequest(self, username, password):
        '''
        登录管理员
        '''
        s = db.session()
        try:
            admin = s.query(Admin).filter(Admin.username == username).first()
            if not admin:
                return str('管理员不存在')

            is_lock = s.query(LoginLock).filter(LoginLock.user_id == admin.admin_id).first()
            if is_lock and is_lock.number >= base_info['lock_times']:
                if datetime.datetime.now() < is_lock.lock_time:
                    return str('账号锁定中, 请在%s分钟后重试' % (is_lock.lock_time - datetime.datetime.now()).minute)

            if admin.password != Config().get_md5(password):
                number = 1
                if is_lock:
                    number = is_lock.number + 1
                    if number >= base_info['lock_times']:
                        add_minutes = (number - base_info['lock_times']) + 1
                        is_lock.lock_time = datetime.datetime.now() + datetime.timedelta(minutes=add_minutes)
                    is_lock.number = number
                else:
                    s.add(LoginLock(
                        lock_id=uuid.uuid4(),
                        user_id=admin.admin_id,
                        flag=False,
                        number=number,
                        ip=request.headers['X-Real-Ip'] if request.headers.has_key('X-Real-Ip') else request.remote_addr
                    ))
                s.commit()
                if number - base_info['lock_times'] == 0:
                    return str('密码不正确, 您的账号已经被锁定, 请在%s分钟后重试' % add_minutes)
                else:
                    return str('密码不正确, 还有%s次机会' % (base_info['lock_times'] - number))

            if admin.is_disabled:
                return str('管理员被禁用')

            menu = []
            interface = []

            role = s.query(Role).filter(Role.role_id == admin.role_id).first()
            if role:
                if role.mark == default['role_mark']:
                    interface = [value.to_json() for value in s.query(Interface).all()]
                    menu = [value.to_json() for value in s.query(Menu).all()]
                else:
                    for i in role.menus.order_by(Menu.sort, Menu.id):
                        menu.append(i.to_json())
                    for i in role.interfaces:
                        interface.append(i.to_json())

            user = copy.deepcopy(admin.to_json())
            del user['id']
            del user['create_time']
            del user['update_time']
            user['mark'] = role.mark

            # 登录成功删除掉原来的锁定记录
            if is_lock:
                s.delete(is_lock)
                s.commit()
                    
            return {
                'menus': menu,
                'interface': interface,
                'user': user
            }
        except Exception as e:
            print e
            return str(e.message)

    def ModifyAdminRequest(self, admin_id, params):
        '''
        修改管理员信息
        '''
        s = db.session()
        try:
            admin = s.query(Admin).filter(Admin.admin_id == admin_id).first()
            if not admin:
                return str('管理员不存在')
            if admin.is_disabled:
                return str('管理员被禁用')
            
            role = s.query(Role).filter(Role.role_id == params['role_id']).first()

            if not role:
                return str('角色不存在')

            if admin.role_id != role.role_id and role.mark == default['role_mark']:
                return str('不能设为为超级管理员')

            admin.nickname = params['nickname']
            admin.sex = params['sex']
            admin.role_id = params['role_id']
            admin.avatarUrl = params['avatarUrl']
            admin.email = params['email']
            admin.is_disabled = params['is_disabled']
            if params['password'] != admin.password:
                admin.password = Config().get_md5(params['password'])

            user = copy.deepcopy(admin.to_json())
            del user['id']
            del user['create_time']
            del user['update_time']
            user['mark'] = role.mark

            s.commit()
            return user
        except Exception as e:
            print e
            s.rollback()
            return str(e.message)

    def LockAdminRequest(self, admin_id, is_disabled):
        '''
        禁用管理员
        '''
        s = db.session()
        try:
            s.query(Admin).filter(Admin.admin_id.in_(admin_id)).update({Admin.is_disabled: is_disabled}, synchronize_session=False)
            s.commit()
            return True
        except Exception as e:
            print e
            s.rollback()
            return str(e.message)

    def DelAdminRequest(self, admins):
        '''
        删除管理员
        '''
        s = db.session()
        try:
            for admin in admins:
                result = s.query(Admin).filter(Admin.admin_id == admin['admin_id']).first()
                s.delete(result)
            s.commit()
            return True
        except Exception as e:
            print e
            s.rollback()
            return str(e.message)
