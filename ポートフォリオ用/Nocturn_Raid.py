
#必要なライブラリをインポート
import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import random, dice, asyncio
import numpy as np

blacklist = ["1076422611325702236","1093041645114622004","1032532645655105536","931562992041099275","1081170888063459368"]


#ボス戦用配列
current_mission = {}
current_battle = {} #現在戦闘しているチャンネル
current_party = {} #パーティーメンバー
current_turn = {} #現在ターン
mission_prog = {} #現在の階層
show_turn = {} #表示用ターン

gimmick_prog = False #ギミックが進行中かどうか
act = False
rest = False
battle = False

selc_id = ["a","b","c","d","e","f","g"]
boss_list = ["mf1","nb1","nb2"]
battle_ids = {"mf1":["x10"],
              "nb2":["bmp2m","t95u","end"],
              "nb1":["sicario","sicario"]}

#ボス戦用クラス
class Actor:
    def __init__(self, name, hp, max_hp):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp

class Enemy(Actor):
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp, max_hp)
        self.enemy = self.__class__.__name__
      
    # NEW METHOD
    def rehydrate(self, name, hp, max_hp):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp

#---T-95U---
class t95u(Enemy):
    floar_name = "第三世代主力戦車『T-95U』"
    gimmick_name_list = {1:["152MM滑腔砲","152MM滑腔砲","第三世代型ATGM"]}
    phase = 1
    diff = "extreme"
    armor = 30
    attack_selc = 4
    Bhp = 250
    Bname = "T-95U"
    pic = "https://media.discordapp.net/attachments/1081260969256296528/1098943461102723213/4DA5929FEF1CE337AAD404EE4D965AFC9E0E141A.png?width=875&height=513"
    #ここから攻撃選択

    p1 = {1:{"name":"152MM滑腔砲", "type":"single", "damage":"15d10+2", "text":"〈戦車砲がこちらを向く〉","desc":"複合装甲Mk1貫通/ 物理/ 単体"},
          2:{"name":"152MM滑腔砲", "type":"single", "damage":"15d10+2", "text":"〈戦車砲がこちらを向く〉","desc":"複合装甲Mk1貫通/ 物理/ 単体"},
          3:{"name":"第三世代型ATGM", "type":"single", "damage":"10d10+10", "text":"〈対戦車ミサイルが放たれる〉","desc":"複合装甲Mk1貫通/ 回避-15/ 物理/ 単体"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold

#---BMP-2M---
class bmp2m(Enemy):
    boss_name = "試作戦車破壊"
    floar_name = "歩兵戦闘車『BMP-2M』"
    gimmick_name_list = {1:["第三世代型ATGM","第三世代型ATGM","30MM機関砲"]}
    phase = 1
    diff = "extreme"
    armor = 15
    attack_selc = 4
    Bhp = 200
    Bname = "BMP-2M"
    pic = "https://media.discordapp.net/attachments/1081260969256296528/1098943479591211088/bmp-2m.png"
    #ここから攻撃選択

    p1 = {1:{"name":"第三世代型ATGM", "type":"single", "damage":"10d10+10", "text":"〈対戦車ミサイルが放たれる〉","desc":"複合装甲Mk1貫通/ 回避-15/ 物理/ 単体"},
          2:{"name":"第三世代型ATGM", "type":"single", "damage":"10d10+10", "text":"〈対戦車ミサイルが放たれる〉","desc":"複合装甲Mk1貫通/ 回避-15/ 物理/ 単体"},
          3:{"name":"30MM機関砲", "type":"single", "damage":"3d15+3", "text":"〈機関砲から徹甲弾が飛び出す〉","desc":"物理/ 単体"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold

#---2層ボス---
class d2(Enemy):
    floar_name = "魔導の塔第二層『絡繰騎士』"
    gimmick_name_list = {1:["IV型魔導槍","死の槍衾","右翼突進","薙ぎ払い","薙ぎ払い"]}
    phase = 1
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 20
    attack_selc = 6
    Bhp = 300
    Bname = "絡繰騎士"
    #ここから攻撃選択

    p1 = {1:{"name":"IV型魔導槍", "type":"role", "damage":"2d20+7", "target":"tank", "text":"〈絡繰騎士が攻撃を準備している〉","desc":"血属性/ 物理/ 回避不可/ 単体"},
          2:{"name":"死の槍衾", "type":"all", "damage":"2d15+3", "text":"〈絡繰騎士が攻撃を準備している〉","desc":"血属性/ 物理/ 回避不可/ 全体"},
          3:{"name":"右翼突進", "type":"locate", "damage":"2d25+7", "danger_locate":["N","W","S","SW","NW","Center"], "text":"〈絡繰騎士が攻撃を準備している〉","desc":"火属性/ 魔法/ 回避不可/ 複数"},
          4:{"name":"薙ぎ払い", "type":"locate", "damage":"2d30+7", "danger_locate":["N","W","S","SW","NW","Center"], "text":"〈絡繰騎士が右腕を掲げる〉","desc":"血属性/ 物理/ 回避不可/ 複数"},
          5:{"name":"薙ぎ払い", "type":"locate", "damage":"2d30+7", "danger_locate":["E","N","S","SE","NE","Center"], "text":"〈絡繰騎士が左上を掲げる〉","desc":"血属性/ 物理/ 回避不可/ 複数"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold


#Bot関連設定
description = "Emeth V1.3"
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?', description=description, help_command=None, intents=intents)

#Botログイン時処理
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

#塔開始進行用コマンド
@bot.command(name="boss")
async def boss(ctx,bossID:str):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    if bossID not in boss_list:
        await ctx.send("`IDが間違っています`")
        return
    global rest, battle,gimmick_prog
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    #既にレイド中であれば
    if channelID in current_party:
        await ctx.send("`現在別のパーティーが突入中です`")
        return
    #タワーに突入していない場合
    battle = True
    first_boss = battle_ids[bossID]
    #---クラス処理関連---
    cls = globals()[first_boss[0]]
    bossData = cls()
    current_battle[channelID] = bossData #専用配列にチャンネルIDとボスIDを紐付けて登録
    #---辞書への初期値関連---
    current_mission[channelID] = bossID
    show_turn[channelID] = 0
    current_party[channelID] = {str(ctx.author.display_name):"front"} #パーティー用の専用配列を作成
    mission_prog[channelID] = 0 #チャンネルの階層を1層に設定
    current_turn[channelID] = 0 #現在ターンを0に設定
    picture = bossData.pic

    await ctx.send(f"**`任務名: {bossData.boss_name}`**\n`チャンネル: {ctx.channel.name}`\n`?turn 参加`で任務に参加後、戦闘を開始")
    embedPhase1=discord.Embed(title=f"{bossData.floar_name}",
                            description=" ",
                            color=0x6E6636)
    embedPhase1.set_image(url=picture)
    await ctx.send(embed=embedPhase1) #ヘッダー表示

#ギミック型レイド用コマンド
@bot.command(name="turn", help="?turn [内容]")
async def turn(ctx, msg:str = "NaN"):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    global gimmick_prog, act, battle, rest
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    #もしmsgが入力されていなければ
    if msg == "NaN":
        await ctx.reply("`> 内容を入力してください`")
        return
    #チャンネルIDが辞書に登録されていなければ
    if channelID not in current_mission:
        await ctx.reply("`> 戦闘を開始していません`")
        return
    usr_name = ctx.author.display_name #ニックネームを取得
    if channelID in current_battle:
        bossData = current_battle[channelID] #ボスインスタンスを取得
    counted_turn = show_turn[channelID]
    if msg != "ターン":
        await ctx.send(f"`現在ターン:{counted_turn}`")
    if msg == "ターン":
        act = True
        current_turn[channelID] += 1
        show_turn[channelID] += 1
        counted_turn = show_turn[channelID]
        await ctx.send(f"`現在ターン:{counted_turn}`")
        if current_turn[channelID] == bossData.attack_selc:
            current_turn[channelID] = 1
        await gimmick(ctx)
    elif "参加" in msg:
        update_dict = current_party[channelID]
        update_dict[usr_name] = "front"
        current_party.update(update_dict)
        await ctx.reply("`> 任務参加者に登録しました`")
    elif "ダメージ" in msg:
        dmg = msg.split("ダ")
        print("ダメージ判定")
        print(dmg)
        #---ここまでDPSチェック判定---
        #ダメージが100から200の間なら
        if 200 >= int(dmg[0]) > 100:
            fix_damage = (int(dmg[0]) * 0.5) - bossData.armor
        #ダメージが200以下なら
        elif int(dmg[0]) < 200:
            fix_damage = (int(dmg[0]) * 0.6) - bossData.armor
        #ダメージが200以上なら
        elif int(dmg[0]) > 200:
            fix_damage = (int(dmg[0]) * 0.3) - bossData.armor
        #ダメージが100以下なら
        else:
            fix_damage = int(dmg[0]) - bossData.armor
        bossData.Bhp -= fix_damage
        await ctx.send(f"> **`{usr_name}`**は**`{bossData.Bname}`**に`{fix_damage}ダメージを与えた！`\n`残りHP:{bossData.Bhp}`")
        print(bossData.Bhp)
        if bossData.Bhp <= 0:
            del current_battle[channelID]
            mission_prog[channelID] += 1 #進行状況をインクリメント
            current_turn[channelID] = 0
            show_turn[channelID] = 0
            await ctx.send(f"`>{usr_name}が{bossData.Bname}へ与えた攻撃が決定打となり、対象を撃破することに成功した`")
            await ctx.send("`>戦闘終了。このまま<?turn 続行>と入力してください`")
            battle = False
    elif msg == "続行":
        if battle == True:
            await ctx.send("`まだ戦闘が終わっていません`")
            return
        mission_id = current_mission[channelID]
        current_mission_ids = battle_ids[mission_id]
        now_prog = mission_prog[channelID]
        if current_mission_ids[now_prog] == "end":
            await ctx.send("`最後の敵を倒しました。任務完了です`")
            del mission_prog[channelID], current_turn[channelID], show_turn[channelID], current_party[channelID], current_mission[channelID]
            return
        battle = True
        #---クラス処理関連---
        cls = globals()[current_mission_ids[now_prog]]
        bossData = cls()
        current_battle[channelID] = bossData #専用配列にチャンネルIDとボスIDを紐付けて登録
        picture = bossData.pic
        embedPhase1=discord.Embed(title=f"{bossData.floar_name}",
                                description=" ",
                                color=0x6E6636)
        embedPhase1.set_image(url=picture)
        await ctx.send(embed=embedPhase1) #ヘッダー表示
    elif msg == "中断":
        await ctx.send("中断します")
        battle = False
        rest = False
        gimmick_prog = False
        del current_battle[channelID]
        del current_party[channelID]
        del current_turn[channelID]
    elif msg == "完了":
        act = True
        await ctx.send(f">`{usr_name}の手番を完了した`")
        await ctx.send("全員の手番が終わったのであれば`?trait ターン`を。その他の場合は2分以内に手番を完了してください。")
        await asyncio.sleep(2)
        act = False
        for i in range(120):#120秒待つ
            await asyncio.sleep(1) 
            if act == True:
                return
        if gimmick_prog == False: #ギミック処理中ではなく、対象が未行動であれば
            current_turn[channelID] += 1
            if current_turn[channelID] == bossData.attack_selc:
                current_turn[channelID] = 1
            await gimmick(ctx)
    elif msg == "開始":
        await ctx.send(">開始します。一人2分以内に手番を終えてください。完了したら`?trait 完了`と入力してください。")
        for i in range(120):
            await asyncio.sleep(1)
            if act == True:
                return
        if gimmick_prog == False: #ギミック処理中ではなく、対象が未行動であれば
            current_turn[channelID] += 1
            await gimmick(ctx)
    else:
        await ctx.reply("`>不正なコマンドです`")

#時間カウンター用関数
@commands.command()
async def counter(ctx,time:int):
    msg = await ctx.send(f"`発動まで{time}...`")
    for i in reversed(range(time)):
        await asyncio.sleep(1)
        refr = f"`発動まで{i}...`"
        await msg.edit(content=refr)
    await msg.edit(content="`>ギミック発動`")

#ギミック処理用関数
@commands.command()
async def gimmick(ctx):
    target_selcs = []
    global gimmick_prog
    gimmick_prog = True
    channelID = str(ctx.channel.id) #チャンネルIDを取得
    turn_count = current_turn[channelID]
    now_turn = turn_count- 1 #現在のターンを取得
    bossData = current_battle[channelID] #ボスインスタンスを取得
    name_list = bossData.gimmick_name_list[bossData.phase] #ギミック名のリストを取得
    gimmick_data = bossData.p1[turn_count] #辞書から現在ターンに対応したギミックデータを取得

    desc = gimmick_data["desc"]
    atk_dmg = gimmick_data["damage"]
    texts = gimmick_data["text"]
    atk_rst = dice.roll(atk_dmg) #攻撃ダメージを取得

    #<---ロール選択攻撃--->
    if gimmick_data["type"] == "role":
        target_roles = [k for k, v in current_party[channelID].items() if v == gimmick_data["target"]]  
        list_form = ''.join(map(str, target_roles))
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    #<---全体攻撃--->
    elif gimmick_data["type"] == "all":
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
    elif gimmick_data["type"] == "single":
        fronts = [k for k, v in current_party[channelID].items() if v == 'front']
        if len(fronts) == 1:
            await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {fronts[0]}に{atk_rst}ダメージの攻撃`") 
        else:
            target = (random.randrange(1,len(fronts)+1,1))
            await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {fronts[target]}に{atk_rst}ダメージの攻撃`") 
    gimmick_prog = False

#BGMフェードアウトコマンド
async def FadeOut(ctx):
    for i in reversed(range(1,10)):
        volume = i*10
        ctx.voice_client.source.volume = volume / 100
        await asyncio.sleep(0.3)
        print(volume)
    for i in reversed(range(10)):
        volume = i
        ctx.voice_client.source.volume = volume / 100
        await asyncio.sleep(0.2)
        print(volume)
    ctx.voice_client.stop()


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]

#Bot起動
bot.run("TOKEN")