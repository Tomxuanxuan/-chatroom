import socket,select
import time,hashlib,random,sys,struct,os
import pymysql
import signal
from config.baseconfig import *
from model.model import GetDBConnect
import json
#分隔字符用 :*:

red="\033[0;31m"
green="\033[0;32m"
none="\033[0m"
def handler(signal_num,frame):
    print("service stopping!")
    sys.exit(signal_num)
signal.signal(signal.SIGINT,handler)
class Table_ctrl():
    def __init__(self,tablename):
        self.tablename=tablename
        self.connect_db()
    def connect_db(self):
        try:
            self.conn = pymysql.connect(user=db_user ,password=db_password, database=db_name, charset="utf8")
        except:
            os.system("service mysql start")
            self.conn = pymysql.connect(user=db_user, password=db_password, database=db_name, charset="utf8")
        finally:
            self.cur=self.conn.cursor()
    def get_timeId(self):
        now=time.time()
        intnow=int(now)
        ms=int((now-intnow)*1000)
        timeId=time.strftime("%y%m%d%H%M%S",time.localtime(time.time()))+str(ms)
        return timeId
    def write_db(self,*data):
        '''插入数据库'''
        sql="INSERT INTO "+str(self.tablename)+" VALUES('"+self.get_timeId()+"'"
        for i in range(len(data)):
            if type(data[i])==type("string"):
                sql+=",'"+data[i]+"'"
            else:
                sql+=","+str(data[i])
        sql+=")"
        try:
            self.cur.execute(sql.encode('utf-8'))
            self.conn.commit()
        except Exception as e:
            print("writting  database error:%s"%e)
    def checkExist(self,column,value):
        Exist=False
        if type(value)==type("string"):
            sql="select * from "+str(self.tablename)+" where "+str(column)+"='"+str(value)+"'"
        else:
            sql="select * from "+str(self.tablename)+" where "+str(column)+"="+str(value)
        try:
            self.cur.execute(sql)
            if self.cur.fetchone():
                    Exist=True
        except:
            print("check value Error!")
        return Exist
    def query_db(self,kColumn,kValue,queryField):
        if type(kValue)==type("string"):
            sql="select %s from %s where %s='%s'"%(queryField,self.tablename,kColumn,kValue)
        else:
            sql="select %s from %s where %s=%s"%(queryField,self.tablename,kColumn,kValue)
        print(sql)
        try:
            self.cur.execute(sql)
            return self.cur.fetchone()[0]
        except:
            print("query Error!")
    def __del__(self):
        self.conn.close()
class Login(Table_ctrl):
    '''登录'''
    def __init__(self,username,password):
        Table_ctrl.__init__(self,"USER")
        self.username=username
        self.password=password
    def login(self):
        sha1=hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        self.password=sha1.hexdigest()
        return self.isLegal(self.username,self.password)
    def isLegal(self,username,password):
        sql="SELECT * FROM user WHERE username='{0}' AND password='{1}'".format(username,password)
        print(sql)
        self.cur.execute(sql)
        result=self.cur.fetchone()
        print(result)
        if result:
            self.niname=result[3]
            #假如是超级用户
            if self.username == 'admin':
                print('超级用户')
                return 'super'
            return True
        else:
            return False
class Register(Table_ctrl):
    '''注册'''
    def __init__(self,username,password,niname):
        Table_ctrl.__init__(self,"USER")
        self.username=username
        self.password=password
        self.niname=niname
        self.age=0
        self.sex='N'
        self.picId='NULL'
    def register(self):
        sha1=hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        self.password=sha1.hexdigest()
        return self.isLegal()
    def isLegal(self):
        if self.checkExist("USERNAME",self.username) or  self.checkExist("NINAME",self.niname):
           return False
        self.write_db(self.username,self.password,self.niname,self.age,self.sex,self.picId)
        return True

def offline(sock):
    '''离线'''
    if online.get(sock):
        del online[sock]
    if online_niname.get(sock):
        broadcast_data(sock,"system:*:offline:%s" % load_values)
        print(green+"[%s] is offline" % load_values)
        del online_niname[sock]
    print(red+"Client (%s,%s) disconnected." % sock.getpeername()+none)
    sock.close()
    CONNECTION_LIST.remove(sock)
    for con_dict in CONNECTION_DICT:
        if con_dict['socket'] == sock:
            CONNECTION_DICT.remove(con_dict)
    print('链接字典:', CONNECTION_DICT)
