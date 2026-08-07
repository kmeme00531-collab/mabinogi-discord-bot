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


@bot.tree.command(name="setchannel", description="현재 채널을 알림 채널로 설정")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction):
    config["CHANNEL_ID"] = interaction.channel.id
    save_config(config)
    await interaction.response.send_message("✅ 알림 채널이 설정되었습니다.", ephemeral=True)


@tasks.loop(minutes=1)
async def barrier_alarm():
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
