
import discord
import japanize_matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
from discord.ext import tasks
from discord.ext.commands import Bot
import asyncio

#リセットする必要なし
graph_user = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,1,8,6,3,3,1,8]
graph_msg = [0,0,0,0,0,0,0,0,0,0,0,11,16,132,162,5,119,302,760,546,337,371,423,889]
day = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
#リセットする必要あり
msg_num = 0
active_users = 0
users = {}
alerdy = False
alerdy_ref = False
#1時間ごとにリセット
msg_1hr = 0
users_1hr = 0
users_1hr_temp = {}


description = '''テスト用botです'''
JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
daytime = now.strftime('%Y/%m/%d %H:%M:%S')

intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?',  help_command = None, description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'active.pyをログインしました: {bot.user} (ID: {bot.user.id})')
    print(daytime)
    loop.start()
    loop2.start()
    channel = bot.get_channel(1085309399955943454)
    await channel.send(f"起動時間：{daytime}\nactive.pyを起動しました。\nV1.2")
    print('------')


@tasks.loop(seconds=60)
async def loop2():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    now_M = now.strftime('%M')
    global msg_num,active_users,graph_user,graph_msg,alerdy_ref,msg_1hr,users_1hr,users_1hr_temp
    if now_M == "55" or now_M == "56": #もし55分か56分であれば
        users_1hr_listed = users_1hr * 40
        graph_user.append(users_1hr_listed) #ユーザー数配列の最後尾に現在の値を追加
        graph_msg.append(msg_1hr) #メッセージ数配列の最後尾に現在の値を追加
        channel = bot.get_channel(1085309399955943454)
        await channel.send(f"`現在時刻:{daytime}`\n1時間のユーザー数:{users_1hr}\n1時間のメッセージ数:{msg_1hr}\n累計ユーザー数:{active_users}\n累計メッセージ数:{msg_num}")
        del graph_msg[0]    #メッセージ数リストの最初を削除
        del graph_user[0]  #ユーザー数リストの最初を削除
        msg_1hr = 0
        users_1hr = 0
        users_1hr_temp.clear()
        await asyncio.sleep(120)
    else:
        pass

@tasks.loop(seconds=60)
async def loop():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_HM = now.strftime('%H:%M')
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')

    #グローバル変数宣言
    global day,msg_num,active_users,graph_user,graph_msg,alerdy

    #アクティブユーザー数
    x = day
    y = graph_user

    #メッセージ数
    x2 = day
    y2 = graph_msg

    channel = bot.get_channel(1003852099408371742) #チャンネルを指定
    print(now_HM)
    
    if now_HM == "23:58" or now_HM == "23:59": #現在時刻が23時58分もしくは59分なら
        fig = plt.figure(figsize=(9,5)) #図のサイズを指定
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0
        plt.title("Active Users and Messages",size = 20, color = "black")#グラフタイトル
        plt.title(daytime,loc="right", size = 10)#グラフタイトル
        plt.grid()  # グリッド線の表示 

        plt.text(23.4, 1000, '25人', ha='left', va='center') #バブル用文字列
        plt.text(23.4, 800, '20人', ha='left', va='center') #好景気用文字列
        plt.text(23.4, 600, '15人', ha='left', va='center') #通常用文字列
        plt.text(23.4, 400, '10人', ha='left', va='center') #不景気用文字列
        plt.text(23.4, 200, '5人', ha='left', va='center') #暴落用文字列
        plt.text(23.4, 0, '0人', ha='left', va='center') #大恐慌文字列

        plt.plot(x,y,label="ユーザー数",lw=1,color="r") #グラフ作成
        plt.plot(x2,y2,label="メッセージ数",lw=1,color="green") #グラフ作成
        plt.fill_between(x2, y2,0,alpha=0.2,color="green")
        plt.yticks(range(0, 1400, 200)) #y軸の数値を設定
        plt.xticks([23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]) 
        plt.tick_params(axis="y", colors="g", labelsize=12)
        plt.legend(loc='lower left', bbox_to_anchor=(1, 1)) #ラベルを表示
        plt.savefig('active.png', bbox_inches='tight')
        plt.clf()
        plt.close()

        file = discord.File("active.png", filename="active.png")
        embed=discord.Embed(title=f"Active User Report:{daytime}",
                    description="",
                    color=0x6E6636)
        embed.set_footer(text="Made by mayonaka | " + daytime)
        embed.add_field(name="`アクティブユーザー数:`", value=active_users)
        embed.add_field(name="`ユーザーメッセージ数:`", value=msg_num)
        await channel.send(file=file,embed=embed)
        users.clear()
        active_users = 0
        msg_num = 0
        await asyncio.sleep(120)
    else:
        pass


@bot.event #メッセージを受信した際に起動
async def on_message(message):
    global msg_num, active_users,users_1hr,msg_1hr
    usr_id = message.author.id
    bot_id = ["261302296103747584","1016794326115823708","978980960311844904"]
    print(usr_id)
    print(users.keys())
    if message.author == bot.user or str(usr_id) in bot_id:
        return
    elif usr_id not in users.keys(): #メッセージの送信者がユーザーであり、かつその日の発言が初めてであれば
        msg_num += 1 #メッセージ計測数を1増やす
        msg_1hr += 1
        users[usr_id] = 1 #ユーザー辞書にIDを追加
        users_1hr_temp[usr_id] = 1
        print(msg_num)
        print("初めての発言判定")
    elif usr_id in users.keys():
        msg_num += 1 #メッセージ計測数を1増やす
        msg_1hr += 1
        users[usr_id] += 1 #ユーザー辞書の発言数を1増やす
        print(msg_num)
        print("すでに発言した判定")
        if usr_id in users_1hr_temp.keys():
            users_1hr_temp[usr_id] += 1
        elif usr_id not in users_1hr_temp.keys():
            users_1hr_temp[usr_id] = 1
        if users[usr_id] == 100: #そのユーザーの発言数が100に達したら
            active_users += 1 #アクティブユーザー数を1増やす
            print("100回に到達した判定")
        if users_1hr_temp[usr_id] == 50: #1日のユーザーID集計に既に記録されていて、かつ1時間区切りのリストの発言数が100になったら
            users_1hr += 1 #1時間区切りのアクティブユーザー数を1増やす
        else:
            pass
    else:
        pass
        

bot.run('TOKEN')