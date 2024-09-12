import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from views.subdomain_creation import SubdomainCreationView
from cloudflare import get_user_subdomains, delete_subdomain

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Load data from JSON
def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            return json.load(f)
    return {"admins": [], "users": {}}

# Save data to JSON
def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Check if user is an admin
def is_admin(user_id):
    data = load_data()
    return user_id in data['admins']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="create-subdomain", description="Create a new subdomain")
async def create_subdomain(interaction: discord.Interaction):
    view = SubdomainCreationView()
    embed = discord.Embed(title="Subdomain Creation", description="*Let's create a subdomain!*", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, view=view)
    await view.wait()

@bot.tree.command(name="list", description="Show subdomains under the user")
async def list_subdomains(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_data()
    if user_id in data['users']:
        subdomains = data['users'][user_id]
        embed = discord.Embed(title="Your Subdomains", description=f"{', '.join(subdomains)}", color=discord.Color.blue())
    else:
        embed = discord.Embed(title="No Subdomains", description="You don't have any subdomains.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Show user info (Bot admin only)")
async def userinfo(interaction: discord.Interaction, user: discord.User):
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    user_id = str(user.id)
    if user_id in data['users']:
        subdomains = data['users'][user_id]
        embed = discord.Embed(title=f"User Info: {user.name}", description=f"Total domains: {len(subdomains)}\nDomains: {', '.join(subdomains)}", color=discord.Color.blue())
    else:
        embed = discord.Embed(title=f"User Info: {user.name}", description="No subdomains registered.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Ban user and delete all their subdomains (Bot admin only)")
async def ban_user(interaction: discord.Interaction, user: discord.User):
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    user_id = str(user.id)
    if user_id in data['users']:
        subdomains = data['users'][user_id]
        for subdomain in subdomains:
            await delete_subdomain(subdomain)
        del data['users'][user_id]
        save_data(data)
        embed = discord.Embed(title="User Banned", description=f"User {user.name} has been banned and all their subdomains have been deleted.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="No Subdomains", description=f"User {user.name} has no subdomains to delete.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="whois", description="Look up the subdomain registered by the user (Bot admin only)")
async def whois(interaction: discord.Interaction, domain: str):
    if not is_admin(interaction.user.id):
        embed = discord.Embed(title="Permission Denied", description="You don't have permission to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    for user_id, subdomains in data['users'].items():
        if domain in subdomains:
            user = await bot.fetch_user(int(user_id))
            embed = discord.Embed(title="Whois Lookup", description=f"Domain {domain} is registered by user {user.name} (ID: {user_id})", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
            return
    embed = discord.Embed(title="Whois Lookup", description=f"Domain {domain} is not registered by any user.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove", description="Delete user's subdomain")
async def remove_subdomain(interaction: discord.Interaction, domain: str):
    user_id = str(interaction.user.id)
    data = load_data()
    if user_id in data['users'] and domain in data['users'][user_id]:
        if await delete_subdomain(domain):
            data['users'][user_id].remove(domain)
            save_data(data)
            embed = discord.Embed(title="Subdomain Deleted", description=f"Subdomain {domain} has been deleted.", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Deletion Failed", description=f"Failed to delete subdomain {domain}.", color=discord.Color.red())
    else:
        embed = discord.Embed(title="Ownership Issue", description=f"You don't own the subdomain {domain}.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
