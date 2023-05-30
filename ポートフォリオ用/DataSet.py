import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import gspread
import pandas as pd
import time
import threading
import random
from oauth2client.service_account import ServiceAccountCredentials

#スプレッドシート関連
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
json = 'strl-380010-d9b3efdea4a1.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json, scope)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1vXe0TvwhgoOypM4xGF-fkQPYSNaLwTJVN06LmonCfoA'
workbook = gc.open_by_key(SPREADSHEET_KEY)
Fdatasheet = workbook.worksheet("Fユーザーデータ")
Ndatasheet = workbook.worksheet("Nユーザーデータ")
COMdatasheet = workbook.worksheet("コマンド登録")

JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
daytime = now.strftime('%Y/%m/%d %H:%M:%S')

#QPとレベルの対応用
qp_level = {"1":"3","2":"4","3":"5","4":"6","5":"7"}
#インスタンス名
numbers = 0
#ブラックリスト
blacklist = ["1076422611325702236","1093041645114622004","1032532645655105536","931562992041099275","1081170888063459368","872546782700273694","1066977490339373076","883332312484446229"]

# ID{名前, 報酬, 違約金, 判定回数}
bites_ID = {"n1":{"name":"`道路工事","reward":150,"fail":-100,"needs":5,"needs_suc":3,"type":"linear"},
            "n2":{"name":"`新聞配達","reward":200,"fail":-150,"needs":5,"needs_suc":3,"type":"serial"},
            "n3":{"name":"`事務業務","reward":150,"fail":-100,"needs":5,"needs_suc":3,"type":"linear"},
            "n4":{"name":"`下水管敷設","reward":150,"fail":-100,"needs":10,"needs_suc":6,"type":"linear"},
            "n5":{"name":"`キャバレー","reward":150,"fail":-100,"needs":10,"needs_suc":6,"type":"linear"},
            "n6":{"name":"`ホストクラブ","reward":200,"fail":-100,"needs":10,"needs_suc":6,"type":"linear"},
            "f1":{"name":"`運搬業務","reward":200,"fail":-100,"needs":5,"needs_suc":3,"type":"linear"},
            "f2":{"name":"`客引き","reward":100,"fail":-50,"needs":5,"needs_suc":3,"type":"linear"},
            "f3":{"name":"`手紙配達人","reward":100,"fail":-50,"needs":5,"needs_suc":3,"type":"linear"},
            "f4":{"name":"`魔導書複写業務","reward":200,"fail":-100,"needs":5,"needs_suc":3,"type":"linear"},
            }

description = '''テスト用botです'''
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?',  help_command = None, description=description, intents=intents)


class MakeList(discord.ui.View):
    def __init__(self,usr_id):
        super().__init__()
        self.add_item(CommandList(usr_id=usr_id))

class CommandList(discord.ui.Select): #セレクトメニューの選択肢を追加するクラス
    def __init__(self,usr_id):
        COM = pd.DataFrame(COMdatasheet.get_all_values()[1:],columns=COMdatasheet.get_all_values()[0])
        chatpaletts = COM[usr_id]
        options_list=[]
        for item in chatpaletts:
            options_list.append(discord.SelectOption(label=item, description=''))
    
        super().__init__(placeholder='', min_values=1, max_values=1, options=options_list)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```{self.values[0]}```", ephemeral=True)

class TrueButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label:str = "チャットパレット",usr_id):
        super().__init__(style=style, label=label, disabled=False)
        self.usr_id = usr_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=MakeList(self.usr_id), ephemeral=True)
        await interaction.message.delete()

def fantasia(usr_id):
    stopper = False
    while stopper == False: #ストッパーがFalseである限りループ
        print("ファンタジアループ開始")
        time.sleep(1800) #30分待つ
        Fdf = pd.DataFrame(Fdatasheet.get_all_values()[1:],columns=Fdatasheet.get_all_values()[0])
        Fdfa = Fdf.set_index("ユーザーID")
        current_stmn = int(Fdfa.at[usr_id,"スタミナ"]) #現在のスタミナ値を取得
        max_stmn = int(Fdfa.at[usr_id,"スタミナ上限"]) #スタミナ上限を取得
        if current_stmn == max_stmn: #現在値と上限が等しければ
            stopper = True
            break #ループを終了
        elif current_stmn == (max_stmn - 1): #上限-1が現在値であれば
            stopper = True
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            latest_stmn = current_stmn + 1
            Fdatasheet.update_cell(target_ind,target_clm,str(latest_stmn))
            break #ループ終了
        else:
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            latest_stmn = current_stmn + 1 #現在値に+1したものを更新
            Fdatasheet.update_cell(target_ind,target_clm,str(latest_stmn))

