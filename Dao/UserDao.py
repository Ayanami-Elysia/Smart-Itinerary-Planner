import pymysql



# 数据库连接
def get_connection():
    return pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='py_beijing')

# 管理员登陆
def loginDao(username,password,role):
    conn = get_connection()
    cursor3=conn.cursor()
    cursor3.execute('select * from `py_user` where username = %s and password = %s and role = %s' ,(username,password,role))
    res = cursor3.fetchall()
    conn.commit()
    conn.close()
    return res

# 注册检测
def GetuserDao(username):
    conn = get_connection()
    cursor2 = conn.cursor()
    cursor2.execute('select * from `py_user` where username = %s ', (username))
    res = cursor2.fetchall()
    conn.commit()
    conn.close()
    return res

# 管理员注册
def Addregister(username,password,role):
    conn = get_connection()
    cursor1 = conn.cursor()
    cursor1.execute('insert into `py_user` (username, password, nickname,role) values (%s, %s, %s, %s)',
                    (username, password, username,role))
    conn.commit()
    conn.close()
    return

# 查询列表
def ListDao(username=None, page=1, limit=20):
    conn = get_connection()
    cursor4 = conn.cursor()
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 构建基础查询语句
    base_sql = "select * from py_user where role ='user'"
    count_sql = "select count(*) from py_user where role ='user'"

    # 如果有用户名参数,添加搜索条件
    if username:
        base_sql += " and username like %s"
        count_sql += " and username like %s"
        search_param = f"%{username}%"
        
        # 获取总数
        cursor4.execute(count_sql, (search_param,))
        # 获取总记录数
        total = cursor4.fetchone()[0]
        # 执行分页查询
        cursor4.execute(base_sql + " LIMIT %s,%s", (search_param, offset, limit))
    else:
        # 无搜索条件的查询
        # 获取总数
        cursor4.execute(count_sql)
        # 获取总记录数
        total = cursor4.fetchone()[0]
        # 执行分页查询
        cursor4.execute(base_sql + " LIMIT %s,%s", (offset, limit))
    
    data = cursor4.fetchall()
    
    conn.commit()
    conn.close()
    
    return {
        "total": total,
        "data": data
    }
# 删除用户
def DeleteUserDao(id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "delete from py_user where id = %s"
    cursor.execute(sql, (id,))
    conn.commit()
    conn.close()
    return True


# 新增用户
def AddUserDao(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """insert into py_user(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks,role) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'user')"""
    cursor.execute(sql, (username, password, nickname, sex, age, phone, email, birthday, card, content, remarks))
    conn.commit()
    conn.close()
    return True

def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM py_user WHERE id = %s"
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        print(f"获取用户信息失败: {str(e)}")
        return None

def update_user(user_id, username, password, nickname, sex, age, phone, email, birthday=None, card=None, content=None, remarks=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """UPDATE py_user SET username=%s, password=%s, nickname=%s, 
                    sex=%s, age=%s, phone=%s, email=%s, birthday=%s, 
                    card=%s, content=%s, remarks=%s WHERE id=%s"""
        print(user_id, username, password, nickname, sex, age, phone, email, birthday, card, content, remarks)
        print("UPDATE py_user SET username=%s, password=%s, nickname=%s,sex=%s, age=%s, phone=%s, email=%s, birthday=%s,card=%s, content=%s, remarks=%s WHERE id=%s"%(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks, user_id))
        cursor.execute(sql, (username, password, nickname, sex, age, phone, email, birthday, card, content, remarks, user_id))
            
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"更新用户信息失败: {str(e)}")
        return False
# 查询管理员列表
def ListAdminDao(username=None, page=1, limit=20):
    conn = get_connection()
    cursor4 = conn.cursor()
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 构建基础查询语句
    base_sql = "select * from py_user where role ='admin'"
    count_sql = "select count(*) from py_user where role ='admin'"

    # 如果有用户名参数,添加搜索条件
    if username:
        base_sql += " and username like %s"
        count_sql += " and username like %s"
        search_param = f"%{username}%"
        
        # 获取总数
        cursor4.execute(count_sql, (search_param,))
        # 获取总记录数
        total = cursor4.fetchone()[0]
        # 执行分页查询
        cursor4.execute(base_sql + " LIMIT %s,%s", (search_param, offset, limit))
    else:
        # 无搜索条件的查询
        # 获取总数
        cursor4.execute(count_sql)
        # 获取总记录数
        total = cursor4.fetchone()[0]
        # 执行分页查询
        cursor4.execute(base_sql + " LIMIT %s,%s", (offset, limit))
    
    data = cursor4.fetchall()
    
    conn.commit()
    conn.close()
    
    return {
        "total": total,
        "data": data
    }

def AddAdminDao(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """insert into py_user(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks,role) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'admin')"""
    cursor.execute(sql, (username, password, nickname, sex, age, phone, email, birthday, card, content, remarks))
    conn.commit()
    conn.close()
    return True