
#必要なライブラリをインポート
import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import random, dice, asyncio

blacklist = ["1076422611325702236215"]

#ボス戦用配列
current_battle = {}
current_party = {} #パーティーメンバー
current_party_loc = {} #メンバーの位置
current_party_react = {}
current_turn = {}
test_dict = {}

gimmick_prog = False
act = False


selc_id = ["a","b","c","d","e","f","g"]
streaming_P0 = False
streaming_P1 = False

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

class f1(Enemy):
    quest_name = "レイドバトル - 氏族長討伐任務"
    p0_attack_selc = 5
    p1_attack_selc = 3
    phase = 0
    aromor = 300
    diff = "normal"
    turn_attack = 0
    phase1_hp = 5000
    #ここから攻撃選択肢
    attack_body = {"a":"90d6+1$大地の怒り/ 土属性/ 物理/ 全体$「偉大なる地の力を見よ！」",
                "b":"30d10+5$ランドスライド/ 土属性/ 物理/ 単体$「遥かなる地下へ沈むが良い！」",
                "c":"30d15+2$クエイク/ 土属性/ 物理/ 単体/$「地は我自身である！」",
                "d":"40d10+5$メガ・ランドスライド/ 土属性/ 物理/ 全体$「ここで終わりだ！」",
                "e":"60d6+5$アースブレイド/ 土属性/ 魔法/ 単体$「我が刃よ、敵を切り裂け！」",
    }
    attack_body_p1 = {"a":"20d40+10$アースクエイク/ 土属性/ 物理/ 全体$「大地の怒りを受けよ！」",
                      "b":"80d10+10$メガ・アースブレイド/ 土属性/ 魔法/ 単体$「これぞ我が剣よ！」",
                      "c":"80d8+10$メガ・ランドスライド/ 土属性/ 物理/ 全体$「ここで終わりだ！」",
    }
    def __init__(self):
        super().__init__("巨人族の氏族長", 400) # HP, attack, defense, XP, gold

class f3(Enemy):
    quest_name = "高難易度レイドバトル - 真水竜討滅任務"
    p0_attack_selc = 5
    p1_attack_selc = 5
    p2_attack_selc = 6
    phase = 0
    phase1_hp = 600
    aromor = 45
    diff = "hard"
    turn_attack = 0
    #ここから攻撃選択
    attack_body = {"a":"5d10+5$スピニング・ダイブ/ 水属性/ 物理/ 全体$「......」",
                    "b":"6d10+5$ウォーター・ブレード/ 水属性/ 魔法/ 全体$「......」",
                    "c":"8d10+5$叩きつけ/ 無属性/ 物理/ 単体/$「......」",
                    "d":"6d8+5$ウォーター・カスケード/ 水属性/ 魔法/ 全体$「......」",
                    "e":"2d30+5$自己回復/ 特殊/ 回復$「...」",
    }
    attack_body_p1 = {"a":"8d10+20$タイダル・ウェイヴ/ 水属性/ 物理/ 全体$「......」",
                    "b":"2d30+10$スーパーソニック・ウォーターブレード/ 水属性/ 魔法/ 単体$「......」",
                    "c":"8d10+5$グレートフロード/ 水属性/ 魔法/ 全体/$「......」",
                    "d":"6d10+5$大津波/ 水属性/ 物理/ 全体$「......」",
                    "e":"3d30+5$自己回復/ 特殊/ 回復$「...」",
    }
    attack_body_p2 = {"a":"8d10+20$グランドフォール/ 水属性/ 物理/ 全体$「......」",
                    "b":"6d10+5$ウォーター・ブレード/ 水属性/ 魔法/ 単体$「......」",
                    "c":"8d10+5$叩きつけ/ 無属性/ 物理/ 単体/$「......」",
                    "d":"6d8+5$ウォーター・カスケード/ 水属性/ 魔法/ 単体$「......」",
                    "e":"1d60+10$ウォータージェット/ 水属性/ 魔法/ 全体$「...」",
                    "f":"4d30+5$自己回復/ 特殊/ 回復$「...」",
    }
    def __init__(self):
        super().__init__("水竜", 500) # HP, attack, defense, XP, gold