def nocturn(usr_id):
    stopper = False
    while stopper == False: #ストッパーがFalseである限りループ
        print("ノクターンループ開始")
        time.sleep(1800) #30分待つ
        Ndf = pd.DataFrame(Ndatasheet.get_all_values()[1:],columns=Ndatasheet.get_all_values()[0])
        Ndfa = Ndf.set_index("ユーザーID")
        current_stmn = int(Ndfa.at[usr_id,"スタミナ"]) #現在のスタミナ値を取得
        max_stmn = int(Ndfa.at[usr_id,"スタミナ上限"]) #スタミナ上限を取得
        if current_stmn == max_stmn: #現在値と上限が等しければ
            stopper = True
            break #ループを終了
        elif current_stmn == (max_stmn - 1): #上限-1が現在値であれば
            stopper = True
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            latest_stmn = current_stmn + 1
            Ndatasheet.update_cell(target_ind,target_clm,str(latest_stmn))
            break #ループ終了
        else:
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            latest_stmn = current_stmn + 1 #現在値に+1したものを更新
            Ndatasheet.update_cell(target_ind,target_clm,str(latest_stmn))
      

@bot.event
async def on_ready():
    print(f'Dataset.pyをログインしました: {bot.user} (ID: {bot.user.id})')
    print(daytime)
    qp_reset.start()
    #channel = bot.get_channel(1085309399955943454)
    #await channel.send(f"起動時間：{daytime}\nDataset.pyを起動しました。")
    print('------')

#QPリセット用
@tasks.loop(seconds=60)
async def qp_reset():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_HM = now.strftime('%H:%M')
    global numbers
    if now_HM == "00:01" or now_HM == "00:02":
        max = Ndatasheet.col_values(9)
        max_f = Fdatasheet.col_values(9)
        max.remove("QP上限")
        max.insert(0, "QP")
        max_f.remove("QP上限")
        max_f.insert(0, "QP")
        workbook.values_clear("'Fユーザーデータ'!H2:H10")
        workbook.values_clear("'Nユーザーデータ'!H2:H10")
        for i in range(len(max)):
            Ndatasheet.update_cell(i+1,8,max[i])
        for d in range(len(max_f)):
            Fdatasheet.update_cell(d+1,8,max_f[d])
        max.clear()
        max_f.clear()
        numbers = 0
    else:
        pass

#ブラックリストコマンド
@bot.command()
async def black(ctx, mode:str = "表示", ID:str=""):
    global blacklist
    if mode == "追加":
        blacklist.append(ID)
    elif mode == "削除":
        blacklist.remove(ID)
    elif mode == "表示":
        intel = ""
        for i in range(len(blacklist)):
            usr_id = int(blacklist[i])
            user = await bot.fetch_user(usr_id)
            intel += f"gather - {i}. ユーザー名:{user.name}{user.discriminator}\n "
        await ctx.send(intel)

@bot.command()
async def mail(ctx, msg:str="null"):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        return
    if msg == "null":
        await ctx.send("内容が未入力です")
        return
    channel = bot.get_channel(1099566886183763989)
    await channel.send(msg)

#キャラ登録コマンド
@bot.command()
async def register(ctx, world:str, name:str, money:str, stamina:str, level:str):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    
    Fdf = pd.DataFrame(Fdatasheet.get_all_values()[1:],columns=Fdatasheet.get_all_values()[0])
    Ndf = pd.DataFrame(Ndatasheet.get_all_values()[1:],columns=Ndatasheet.get_all_values()[0])
    if world == "f": #ファンタジアの場合
        if usr_id not in str(Fdf["ユーザーID"]): #ユーザーIDがFのユーザーIDに登録されていれば
            Fdatasheet.append_row(['null',usr_id,name,0,money,0,stamina,0,qp_level[level]])
            await ctx.send("> ファンタジア用キャラクター: "+name+"を登録しました。")
        else:
            await ctx.send("> 既に登録済みです")

    elif world == "n": #ノクターンの場合
        if usr_id not in str(Ndf["ユーザーID"]):
            #番号 | ID | 名前 | 所持金 | 最大資金 | スタミナ | 最大スタミナ | QP | 最大QP(レベル)
            Ndatasheet.append_row(['null',usr_id,name,0,money,0,stamina,0,qp_level[level]])
            await ctx.send("> ノクターン用キャラクター: "+name+"を登録しました。")
        else:
            await ctx.send("> 既に登録済みです")
    else:
        pass

