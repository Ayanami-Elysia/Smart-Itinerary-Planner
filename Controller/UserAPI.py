from flask import Blueprint, jsonify, request, render_template, session
from Dao.UserDao import *
import pymysql

# from urllib import request
from flask import Blueprint,jsonify,request

user_api= Blueprint('user_api', __name__)


@user_api.route('/loginApi', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(data)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        # 验证必填参数
        if not all([username, password, role]):
            return jsonify({
                'msg': '请填写所有必填项',
                'code': 400
            })
            
        res = loginDao(username, password, role)
        
        if res and len(res) > 0:
            body = {
                'id': res[0][0],
                'username': res[0][1],
                'password': res[0][2],
                'nickname': res[0][3],
                'sex': res[0][4],
                'age': res[0][5],
                'phone': res[0][6],
                'email': res[0][7],
                'birthday': res[0][8],
                'card': res[0][9],
                'content': res[0][10],
                'remarks': res[0][11],
                'role': role,  # 保存原始角色值，便于前端判断
                'role_name': '管理员' if role == 'admin' else '用户',
                'token': res[0][0]
            }
            
            # 将用户信息保存到 session 中
            session['user_id'] = body['id']
            session['username'] = body['username']
            session['role'] = body['role']
            session['nickname'] = body['nickname']
            session['logged_in'] = True
            
            return jsonify({
                'msg': '登录成功',
                'data': body,
                'code': 200
            })
        else:
            return jsonify({
                'msg': '账号或密码不正确',
                'code': 400
            })
            
    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'msg': '登录失败，请稍后重试',
            'code': 500
        })

@user_api.route('/logout', methods=['POST', 'GET'])
def logout():
    # 清除 session 中的用户信息
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('nickname', None)
    session.pop('logged_in', None)
    
    return jsonify({
        'msg': '退出登录成功',
        'code': 200
    })

@user_api.route('/checkLogin', methods=['GET'])
def check_login():
    if session.get('logged_in'):
        user_data = {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'nickname': session.get('nickname'),
        }
        return jsonify({
            'code': 200,
            'msg': '用户已登录',
            'data': user_data
        })
    else:
        return jsonify({
            'code': 401,
            'msg': '用户未登录'
        })

@user_api.route('/registerApi', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        email = data.get('email')
        role = data.get('role', 'user')  # 默认为普通用户
        
        # 验证必填字段
        if not all([username, password, phone, email]):
            return jsonify({
                'code': 400,
                'message': '请填写所有必填项'
            })
            
        # 检查用户名是否已存在
        if GetuserDao(username):
            return jsonify({
                'code': 400,
                'message': '用户名已存在'
            })
            
        # 调用 DAO 层注册方法
        Addregister(username, password,role)
        
        return jsonify({
            'code': 200,
            'message': '注册成功'
        })
        
    except Exception as e:
        print(f"注册错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '注册失败，请稍后重试'
        })

@user_api.route('/userlist' , methods=[ 'POST'])
def getuserlist():
    data = request.get_json()
    username = data.get('username')
    page = data.get('page', 1)
    limit = data.get('limit', 20)
    res = ListDao(username=username, page=page, limit=limit)
    data = res['data']
    total = res['total']
    datalist=[]
    for user in data:
        print(user)
        body = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'nickname': user[3],
            'sex': user[4],
            'age': user[5],
            'phone': user[6],
            'email': user[7],
            'birthday': user[8],
            'card': user[9],
            'content': user[10],
            'remarks': user[11],
            'role': user[12],
            'token': user[0]
        }
        datalist.append(body)
    data = {
        'msg': '查询成功',
        'data': datalist,
        'total': total,
        'code': 200
        }

    return jsonify(data)
@user_api.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    try:
        DeleteUserDao(id)
        return jsonify({
            'msg': '删除成功',
            'code': 200
        })
    except Exception as e:
        return jsonify({
            'msg': '删除失败',
            'code': 500
        })


@user_api.route('/add', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        birthday = data.get('birthday')
        card = data.get('card')
        content = data.get('content')
        remarks = data.get('remarks')

        AddUserDao(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks)
        return jsonify({
            'msg': '添加成功',
            'code': 200
        })
    except Exception as e:
        return jsonify({
            'msg': '添加失败', 
            'code': 500
        })

@user_api.route('/edituser')
def edit_user_page():
    user_id = request.args.get('id')
    user_tuple = get_user_by_id(user_id)
    # 将元组转换为字典，确保包含所有数据库字段
    user = {
        'id': user_tuple[0],
        'username': user_tuple[1],
        'password': user_tuple[2],
        'nickname': user_tuple[3],
        'sex': user_tuple[4],
        'age': user_tuple[5],
        'phone': user_tuple[6],
        'email': user_tuple[7],
        'birthday': user_tuple[8],
        'card': user_tuple[9],
        'content': user_tuple[10],
        'remarks': user_tuple[11],
        'role': user_tuple[12]
    }
    print("用户数据:", user)  # 添加调试输出
    return render_template('edituser.html', user=user)

@user_api.route('/edit', methods=['POST'])
def edit_user():
    data = request.get_json()
    try:
        user_id = data.get('id')
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        birthday = data.get('birthday')
        card = data.get('card')
        content = data.get('content')
        remarks = data.get('remarks')
        
        # 更新用户信息
        success = update_user(user_id, username, password, nickname, sex, age, phone, email, birthday, card, content, remarks)
        
        if success:
            return jsonify({"code": 200, "message": "更新成功"})
        else:
            return jsonify({"code": 500, "message": "更新失败"})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)})
    