class f2(Enemy):
    quest_name = "レイドバトル - 古代の亡骸騎士"
    p0_attack_selc = 4
    p1_attack_selc = 4
    phase = 0
    phase1_hp = 1500
    aromor = 25
    turn_attack = 0
    diff = "normal"
    #ここから攻撃選択肢
    attack_body = {"a":"2d20+7$アールヴァン・ソード/ 無属性/ 物理/ 単体$「...」",
                "b":"4d20+14$エンシェント・ワイルドタックル/ 無属性/ 物理/ 単体$「...」",
                "c":"6d6+3$エンシェント・エーテルアロー/ 血属性/ 魔法/ 物理防護貫通/ 単体$「...」",
                "d":"3d10+10$CVI型魔導銃/ 血属性/ 物理/ 物理防護貫通/ 単体$「...」",
    }
    attack_body_p1 = {"a":"9d10+10$ハンド・オブ・エンパイア/ 血属性/ 物理/ 単体$「帝国万歳」",
                      "b":"6d8+10$エンシェント・マギカブラスト/ 血属性/ 魔法/ 物理防護貫通/ 全体$「...帝国に逆らうものへ死を」",
                      "c":"7d10+10$XII型魔導携帯爆弾/ 火属性/ 物理/ 全体$「帝国の為に」",
                      "d":"7d15+10$エンシェント・エーテルブレード/ 血属性/ 魔法/ 物理防護貫通/ 単体$「我が身が朽ちようとも...」",

    }
    def __init__(self):
        super().__init__("亡骸騎士", 500) # HP, attack, defense, XP, gold

class f01(Enemy):
    quest_name = "レイドバトル - ホブゴブリン討伐任務"
    p0_attack_selc = 4
    p1_attack_selc = 4
    phase = 0
    aromor = 15
    diff = "beginer"
    turn_attack = 0 #ターン移行時に行う攻撃
    phase1_hp = 350
    #ここから攻撃選択肢
    attack_body = {"a":"2d20+5$教会の鋸斧/ 無属性/ 物理/ 単体$「......」",
                "b":"3d12+5$斬猪刀/ 無属性/ 物理/ 単体$「......」",
                "c":"6d6+4$エーテルバースト/ 火属性/ 魔法/ 全体/$「...」",
                "d":"1d1+49$アップルグミ/ 特殊/ 回復$「...」",
    }
    attack_body_p1 = {"a":"4d10+10$エンチャント・ソード/ 火属性/ 物理/ 単体$「...」",
                      "b":"7d6+6$エーテルブレード/ 火属性/ 魔法/ 単体$「......」",
                      "c":"2d30+5$古びた銃/ 無属性/ 物理/ 全防護貫通/ 単体$「......」",
                      "d":"1d1+49$アップルグミ/ 特殊/ 回復$「...」",
    }
    def __init__(self):
        super().__init__("ホフゴブリンの戦士", 350) # HP, attack, defense, XP, gold

class f02(Enemy):
    quest_name = "レイドバトル - グレートウルフ討伐任務"
    p0_attack_selc = 3
    p1_attack_selc = 3
    phase = 0
    aromor = 10
    diff = "beginer"
    turn_attack = 0 #ターン移行時に行う攻撃
    phase1_hp = 150
    #ここから攻撃選択肢
    attack_body = {"a":"4d10+5$狼爪/ 無属性/ 物理/ 単体$「......」",
                "b":"3d12+5$跳躍衝撃/ 無属性/ 物理/ 全体$「......」",
                "c":"1d1+29$舐傷/ 特殊/ 回復$「...」",
    }
    attack_body_p1 = {"a":"5d10+10$狼爪一撃/ 無属性/ 物理/ 単体$「...」",
                      "b":"3d15+10$跳躍破撃/ 無属性/ 物理/ 全体$「......」",
                      "c":"1d1+29$舐傷/ 特殊/ 回復$「...」",
    }
    def __init__(self):
        super().__init__("グレートウルフ", 150) # HP, attack, defense, XP, gold

class n1(Enemy):
    quest_name = "レイドバトル - 強化パワーアーマー兵排除"
    p0_attack_selc = 3
    p1_attack_selc = 4
    phase = 0
    phase1_hp = 1000
    diff = "normal"
    aromor = 15
    turn_attack = 3
    #ここから攻撃選択肢
    attack_body = {"a":"3d8+3$FALカスタム/ 物理/ 単体/ 連射$「...」$1d19+1",
                "b":"3d15+15$XM109 ペイロード/ 物理/ 全体/ 連射$「...」$1d3+0",
                "c":"1d25+10$Mk79 電磁加速拳銃/ 防護貫通/ 単体$「...」",
    }
    attack_body_p1 = {"a":"3d6+0$XM214 MicroGun/ 物理/ 全体/ 連射$「...」$2d25+1",
                      "b":"6d10+5$MGL-140/ 物理/ 全体$「.....」",
                      "c":"3d6+8$AUG Custom(強装)/ 物理/ 単体/ 連射$「...」$3d5+0",
                      "d":"7d10+10$XHsATR-01 試製電磁対戦車ライフル/ 防護貫通/ 単体$「.....」",
    }
    def __init__(self):
        super().__init__("T-51PA兵", 800) # HP, attack, defense, XP, gold