#お金周り
@bot.command()
async def gold(ctx, world:str, credit:str, purpse:str = "無記載"):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        return
    Ndf = pd.DataFrame(Ndatasheet.get_all_values()[1:],columns=Ndatasheet.get_all_values()[0])
    Fdf = pd.DataFrame(Fdatasheet.get_all_values()[1:],columns=Fdatasheet.get_all_values()[0])
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    if usr_id in str(Ndf["ユーザーID"]) and world == "n":
        Ndfa = Ndf.set_index("ユーザーID")
        if "+" in credit: #入金の場合
            money = credit.replace("+","")
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 4
            current_money = int(Ndfa.at[usr_id,"ゴールド"]) + int(money)
            max_money = int(Ndfa.at[usr_id,"ゴールド上限"])
            if current_money > int(max_money):
                await ctx.send("`>資金上限です`")
            else:
                Ndatasheet.update_cell(target_ind,target_clm,str(current_money))
                await ctx.send(f"`>ノクターンで{money}Gを入金しました。`\n`現在所持金: {current_money}/{max_money} | 備考: {purpse}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 追加日時:{daytime}`")
        elif "-" in credit: #出金の場合
            money = credit.replace("-","")
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 4
            current_money = int(Ndfa.at[usr_id,"ゴールド"]) - int(money)
            max_money = int(Ndfa.at[usr_id,"ゴールド上限"])
            if current_money < 0:
                await ctx.send("`>お金が不足しています`")
            else:
                Ndatasheet.update_cell(target_ind,target_clm,str(current_money))
                await ctx.send(f"`>ノクターンで{money}Gを出金しました。`\n`現在所持金: {current_money}/{max_money} | 備考: {purpse}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 追加日時:{daytime}`")
        else:
            print("エラー")
            pass
    elif usr_id in str(Fdf["ユーザーID"]) and world == "f":
        Fdfa = Fdf.set_index("ユーザーID")
        if "+" in credit: #入金の場合
            money = credit.replace("+","")
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 4
            current_money = int(Fdfa.at[usr_id,"ゴールド"]) + int(money)
            max_money = Fdfa.at[usr_id,"ゴールド上限"]
            if current_money > int(max_money):
                await ctx.send("`>資金上限です`")
            else:
                Fdatasheet.update_cell(target_ind,target_clm,str(current_money))
                await ctx.send(f"`>ファンタジアで{money}Gを入金しました。`\n`現在所持金: {current_money}/{max_money} | 備考: {purpse}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 追加日時:{daytime}`")
        elif "-" in credit: #出金の場合
            money = credit.replace("-","")
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 4
            current_money = int(Fdfa.at[usr_id,"ゴールド"]) - int(money)
            max_money = Fdfa.at[usr_id,"ゴールド上限"]
            if current_money < 0:
                await ctx.send("`>お金が不足しています`")
            else:
                Fdatasheet.update_cell(target_ind,target_clm,str(current_money))
                await ctx.send(f"`>ファンタジアで{money}Gを出金しました。`\n`現在所持金: {current_money}/{max_money} | 備考: {purpse}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 追加日時:{daytime}`")
        else:
            print("エラー")
            pass
    else:
        print("未登録")
        await ctx.send("> 登録されていません")