def broadcast_data (sock, message):
    '''广播数据'''
    global online
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock and socket!=sys.stdin and online.get(socket):
            try :
                if message:
                    message+="\n"
                    socket.send(message.encode())
            except Exception as e:
                print("Error:%s"%e)
                socket.close()
                CONNECTION_LIST.remove(socket)
def broadcast_data_load(load_values):
    '''
    组播 给登录用户好友发送消息
    :param load_values: 登录用户信息
    :return:
    '''
    if 'friends' in load_values:    #存在好友
        for load_friend in load_values['friends']:
            for online_user in CONNECTION_DICT:
                if load_friend['id'] == online_user['user_id']:
                    mes = 'system:*:登录:[{0}]上线了'.format(load_values['niname'])
                    online_user['socket'].send(mes.encode())
def broadcast_data_offline(sock):
    '''
    组播 给用户好友发送离线消息 删除在线用户
    :param sock: 离线用户sock
    :return:
    '''
    print('broadcast_data_offline')

    print(CONNECTION_DICT)
    for load_user in CONNECTION_DICT:
        if load_user['socket'] == sock:

            offline_user_id = load_user['user_id']  #离线用户 id
            friends = GetDBConnect(userid=offline_user_id).get_friend_users()
            print('朋友们：', friends)
            for friend in friends:
                for online_friend in CONNECTION_DICT:
                    if 'user_id' in online_friend:  #避免单人登录下线报错
                        if friend['id'] == online_friend['user_id']:
                            mes = 'system:*:离线:[{0}]下线了'.format(load_user['niname'])
                            online_friend['socket'].send(mes.encode())
                            print(mes)
            sock.close()
            CONNECTION_LIST.remove(sock)
            CONNECTION_DICT.remove(load_user)
            print('关闭链接')

            break




