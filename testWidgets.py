import tkinter as tk
from tkinter import messagebox
from config.baseconfig import server_address, server_port
from socket import *

# from chatroom import main
# from chatroom import main
from chatroom import mainchat

# 设置窗口居中
def window_info():
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws / 2) - 200
    y = (hs / 2) - 200
    print("%d,%d" % (ws, hs))
    return x, y


# 设置登陆窗口属性
window = tk.Tk()
window.title('QICQ程序')
a, b = window_info()
window.geometry("450x300+%d+%d" % (a, b))

# 登陆界面的信息
tk.Label(window, text="QICQ聊天程序", font=("宋体", 32)).place(x=80, y=50)
tk.Label(window, text="账号：").place(x=120, y=150)
tk.Label(window, text="密码：").place(x=120, y=190)
# 显示输入框
var_usr_name = tk.StringVar()
# 显示默认账号
var_usr_name.set('jin')
entry_usr_name = tk.Entry(window, textvariable=var_usr_name)
entry_usr_name.place(x=190, y=150)
var_usr_pwd = tk.StringVar()
# 设置输入密码后显示*号
entry_usr_pwd = tk.Entry(window, textvariable=var_usr_pwd, show='*')
entry_usr_pwd.place(x=190, y=190)

user_level = 'public'

def get_info():
    '''获取返回信息'''
    while True:
        data = client.recv(2048)
        # system: login\nsuccess: % s
        print('获取到信息', data.decode())
        # login:*:success:*:username
        msg = data.decode().strip().split(':*:')
        if msg[0] == 'login':
            if msg[1] == 'success':
                #超级用户
                if msg[-1] == 'super':
                    print('super')
                    global user_level
                    user_level = 'super'

                #{'user_id': 1, 'username': 'admin', 'niname': '管理员'}
                user_info = msg[2]

                tk.Frame(window).destroy()
                mainchat(window, user_level, user_info, client)

            else:
                messagebox.showinfo(title='错误', message='用户名或密码不正确')
            break

    # window.destroy()
    # main()


# 登陆函数
def usr_login():
    print('登录')
    # # 获取输入的账号密码
    usr_name = var_usr_name.get()
    usr_pwd = var_usr_pwd.get()

    if not usr_name or not usr_pwd:
        messagebox.showinfo(title='调皮', message='用户名或密码不能为空')
    else:
        #封装消息
        message = 'login:*:' + usr_name + ':*:' + usr_pwd + ':*:' + str(ip)
        client.send(message.encode())

        get_info()


# 注册账号
def usr_sign_up():
    print('注册')
    # def sign_to_Pyhon():
    #     np = new_pwd.get()
    #
    # npc = new_pwd_confirm.get()
    # nn = new_name.get()
    #
    # dicts = SQL.load('login')
    # print(dicts)
    # bool = False
    # for row in dicts:
    #     if nn == row["name"]:
    #         bool = True
    #     print(row)
    # if np != npc:
    #     tk.messagebox.showerror('对不起', '两次密码输入不一致！')
    # elif bool:
    #     tk.messagebox.showerror(('对不起', '此账号已经存在!'))
    # else:
    #     try:
    #         SQL.insert_login(str(nn), str(np))
    #     tk.messagebox.showinfo('Welcome', '您已经注册成功！')
    #     except:
    #     tk.messagebox.showerror(('注册失败!'))
    #     window_sign_up.destroy()
    # 创建top窗口作为注册窗口
    window_sign_up = tk.Toplevel(window)
    window_sign_up.geometry('350x200')
    window_sign_up.title('注册')

    new_name = tk.StringVar()
    new_name.set('1400370115')
    tk.Label(window_sign_up, text='账号:').place(x=80, y=10)
    entry_new_name = tk.Entry(window_sign_up, textvariable=new_name)
    entry_new_name.place(x=150, y=10)

    new_pwd = tk.StringVar()
    tk.Label(window_sign_up, text='密码:').place(x=80, y=50)
    entry_usr_pwd = tk.Entry(window_sign_up, textvariable=new_pwd, show='*')
    entry_usr_pwd.place(x=150, y=50)

    new_pwd_confirm = tk.StringVar()
    tk.Label(window_sign_up, text='再次输入:').place(x=80, y=90)
    entry_usr_pwd_again = tk.Entry(window_sign_up, textvariable=new_pwd_confirm, show='*')
    entry_usr_pwd_again.place(x=150, y=90)

    btn_again_sign_up = tk.Button(window_sign_up, text='注册', command=sign_to_Pyhon)
    btn_again_sign_up.place(x=160, y=130)


# 登陆和注册按钮
btn_login = tk.Button(window, text="登陆", command=usr_login)
btn_login.place(x=170, y=230)
btn_sign_up = tk.Button(window, text="注册", command=usr_sign_up)
btn_sign_up.place(x=270, y=230)


if __name__ == '__main__':
    #连接服务器
    try:
        client = socket(AF_INET, SOCK_STREAM)
        client.connect((server_address, server_port))
        print('client:', client)
        ip = client.getsockname()    #获取本机ip地址
        print(ip)
    except:
        client.close()

    window.mainloop()
