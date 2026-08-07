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
    "🐱 결계가 열렸다옹! 냥냥~ 출발하자!"
]

BOSS_TIMES = [12, 18, 20, 22]

BOSS_MESSAGES = [
    "킁킁… 강한 기운이 느껴진다옹. 5분 뒤 필드보스 출현이다냥! ⚔️"
]

sent_boss_alarm = []


def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"CHANNEL_ID": 0}, f, indent=4)

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


@bot.tree.command(
    name="setchannel",
    description="현재 채널을 알림 채널로 설정"
)
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction):
    config["CHANNEL_ID"] = interaction.channel.id
    save_config(config)

    print(config)

    await interaction.response.send_message(
        "✅ 알림 채널이 설정되었습니다.",
        ephemeral=True
    )


@tasks.loop(minutes=1)
async def barrier_alarm():
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    print("결계 체크", now)

    if now.minute != 0:
        return

    channel_id = config.get("CHANNEL_ID", 0)

    if channel_id == 0:
        return

    channel = bot.get_channel(channel_id)

    if channel is None:
        return

await channel.send(random.choice(CAT_MESSAGES))


@tasks.loop(seconds=30)
async def boss_alarm_check():
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    # 55분에만 체크 (보스 5분 전)
    if now.minute != 55:
        return

    alarm_hour = now.hour + 1

    if alarm_hour not in BOSS_TIMES:
        return

    if alarm_hour in sent_boss_alarm:
        return

    channel_id = config.get("CHANNEL_ID", 0)

    if channel_id == 0:
        return

    channel = bot.get_channel(channel_id)

    if channel is None:
        return

    await channel.send(random.choice(BOSS_MESSAGES))
    sent_boss_alarm.append(alarm_hour)

    print("필드보스 알림 전송:", alarm_hour)

    # 자정에 초기화
    if now.hour == 0 and now.minute == 0:
        sent_boss_alarm.clear()


bot.run(os.getenv("TOKEN"))
