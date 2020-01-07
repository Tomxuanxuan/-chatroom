
#对数据库进行操作
from config.baseconfig import db_name, db_password, db_user,db_host
import pymysql

class GetDBConnect():
    def __init__(self,  userid):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        # self.username = username    #登录用户名
        self.user_id = userid

        self.db_conn = pymysql.connect(self.db_host, self.db_user,self.db_password, self.db_name)


    def get_all_users(self):
        '''获取所有用户，结果返回[xx,xx]'''
        sql = "SELECT * FROM USER"
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()

        all_users = []

        for result in results:
            res = {}
            res['id'] = result[0]
            res['name'] = result[1]    #用户名
            res['niname'] = result[3]
            res['address'] = result[7]
            all_users.append(res)
        return all_users

    def get_friend_users(self):
        '''普通用户，获取朋友'''
        print('get_friend_users')
        sql = "SELECT * FROM friend WHERE user_id = '%i'" % self.user_id
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()

        res_name = []
        all_users = []
        for result in results:
            friend_id = result[2]
            sql = "SELECT * FROM USER WHERE id=%i" % friend_id
            # sql = "SELECT * FROM USER"
            cursor.execute(sql)
            results2 = cursor.fetchall()
            for result in results2:
                res = {}
                res['id'] = result[0]
                res['name'] = result[1]  # 用户名
                res['niname'] = result[3]
                res['address'] = [7]
                all_users.append(res)
        return all_users

    def save_login_info(self, values):
        '''登录用户保存 ip 地址等信息'''
        # {'user_id': 1, 'username': 'admin', 'niname': '管理员', 'ip': '127.0.0.1'}
        print('save_login_info')
        user_id = values['user_id']
        ip = values['ip']

        sql = "UPDATE USER SET address=\"%s\", is_online=%i WHERE id=%i" % (ip, True, user_id)
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        self.db_conn.commit()


    def save_chat_message(self, values):
        '''保存聊天信息'''
        # {'send_user': {'user_id': 1, 'username': 'admin', 'niname': '管理员'},
        #  'recv_user': {'id': 2, 'name': 'xixi', 'niname': '西西'}, 'content': '123qwe',
        #  'send_time': '2019-10-20 18:51:23'}
        recv_name = values['recv_user']
        recv_id = self.get_recv_user(recv_name)[0]['id']

        insert_info = (values['send_user']['user_id'], values['send_user']['username'], recv_id, recv_name, values['content'], values['send_time'])
        sql = 'INSERT INTO CONTENT (SEND_ID, SEND_NAME, RECIVE_ID, RECIVE_NAME, MESSAGE, CREATE_TIME) VALUE {0}'.format(insert_info)

        try:
            cursor = self.db_conn.cursor()
            cursor.execute(sql)
            self.db_conn.commit()   #提交

        except Exception as e:
            print('保存数据失败', e)
            self.db_conn.rollback()
            return False
        print('保存成功')
        return recv_id

    def get_user_message(self, recv_user_name):
        '''获取用户消息'''
        sql = 'SELECT * FROM CONTENT WHERE RECIVE_NAME = \'{0}\' OR SEND_NAME =\'{1}\''.format(recv_user_name, recv_user_name)
        cursor = self.db_conn.cursor()
        cursor.execute(sql)

        results = cursor.fetchall()

        return results

    def get_recv_user(self, recv_user_name):
        '''获取用户信息'''
        sql = 'SELECT * FROM USER WHERE USERNAME = \'{0}\' '.format(recv_user_name)
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()

        all_users = []
        res = {}
        res['id'] = result[0]
        res['name'] = result[1]  # 用户名
        res['niname'] = result[3]
        res['address'] = result[7]
        all_users.append(res)

        return all_users