class n2(Enemy):
    quest_name = "レイドバトル - 危険ローグ排除"
    p0_attack_selc = 6
    p1_attack_selc = 6
    phase = 0
    phase1_hp = 140
    diff = "mediaum"
    aromor = 55
    turn_attack = 5
    #ここから攻撃選択肢
    attack_body = {"a":"1d1+29$ヴォルター注射式回復剤/ 特殊/ 回復$「ダメージを食らいすぎたな、回復する」",
                "b":"6d14+6$M202A1/ 全体$「吹き飛べ！」",
                "c":"2d18+2$MODEL1890(強装)/ 単体/ 連射$「食らえ！」$1d5+1",
                "d":"3d6+7$20式自動小銃(強装)/ 単体/ 連射$「ハチの巣にしてやる！」$1d4+1",
                "e":"3d6+5$G36K改(強装)/ 単体/ 連射$「くたばっちまえ！」$1d10+3",
                "f":"9d6+8$コンテンダー改(強装)/ 単体$「くたばっちまえ！」",
    }
    attack_body_p1 = {"a":"8d10+10$XRM2E1 試作式レールガン改/ 防護貫通/ 単体$「こいつを使うしかねえか」",
                      "b":"4d10+0$MGL-140/ 物理/ 全体/ 連射$「こんな所で死んでたまるか！」$1d6+0",
                      "c":"3d6+8$AUG Custom(強装)/ 物理/ 単体/ 連射$「唸れ、俺のAUG！」$3d5+0",
                      "d":"1d1+49$ヘビースティム・改/ 特殊/ 回復$「出し惜しみはなしだ」",
                      "e":"5d10+5$エレメンツ・レーザー/ 幻影術/ 防護貫通/ 単体$「うおぉぉ！」",
                      "f":"3d5+5$黄昏のメヌエット(強装)/ 物理/ 全体/ 連射$「苦労して制作した俺の秘密兵器、食らいやがれ！」$1d10+5",
    }
    def __init__(self):
        super().__init__("危険なローグ", 90) # HP, attack, defense, XP, gold

class e1(Enemy):
    quest_name = "特殊レイド - 炎竜追憶戦"
    gimmick_name_list = {1:["インシネレート","フレイムバースト","灼熱の火炎","エラプション","インシネレート","光輝の槍","光輝の槍"]}
    phase = 1
    phase1_hp = 500
    diff = "extreme"
    music = "music/rubikante.mp3"
    dps_check = False
    dps_check_hp = 0
    armor = 15
    #ここから攻撃選択

    p1 = {1:{"name":"インシネレート", "type":"role", "damage":"2d35+7", "target":"tank", "text":"〈レッサーヒュドラの口部から炎が漏れ出す〉","desc":"火属性/ 魔法/ 単体"},
          2:{"name":"フレイムバースト", "type":"all", "damage":"2d15+7", "text":"〈レッサーヒュドラの全身から魔力が溢れる〉","desc":"火属性/ 魔法/ 全体"},
          3:{"name":"灼熱の火炎", "type":"select", "damage":"2d25+7", "true_select":"A", "text":"〈レッサーヒュドラの両翼が輝きを発する〉","desc":"火属性/ 魔法/ 回避不可/ 複数"},
          4:{"name":"エラプション", "type":"locate", "damage":"2d25+7", "attack_locate":"EW", "text":"〈北側で急激に魔力が増加している〉\n`北西/北東/南西/南東に移動可能`","desc":"火属性/ 魔法/ 回避不可/ 複数"},
          5:{"name":"インシネレート", "type":"role", "damage":"2d35+7", "target":"tank", "text":"〈レッサーヒュドラの口部から炎が漏れ出す〉","desc":"火属性/ 魔法/ 単体"},
          6:{"name":"光輝の槍", "type":"check", "damage":"2d30+10", "target_hp":200, "text":"〈光り輝く巨大な槍が現れた。あれが放たれれば只では済まないだろう。その前に破壊しなくては〉","desc":"火属性/ 魔法/ 単体"},
          7:{"name":"光輝の槍", "type":"check_fail", "damage":"4d30+10", "target_hp":200, "text":"〈光り輝く巨大な槍が現れた。あれが放たれれば只では済まないだろう〉","desc":"火属性/ 魔法/ 回避不可/ 全体"}

    }

    def __init__(self):
        super().__init__("記憶の炎竜", 500) # HP, attack, defense, XP, gold