#QP周り
@bot.command()
async def qp(ctx, world:str, qps:str, quest:str = "無記載"):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        return
    Ndf = pd.DataFrame(Ndatasheet.get_all_values()[1:],columns=Ndatasheet.get_all_values()[0])
    Fdf = pd.DataFrame(Fdatasheet.get_all_values()[1:],columns=Fdatasheet.get_all_values()[0])
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    #ノクターンの場合
    if usr_id in str(Ndf["ユーザーID"]) and world == "n":
        Ndfa = Ndf.set_index("ユーザーID")
        if "-" in qps: #消費の場合
            qp_num = qps.replace("-","")
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 8
            current_qp = int(Ndfa.at[usr_id,"QP"]) - int(qp_num)
            max_qp = int(Ndfa.at[usr_id,"QP上限"])
            if current_qp < 0:
                await ctx.send("`>QPが足りません`")
            else:
                Ndatasheet.update_cell(target_ind,target_clm,str(current_qp))
                await ctx.send(f"`>ノクターンのQPを{qp_num}消費しました。`\n`現在QP: {current_qp}/{max_qp} | 消費理由: {quest}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 消費日時:{daytime}`")
        elif "+" in qps: #回復の場合
            qp_num = qps.replace("+","")
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 8
            current_qp = int(Ndfa.at[usr_id,"QP"]) + int(qp_num)
            max_qp = int(Ndfa.at[usr_id,"QP上限"])
            if current_qp > max_qp:
                await ctx.send("`>既に全回復しています`")
            else:
                Ndatasheet.update_cell(target_ind,target_clm,str(current_qp))
                await ctx.send(f"`>ノクターンのQPを{qp_num}回復しました。`\n`現在QP: {current_qp}/{max_qp}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 回復日時:{daytime}`")
        else:
            pass
    #ファンタジアの場合
    elif usr_id in str(Fdf["ユーザーID"]) and world == "f":
        Fdfa = Fdf.set_index("ユーザーID")
        if "-" in qps: #消費の場合
            qp_num = qps.replace("-","")
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 8
            current_qp = int(Fdfa.at[usr_id,"QP"]) - int(qp_num)
            max_qp = int(Fdfa.at[usr_id,"QP上限"])
            if current_qp < 0:
                await ctx.send("`>QPが足りません`")
            else:
                Fdatasheet.update_cell(target_ind,target_clm,str(current_qp))
                await ctx.send(f"`>ファンタジアのQPを{qp_num}消費しました。`\n`現在QP: {current_qp}/{max_qp} | 消費理由: {quest}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 消費日時:{daytime}`")
        elif "+" in qps: #回復の場合
            qp_num = qps.replace("+","")
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 8
            current_qp = int(Fdfa.at[usr_id,"QP"]) + int(qp_num)
            max_qp = int(Fdfa.at[usr_id,"QP上限"])
            if current_qp > max_qp:
                await ctx.send("`>既に全回復しています`")
            else:
                Fdatasheet.update_cell(target_ind,target_clm,str(current_qp))
                await ctx.send(f"`>ファンタジアのQPを{qp_num}回復しました。`\n`現在QP: {current_qp}/{max_qp}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 回復日時:{daytime}`")
        else:
            pass
    else:
        await ctx.send("> 登録されていません")

