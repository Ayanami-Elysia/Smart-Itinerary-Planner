import pymysql

def get_connection():
    """
    获取数据库连接
    
    Returns:
        pymysql.Connection: 数据库连接对象，连接失败返回None
    """
    try:
        # 数据库连接参数，可以根据实际环境配置
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 根据实际环境修改
            database='py_beijing',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None