#helpコマンド時の表示設定
class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "ボス関連コマンド"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"
    def get_ending_note(self):
        return (f"-----------------------------------")

#----音楽ループ----
@tasks.loop(seconds=160)
async def loop_boss2P0(ctx):
    global streaming_P0
    music = "music/titan_8bit.mp3"
    if streaming_P0 == True:
        voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
        ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
        PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1.0) #可変音源に設定
        voice_client.play(PCMVT) #音楽再生
    else:
        streaming_P0 = True
        print("ループした")

@tasks.loop(seconds=315)
async def loop_boss2P1(ctx):
    global streaming_P1
    music = "music/titan.mp3"
    if streaming_P1 == True:
        voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
        ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
        PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1.0) #可変音源に設定
        voice_client.play(PCMVT) #音楽再生
    else:
        streaming_P1 = True
        print("ループした")

#Bot関連設定
description = "Emeth V1.3"
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?', description=description, help_command=JapaneseHelpCommand(), intents=intents)

#Botログイン時処理
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

#ボス戦開始用コマンド
@bot.command(name="boss", help="?boss [ボス戦ID]")
async def boss(ctx,boss_id:str = "null"):
    if str(ctx.author.id) in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    #もしボスIDが入力されていなければ
    if boss_id == "null":
        await ctx.reply("`> ボス戦IDを入力してください`")
        return
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    if channelID in current_battle:
        await ctx.reply("`> 既にボス戦を開始しています`")
        return
    cls = globals()[boss_id]
    bossData = cls()
    current_party[channelID] = {str(ctx.author.display_name):"front"} #パーティー用の専用配列を作成
    current_battle[channelID] = bossData #専用配列にチャンネルIDとボスIDを紐付けて登録
    if bossData.diff != "extreme":
        current_turn[channelID] = 1
        await ctx.send(f"**`ボス戦名: {bossData.quest_name}`**\n`チャンネル: {ctx.channel.name}`\n`?turn 前衛/後衛`で前衛か後衛かを宣言後、クエストを開始")
        return
    else:#極コンテンツの場合
        #---BGM関連処理---
        current_turn[channelID] = 0
        current_party_loc[channelID] = {str(ctx.author.display_name):"NE"} #メンバー位置の専用配列を作成
        #if ctx.author.voice is None:
        #    await ctx.send("ボイスチャンネルに参加してからコマンドを打ってください")
        #    return
        #await ctx.author.voice.channel.connect() #ボイスチャンネルに参加
        #voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
        #music = bossData.music
        #ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
        #PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1.0) #可変音源に設定
        #voice_client.play(PCMVT) #音楽再生
        await ctx.send(f"**`クエスト名: {bossData.quest_name}`**\n`チャンネル: {ctx.channel.name}`\n`?trait [ロール]`でロールを宣言後、クエストを開始")
        embedPhase1=discord.Embed(title="［―――追憶戦―――］",
                                description=" ",
                                color=0x6E6636)
        await ctx.send(embed=embedPhase1) #ヘッダー表示

