#encoding=utf8
#!/usr/bin/python
#import sqlite3
from flask import Flask, jsonify, session, redirect, url_for, escape, request, flash
from flask import render_template
import os, time, json,re,sys, chardet
from datetime import timedelta

#from Crypto.Cipher import AES
#from binascii import b2a_hex, a2b_hex
from app import app
from app.Sqllite import MySqlite
from app.Encrypt import EncryptStr

reload(sys)
sys.setdefaultencoding('utf8')

#app = Flask(__name__)

# 当前目录
currentpath = os.getcwd()

# 过滤list
def filterlist(key, listt):
    lista = []
    if isinstance(listt,list):
        for i in listt:
            # 迭代字典的value
            for v in i.values():
                v=str(v).encode("utf-8")
                # 匹配正则表达式需要compile
                regex = re.compile(r"(.*)(%s)(.*)" %key)
                # 失败返回None
                result = regex.match(str(v))
                if result is not None:
                    # 匹配成功，插入列表，跳出巡检
                    lista.append(i)
                    break
    return lista



my = MySqlite()
my.init_user()
#app.secret_key = 'saffllld33ww?SFjjjj'
en = EncryptStr('keyskeyskeyskeys')

# 主页，头部导航栏
@app.route('/',methods=['GET', 'POST'])
@app.route('/main',methods=['GET', 'POST'])
def main():
    lista = my.get_type_list()
#    listb = my.get_type_list()
    listc = my.get_url_list()
    liste = []
    for j in range(len(listc)):
        i = listc[j]
        listd=my.get_type_list(i['typeID'])
        if listd:
#            listc.remove(i)
#        else:
            i['typename'] = listd[0]['typename']
            liste.append(i)
    # 搜索框，过滤正则，实现搜索功能 
    if request.method == 'POST':
        key = request.form.get('key','')
        key = str(key).encode("utf-8")
        liste = filterlist(key, liste)
 #   return render_template('main.html', types=lista, urls=listc, type1=listb[0])
    print liste
    return render_template('main.html', types=lista, urls=liste)   
 #   return render_template('main.html', types=lista)

# 类型管理界面
@app.route('/typemanage', methods=['GET', 'POST'])
def typemanage():
    lista = my.get_type_list()
    print lista
    # 搜索框，过滤正则，实现搜索功能 
    if request.method == 'POST':
        key = request.form.get('key','')
        key = key.encode("utf-8")
        lista = filterlist(key, lista)
    return render_template('type_list.html', types=lista)

# 添加类型界面
@app.route('/typeadd', methods=['GET', 'POST'])
def typeadd():
    if request.method == 'GET':
        lista = my.get_type_list()
        return render_template('type_add.html', types=lista)
    else:
        parm1 = request.form.get("typename")
        parm2 = request.form.get("sortID")
        if my.is_number(parm2):
            result = my.add_type(parm1, parm2)
        else:
            flash(u"sortID必须为数字，请重新添加")
            return redirect('/typeadd')
        if result is False:
            flash(u"类型已存在")
            return redirect('/typeadd')
        return redirect('/typemanage')

# 删除类型
@app.route('/typedelete', methods=['GET'])
def typedelete():
    parm1 = request.args.get('typeID','')
    my.delete_type(parm1)
    return redirect("/typemanage")

# 更新类型
@app.route('/typeupdate', methods=['GET','POST'])
def typeupdate():
    ID = request.args.get('typeID', '')
    typename = my.get_type_list(ID)[0]["typename"]
    if request.method == 'GET':
        parm1 = request.args.get('typeID', '')
        lista = my.get_type_list()
        listb = my.get_type_list(parm1)
        return render_template('type_update.html', types=lista, type=listb[0])
    else:
        print typename
        parm1 = request.form.get('typeID', '')
        parm2 = request.form.get('typename', '')
        parm3 = request.form.get('sortID', '')
        if my.is_number(parm3):
            result = my.update_type(parm1, parm2, parm3, typename)
        else:
            flash(u"sortID必须为数字，请重新添加")
            return redirect('/typeupdate?typeID=%s'%ID)
        if result is False:
            flash(u"类型已存在")
            return redirect('/typeupdate?typeID=%s'%ID)
        return redirect('/typemanage')


# 显示url
@app.route('/urlshow/<typeID>', methods=['GET', 'POST'])
def urlshow(typeID):
    lista = my.get_type_list()
    listb = my.get_type_list(typeID)
    listc = my.get_url_list(typeID)
    # 搜索框，过滤正则，实现搜索功能 
    if request.method == 'POST':
        key = request.form.get('key','')
        key = str(key).encode("utf-8")
        listc = filterlist(key, listc)
    return render_template('url_list.html', types=lista, urls=listc, type1=listb[0])

