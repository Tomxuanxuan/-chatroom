from tkinter import *

import time
import random
import json
from tkinter import messagebox
import os
import sys

from model.model import *
import threading
from PIL import Image
from PIL import ImageTk


class mainchat():
    def __init__(self, window, user_level, user_info, client):
        self.window = window
        self.user_level = user_level
        # 当前登录用户信息 username
        load_user = eval(user_info)
        self.user_info = {'user_id': load_user['user_id'], 'username':load_user['username']}    #当前登录用户
        self.friends = load_user['friends'] #登录用户好友

        self.window.title('聊天窗口')  # 窗口名称
        self.window.geometry("795x530")
        # self.window.resizable(0, 0)  # 禁止调整窗口大小
        self.window.attributes("-alpha", 1)    #设置窗口的透明度,1为不透明，0为完全透明
        self.window.config(background = "pink") #背景色
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # 设置窗口图标
        # self.window.iconbitmap('spider_128px_1169260_easyicon.net.ico')

        self.client = client    #保存客户端连接信息

        self.recv_user_info = {}    #保存收消息用户信息
        self.note_info = ''

        ###******创建frame容器******###

        # 第一列
        frmA1 = Frame(width=209, height=30)
        frmA2 = Frame(width=209, height=500)
        # frmA3 = Frame(width=240, height=140)
        # frmA4 = Frame(width=240, height=30)
        # 第二列
        frmB1 = Frame(width=385, height=330)
        frmB2 = Frame(width=385, height=200)
        # frmB3 = Frame(width=360, height=30, background='blue')
        # 第三列
        frmC1 = Frame(width=200, height=30)
        frmC11 = Frame(width=200, height=400)
        frmC12 = Frame(width=200, height=200,)

        ###******创建frame容器******###

        ###******创建控件******###

        # A1,A3
        self.nameLabel = Label(frmA1, text='联系人', font="Times 16 bold italic")

        self.scroLianxi = Scrollbar(frmA2, width=12, troughcolor="blue")

        # Listbox控件
        self.listLianxi = Listbox(frmA2, width=22, height=24,
                                  yscrollcommand=self.scroLianxi.set)  # 连接listbox 到 vertical scrollbar

        # B1,B2Text控件
        self.txtMsgList = Text(frmB1, width=52, height=22 ,background='LightBlue',
highlightcolor='white')  # frmB1表示父窗口
        self.scroMsgList = Scrollbar(frmB1, width=12, command=self.txtMsgList.yview)

        self.txtMsgList.config(yscrollcommand=self.scroMsgList.set)

        # 创建并配置标签tag属性
        self.txtMsgList.tag_config('redcolor',  # 标签tag名称
                              foreground='#FF4500')  # 标签tag前景色，背景色为默认白色

        self.txtMsg = Text(frmB2, width=54, height=10, background='LightCyan', highlightcolor='LightCyan')
        self.txtMsg.bind("<KeyPress-Return>", self.sendMsgEvent)  # 事件绑定，定义快捷键

        # Button控件
        self.btnSend = Button(frmB2, text='发 送', width=8, cursor='heart', command=self.sendMsg)
        self.btnCancel = Button(frmB2, text='取消', width=8, cursor='shuttle', command=self.cancelMsg)

        #C1,C11
        self.label_friend = Label(frmC1, text='通知', font="Times 16 bold italic")

        self.txtLabel = Label(frmC11, justify='left', wraplength=200)  # wraplength达到多少宽度后换行
        filepath = 'static/images/' + str(random.randint(1, 35)) + '.png'
        # img_gif = self.getImageWidget(filepath)
        global img_gif
        img_gif = PhotoImage(file=filepath)
        self.label_img = Label(frmC12, image=img_gif)




        # 好友（管理员是所有用户）
        self.all_users = self.friends

        # [{'id': 1, 'name': 'admin', 'niname': '管理员'}, {'id': 2, 'name': 'xixi', 'niname': '西西'},
        #  {'id': 3, 'name': 'xp', 'niname': '小平'}, {'id': 4, 'name': 'xw', 'niname': '小汪'}]

        for user in self.all_users:
            self.listLianxi.insert(END, str(user['niname'] + '--' + user['name']))
            self.listLianxi.see(END)

        self.scroLianxi.config(command=self.listLianxi.yview)  # scrollbar滚动时listbox同时滚动

        # 为选中的用户绑定双击事件
        self.listLianxi.bind("<Double-Button-1>", self.listLianxi_show_msg)



        ###******创建控件******###

        ###******窗口布局******###

        frmA1.grid(row=0, column=0 )
        frmA2.grid(row=1, column=0, rowspan=2, sticky=N)

        frmB1.grid(row=0, column=1, rowspan=2, sticky=W)
        frmB2.grid(row=2, column=1,  sticky=N, rowspan=1)
        # frmB3.grid(row=3, column=1,  sticky=W, ipady=20)

        frmC1.grid(row=0, column=2)
        frmC11.grid(row=1, column=2, rowspan=2, sticky=N)
        frmC12.grid(row=2, column=2, rowspan=1)

        ###******窗口布局******###

        # 固定大小
        frmA1.grid_propagate(0)
        frmA2.grid_propagate(0)
        # frmA3.grid_propagate(0)
        # frmA4.grid_propagate(0)

        frmB1.grid_propagate(0)
        frmB2.grid_propagate(0)
        # frmB3.grid_propagate(0)

        frmC1.grid_propagate(0)
        frmC11.grid_propagate(0)
        frmC12.grid_propagate(0)
        # frmC2.grid_propagate(0)
        # frmC3.grid_propagate(0)

        ###******控件布局******###
        self.label_friend.grid()
        self.txtMsg.grid(row=0, column=0, columnspan=4)
        self.btnSend.grid(row=1, column=2, sticky=E, pady=5, ipady=3)
        self.btnCancel.grid(row=1, column=3, sticky=W, pady=5, ipady=3)
        # self.btnSerch.grid(row=0, column=1)

        self.nameLabel.grid()
        # self.sizeLabel.grid(row=0, column=0)

        self.txtMsgList.grid(row=0, column=0)
        self.scroMsgList.grid(row=0, column=1, ipady=134, sticky=N)
        self.txtMsg.grid()

        # self.entrySerch.grid(row=0, column=0)

        self.scroLianxi.grid(row=0, column=1, ipady=175, sticky=N)

        self.listLianxi.grid(row=0, column=0, sticky=N)

        # self.scroFriend.grid(row=0, column=1, ipady=22)
        # self.listFriend.grid(row=0, column=0)


        self.txtLabel.grid(row=1, column=0, sticky=W)
        self.label_img.grid(row=0, column=0, sticky=E)


        threading.Thread(target=self.showinfo).start()

    def showinfo(self):
        '''接收消息'''
        while True:
            data = self.client.recv(2048)
            decode_data = data.decode()
            print('接收到消息', data)
            if decode_data:
                if decode_data.startswith('system'):
                    #处理系统消息
                    print('系统消息', decode_data)
                    self.txtLabel_show_info(decode_data)
                if decode_data.startswith('records'):
                    #处理历史记录消息
                    res_message = decode_data.split(':*:')[1]
                    print('res', res_message)
                    records_messages = eval(res_message)
                    print(records_messages)
                    for record in records_messages:
                        user_name = record['user_name']
                        send_time = record['send_time']
                        content = record['content']
                        info = '\n'+user_name + '  ' + send_time + '\n' + content
                        self.txtMsgList.insert(END, info, 'greencolor')  # 在结尾插入信息
                else:
                    print('进入这里', decode_data)
                    json_de_data = json.loads(decode_data)
                    send_username = json_de_data['send_user']['username']
                    send_time = json_de_data['send_time']
                    content = json_de_data['content']
                    res = "{0} {1}:\n{2}\n".format(send_username, send_time, content)
                    print(res)
                    self.txtMsgList.insert(END, res, 'redcolor')  # 在结尾插入信息
                    self.txtMsgList.see(END)    #保证滚动条在最下面
            else:
                break



    def listLianxi_show_msg(self, ev):
        '''右侧 label显示选中的用户，消息栏显示未读消息'''
        print('选择的用户')
        key = self.listLianxi.curselection()[0]
        recv_user = self.listLianxi.get(key)
        recv_user_name = recv_user.split('--')[-1]

        print('recv_user_name', recv_user_name)
        self.recv_user_info = recv_user_name
        self.nameLabel.config(text='%s' % recv_user)

        self.txtMsgList.delete(1.0, END)  # 清空消息框

        #发送消息让查询历史记录
        # self.get_user_message(recv_user_name)


    def get_user_message(self, recv_user_name):
        '''
        查询历史记录
        :param recv_user_name:
        :return:
        '''
        message = 'records:*:' + recv_user_name
        self.client.send(message.encode())


    def sendMsg(self):  # 发送消息
        send_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        send_msg = self.txtMsg.get('0.0', END)
        print('发送的消息', send_msg)
        values = {}
        #发送消息信息
        values['send_user'] = self.user_info    #登录用户信息
        values['recv_user'] = self.recv_user_info   #用户昵称

        values['content'] = send_msg.strip()    #发送的消息
        values['send_time'] = send_time #发送消息的时间
        print(values)

        if values['content']:   #只能发送非空消息
            if not self.recv_user_info:
                # 未选择用户
                messagebox.showinfo("错误", "未选择发送用户！！")
            else:
                # 发送数据到服务器
                message = 'msg:*:' + str(values)
                self.client.send(message.encode())
                res = "{0} {1}:\n{2}\n".format(self.user_info['username'], send_time, send_msg.strip())
                self.txtMsgList.insert(END, res, 'red')
                self.txtMsgList.see(END)
                self.txtMsg.delete(1.0, END)  #清空输入框

    def txtLabel_show_info(self, sysinfo):
        '''右侧标签显示系统消息'''
        res = sysinfo.split(':*:')
        time_now = time.strftime("%H:%M ", time.localtime())
        self.note_info += (time_now+res[-1] + '\n')
        note_list = self.note_info.split('\n')

        if len(note_list) >= 19:
            self.note_info = note_list[-2] + '\n'

        self.txtLabel.configure(text=self.note_info)

    def getImageWidget(self, filepath):
        '''
        获取图片对象
        :param filepath: 图片路径
        :return:
        '''
        global img
        if os.path.exists(filepath) and os.path.isfile(filepath):
            img = Image.open(filepath)
            print(img)
            print(img.size)
            img = ImageTk.PhotoImage(img)
            return img

    def on_closing(self):
        '''
        关闭窗口调用
        :return:
        '''
        message = 'logout:*:' + str(self.user_info)
        print('on_closing', message)
        self.client.send(message.encode())
        self.window.destroy()
        sys.exit(0)



    def cancelMsg(self):  # 取消消息
        self.txtMsg.delete('0.0', END)

    def sendMsgEvent(self, ev):  # 发送消息事件
        if ev.keysym == "Return":  # 按回车键可发送
            self.sendMsg()



    def message(self):  # 弹出窗口
        messagebox.showinfo("联系人搜索", "这是一个假的功能！！")