#ギミック型レイド用コマンド
@bot.command(name="trait", help="?trait [内容]")
async def trait(ctx, msg:str = "NaN"):
    global gimmick_prog, act
    #ユーザーがブラックリストに登録されていたらreturn
    if str(ctx.author.id) in blacklist:
        await ctx.send("discord.ext.commands.errors.CommandInvokeError: Command raised an exception: HTTPException: 400 Bad Request (error code: 50006): Cannot send message")
        return
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    #もしmsgが入力されていなければ
    if msg == "NaN":
        await ctx.reply("`> 内容を入力してください`")
        return
    #チャンネルIDが辞書に登録されていなければ
    if channelID not in current_battle:
        await ctx.reply("`> ボス戦を開始していません`")
        return
    usr_name = ctx.author.display_name #ニックネームを取得
    bossData = current_battle[channelID] #ボスインスタンスを取得
    if msg == "ターン":
        current_turn[channelID] += 1
        if current_turn[channelID] == 7:
            current_turn[channelID] = 1
        await gimmick(ctx)
    elif msg == "北東":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "NE"
        current_party.update(update_dict)
        await ctx.reply("`> 北東に移動しました`")
    elif msg == "南東":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "SE"
        current_party.update(update_dict)
        await ctx.reply("`> 南東に移動しました`")
    elif msg == "北西":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "NW"
        current_party.update(update_dict)
        await ctx.reply("`> 北西に移動しました`")
    elif msg == "南西":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "SW"
        current_party_loc.update(update_dict)
        await ctx.reply("`> 南西に移動しました`")

    elif "ダメージ" in msg:
        dmg = msg.split("ダ")
        print("ダメージ判定")
        print(dmg)
        if bossData.dps_check == True:
            if int(dmg[0]) > 200:
                fix_damage = (int(dmg[0]) * 0.5) - bossData.armor
            else:
                fix_damage = int(dmg[0]) - bossData.armor    
            bossData.dps_check_hp -= fix_damage
            await ctx.send(f"> **`{usr_name}`**は対象に`{fix_damage}ダメージを与えた！`\n`残りHP:{bossData.dps_check_hp}`")
            print(bossData.dps_check_hp)     
            if bossData.dps_check_hp <= 0:
                current_turn[channelID] += 1
                await gimmick(ctx)
                bossData.dps_check = False
        else:
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
            bossData.hp -= fix_damage
            await ctx.send(f"> **`{usr_name}`**は**`{bossData.name}`**に`{fix_damage}ダメージを与えた！`\n`残りHP:{bossData.hp}`")
            print(bossData.hp)
            if bossData.hp <= 0:
                await ctx.send(f"`>{usr_name}が{bossData.name}へ一撃を加えるのと同時、その巨体が地に崩れ墜ちる。戦いの末、あなた方は勝利を掴み取ることができた。`")
                await ctx.send("`>戦闘終了`")
                del current_battle[channelID]
                del current_party[channelID]
                del current_turn[channelID]
                del current_party_loc[channelID]
                current_party_react.clear()

    elif msg == "中断":
        await ctx.send("中断します")
        del current_battle[channelID]
        del current_party[channelID]
        del current_turn[channelID]
        del current_party_loc[channelID]
        current_party_react.clear()

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
            if current_turn[channelID] == 7:
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

    elif msg == "タンク": #タンクロール設定
        current_party_react[usr_name] = "F"
        update_dict = current_party[channelID]
        if "tank" in update_dict.values():
            await ctx.reply("`> 既にタンクが存在します`")   
            return         
        update_dict[usr_name] = "tank"
        current_party.update(update_dict)
        await ctx.reply("`> タンクに設定しました`")
    elif msg == "ヒーラー": #ヒーラーロール設定
        current_party_react[usr_name] = "F"
        update_dict = current_party[channelID]
        if "healer" in update_dict.values():
            await ctx.reply("`> 既にヒーラーが存在します`")   
            return         
        update_dict[usr_name] = "healer"
        current_party.update(update_dict)
        await ctx.reply("`> ヒーラーに設定しました`")
    elif msg == "アタッカー": #アタッカーロール設定
        current_party_react[usr_name] = "F"
        update_dict = current_party[channelID]
        if list(update_dict.values()).count('dps') == 2:
            await ctx.reply("`> 既にアタッカーが二人存在します`")   
            return         
        update_dict[usr_name] = "dps"
        current_party.update(update_dict)
        await ctx.reply("`> アタッカーに設定しました`")
    else:
        await ctx.reply("`>不正なコマンドです`")
                       
