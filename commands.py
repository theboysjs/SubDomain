
import discord
from discord import app_commands
from discord.ext import commands
import json

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"admins": [], "users": {}, "banned_users": []}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

def is_admin(user_id):
    data = load_data()
    return str(user_id) in data['admins']

@app_commands.command(name="ban", description="Ban a user from using the bot")
@app_commands.checks.has_permissions(administrator=True)
async def ban(interaction: discord.Interaction, user: discord.User):
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    data = load_data()
    if str(user.id) not in data['banned_users']:
        data['banned_users'].append(str(user.id))
        save_data(data)
        await interaction.response.send_message(f"{user.mention} has been banned from using the bot.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{user.mention} is already banned from using the bot.", ephemeral=True)