@user_api.route('/adminlist' , methods=[ 'POST'])
def getadminlist():
    data = request.get_json()
    username = data.get('username')
    page = data.get('page', 1)
    limit = data.get('limit', 20)
    res = ListAdminDao(username=username, page=page, limit=limit)
    data = res['data']
    total = res['total']
    datalist=[]
    for user in data:
        print(user)
        body = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'nickname': user[3],
            'sex': user[4],
            'age': user[5],
            'phone': user[6],
            'email': user[7],
            'birthday': user[8],
            'card': user[9],
            'content': user[10],
            'remarks': user[11],
            'role': user[12],
            'token': user[0]
        }
        datalist.append(body)
    data = {
        'msg': '查询成功',
        'data': datalist,
        'total': total,
        'code': 200
        }

    return jsonify(data)
@user_api.route('/addadmin', methods=['POST'])
def add_admin():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        birthday = data.get('birthday')
        card = data.get('card')
        content = data.get('content')
        remarks = data.get('remarks')

        AddAdminDao(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks)
        return jsonify({
            'msg': '添加成功',
            'code': 200
        })
    except Exception as e:
        return jsonify({
            'msg': '添加失败',
            'code': 500
        })

@user_api.route('/getUserInfo', methods=['GET'])
def get_user_info():
    try:
        user_id = request.args.get('id')
        if not user_id:
            return jsonify({
                'code': 400,
                'msg': '缺少用户ID参数'
            })
            
        # 检查是否是当前登录用户请求自己的信息
        if session.get('logged_in') and str(session.get('user_id')) == str(user_id):
            # 获取用户信息
            user_info = get_user_by_id(user_id)
            
            if user_info:
                data = {
                'id': user_info[0],
                'username': user_info[1],
                'nickname': user_info[3],
                'sex': user_info[4],
                'age': user_info[5],
                'phone': user_info[6],
                'email': user_info[7],
                'birthday': user_info[8],
                'card': user_info[9],
                'content': user_info[10],
                'remarks': user_info[11],
                'role': session.get('role')
                }
                
                return jsonify({
                    'code': 200,
                    'msg': '获取用户信息成功',
                    'data': data
                })
            else:
                return jsonify({
                    'code': 404,
                    'msg': '用户不存在'
                })
        else:
            return jsonify({
                'code': 403,
                'msg': '无权访问此用户信息'
            })
            
    except Exception as e:
        print(f"获取用户信息错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取用户信息失败'
        })

@user_api.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        data = request.get_json()
        user_id = data.get('id')
        
        # 检查是否是当前登录用户更新自己的信息
        if not session.get('logged_in') or str(session.get('user_id')) != str(user_id):
            return jsonify({
                'code': 403,
                'msg': '无权更新此用户信息'
            })
        
        # 获取表单数据
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        birthday = data.get('birthday')
        card = data.get('card')
        content = data.get('content')
        
        # 获取当前用户信息
        user_info = get_user_by_id(user_id)
        if not user_info:
            return jsonify({
                'code': 404,
                'msg': '用户不存在'
            })
        
        # 保留原始密码
        password = user_info[2]
        
        # 更新用户信息
        success = update_user(
            user_id, 
            user_info[1],  # 保持原用户名不变
            password,      # 保持原密码不变
            nickname, 
            sex, 
            age, 
            phone, 
            email, 
            birthday, 
            card, 
            content,
            user_info[11]  # 保持原备注不变
        )
        
        if success:
            # 更新session中的昵称
            if nickname:
                session['nickname'] = nickname
                
            return jsonify({
                'code': 200,
                'msg': '个人资料更新成功'
            })
        else:
            return jsonify({
                'code': 500,
                'msg': '个人资料更新失败'
            })
            
    except Exception as e:
        print(f"更新个人资料错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'更新个人资料失败: {str(e)}'
        })

@user_api.route('/update_password', methods=['POST'])
def update_password():
    try:
        data = request.get_json()
        user_id = data.get('id')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # 验证必填字段
        if not all([user_id, current_password, new_password]):
            return jsonify({
                'code': 400,
                'msg': '缺少必要参数'
            })
        
        # 检查是否是当前登录用户更新自己的密码
        if not session.get('logged_in') or str(session.get('user_id')) != str(user_id):
            return jsonify({
                'code': 403,
                'msg': '无权更新此用户密码'
            })
        
        # 获取当前用户信息
        user_info = get_user_by_id(user_id)
        if not user_info:
            return jsonify({
                'code': 404,
                'msg': '用户不存在'
            })
        
        # 验证当前密码是否正确
        if user_info[2] != current_password:
            return jsonify({
                'code': 400,
                'msg': '当前密码不正确'
            })
        
        # 更新用户密码
        success = update_user(
            user_id, 
            user_info[1],   # 保持原用户名不变
            new_password,   # 新密码
            user_info[3],   # 保持原昵称不变
            user_info[4],   # 保持原性别不变
            user_info[5],   # 保持原年龄不变
            user_info[6],   # 保持原电话不变
            user_info[7],   # 保持原邮箱不变
            user_info[8],   # 保持原生日不变
            user_info[9],   # 保持原身份证不变
            user_info[10],  # 保持原内容不变
            user_info[11]   # 保持原备注不变
        )
        
        if success:
            return jsonify({
                'code': 200,
                'msg': '密码更新成功'
            })
        else:
            return jsonify({
                'code': 500,
                'msg': '密码更新失败'
            })
            
    except Exception as e:
        print(f"更新密码错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'更新密码失败: {str(e)}'
        })

  