#ボス戦管理コマンド
@bot.command(name="turn", help="?turn [内容]")
async def turn(ctx, msg:str = "null"):
    global streaming_P0, streaming_P1
    if str(ctx.author.id) in blacklist:
        await ctx.send("discord.ext.commands.errors.CommandInvokeError: Command raised an exception: HTTPException: 400 Bad Request (error code: 50006): Cannot send message")
        return
    #もしmsgが入力されていなければ
    if msg == "null":
        await ctx.reply("`> 内容を入力してください`")
        return
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    #チャンネルIDが辞書に登録されていなければ
    if channelID not in current_battle:
        await ctx.reply("`> ボス戦を開始していません`")
        return
    usr_name = ctx.author.display_name #ニックネームを取得
    bossData = current_battle[channelID] #ボスインスタンスを取得
    if "前衛" in msg:
        update_dict = current_party[channelID]
        update_dict[usr_name] = "front"
        current_party.update(update_dict)
        await ctx.reply("`> 前衛に設定しました`")
    elif "後衛" in msg:
        update_dict = current_party[channelID]
        update_dict[usr_name] = "back"
        current_party.update(update_dict)
        await ctx.reply("`> 後衛に設定しました`")
    elif "ダメージ" in msg:
        dmg = msg.split("ダ")
        print(bossData.hp)
        #フェーズ1以上でかつダメージが200以下なら
        if bossData.phase >= 1 and int(dmg[0]) < 200:
            fix_damage = (int(dmg[0]) * 0.6) - bossData.aromor
        #ダメージが200以上なら
        elif int(dmg[0]) > 200:
            fix_damage = (int(dmg[0]) * 0.3) - bossData.aromor
        #ダメージが100から200の間なら
        elif 200 >= int(dmg[0]) > 100:
            fix_damage = (int(dmg[0]) * 0.5) - bossData.aromor
        #ダメージが100以下なら
        else:
            fix_damage = int(dmg[0]) - bossData.aromor
        #最終ダメージがマイナスなら0にする
        if fix_damage <= 0:
            fix_damage = 0
        bossData.hp -= fix_damage
        print(bossData.hp)
        await ctx.send(f"> **`{usr_name}`**は**`{bossData.name}`**に`{fix_damage}ダメージを与えた！`\n`残りHP:{bossData.hp}`")
        #hpが0になり、かつフェーズ0だった場合
        if bossData.hp <= 0 and bossData.phase == 0:
            bossData.phase = 1
            bossData.hp = bossData.phase1_hp
            #ターンカウントをリセット
            current_turn[channelID] = 0
            print("フェーズ1")
            print(current_turn[channelID])
            await ctx.send("```ボスのHPを全て削り切った。...だが、ボスは未だ倒れていない```")
            await asyncio.sleep(2)
            await ctx.send("```それどころか、より力を増している。あなた方を真の脅威であると感じたようだ```")
            await ctx.send("`> ボスのHPが全回復した！`")
            current_turn[channelID] += 1
            await attack(ctx,bossData.turn_attack)
            return
        #hpが0になり、かつフェーズ1で、難易度がハードでなければ
        elif bossData.hp <= 0 and bossData.phase == 1 and bossData.diff != "hard":
            await ctx.send("`> 戦闘終了`")
            await asyncio.sleep(2)
            del current_battle[channelID]
            del current_party[channelID]
            del current_turn[channelID]
        #hpが0になり、かつフェーズ1で難易度がハードならフェーズ2に移行
        elif bossData.hp <= 0 and bossData.phase == 1 and bossData.diff == "hard":
            print("フェーズ2")
            bossData.phase = 2
            bossData.hp = 1000
            #ターンカウントをリセット
            current_turn[channelID] = 0
            print(current_turn[channelID])
            await ctx.send("```ボスが倒れ伏す。完全に討伐したかと安堵したのも束の間、再びその巨大が起き上がった```")
            await asyncio.sleep(2)
            await ctx.send("```全身の傷は瞬く間に消え、凄まじい闘志がボスの全身から湧き出ている```")
            await ctx.send("`> ボスのHPが全回復した！`")
            current_turn[channelID] += 1
            await attack(ctx,bossData.turn_attack)    
        #hpが0でフェーズが2かそれ以上なら戦闘終了   
        elif bossData.hp <= 0 and bossData.phase >= 2:
            await ctx.send("`> 戦闘終了`")
            await asyncio.sleep(2)
            del current_battle[channelID]
            del current_party[channelID]
            del current_turn[channelID]            
    elif "除外" in msg:
        update_dict = current_party[channelID]
        update_dict[usr_name] = "dead"
        current_party.update(update_dict)
        await ctx.send(f"`> {usr_name}を除外設定しました`")    
    elif "ターン" in msg:
        current_turn[channelID] += 1
        await attack(ctx)
        return
    elif "回復" in msg:
        heal = msg.split("回")
        heal_num = int(heal[0])
        bossData.hp += int(heal[0])
        print(bossData.hp)
        await ctx.send(f">`ボスのHPを{heal_num}回復させました(ダメージミス修正用)`")
    elif "中断" in msg:
        await ctx.send("戦闘を中断します")
        #await ctx.guild.voice_client.disconnect()
        del current_battle[channelID]
        del current_party[channelID]
        del current_turn[channelID]
    else:
        await ctx.send("`> 不正なコマンドです`")
        return

