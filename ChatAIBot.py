import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Discord 設置
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 全域變數定義
HISTORY_LIMIT = 10  # 傳給 API 的最大歷史句數
COMPRESS_COUNT = 5  # 保留未壓縮的近期句數

# 角色設定
CHARACTER_PROFILE = {
    "name": "艾莉絲",
    "personality": "溫柔、聰明、喜歡幫助人、有點幽默",
    "background": "來自奇幻世界的精靈學者，研究人類文化",
    "tone": "友好而有智慧，偶爾帶點俏皮"
}

conversation_history = []
command_mode = True

def save_history():
    with open('conversation_history.json', 'w', encoding='utf-8') as f:
        for entry in conversation_history:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def load_history():
    global conversation_history
    conversation_history = []
    try:
        with open('conversation_history.json', 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    conversation_history.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            # 只保留最後 HISTORY_LIMIT 句
            conversation_history = conversation_history[-HISTORY_LIMIT:]
    except FileNotFoundError:
        conversation_history = []

async def call_gemini_api(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(f"{url}?key={api_key}", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"錯誤：API 回應碼 {response.status_code}"
    except Exception as e:
        return f"錯誤：{str(e)}"

async def compress_history_with_gemini(history, compress_count=COMPRESS_COUNT):
    if len(history) <= HISTORY_LIMIT:
        return history.copy()

    to_compress = history[:-compress_count]
    to_keep = history[-compress_count:]

    if not to_compress:
        return to_keep

    history_text = "\n".join([f"[{h['time']}] {h['role']}: {h['content']}" for h in to_compress])
    summary_prompt = f"請將以下對話歷史壓縮成一句簡潔自然的摘要：\n{history_text}"
    summary = await call_gemini_api(summary_prompt)

    compressed_entry = {
        "time": to_compress[-1]['time'],
        "role": "系統",
        "content": f"對話摘要：{summary}"
    }

    return [compressed_entry] + to_keep

def create_prompt(question):
    character_prompt = f"你是一個名叫{CHARACTER_PROFILE['name']}的角色，" \
                     f"性格是{CHARACTER_PROFILE['personality']}，" \
                     f"背景是{CHARACTER_PROFILE['background']}，" \
                     f"說話語氣是{CHARACTER_PROFILE['tone']}。請根據這個設定回答問題。"
    history_text = "\n過去的對話記錄：\n" + "\n".join(
        [f"[{h['time']}] {h['role']}: {h['content']}" 
         for h in conversation_history[-HISTORY_LIMIT:]]
    ) if conversation_history else ""
    return f"{character_prompt}\n{history_text}\n現在的問題：{question}"

async def process_gemini_response(channel, question, is_cmd=False):
    full_prompt = create_prompt(question)
    answer = await call_gemini_api(full_prompt)
    if not is_cmd:
        conversation_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": "user",
            "content": question
        })
        conversation_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": CHARACTER_PROFILE['name'],
            "content": answer
        })
        save_history()
    await channel.send(f"{CHARACTER_PROFILE['name']}：{answer}")

@bot.event
async def on_ready():
    await bot.tree.sync()  # 移除 guild 限制，同步到所有伺服器
    load_history()
    print(f'機器人已啟動：{bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        await process_gemini_response(message.channel, message.content)
    elif message.guild and not command_mode:  # 移除 ALLOWED_GUILD_ID 檢查
        dm_channel = await message.author.create_dm()
        await message.channel.send(f"{CHARACTER_PROFILE['name']}：我已將我們的對話轉到你的DM！")
        await process_gemini_response(dm_channel, message.content)

@bot.tree.command(
    name="role",
    description="問艾莉絲一個問題"
)  # 移除 guild 限制
async def role(interaction: discord.Interaction, question: str):
    dm_channel = await interaction.user.create_dm()
    await interaction.response.send_message(f"{CHARACTER_PROFILE['name']}：我會在你的DM中回答！")
    await process_gemini_response(dm_channel, question)

@bot.tree.command(
    name="summarize",
    description="讓艾莉絲壓縮對話歷史成摘要"
)  # 移除 guild 限制
@app_commands.describe(count="要保留未壓縮的句數（預設5）")
async def summarize(interaction: discord.Interaction, count: int = COMPRESS_COUNT):
    global conversation_history
    await interaction.response.defer()
    dm_channel = await interaction.user.create_dm()
    
    if len(conversation_history) <= HISTORY_LIMIT:
        await dm_channel.send(f"{CHARACTER_PROFILE['name']}：對話歷史還不夠長，無需壓縮哦～")
    else:
        compressed_history = await compress_history_with_gemini(conversation_history, compress_count=count)
        conversation_history = compressed_history
        save_history()
        await dm_channel.send(f"{CHARACTER_PROFILE['name']}：我已經把之前的對話壓縮成摘要啦！現在歷史只保留 {len(conversation_history)} 句。")
    
    await interaction.followup.send(f"{CHARACTER_PROFILE['name']}：壓縮完成，請查看DM！")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))