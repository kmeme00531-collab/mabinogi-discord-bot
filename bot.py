import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import random
import logging
import os

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"

CAT_MESSAGES = [
    "🌌 흠냐옹~ 결계가 열렸다옹… 어서 가보라옹~",
    "🌌 킁킁… 수상한 기운이 난다옹. 아무래도 결계가 열릴 것 같다옹~",
    "🌌 야옹! 기다리던 시간이 왔다옹… 결계다옹~",
    "🌌 밥은 먹고 다니냐옹? 밥은 걸러도 결계 시간은 챙기라옹~",
    "🌌 흠냐옹~ 결계 조심히 다녀오라옹~",
    "🌌 보상이 받고 싶냐옹? 자, 받으라옹… 내 결계 알림~",
    "🌌 킁킁… 결계 냄새가 츄르보다 더 진하게 난다옹. 얼른 가져오라옹~",
    "🌌 야옹~ 아직도 여기 있냐옹…? 결계나 빨리 가라옹~",
    "🌌 결계는 기다려주지 않는다옹… 자, 출발하라옹~",
    "🌌 행운을 빌어주겠다옹~ (꾸욱 꾹~)"
]

BOSS_LIST = {
    "마비노기 모바일 필드보스": [12, 18, 20, 22]
}


BOSS_MESSAGES = [
    "킁킁… 강한 기운이 느껴진다옹. 5분 뒤에 필드보스가 나타난다옹~",
    "야옹~ 슬슬 움직여야 할 시간이다옹… 필드보스를 해치우러 가라옹~",
    "흠냐옹~ 필드보스가 곧 깨어난다옹~",
    "냐옹~ 밥은 놓쳐도 필드보스는 챙기라옹~",
    "어서 준비하라옹~ 꾸물대다 필드보스를 놓친다옹~",
    "냐옹~ 무기는 챙겼냐옹? 이제 필드보스를 치러 출발하라옹~",
    "흠냐옹~ 지금 출발하면 필드보스 시간에 딱 맞는다옹~ 어서 가라옹~",
    "필드보스 길러 집사가 되어보라옹~",
    "냐옹! 지금 가면 필드보스를 칠 수 있다옹~",
    "자, 필드보스를 해치우러 출발하라옹… 내가 응원해주겠다옹~"
]


sent_boss_alarm = []

BOSS_TIMES = [12, 18, 20, 22]


@tasks.loop(seconds=30)
async def boss_alarm_check():
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    # 55분에만 체크 (필드보스 5분 전)
    if now.minute != 55:
        return

    alarm_hour = now.hour + 1

    if alarm_hour not in BOSS_TIMES:
        return

    if alarm_hour in sent_boss_alarm:
        return

    config = load_config()

    channel = bot.get_channel(config["CHANNEL_ID"])

    if channel:
        message = random.choice(BOSS_MESSAGES)
        await channel.send(message)
        sent_boss_alarm.append(alarm_hour)

    print("필드보스 체크 실행됨", now)

    # 날짜 변경 시 초기화
    if now.hour == 0 and now.minute == 0:
        sent_boss_alarm.clear()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"TOKEN": "", "CHANNEL_ID": 0}, f, indent=4)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


config = load_config()

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()

    print(f"{bot.user} 로그인 완료")

    if not barrier_alarm.is_running():
        barrier_alarm.start()

    if not boss_alarm_check.is_running():
        boss_alarm_check.start()

@bot.tree.command(name="setchannel", description="현재 채널을 알림 채널로 설정")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction):
    config["CHANNEL_ID"] = interaction.channel.id
    save_config(config)

    print(config)   # ← 이 한 줄 추가

    await interaction.response.send_message(
        "✅ 알림 채널이 설정되었습니다.",
        ephemeral=True
    )


@tasks.loop(minutes=1)
async def barrier_alarm():
    print("결계 체크", datetime.now(ZoneInfo("Asia/Seoul")))

    now = datetime.now(ZoneInfo("Asia/Seoul"))

    if now.minute != 0:
        return

    channel_id = config.get("CHANNEL_ID", 0)

    if channel_id == 0:
        return

    channel = bot.get_channel(channel_id)

    if channel is None:
        return

    await channel.send(random.choice(CAT_MESSAGES))


bot.run(os.getenv("TOKEN"))