# 增加网址
@app.route('/urladd', methods=['GET', 'POST'])
@app.route('/urladd/<typeID>', methods=['GET', 'POST'])
def urladd(typeID=None):
    if request.method == 'GET':
        lista = my.get_type_list(typeID)
        listb = my.get_url_list()
        listc = my.get_type_list()
        return render_template('url_add.html', type=lista[0], urls=listb, types=listc)
    else:
        parm1 = request.form.get('typeID','')
        parm2 = request.form.get('urlname','')
        parm3 = request.form.get('url','')
        parm4 = request.form.get('user','')
        parm5 = request.form.get('passwd','')
        parm6 = request.form.get('sortID','')
        parm7 = request.form.get('env','')
        parm5 = en.encrypt(parm5)
        if my.is_number(parm6):
            result = my.add_url(parm1, parm2, parm3, parm4, parm5, parm6, parm7)
        else:
            flash(u"sortID必须为数字，请重新添加")
            if typeID:
                return redirect('/urladd/'+typeID)
            else:
                return redirect('/urladd')
        if result is False:
            flash(u"类型已存在")
            if typeID:
                return redirect('/urladd/'+typeID)
            else:
                return redirect('/urladd')
        if typeID: 
            return redirect('/urlshow/'+typeID)
        else:
            return redirect('/main')

# 删除网址
@app.route('/urldelete/<typeID>', methods=['GET'])
@app.route('/urldelete', methods=['GET'])
def urldetete(typeID=None):
    parm1 = request.args.get('urlID','')
    my.delete_url(parm1)
    if typeID:
        return redirect('/urlshow/'+typeID)
    else:
        return redirect('/')

# 修改网址
@app.route('/urlupdate/<typeID>', methods=['GET','POST'])
@app.route('/urlupdate', methods=['GET','POST'])
def urlupdate(typeID=None):
    if request.method == 'GET':
        urlID = request.args.get('urlID','')
        lista = my.get_type_list()
        listb = my.get_url_byID(urlID)
        listc = my.get_type_list(typeID)
        return render_template("url_update.html", types=lista, url=listb, type=listc[0])
    else:
        parm0 = request.form.get('urlID','')
        parm1 = request.form.get('typeID','')
        parm2 = request.form.get('urlname','')
        parm3 = request.form.get('url','')
        parm4 = request.form.get('user','')
        parm5 = request.form.get('passwd','')
        parm6 = request.form.get('sortID','')
        parm7 = request.form.get('env','')
        a = my.get_url_byID(parm0)
        passwd = a["passwd"]
        if parm5 != passwd:
            parm5 = en.encrypt(parm5)
        my.update_url(parm0,parm1,parm2,parm3,parm4,parm5,parm6, parm7)
        if typeID:  
            return redirect('/urlshow/'+typeID)
        else:
            return redirect('/main')

# 修改用户密码
@app.route('/changepwd', methods=['GET', 'POST'])
def changepwd():
    if request.method == 'GET':
        lista = my.get_type_list()
        return render_template('changepwd.html',types=lista)
    else:
        username = session.get('username')
        oldpasswd = request.form.get('oldpwd')
        newpasswd1 = request.form.get('newpwd1')
        newpasswd2 = request.form.get('newpwd2')
        # 新密码两次一致
        if newpasswd1 != newpasswd2:
            flash(u'两次密码输入不一致，请重新输入')
            return redirect('/changepwd')
        else:
            # 获取旧密码，判断旧密码输入正误
            parm1 = my.get_passwd(username)
            parm1 = en.decrypt(parm1)
            newpasswd = en.encrypt(newpasswd1)
            if parm1 != oldpasswd:
                flash(u'原密码输入错误')
                return redirect('/changepwd')
            else:
                try:
                    my.chg_passwd(username, newpasswd)
                except:
                    flash(u'密码未完成')
        #flash(u'密码修改完成')
            # 
        return redirect('/main')

# 显示密码
@app.route('/geturlpasswd')
def geturlpasswd():
    parm1 = request.args.get('urlID','')
    listb = my.get_url_byID(parm1)
    #listb["passwd"] = en.decrypt("listb['passwd']")
#    listb["passwd"] = "111"
    print(listb)
    listb["passwd"] = en.decrypt(listb['passwd'])
    return json.dumps(listb)

# 登录
@app.route("/login", methods=['GET', 'POST'])
def login():
#    form1 = form.LoginForm()
    # 设置session为永久
    session.permanent = True
    # 设置session的有效时间
    app.permanent_session_lifetime = timedelta(minutes=180)
    if request.method == "GET":
        return render_template('login.html')
    else:
        parm1 = request.form.get('username','')
        parm2 = request.form.get('password','')
        try:
            parm3 = my.get_passwd(parm1)
        except:
            flash(u"用户名密码错误")
            return render_template('login.html')
        parm3 = en.decrypt(parm3)
        if parm2 == parm3:
            session['username'] = parm1
            return redirect("/")

        else:
            flash(u"用户名密码错误")
#            return render_template('login.html', form=form1)
            return render_template('login.html')

# 登出
@app.route("/logout", methods=['GET','POST'])
def logout():
    user = session.get('username')
    if user:
        session.pop('username', None)
        return redirect('/login')

# 请求前登录
@app.before_request
def login_request():
    pathlist = []
    pathlist.append('/login')
    a = re.match(r'/static/(.*)', request.path, re.M|re.I)
    if a:
        pathlist.append(request.path)
    if request.path in pathlist:
        return None
    user = session.get('username')
    if not user:
        return redirect('/login')
    return None



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9527)