@commands.command()
async def attack(ctx,turn_attack:int=0):
    channelID = str(ctx.channel.id) #チャンネルIDを取得
    if channelID not in current_battle:
        await ctx.reply("`> ボス戦を開始していません`")
        return
    bossData = current_battle[channelID] #ボスインスタンスを取得
    if bossData.diff == "normal":
        #フェーズ0の場合
        if bossData.phase == 0:
            act_selc = random.randrange(1,bossData.p0_attack_selc+1,1) #ボスがどの行動をするかを選択
        #フェーズ0以外の場合
        else:
            act_selc = random.randrange(1,bossData.p1_attack_selc+1,1) #ボスがどの行動をするかを選択
        #ターンアタックが0なら
        if turn_attack == 0:
            tgt = selc_id[act_selc-1]
        #ターンアタックが指定されていれば
        else:
            tgt = selc_id[turn_attack]
        if bossData.phase == 0:
            act_main = bossData.attack_body[tgt] #選ばれた行動の全文を取得
        else:
            act_main = bossData.attack_body_p1[tgt] #選ばれた行動の全文を取得
        act_slice = act_main.split("$") #全文を$で区切る
        #ダイスを振る必要がなければ
        if "非攻撃" in act_slice[1]: 
            await ctx.send(f"`{act_slice[1]}`\n{act_slice[2]}")
        #全体攻撃で連射であれば
        elif "全体" in act_slice[1] and "連射" in act_slice[1]: 
            atk_rst = dice.roll(act_slice[0])
            rensya = dice.roll(act_slice[3])
            await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> 全体に{atk_rst}ダメージｘ{rensya}発の攻撃`") 
        #全体攻撃であれば
        elif "全体" in act_slice[1]: 
            atk_rst = dice.roll(act_slice[0])
            await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
        #回復行動であれば
        elif "回復" in act_slice[1]: 
            heal_rst = dice.roll(act_slice[0])
            bossData.hp += heal_rst
            await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> ボスのHPが{heal_rst}回復した`")
        #単体攻撃で連射の場合
        elif "連射" in act_slice[1]: 
            fronts = [k for k, v in current_party[channelID].items() if v == 'front']       
            if len(fronts) == 1:
                atk_rst = dice.roll(act_slice[0])
                rensya = dice.roll(act_slice[3])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[0]}に{atk_rst}ダメージｘ{rensya}発の攻撃`")
            else:
                target = (random.randrange(1,len(fronts)+1,1))
                atk_rst = dice.roll(act_slice[0])
                rensya = dice.roll(act_slice[3])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[target]}に{atk_rst}ダメージｘ{rensya}発の攻撃`")   
        #単体攻撃で単発の場合
        else:
            fronts = [k for k, v in current_party[channelID].items() if v == 'front']
            if len(fronts) == 1:
                atk_rst = dice.roll(act_slice[0])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[0]}に{atk_rst}ダメージの攻撃`")
            else:
                target = (random.randrange(1,len(fronts)+1,1))
                atk_rst = dice.roll(act_slice[0])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[target]}に{atk_rst}ダメージの攻撃`")
    else:
        #フェーズ0
        if bossData.phase == 0:
            act_selc = current_turn[channelID]
            tgt = selc_id[act_selc-1]
            #行動が一巡したらカウンターを0に戻す
            if act_selc == bossData.p0_attack_selc:
                current_turn[channelID] = 0
            act_main = bossData.attack_body[tgt]
        #フェーズ1
        elif bossData.phase == 1:
            act_selc = current_turn[channelID]
            tgt = selc_id[act_selc-1]
            #行動が一巡したらカウンターを0に戻す
            if act_selc == bossData.p1_attack_selc:
                current_turn[channelID] = 0
            act_main = bossData.attack_body_p1[tgt]
        #フェーズ2
        elif bossData.phase == 2:
            act_selc = current_turn[channelID]
            tgt = selc_id[act_selc-1]
            #行動が一巡したらカウンターを0に戻す
            if act_selc == bossData.p2_attack_selc:
                current_turn[channelID] = 0
            act_main = bossData.attack_body_p2[tgt]
        #フェーズ3以降
        else:
            pass
        act_slice = act_main.split("$") #全文を$で区切る
        if "非攻撃" in act_slice[1]: 
            await ctx.send(f"`{act_slice[1]}`\n{act_slice[2]}")
        #全体攻撃で連射であれば
        elif "全体" in act_slice[1] and "連射" in act_slice[1]: 
            atk_rst = dice.roll(act_slice[0])
            rensya = dice.roll(act_slice[3])
            await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> 全体に{atk_rst}ダメージｘ{rensya}発の攻撃`") 
        #全体攻撃であれば
        elif "全体" in act_slice[1]: 
            atk_rst = dice.roll(act_slice[0])
            await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
        #回復行動であれば
        elif "回復" in act_slice[1]: 
            heal_rst = dice.roll(act_slice[0])
            bossData.hp += heal_rst
            await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> ボスのHPが{heal_rst}回復した`")
        #単体攻撃で連射の場合
        elif "連射" in act_slice[1]: 
            fronts = [k for k, v in current_party[channelID].items() if v == 'front']       
            if len(fronts) == 1:
                atk_rst = dice.roll(act_slice[0])
                rensya = dice.roll(act_slice[3])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[0]}に{atk_rst}ダメージｘ{rensya}発の攻撃`")
            else:
                target = (random.randrange(1,len(fronts)+1,1))
                atk_rst = dice.roll(act_slice[0])
                rensya = dice.roll(act_slice[3])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[target]}に{atk_rst}ダメージｘ{rensya}発の攻撃`")   
        #単体攻撃で単発の場合
        else:
            fronts = [k for k, v in current_party[channelID].items() if v == 'front']
            if len(fronts) == 1:
                atk_rst = dice.roll(act_slice[0])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[0]}に{atk_rst}ダメージの攻撃`")
            else:
                target = (random.randrange(1,len(fronts)+1,1))
                atk_rst = dice.roll(act_slice[0])
                await ctx.send(f"```{act_slice[2]}```\n`{act_slice[1]}`\n`> {fronts[target]}に{atk_rst}ダメージの攻撃`")
  
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

    if gimmick_data["type"] == "role":
        target_roles = [k for k, v in current_party[channelID].items() if v == gimmick_data["target"]]  
        list_form = ''.join(map(str, target_roles))
        await ctx.send(f"> **{bossData.name}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    elif gimmick_data["type"] == "all":
        await ctx.send(f"> **{bossData.name}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
    elif gimmick_data["type"] == "select":
        stopper = False
        await ctx.send(f"`>{bossData.name}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        embedPhase1=discord.Embed(title="移動先を選択",
                                description=":regional_indicator_a: - 上\n:regional_indicator_b: - 下\n:regional_indicator_c: - 右\n:regional_indicator_d: - 左",
                                color=0x6E6636)
        select_msg = await ctx.send(embed=embedPhase1) #ヘッダー表示
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter A}')
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter B}')
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter C}')
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter D}')
        #リアクション判定部分
        @bot.event
        async def on_reaction_add(reaction, user):
            if stopper == True:
                return
            if str(reaction.emoji) == '\N{Regional Indicator Symbol Letter A}':
                current_party_react[user.display_name] = "A"
            elif str(reaction.emoji) == '\N{Regional Indicator Symbol Letter B}':
                current_party_react[user.display_name] = "B"
            elif str(reaction.emoji) == '\N{Regional Indicator Symbol Letter C}':
                current_party_react[user.display_name] = "C"
            elif str(reaction.emoji) == '\N{Regional Indicator Symbol Letter D}':
                current_party_react[user.display_name] = "D"
        await counter(ctx,5) 
        stopper = True

        target_selcs = [k for k, v in current_party_react.items() if v != gimmick_data["true_select"]]  
        list_form = '、'.join(map(str, target_selcs))
        await ctx.send(f"> **{bossData.name}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    elif gimmick_data["type"] == "locate":
        await ctx.send(f"`>{bossData.name}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        await counter(ctx,10) 
        target_selcs = [k for k, v in current_party_react.items() if v != gimmick_data["attack_locate"]]  
        list_form = '、'.join(map(str, target_selcs))
        await ctx.send(f"> **{bossData.name}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    elif gimmick_data["type"] == "check":
        bossData.dps_check = True
        bossData.dps_check_hp = gimmick_data["target_hp"]
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
    elif gimmick_data["type"] == "check_fail" and bossData.dps_check == True:
        await ctx.send(f"> **{bossData.name}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
    elif gimmick_data["type"] == "check_fail" and bossData.dps_check == False:
        await ctx.send("`>どうにか敵を倒すことができた。`") #ヒントテキストを表示
        bossData.dps_check = False
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

#Bot起動
bot.run("TOKEN")