#スタミナ周り
@bot.command()
async def stamina(ctx, world:str, stmn:str, purpse:str = "無記載"):
    global numbers
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        return
    Ndf = pd.DataFrame(Ndatasheet.get_all_values()[1:],columns=Ndatasheet.get_all_values()[0])
    Fdf = pd.DataFrame(Fdatasheet.get_all_values()[1:],columns=Fdatasheet.get_all_values()[0])
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    #ノクターンの場合
    if usr_id in str(Ndf["ユーザーID"]) and world == "n":
        Ndfa = Ndf.set_index("ユーザーID")
        if "-" in stmn: #消費の場合
            stmn_num = stmn.replace("-","")
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            current_stmn = int(Ndfa.at[usr_id,"スタミナ"]) - int(stmn_num)
            max_stmn = int(Ndfa.at[usr_id,"スタミナ上限"])
            if current_stmn < 0:
                await ctx.send("`>スタミナが足りません`")
            else:
                Ndatasheet.update_cell(target_ind,target_clm,str(current_stmn))
                await ctx.send(f"`>ノクターンのスタミナを{stmn_num}消費しました。`\n`現在スタミナ: {current_stmn}/{max_stmn} | 消費理由: {purpse}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 消費日時:{daytime}`")
                instance_name = str(numbers) #インスタンス名を設定
                instance_name = threading.Thread(target=nocturn, args=(usr_id,)) #インスタンス生成
                instance_name.start()
                numbers += 1 #インスタンス名用変数をインクリメント

        elif "+" in stmn: #回復の場合
            stmn_num = stmn.replace("+","")
            target_ind = (Ndfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            current_stmn = int(Ndfa.at[usr_id,"スタミナ"]) + int(stmn_num)
            max_stmn = int(Ndfa.at[usr_id,"スタミナ上限"])
            if current_stmn > max_stmn:
                await ctx.send("`>既に全回復しています`")
            else:
                Ndatasheet.update_cell(target_ind,target_clm,str(current_stmn))
                await ctx.send(f"`>ノクターンのスタミナを{stmn_num}回復しました。`\n`現在スタミナ: {current_stmn}/{max_stmn}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 回復日時:{daytime}`")
        else:
            print("エラー")
            pass
    #ファンタジアの場合
    elif usr_id in str(Fdf["ユーザーID"]) and world == "f":
        Fdfa = Fdf.set_index("ユーザーID")
        if "-" in stmn: #消費の場合
            stmn_num = stmn.replace("-","")
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            current_stmn = int(Fdfa.at[usr_id,"スタミナ"]) - int(stmn_num)
            max_stmn = int(Fdfa.at[usr_id,"スタミナ上限"])
            if current_stmn < 0:
                await ctx.send("`>スタミナが足りません`")
            else:
                Fdatasheet.update_cell(target_ind,target_clm,str(current_stmn))
                await ctx.send(f"`>ファンタジアのスタミナを{stmn_num}消費しました。`\n`現在スタミナ: {current_stmn}/{max_stmn} | 消費理由: {purpse}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 消費日時:{daytime}`")
                instance_name = str(numbers) #インスタンス名を設定
                instance_name = threading.Thread(target=fantasia, args=(usr_id,)) #インスタンス生成
                instance_name.start()
                numbers += 1 #インスタンス名用変数をインクリメント

        elif "+" in stmn: #回復の場合
            stmn_num = stmn.replace("+","")
            target_ind = (Fdfa.index.get_loc(usr_id)) + 2
            target_clm = 6
            current_stmn = int(Fdfa.at[usr_id,"スタミナ"]) + int(stmn_num)
            max_stmn = int(Fdfa.at[usr_id,"スタミナ上限"])
            if current_stmn > max_stmn:
                await ctx.send("`>既に全回復しています`")
            else:
                Fdatasheet.update_cell(target_ind,target_clm,str(current_stmn))
                await ctx.send(f"`>ファンタジアのスタミナを{stmn_num}回復しました。`\n`現在スタミナ: {current_stmn}/{max_stmn}`")
                await ctx.send(f"`使用者名:{ctx.author.display_name} | 回復日時:{daytime}`")
        else:
            pass

@bot.command()
async def status(ctx, world:str):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    Ndf = pd.DataFrame(Ndatasheet.get_all_values()[1:],columns=Ndatasheet.get_all_values()[0])
    Fdf = pd.DataFrame(Fdatasheet.get_all_values()[1:],columns=Fdatasheet.get_all_values()[0])
    if usr_id in str(Ndf["ユーザーID"]) and world == "n":
        Ndfa = Ndf.set_index("ユーザーID")
        JST = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(JST)
        daytime = now.strftime('%Y/%m/%d %H:%M:%S')
        embed_title=discord.Embed(title=f"ステータス:"+(Ndfa.at[usr_id,"名前"]),
                            description="```こちらはノクターンキャラのステータスです```",
                            color=0xFFFFFF) 
        embed_title.add_field(name="`所持金:`", value=(Ndfa.at[usr_id,"ゴールド"])+"/"+(Ndfa.at[usr_id,"ゴールド上限"]), inline=True)
        embed_title.add_field(name="`スタミナ:`", value=(Ndfa.at[usr_id,"スタミナ"])+"/"+(Ndfa.at[usr_id,"スタミナ上限"]), inline=True)
        embed_title.add_field(name="`QP:`", value=(Ndfa.at[usr_id,"QP"])+"/"+(Ndfa.at[usr_id,"QP上限"]), inline=True)
        embed_title.set_footer(text=f"Made by まよなか | {daytime}")
        await ctx.send(embed=embed_title)
    elif usr_id in str(Fdf["ユーザーID"]) and world == "f":
        Fdfa = Fdf.set_index("ユーザーID")
        JST = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(JST)
        daytime = now.strftime('%Y/%m/%d %H:%M:%S')
        embed_title=discord.Embed(title=f"ステータス:"+(Fdfa.at[usr_id,"名前"]),
                            description="```こちらはファンタジアキャラのステータスです```",
                            color=0xFFFFFF) 
        embed_title.add_field(name="`所持金:`", value=(Fdfa.at[usr_id,"ゴールド"])+"/"+(Fdfa.at[usr_id,"ゴールド上限"]), inline=True)
        embed_title.add_field(name="`スタミナ:`", value=(Fdfa.at[usr_id,"スタミナ"])+"/"+(Fdfa.at[usr_id,"スタミナ上限"]), inline=True)
        embed_title.add_field(name="`QP:`", value=(Fdfa.at[usr_id,"QP"])+"/"+(Fdfa.at[usr_id,"QP上限"]), inline=True)
        embed_title.set_footer(text=f"Made by まよなか | {daytime}")
        await ctx.send(embed=embed_title)
    else:
        await ctx.send("`未登録です`")

#バイトコマンド
@bot.command()
async def part(ctx, bytes:str, skill:str, num:str, sup:str = "No"):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    results = "" #結果格納用
    rewards = 0 #報酬G
    #1回毎に使用
    isolated_results = ""
    succes = 0 #各バイトごと成功回数
    TF = "default"
    TF_final = "default"
    if int(num) > 5:
        await ctx.send("5回以上は行えません")
        return
    if usr_id in blacklist:
        return
    for i in range(int(num)): #バイトを行う回数
        for b in range(bites_ID[bytes]["needs"]):
            target = random.randrange(1,101,1)
            print(target)
            if target < int(skill)-5: #判定結果が目標値以下もしくは同値
                TF = "成功"
                isolated_results += "成功"
                succes += 1
            elif 96 > target > int(skill): #判定結果が目標値以上
                TF = "失敗"
                isolated_results += "失敗"
            elif target == 100:
                TF = "100ファン"
                isolated_results += "ファンブル"
                break
            elif target >= 96: #判定結果が96と同じかそれ以上
                TF = "ファンブル"
                isolated_results += "ファンブル"
                break
            elif int(skill)-5 <= target <= int(skill): #判定結果がスキル-5とスキル値の範囲であれば
                TF = "クリティカル"
                isolated_results += "クリティカル"
                break
            if bites_ID[bytes]["type"] == "linear" and succes == bites_ID[bytes]["needs_suc"]: #判定方式が通常であり3回成功していればBreak
                break
        
        print(isolated_results)
        print("----")
        if bites_ID[bytes]["type"] == "linear": #判定方式が通常型であれば
            if succes == bites_ID[bytes]["needs_suc"] or TF == "クリティカル":
                rewards += bites_ID[bytes]["reward"]
                TF_final = "成功"
            elif TF == "100ファン" and sup != "sp": #100ファンでかつスペシャリストではない
                rewards += (bites_ID[bytes]["fail"]) * 2
                TF_final = "100ファン"
            elif "ファン" in TF and sup != "sp": #ファンブルでかつスペシャリストではない
                rewards += (bites_ID[bytes]["fail"]) * 2
                TF_final = "ファンブル"
            elif "ファン" in TF and sup == "sp": #ファンブルでかつスペシャリストであれば
                rewards += bites_ID[bytes]["reward"]
                TF_final = "スペシャリストによりクリティカル"
            elif succes == bites_ID[bytes]["needs_suc"] -1 and sup == "sp": #もしスペシャリストで、後1回で成功なら
                rewards += bites_ID[bytes]["reward"]
                TF_final = "スペシャリストにより成功"
            else:
                rewards += bites_ID[bytes]["fail"]
                TF_final = "失敗"

        elif bites_ID[bytes]["type"] == "serial": #判定方式が連続型であれば
            if "成功成功成功" in isolated_results or TF == "クリティカル": #3連続で成功しているかクリティカルであれば
                rewards += bites_ID[bytes]["reward"]
                TF_final = "成功"
            elif TF == "100ファン" and sup != "sp": #100ファンでかつスペシャリストではない
                rewards += (bites_ID[bytes]["fail"]) * 2
                TF_final = "100ファン"
            elif TF == "ファンブル" and sup != "sp": #ファンブルでかつスペシャリストではない
                rewards += (bites_ID[bytes]["fail"]) * 2
                TF_final = "ファンブル"
            elif TF == "ファンブル" and sup == "sp": #ファンブルでかつスペシャリストであれば
                rewards += bites_ID[bytes]["reward"]
                TF_final = "スペシャリストによりクリティカル"
            elif "成功成功" in isolated_results and sup == "sp": #もしスペシャリストで、後1回で成功なら
                rewards += bites_ID[bytes]["reward"]
                TF_final = "スペシャリストにより成功"                
            else:
                rewards += bites_ID[bytes]["fail"]
                TF_final = "失敗"

        formated = str(i+1) +"回目: " + TF_final + "\n"
        results += formated
        succes = 0
        isolated_results = ""
    #バイト判定がすべて終わったら結果を送信
    await ctx.reply("```"+results+"```")
    await ctx.send(bites_ID[bytes]["name"]+f" | 報酬: {rewards}`")


bot.run("TOKEN")
