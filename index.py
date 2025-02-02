import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# Load hoặc tạo file JSON để lưu trữ thông tin
if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
        data = json.load(f)
else:
    data = {}

# Khởi tạo bot với intents và slash commands
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} đã sẵn sàng!')
    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ {len(synced)} lệnh slash.")
    except Exception as e:
        print(f"Lỗi khi đồng bộ lệnh slash: {e}")

# Lệnh slash để submit thông tin
@bot.tree.command(name="submit", description="Gửi thông tin video, tên ingame và rank")
async def submit(interaction: discord.Interaction, video_link: str, ingame_name: str, rank: str):
    # Lưu thông tin vào JSON
    data[str(interaction.user.id)] = {
        'video_link': video_link,
        'ingame_name': ingame_name,
        'rank': rank
    }

    with open('data.json', 'w') as f:
        json.dump(data, f)

    # Gửi thông báo thành công
    await interaction.response.send_message("Đã gửi thông tin thành công!", ephemeral=True)

    # Gửi video vào kênh đã setup
    if 'server_id' in data and 'channel_id' in data:
        server = bot.get_guild(data['server_id'])
        channel = server.get_channel(data['channel_id'])
        await channel.send(
            f"Video từ {interaction.user.mention}:\n"
            f"Link video: {video_link}\n"
            f"Tên ingame: ||{ingame_name}||\n"
            f"Rank: ||{rank}||"
        )
    else:
        await interaction.followup.send("Chưa setup kênh để gửi video.", ephemeral=True)

# Lệnh slash để setup kênh gửi video
@bot.tree.command(name="setup", description="Setup kênh để gửi video")
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        data['server_id'] = interaction.guild.id
        data['channel_id'] = interaction.channel.id
        with open('data.json', 'w') as f:
            json.dump(data, f)
        await interaction.response.send_message("Đã setup kênh gửi video thành công!", ephemeral=True)
    else:
        await interaction.response.send_message("Bạn không có quyền để thực hiện lệnh này.", ephemeral=True)

# Chạy bot với token
bot.run('...')