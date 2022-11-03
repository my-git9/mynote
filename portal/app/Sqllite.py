#encoding=utf8
#!/usr/bin/python
import sqlite3
import os, time, json,re,sys, chardet
class MySqlite():
    def __init__(self):
        # 连接
        self.conn = sqlite3.connect("sqlite3.db", check_same_thread=False)
        # 创建游标
        cursor = self.conn.cursor()
        #　创建
        sql = "create table if not exists t_user(username varchar(32) primary key, passwd varchar(32))"
        # 执行sql
        cursor.execute(sql)
        sql = "create table if not exists t_type(typeID varchar(32) primary key, typename varchar(32) UNIQUE, sortID integer)"
        cursor.execute(sql)
        sql = "create table if not exists t_url(urlID varchar(32) primary key, typeID varchar(32), urlname varchar(32), url varchar(100), user varchar(32), passwd varchar(32), sortID integer)"
        cursor.execute(sql)
        self.conn.commit()
        # 关闭游标
        cursor.close()

#    def add_colum(self):
#        cursor = self.conn.cursor()
#        sql = "alter table `t_url` add `env` varchar(32)"
#        cursor.execute(sql)
#        self.conn.commit()
#        cursor.close()

    # 富国t_user表没有数据，初始化一个用户admin/admin
    def init_user(self):
        cursor = self.conn.cursor()
        sql="select count(*) from t_user"
        result = cursor.execute(sql)
        # 查询第一个值
        row = result.fetchone()
        if row[0] == 0:
            sql = "insert into t_user(username, passwd) values('admin','admin')"
            cursor.execute(sql)
            # 提交
            self.conn.commit()
        cursor.close()

    # 生成时间戳字符串
    def get_ID(self):
        return "%s"%(int(time.time())*1000000)

    # 查询菜单数据
    def get_type_list(self, typeID=None):
        result = self.get_type(typeID)
        set = []
        for row in result:
            dict = {"typeID":row[0], "typename":row[1], "sortID":row[2]}
            set.append(dict)
        return set

    # 查询类型
    def get_type(self, typeID=None):
        cursor = self.conn.cursor()
        if typeID:
            sql = "select * from t_type where typeID='%s'"%(typeID)
        else:
            sql = "select * from t_type order by sortID desc"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    # 添加类型
    def add_type(self, typename, sortID=9999):
        if self.check_typename(typename):
            return False
        else:
            cursor = self.conn.cursor()
            typeID = self.get_ID()
            sql = "insert into t_type(typeID, typename, sortID) values(%s, '%s', %s)"%(typeID, typename, sortID)
            cursor.execute(sql)
            cursor.close()
            self.conn.commit()
            return True

    # 删除类型
    def delete_type(self, typeID):
        cursor = self.conn.cursor()
        sql = "delete from t_type where typeID='%s'"%(typeID)
        sql1 = "delete from t_url where typeID=%s"%(typeID)
        cursor.execute(sql)
        cursor.execute(sql1)
        self.conn.commit()
        cursor.close()
        return True
    
     # 更新类型
    def update_type(self, typeID, typename, sortID, typename1):
        if self.check_typename(typename) and typename != typename1:
            return False
        else:
            cursor = self.conn.cursor()
            sql = "update t_type set typename='%s', sortID='%s' where typeID='%s'"%(typename, sortID, typeID)
            cursor.execute(sql)
            cursor.close()
            self.conn.commit()
            return True
    


    # 检查typename是否存在
    def check_typename(self, typename):
        cursor = self.conn.cursor()
        sql = "select typeID from t_type where typename='%s'"%(typename)
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        if row:
            return True
        else:
            return False

    # 添加url
    def add_url(self, typeID, urlname, url, user='NULL', passwd='NULL', sortID=9999, env="生产环境"):
        urlID = self.get_ID()
    	cursor = self.conn.cursor()
#        if passwd is not NULL:
#            passwd = encrypt('lovebread', passwd)
    	sql = "insert into t_url values('%s','%s','%s','%s','%s','%s',%s, '%s')"%(urlID, typeID, urlname, url, user, passwd, sortID, env)
        cursor.execute(sql)
        cursor.close()
        self.conn.commit()
    	return True

    # 查询URL
    def get_url_list(self, typeID=None):
    	result = self.get_url(typeID)
    	set = []
    	for row in result:
            dict = {"urlID": row[0], "typeID": row[1], "urlname": row[2], "url": row[3], "user": row[4], "passwd": row[5], "sortID": row[6], "env": row[7]}
            set.append(dict)
        return set

    # 查询url
    def get_url(self, typeID=None):
    	cursor = self.conn.cursor()
    	if typeID:
    		sql = "select * from t_url where typeID='%s' order by sortID desc"%(typeID)
    	else:
    		sql = "select * from t_url order by sortID desc"
    	cursor.execute(sql)
    	result = cursor.fetchall()
    	cursor.close()
    	return result

    def get_url_byID(self, urlID):
        cursor = self.conn.cursor()
        sql = "select * from t_url where urlID='%s'"%(urlID)
        cursor.execute(sql)
        row = cursor.fetchone()
        result = {"urlID": row[0], "typeID": row[1], "urlname": row[2], "url": row[3], "user": row[4], "passwd": row[5], "sortID": row[6], "env": row[7]}
        cursor.close()
        return result

    # 更新url
    def update_url(self, urlID, typeID, urlname, url, user, passwd, sortID, env):
    	cursor = self.conn.cursor()
 #       if passwd is not NULL:
 #           passwd = encrypt('lovebread', passwd)
    	sql = "update t_url set typeID='%s', urlname='%s', url='%s', user='%s', passwd='%s', sortID=%s, env='%s' where urlID='%s'"%(typeID, urlname, url, user, passwd, sortID, env, urlID)
    	cursor.execute(sql)
    	cursor.close()
    	self.conn.commit()
    	return True

    # 检查urlname
    def check_urlname(self, urlname):
    	cursor = self.conn.cursor()
    	sql = "select urlID from t_url where urlname='%s'"%(urlname)
    	cursor.execute(sql)
    	row = cursor.fetchone()
    	cursor.close()
    	if row:
    		return True
    	else:
    		return False

    # 删除url
    def delete_url(self, urlID):
    	cursor = self.conn.cursor()
    	sql = "delete from t_url where urlID=%s"%(urlID)
    	cursor.execute(sql)
    	cursor.close()
    	self.conn.commit()
    	return True

    # 修改密码
    def chg_passwd(self, username, passwd):
        cursor = self.conn.cursor()
        sql = "update t_user set passwd='%s' where username='%s'"%(passwd, username) 
        cursor.execute(sql)
        cursor.close()
        self.conn.commit()
        return True

    # 判断是否为数字
    def is_number(self, str):
        try:
            float(str)
            return True
        except ValueError:
            pass
        return False

    # 获取用户密码
    def get_passwd(self, username):
        cursor = self.conn.cursor()
        sql = "select passwd from t_user where username='%s'"%(username)
        result = cursor.execute(sql)
        passwd = result.fetchone()
        cursor.close() 
        return passwd[0]