def parse_data(socket,data):
    '''解析数据'''
    global online
    global online_niname
    global load_values
    global CONNECTION_LIST
    try:
        mes=data.split(":*:")[0]

        if mes=="data":
            if not  online.get(socket):
                return "system:data\nfailed:loginFirst"
        elif mes=="register":
            datalist=data.split(",")
            username=datalist[1].split(":")[1]
            password=datalist[2].split(":")[1]
            niname=datalist[3].split(":")[1]
            register_user=Register(username,password,niname)
            if register_user.register():
                return "system:register\nsuccess:"+niname
            else:
                return "system:register\nfailed:user or niname exist"
        elif mes=="login":
            if online.get(socket):
                return "system:login\nfailed:login repeat"  #重复登录
            datalist = data.split(":*:")
            username = datalist[1]
            password = datalist[2]
            ip = datalist[3]
            login_user=Login(username, password)
            res = login_user.login()
            if res:
                #登录成功
                tc=Table_ctrl("USER")
                niname=tc.query_db("USERNAME",username,"NINAME")
                user_id = tc.query_db('username', username, 'id')
                print('查看登录用户 id', user_id)

                online[sock]=True
                if not  niname:
                    niname="NULL"
                online_niname[sock]=niname

                #保存登录用户信息
                values = {}
                values['user_id'] = user_id
                values['username'] = username
                values['socket'] = socket
                values['niname'] = niname
                CONNECTION_DICT.append(values)
                # print('链接字典:', CONNECTION_DICT)
                # load_values[sock] = values
                load_values = {}  # 保存登录用户信息 {sock:{user_id:id, ...},}
                load_values['user_id'] = user_id    #登录用户信息 id
                load_values['username'] = username
                load_values['niname'] = niname
                # broadcast_data(sock, "system:*:load:%s" % load_values)  # 广播某个用户登录成功消息
                # 自己写一个给当前登录用户好友群发登录成功系统消息
                if res == 'super':
                    load_values['friends'] = GetDBConnect(userid=user_id).get_all_users()
                    broadcast_data_load(load_values)
                    socket.send(("login:*:success:*:%s:*:super" % load_values).encode())
                    return 'super'

                # load_values['friends'] = GetDBConnect(userid=user_id).get_friend_users()
                friends = GetDBConnect(userid=user_id).get_friend_users()
                res_friends = []
                for friend in friends:
                    for online_user in CONNECTION_DICT:
                        print("friend['id']", friend['id'])
                        print("online_user['user_id']", online_user['user_id'])
                        if friend['id'] == online_user['user_id']:
                            friend['is_online'] = 'True'
                    res_friends.append(friend)
                print('res_friends', res_friends)
                load_values['friends'] = res_friends
                broadcast_data_load(load_values)
                socket.send(("login:*:success:*:%s" % load_values).encode())

                return 'user'
            else:
                socket.send(("login:*:failed").encode())    #登录失败
                return "login:*:failed"
        elif mes=="update":
            if not  online.get(socket):
                return "system:update\nfailed:loginFirst"
            print("update!")
        elif mes=="query":
            if not  online.get(socket):
                return "system:query\nfailed:loginFirst"
            sentence=""
            for i in CONNECTION_LIST:
                if online_niname.get(i):
                    sentence+=","+online_niname.get(i)
            return "system:query\nsuccess:"+sentence
        elif mes == "msg":
            info = data.split(":*:")[-1]
            # {'send_user': {'user_id': 1, 'username': 'admin'}, 'recv_user': {'id': 2, 'name': 'xixi', 'niname': '西西', 'address': "('127.0.0.1', 56527)"}, 'content': '发给 xixi', 'send_time': '2019-12-24 14:17:14'}
            print('收到文本消息')
            print(info)
            dict_info = eval(info)
            #保存聊天消息 （返回收信人 用户id）
            recv_id = GetDBConnect(userid=dict_info['send_user']['user_id']).save_chat_message(dict_info)
            if recv_id:
                #消息保存成功
                print(load_values)
                print(CONNECTION_DICT)
                for online_user in CONNECTION_DICT:
                    try:
                        #接收用户 id 相等，则获取对应的 socket
                        if recv_id == online_user['user_id']:
                            online_user['socket'].send(json.dumps(dict_info).encode())

                    except Exception as e:
                        print('发送消息错误:', e)

                return 'msg:*:ok'
            else:
                return 'msg:*:failed'

        elif mes=="logout":
            logout_user = data.split(':*:')[-1]
            print('logout_user', logout_user)
            broadcast_data_offline(socket)
            # if online.get(sock):
            #     return "system:logout\nFailed:you did not login"
            # broadcast_data(sock,"system:broadcast\nlogout:{0} left the room.".format(online_niname[sock]))
            now=time.strftime("%y-%m-%d",time.localtime(time.time()))
            # logout_flag=True
            return "system:logout\nsuccess:"+now
        elif mes == "records":
            #查询历史记录
            recv_user_name = data.split(":*:")[-1]
            records = GetDBConnect(userid=False).get_user_message(recv_user_name)
            record_list = []
            value = {}
            for record in records:
                value['user_name'] = record[2]
                value['send_time'] = record[6].strftime('%Y-%m-%d %H:%M:%S')
                value['content'] = record[5]
                record_list.append(value)

            print(records)
            if len(record_list) >= 5:
                index = 5
            else:
                index = len(record_list)
            socket.send(('records:*:'+str(record_list[-index:])).encode())   #所有消息记录发送回去
        else:
            return "system:unknown"
    except Exception as e:
        print(" parse data Error:%s"%e)
        return "system:unknown"
if __name__ == "__main__":
    CONNECTION_LIST = [sys.stdin]
    CONNECTION_DICT = []
    RECV_BUFFER = 4096
    PORT = 5000
    #tcp流式套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
    online={}
    online_niname={}


    CONNECTION_LIST.append(server_socket)
    print(green+"聊天服务器在端口启动："+none + str(PORT))
    running=True
    while running:
        #select多路复用，监听到操作则立即返回（读事件，写事件，异常）
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        print('read_sockets:', read_sockets)
        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                message=green+"Client (%s, %s) connected\t" % addr+none
                print(sock)
                #将登陆用户的地址信息写入 user 表
                data = 'addr:*:'+str(addr)
                save_address = parse_data(sock, data)

            elif sock==sys.stdin:
                junk=sys.stdin.readline()
                if junk=="exit":
                    running=False
                else:
                    broadcast_data(sock,"testing\n")
            else:
                try:
                    #服务器收到数据
                    data = sock.recv(RECV_BUFFER)
                    logout_flag = False
                    if data:
                        redata = parse_data(sock, data.decode().rstrip())+"\n"
                        # sock.send(redata.encode())
                        if logout_flag:
                            print('111')
                            broadcast_data_offline(sock)
                            print(CONNECTION_DICT)
                            print(CONNECTION_LIST)
                    else:
                        print('222')
                        broadcast_data_offline(sock)
                        print(CONNECTION_DICT)
                        print(CONNECTION_LIST)
                except Exception as e:
                        print('333')
                        broadcast_data_offline(sock)
                        print(CONNECTION_DICT)
                        print(CONNECTION_LIST)
    server_socket.close()
