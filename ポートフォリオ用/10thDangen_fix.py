import discord
import random
import openpyxl
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands

#Excel参照
book = openpyxl.load_workbook('excel/10thDangen.xlsx')
event = openpyxl.load_workbook('excel/Event.xlsx')
active_sheet = book.worksheets[0]
floor2 = book.worksheets[1]
floor3 = book.worksheets[2]
floor4 = book.worksheets[3]
floor5 = book.worksheets[4]
floor6 = book.worksheets[5]
floor7 = book.worksheets[6]
floor8 = book.worksheets[7]
floor9 = book.worksheets[8]
floor10 = book.worksheets[9]
event_sheet = event.active

JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
dad = now.date().strftime('%Y/%m/%d')
daytime = now.strftime('%Y/%m/%d %H:%M:%S')

#ダンジョン探索結果参照用
DList = ["B2","B3","B4","B5","B6","B7","B8","B9","B10","B11","B12","B13","B14","B15","B16","B17","B18","B19","B20","B21","B22","B23","B24","B25","B26","B27","B28","B29","B30","B31","ev1","ev2","ev3","ENY1","ENY2","ENY3","ENY4","ENY5","ENY6","ENY7","ENY8","ENY9","ENY10"]
Elist = ["B50", "B50","C50","C50", "D50", "E50","E50", "F50","F50"]
BList = ["B51","B51","B51","C51","C51","C51","D51","E51","E51","E51","F51","F51","F51"]
EvntList = {"ev11":{"T":"B2","F":"B3"},"ev12":{"T":"B4","F":"B5"},"ev13":{"T":"B6","F":"B7"},
            "ev21":{"T":"B8","F":"B9"},"ev22":{"T":"B10","F":"B11"},"ev23":{"T":"B12","F":"B13"},
            "ev31":{"T":"B14","F":"B15"},"ev32":{"T":"B16","F":"B17"},"ev33":{"T":"B18","F":"B19"},
            "ev41":{"T":"B20","F":"B21"},"ev42":{"T":"B22","F":"B23"},"ev43":{"T":"B24","F":"B25"},
            "ev51":{"T":"B26","F":"B27"},"ev52":{"T":"B28","F":"B29"},"ev53":{"T":"B30","F":"B31"},
            "ev61":{"T":"B32","F":"B33"},"ev62":{"T":"B34","F":"B35"},"ev63":{"T":"B36","F":"B37"},
            "ev71":{"T":"B38","F":"B39"},"ev72":{"T":"B40","F":"B41"},"ev73":{"T":"B42","F":"B43"},
            "ev81":{"T":"B44","F":"B45"},"ev82":{"T":"B46","F":"B47"},"ev83":{"T":"B48","F":"B49"},
            "ev91":{"T":"B50","F":"B51"},"ev92":{"T":"B52","F":"B53"},"ev93":{"T":"B54","F":"B55"},
            "ev101":{"T":"B56","F":"B57"},"ev102":{"T":"B58","F":"B59"},"ev103":{"T":"B60","F":"B61"}}

#プレイヤーデータ格納用
ID_manage = {}
player = {}

#ボタン用クラス
class TrueButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label:str = "yes", eventCode:str = "001"):
        super().__init__(style=style, label=label, disabled=False)
        self.eventCode = eventCode
        self.dic = EvntList[self.eventCode]["T"]

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"> {interaction.user.display_name}は{self.label}を選択しました。\n" + (event_sheet[self.dic].value))
        await interaction.message.delete()
        

class FalseButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label:str = "no", eventCode:str = "001"):
        super().__init__(style=style, label=label, disabled=False)
        self.eventCode = eventCode
        self.dic = EvntList[self.eventCode]["F"]
        
    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"> {interaction.user.display_name}は{self.label}を選択しました。\n" + (event_sheet[self.dic].value))
        await interaction.message.delete()


description = '''ダンジョン管理bot'''
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = commands.Bot(command_prefix='?',  help_command = None, description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user} (ID: {bot.user.id})')
    print("10thDangen.py起動")
    print('------')
    channel = bot.get_channel(982985477126766632)
    #await channel.send(f"> ダンジョン機能起動: **{daytime}**\n```・西方の古代遺跡〈?fdgt〉```")

@bot.command()
async def fdgtstart(ctx):
    #global active_sheet
    usr_id = int(ctx.author.id)
    if usr_id in ID_manage:
        await ctx.send("> >>あなたは既にダンジョンの内部にいます")
    else:
        ID_manage[usr_id] = 1 #ID管理辞書にUIDと現在階層を追加
        await ctx.send("> 注意: このコマンドを実行した方が進行コマンドを振ってください。")
        player[usr_id] = 1
        #usr_id = DataManage(usr_id)

        await ctx.send("> >>インスタンスが生成されました。")
        file_E = discord.File(fp="image/Dang_Ent2.jpg",filename="Dang_Ent2.jpg",spoiler=False)
        embed=discord.Embed(title="西方の古代遺跡", description="堕神の地の奥深く、山中に存在する古代の遺跡。\nアールヴ帝国の時代に建設されたと思しきその地下巨大構造物には、無数の秘宝が眠っているという。", color=0xff9300)
        embed.set_image(url=f"attachment://Dang_Ent2.jpg")
        await ctx.send(file=file_E,embed=embed)
        file_E.close
        await ctx.send("**現在地点: 1階層 - 入口**")
        await ctx.send("> 進行状況: 1/10")

#1階層
@bot.command()
async def fdgt11(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 10: #もし探索回数が10回なら
            file = discord.File("image/stair.png", filename="stair.png")
            embed=discord.Embed(title="第一階層: 地下への道",
                                description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://stair.png")
            await ctx.send(file=file,embed=embed)
            file.close()
            ID_manage[usr_id] = 2 #現在階層を2層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 10 and ID_manage[usr_id] == 2: #もし探索回数が10回未満でかつ、UIDの階層が1以外であれば
            await ctx.send("> あなたは1階層には居ません")
        else:
            await ctx.send("**現在地点: 1階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/10")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(2)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((active_sheet[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_011(ctx)
            elif cell_name == "ev2":
                await event_012(ctx)
            elif cell_name == "ev3":
                await event_013(ctx)
            else:
                await ctx.send((active_sheet[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#2階層
@bot.command()
async def fdgt12(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 10: #もし探索回数が10回なら
            file = discord.File("image/stair2.png", filename="stair2.png")
            embed=discord.Embed(title="第二階層: 地下への道",
                                description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://stair2.png")
            await ctx.send(file=file,embed=embed)
            file.close()
            ID_manage[usr_id] = 3 #現在階層を3層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 10 and ID_manage[usr_id] != 2: #もし探索回数が10回未満でかつ、UIDの階層が2以外であれば
            await ctx.send("> あなたは2階層には居ません")
        else:
            await ctx.send("**現在地点: 2階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/10")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(3)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor2[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_021(ctx)
            elif cell_name == "ev2":
                await event_022(ctx)
            elif cell_name == "ev3":
                await event_023(ctx)
            else:
                await ctx.send((floor2[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#3階層
@bot.command()
async def fdgt13(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 10: #もし探索回数が10回なら
            Bcell = random.choice(BList) #ボスランダム選択
            file = discord.File("image/FLOOR3BOSS.png", filename="FLOOR3BOSS.png")
            embedB=discord.Embed(title="> フロアボス",description=(floor3[Bcell].value),color=0x6E6636)
            embed=discord.Embed(title="第三階層: フロアの主",
                                description="地下へと続く階段を発見したが、階段を守る存在に行く手を塞がれた。\n次の階層に進む為には、この守護者を倒さなければならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://FLOOR3BOSS.png")
            await ctx.send(file=file,embed=embed)
            await ctx.send(embed=embedB)
            file.close()
            ID_manage[usr_id] = 4 #現在階層を4層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 10 and ID_manage[usr_id] != 3: #もし探索回数が10回未満でかつ、UIDの階層が3以外であれば
            await ctx.send("> あなたは3階層には居ません")
        else:
            await ctx.send("**現在地点: 3階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/10")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(4)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor3[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_031(ctx)
            elif cell_name == "ev2":
                await event_032(ctx)
            elif cell_name == "ev3":
                await event_033(ctx)
            else:
                await ctx.send((floor3[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")
   
#4階層
@bot.command()
async def fdgt14(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 15: #もし探索回数が15回なら
            file = discord.File("image/stair4.jpg", filename="stair04.jpg")
            embed=discord.Embed(title="第四階層: 地下への階段",
                                description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://stair04.jpg")
            await ctx.send(file=file,embed=embed)
            file.close()
            ID_manage[usr_id] = 5 #現在階層を5層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 15 and ID_manage[usr_id] != 4: #もし探索回数が15回未満でかつ、UIDの階層が4以外であれば
            await ctx.send("> あなたは4階層には居ません")
        else:
            await ctx.send("**現在地点: 4階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/15")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(3)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor4[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_041(ctx)
            elif cell_name == "ev2":
                await event_042(ctx)
            elif cell_name == "ev3":
                await event_043(ctx)
            else:
                await ctx.send((floor4[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#5階層
@bot.command()
async def fdgt15(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 15: #もし探索回数が15回なら
            file = discord.File("image/stair5.jpg", filename="stair05.jpg")
            embed=discord.Embed(title="第五階層: 地下への階段",
                                description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://stair05.jpg")
            await ctx.send(file=file,embed=embed)
            file.close()
            ID_manage[usr_id] = 6 #現在階層を6層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 15 and ID_manage[usr_id] != 5: #もし探索回数が15回未満でかつ、UIDの階層が3以外であれば
            await ctx.send("> あなたは5階層には居ません")
        else:
            await ctx.send("**現在地点: 5階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/15")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(3)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor5[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_051(ctx)
            elif cell_name == "ev2":
                await event_052(ctx)
            elif cell_name == "ev3":
                await event_053(ctx)
            else:
                await ctx.send((floor5[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#6階層
@bot.command()
async def fdgt16(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 15: #もし探索回数が15回なら
            Bcell = random.choice(BList) #ボスランダム選択
            file = discord.File("image/FLOOR6BOSS.png", filename="FLOOR6BOSS.png")
            embedB=discord.Embed(title="> フロアボス",description=(floor6[Bcell].value),color=0x6E6636)
            embed=discord.Embed(title="第六階層: フロアの主",
                                description="地下へと続く階段を発見したが、階段を守る存在に行く手を塞がれた。\n次の階層に進む為には、この守護者を倒さなければならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://FLOOR6BOSS.png")
            await ctx.send(file=file,embed=embed)
            await ctx.send(embed=embedB)
            file.close()
            ID_manage[usr_id] = 7 #現在階層を7層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 15 and ID_manage[usr_id] != 6: #もし探索回数が15回未満でかつ、UIDの階層が6以外であれば
            await ctx.send("> あなたは6階層には居ません")
        else:
            await ctx.send("**現在地点: 6階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/15")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(3)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor6[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_061(ctx)
            elif cell_name == "ev2":
                await event_062(ctx)
            elif cell_name == "ev3":
                await event_063(ctx)
            else:
                await ctx.send((floor6[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#----ここから毎回小ボス----
#7階層
@bot.command()
async def fdgt17(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 20: #もし探索回数が20回なら
            Bcell = random.choice(BList) #ボスランダム選択
            file = discord.File("image/FLOOR7BOSS.png", filename="FLOOR7BOSS.png")
            embedB=discord.Embed(title="> フロアボス",description=(floor7[Bcell].value),color=0x6E6636)
            embed=discord.Embed(title="第七階層: フロアの主",
                                description="地下へと続く階段を発見したが、階段を守る存在に行く手を塞がれた。\n次の階層に進む為には、この守護者を倒さなければならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://FLOOR7BOSS.png")
            await ctx.send(file=file,embed=embed)
            await ctx.send(embed=embedB)
            file.close()
            ID_manage[usr_id] = 8 #現在階層を8層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 20 and ID_manage[usr_id] != 7: #もし探索回数が20回未満でかつ、UIDの階層が7以外であれば
            await ctx.send("> あなたは7階層には居ません")
        else:
            await ctx.send("**現在地点: 7階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/20")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(2)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor7[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_071(ctx)
            elif cell_name == "ev2":
                await event_072(ctx)
            elif cell_name == "ev3":
                await event_073(ctx)
            else:
                await ctx.send((floor7[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#8階層
@bot.command()
async def fdgt18(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 20: #もし探索回数が20回なら
            Bcell = random.choice(BList) #ボスランダム選択
            file = discord.File("image/FLOOR8BOSS.png", filename="FLOOR8BOSS.png")
            embedB=discord.Embed(title="> フロアボス",description=(floor8[Bcell].value),color=0x6E6636)
            embed=discord.Embed(title="第八階層: フロアの主",
                                description="地下へと続く階段を発見したが、階段を守る存在に行く手を塞がれた。\n次の階層に進む為には、この守護者を倒さなければならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://FLOOR8BOSS.png")
            await ctx.send(file=file,embed=embed)
            await ctx.send(embed=embedB)
            file.close()
            ID_manage[usr_id] = 9 #現在階層を9層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 20 and ID_manage[usr_id] != 8: #もし探索回数が20回未満でかつ、UIDの階層が8以外であれば
            await ctx.send("> あなたは8階層には居ません")
        else:
            await ctx.send("**現在地点: 8階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/20")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(2)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor8[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_081(ctx)
            elif cell_name == "ev2":
                await event_082(ctx)
            elif cell_name == "ev3":
                await event_083(ctx)
            else:
                await ctx.send((floor8[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#9階層
@bot.command()
async def fdgt19(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 20: #もし探索回数が20回なら
            Bcell = random.choice(BList) #ボスランダム選択
            file = discord.File("image/FLOOR9BOSS.png", filename="FLOOR9BOSS.png")
            embedB=discord.Embed(title="> フロアボス",description=(floor9[Bcell].value),color=0x6E6636)
            embed=discord.Embed(title="第九階層: フロアの主",
                                description="地下へと続く階段を発見したが、階段を守る存在に行く手を塞がれた。\n次の階層に進む為には、この守護者を倒さなければならない。",
                                color=0x6E6636)
            embed.set_image(url="attachment://FLOOR9BOSS.png")
            await ctx.send(file=file,embed=embed)
            await ctx.send(embed=embedB)
            file.close()
            ID_manage[usr_id] = 10 #現在階層を10層に設定
            player[usr_id] = 1 #進捗状況をリセット
        elif player[usr_id] < 20 and ID_manage[usr_id] != 9: #もし探索回数が20回未満でかつ、UIDの階層が9以外であれば
            await ctx.send("> あなたは9階層には居ません")
        else:
            await ctx.send("**現在地点: 9階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/20")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(2)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor9[Ecell_name].value) + "\n x" + Enum)
            #イベント処理
            elif cell_name == "ev1":
                await event_091(ctx)
            elif cell_name == "ev2":
                await event_092(ctx)
            elif cell_name == "ev3":
                await event_093(ctx)
            else:
                await ctx.send((floor9[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#10階層
@bot.command()
async def fdgt10b(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 5: #もし探索回数が5回なら
            Bcell = random.choice(BList) #ボスランダム選択
            file = discord.File("image/FLOOR10BOSS.png", filename="FLOOR10BOSS.png")
            embedB=discord.Embed(title="> ダンジョンボス",description=(floor10[Bcell].value),color=0x6E6636)
            embed=discord.Embed(title="第十階層: ダンジョンの主",
                                description="ついにあなた達は10階層の奥底へと辿り着いた。\n巨大な扉の先には、ダンジョンの主があなた達を待っている。",
                                color=0x6E6636)
            embed.set_image(url="attachment://FLOO109BOSS.png")
            await ctx.send(file=file,embed=embed)
            await ctx.send(embed=embedB)
            file.close()
        elif player[usr_id] < 5 and ID_manage[usr_id] != 10: #もし探索回数が20回未満でかつ、UIDの階層が10以外であれば
            await ctx.send("> あなたは10階層には居ません")
        else:
            await ctx.send("**現在地点: 10階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/5")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                await ctx.send("> ```この階層には、階層主以外の敵は存在しないようだ。```")
            #イベント処理
            elif cell_name == "ev1":
                await event_101(ctx)
            elif cell_name == "ev2":
                await event_102(ctx)
            elif cell_name == "ev3":
                await event_103(ctx)
            else:
                await ctx.send((floor10[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#第一階層イベント
async def event_011(ctx):
    file = discord.File("image/event.png", filename="event.png")
    embed=discord.Embed(title="第一階層: 不可思議な物音",
                        description="ダンジョンを進んでいたあなたは、突然開けた空間に出た。\n地下だというのに、窓からは日光のような光が差し込んでいる。\nそうしているうち、どこからか奇妙な音が聞こえることにあなたは気が付いた。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<確認しに行く>",eventCode="ev11"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev11"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_012(ctx):
    file = discord.File("image/event_2.png", filename="event_2.png")
    embed=discord.Embed(title="第一階層: 奇妙な臭気",
                        description="通路を進んでいると、奇妙な臭気が立ち込める部屋を発見した。\n悪臭とまでは言えないが、なんとなく鼻につくような臭いだ。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_2.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev12"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<正体を確かめる>",eventCode="ev12"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_013(ctx):
    file = discord.File("image/event_3.jpg", filename="event_3.jpg")
    embed=discord.Embed(title="第一階層: 奇妙な光",
                        description="ダンジョンを進んでいると、崩落した壁の瓦礫の下で何かが光っているのを見つけた。\nかなり奥の方にあるようだが、退けられるかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_3.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev13"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<瓦礫を退ける(スタミナ-2)>",eventCode="ev13"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#第二階層イベント
async def event_021(ctx):
    file = discord.File("image/event_11.jpg", filename="event_11.jpg")
    embed=discord.Embed(title="第二階層: 分岐路",
                        description="ダンジョンを進んでいると、途中で道が二方向に分かれている場所に出くわした。\nどちらの通路に進むべきだろうか？",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_11.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<右の道を進む>",eventCode="ev21"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<左の道を進む>",eventCode="ev21"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_022(ctx):
    file = discord.File("image/event_3.jpg", filename="event_3.jpg")
    embed=discord.Embed(title="第二階層: 歪んだ扉",
                        description="ダンジョンを進んでいると、歪んで開かなくなった扉を見つけた。\nその先は暗いが、何か良いものがあるかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_3.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev22"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<扉をこじ開ける(スタミナ-2)>",eventCode="ev22"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_023(ctx):
    file = discord.File("image/event_13.jpg", filename="event_13.jpg")
    embed=discord.Embed(title="第二階層: 展示室",
                        description="開けた空間に出た。損壊もあまり激しくないようで、魔導灯が室内を照らしている。\n室内にはいくつかのガラスケースがあり、その中の二つはまだ中に何かが置かれているようだ。\nケースを割れば取り出せるかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_13.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<大きなケースを割る>",eventCode="ev23"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<小さなケースを割る>",eventCode="ev23"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#第三階層イベント
async def event_031(ctx):
    file = discord.File("image/event_31.jpg", filename="event_31.jpg")
    embed=discord.Embed(title="第三階層: 線路の奥",
                        description="どこまでも続く半円状のトンネルの先から、甲高い音が聞こえた気がした。\n線路を辿っていけば迷うことはないだろうが...確認するべきだろうか。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_31.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<確認する>",eventCode="ev31"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<確認しない>",eventCode="ev31"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_032(ctx):
    file = discord.File("image/event_32.jpg", filename="event_32.jpg")
    embed=discord.Embed(title="第三階層: 起動中の転移陣: ",
                        description="魔法陣が整然と並ぶエリアを進んでいると、一つだけ起動中の魔法陣を見つけた\n壁の文字には転移と書かれているが、乗ってみるべきだろうか？",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_32.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<転移陣に乗ってみる>",eventCode="ev32"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev32"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_033(ctx):
    file = discord.File("image/event_33.jpg", filename="event_33.jpg")
    embed=discord.Embed(title="第三階層: 魔導駅",
                        description="受付のような場所の先へ進むと、横に広くやけに柱の多い空間に出た。\nアヴァロットの魔導機関車駅にも見えるが、地下では煙を逃がせないからトロッコを走らせていたのだろう。\n線路の反対側にも同じような空間があるようだが、見に行くべきだろうか。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_33.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<見に行く>",eventCode="ev33"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<見に行かない>",eventCode="ev33"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#第四階層イベント
async def event_041(ctx):
    file = discord.File("image/event_41.jpg", filename="event_41.jpg")
    embed=discord.Embed(title="第四階層: 食堂",
                        description="明かりの見える方向へ進むと、荒廃した広い部屋に出た。\n複数のテーブルと椅子があることから、恐らく食堂か何かだったのだろう。\n近くにはキッチンが隣接しているかもしれない。探してみるべきだろうか？",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_41.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<探してみる(スタミナ-1)>",eventCode="ev41"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<探さずに進む>",eventCode="ev41"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_042(ctx):
    file = discord.File("image/event_41.jpg", filename="event_41.jpg")
    embed=discord.Embed(title="第四階層: 奇妙な音",
                        description="通路を進んでいると、どこからか奇妙な音が聞こえてきた。\nかなりひび割れているが女性の声のようで、何事かを言っている。\n音の源を探せば何かあるかもしれない。探してみるべきだろうか。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_41.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<音の源へ行く(スタミナ-2)>",eventCode="ev42"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<行かない>",eventCode="ev42"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_043(ctx):
    file = discord.File("image/event_43.jpg", filename="event_43.jpg")
    embed=discord.Embed(title="第四階層: 遺留物",
                        description="松明の立てられた部屋に入ると、比較的新しい見慣れた羊皮紙が落ちていた。\n見てみると、どうやらこの付近の地図らしい。近くの一点に印がつけてある。\n何があるのかは分からないが、行ってみてもいいかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_43.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<行ってみる(スタミナ-2)>",eventCode="ev43"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev43"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#第五階層イベント
async def event_051(ctx):
    file = discord.File("image/event_51.png", filename="event_51.png")
    embed=discord.Embed(title="第五階層: 奇妙な機械",
                        description="破けたソファとテーブルが置かれた小スペースに、ガラスのケースがついた奇妙な機械があった。\n何気なくスイッチのようなものを押すと、突然魔導灯が点灯し始めた。\n何かできるだろうか？",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_51.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<お金を入れてみる(-100G)>",eventCode="ev51"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev51"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_052(ctx):
    file = discord.File("image/event_51.png", filename="event_51.png")
    embed=discord.Embed(title="第五階層: 洗練されたベッド",
                        description="少し休憩しようと比較的綺麗な部屋に入ると、ガラスで覆われたベッドが置かれていた。\n不思議なことに埃が積もっておらず、まるで新品のようにきれいな状態だ。\nこれに寝転がれば体力も少しは回復するかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_51.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<寝転がってみる(スタミナ-1)>",eventCode="ev52"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<無視して先に進む>",eventCode="ev52"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_053(ctx):
    file = discord.File("image/event_51.png", filename="event_51.png")
    embed=discord.Embed(title="第五階層: 地下公園",
                        description="通路を進んでいると、どこからか水のせせらぎが聞こえてきた。\n音の源を辿ってみると、そこには巨大な地下公園が存在していた。複数の木とベンチ、地面には芝生の生えた土が敷き詰められ、小さな川が流れている。\nここで休憩していけば、体力は回復するだろう。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_51.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<周囲を探索する(スタミナ-2)>",eventCode="ev53"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<休憩する>",eventCode="ev53"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#第六階層イベント
async def event_061(ctx):
    file = discord.File("image/event_61.png", filename="event_61.png")
    embed=discord.Embed(title="第六階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_61.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev61"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev61"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()    

async def event_062(ctx):
    file = discord.File("image/event_61.png", filename="event_61.png")
    embed=discord.Embed(title="第六階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_61.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev62"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev62"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

async def event_063(ctx):
    file = discord.File("image/event_61.png", filename="event_61.png")
    embed=discord.Embed(title="第六階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_61.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev63"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev63"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()  

#第七階層イベント
async def event_071(ctx):
    file = discord.File("image/event_71.png", filename="event_71.png")
    embed=discord.Embed(title="第七階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_71.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev71"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev71"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()    

async def event_072(ctx):
    file = discord.File("image/event_71.png", filename="event_71.png")
    embed=discord.Embed(title="第七階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_71.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev72"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev72"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

async def event_073(ctx):
    file = discord.File("image/event_71.png", filename="event_71.png")
    embed=discord.Embed(title="第七階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_71.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev73"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev73"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

#第八階層イベント
async def event_081(ctx):
    file = discord.File("image/event_81.png", filename="event_81.png")
    embed=discord.Embed(title="第八階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_81.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev81"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev81"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

async def event_082(ctx):
    file = discord.File("image/event_81.png", filename="event_81.png")
    embed=discord.Embed(title="第八階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_81.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev82"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev82"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close() 

async def event_083(ctx):
    file = discord.File("image/event_81.png", filename="event_81.png")
    embed=discord.Embed(title="第八階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_81.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev83"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev83"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close() 

#第九階層イベント
async def event_091(ctx):
    file = discord.File("image/event_91.png", filename="event_91.png")
    embed=discord.Embed(title="第九階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_91.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev91"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev91"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

async def event_092(ctx):
    file = discord.File("image/event_91.png", filename="event_91.png")
    embed=discord.Embed(title="第九階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_91.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev92"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev92"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

async def event_093(ctx):
    file = discord.File("image/event_91.png", filename="event_91.png")
    embed=discord.Embed(title="第九階層: ■■■■",
                        description="どこまでも続く薄暗い通路の奥から声が響く。\nその悍ましい声に、私は不安を掻き立てられた",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_91.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev93"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<そんなものに構っている暇はない>",eventCode="ev93"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()   

#第十階層イベント
async def event_101(ctx):
    file = discord.File("image/event_101.jpg", filename="event_101.jpg")
    embed=discord.Embed(title="第十階層: 巨大シャフト",
                        description="金属で出来たフェンスの向こうに、どこまでも続く巨大な柱が連なっている。\nこの遺跡を建造した人々は、何を目的にあのようなものを作ったのだろうか。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_101.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<これは...何だ？>",eventCode="ev101"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<美しい...>",eventCode="ev101"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()  

async def event_102(ctx):
    file = discord.File("image/event_102.jpg", filename="event_102.jpg")
    embed=discord.Embed(title="第十階層: 隔離壁",
                        description="洞窟を基礎としたような通路を進んでいると、広大な空間に出た。\n視界の先には、空間を切り取るような巨大壁が見える。\nあの向こうには何があるのだろうか。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_102.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<触らぬ神に祟りなしだ>",eventCode="ev102"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<いつの日か解き明かさねばならない>",eventCode="ev102"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close() 

async def event_103(ctx):
    file = discord.File("image/event_103.jpg", filename="event_103.jpg")
    embed=discord.Embed(title="第十階層: 地底湖",
                        description="狭く薄暗い通路を進んでいると、突然視界が開けて広々とした景色が視界に入った。\n日光のように美しい光で照らされたその場所は、どうやら地底湖のようだ。\nいくつかの建物と船らしきものがあるが、調べてみるべきだろうか。",
                        color=0x6E6636)        
    embed.set_image(url="attachment://event_103.jpg")  
    #embed.set_footer(text="𝔄𝔭𝔢𝔯𝔱𝔲𝔯𝔢 𝔖𝔠𝔦𝔢𝔫𝔠𝔢 𝔘𝔫𝔡𝔢𝔯𝔤𝔯𝔬𝔲𝔫𝔡 𝔗𝔢𝔰𝔱 𝔖𝔥𝔞𝔣𝔱 ——— 𝔖𝔦𝔫𝔠𝔢 𝔐ℭ𝔐𝔛𝔏𝔙ℑℑ - 𝔐ℭ𝔐𝔏𝔛𝔛𝔛ℑ𝔛")  
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<調べてみよう>",eventCode="ev103"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<調べる必要はない>",eventCode="ev103"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close() 


#汎用コマンド
@bot.command()
async def escapeD(ctx):
    usr_id = ctx.author.id
    if usr_id in ID_manage:
        await ctx.send("> ダンジョンから脱出します")
        del player[usr_id]
        del ID_manage[usr_id]
    else:
        await ctx.send("> あなたはまだダンジョンに入っていません")

@bot.command()
async def debug_003(ctx):
    await event_103(ctx)

@bot.command()
async def debug_002(ctx):
    await event_102(ctx)

@bot.command()
async def debug_001(ctx):
    await event_101(ctx)


#@bot.command()
#async def purge(ctx):
#    channel = ctx.message.channel
#    deleted = await channel.purge(limit=1000,check = is_me,bulk=False)
#    await channel.send(f'Deleted {len(deleted)} message(s)')

bot.run("TOKEN")