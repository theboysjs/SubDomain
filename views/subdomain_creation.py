import discord
from discord.ui import Select, View, Button
from config import DOMAINS, RECORD_TYPES, RECORD_FEATURES
from cloudflare import create_subdomain
import uuid
import json
import os

class SubdomainCreationView(View):
    def __init__(self):
        super().__init__(timeout=60)  # 60 seconds timeout
        self.domain = None
        self.record_type = None
        self.record_content = None
        self.proxy_status = None
        self.additional_features = {}
        self.uuid = str(uuid.uuid4())
        self.add_item(Select(placeholder="Select a domain", 
                             options=[discord.SelectOption(label=domain) for domain in DOMAINS],
                             custom_id="domain_select"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "domain_select":
            await self.select_domain(interaction)
        elif interaction.data["custom_id"] == "record_type_select":
            await self.select_record_type(interaction)
        elif interaction.data["custom_id"] == "proxy_status_select":
            await self.select_proxy_status(interaction)
        elif interaction.data["custom_id"] == "confirm":
            await self.confirm(interaction)
        elif interaction.data["custom_id"] == "cancel":
            await self.cancel(interaction)
        return True

    async def on_timeout(self):
        # Clear the view when it times out
        self.clear_items()

    async def select_domain(self, interaction: discord.Interaction):
        self.domain = interaction.data["values"][0]
        self.clear_items()
        self.add_item(Select(placeholder="Select a record type", 
                             options=[discord.SelectOption(label=record_type) for record_type in RECORD_TYPES],
                             custom_id="record_type_select"))
        embed = discord.Embed(title="Subdomain Creation", description=f"Selected domain: {self.domain}\nNow, choose a record type:", color=discord.Color.blue())
        await interaction.response.edit_message(embed=embed, view=self)

    async def select_record_type(self, interaction: discord.Interaction):
        self.record_type = interaction.data["values"][0]
        await interaction.response.send_modal(RecordContentModal(self))

    async def select_proxy_status(self, interaction: discord.Interaction):
        self.proxy_status = interaction.data["values"][0] == "True"
        await self.update_view(interaction)

    async def confirm(self, interaction: discord.Interaction):
        await self.finalize_subdomain(interaction)

    async def cancel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Subdomain Creation", description="Subdomain creation cancelled.", color=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=None)

    async def update_view(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Subdomain Creation", color=discord.Color.green())
        embed.add_field(name="Domain", value=self.domain, inline=False)
        embed.add_field(name="Record Type", value=self.record_type, inline=False)
        embed.add_field(name="Record Content", value=self.record_content, inline=False)
        embed.add_field(name="Proxy Status", value="Proxied" if self.proxy_status else "DNS only", inline=False)
        for feature, value in self.additional_features.items():
            embed.add_field(name=feature.capitalize(), value=value, inline=False)
        embed.add_field(name="Confirmation", value="Please confirm or cancel the subdomain creation.", inline=False)
        
        self.clear_items()
        self.add_item(Button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm"))
        self.add_item(Button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel"))
        await interaction.response.edit_message(embed=embed, view=self)

    async def finalize_subdomain(self, interaction: discord.Interaction):
        try:
            success, message = await create_subdomain(self.domain, self.record_type, self.record_content, self.proxy_status, self.additional_features)
            
            if success:
                # Save user data
                data = load_data()
                user_id = str(interaction.user.id)
                if user_id not in data['users']:
                    data['users'][user_id] = []
                subdomain = f"{self.record_content.split(',')[0]}"
                data['users'][user_id].append(subdomain)
                save_data(data)

                embed = discord.Embed(title="Subdomain Created", description=f"Subdomain created successfully!\n{message}", color=discord.Color.green())
                await interaction.response.edit_message(embed=embed, view=None)
                
                # Send DM to user
                dm_embed = discord.Embed(title="Subdomain Registration Successful", color=discord.Color.green())
                dm_embed.add_field(name="Domain", value=subdomain, inline=False)
                dm_embed.add_field(name="Record Type", value=self.record_type, inline=False)
                dm_embed.add_field(name="Content", value=self.record_content.split(',')[1], inline=False)
                dm_embed.add_field(name="Proxy Status", value="Proxied" if self.proxy_status else "DNS only", inline=False)
                for feature, value in self.additional_features.items():
                    dm_embed.add_field(name=feature.capitalize(), value=value, inline=False)
                await interaction.user.send(embed=dm_embed)
            else:
                embed = discord.Embed(title="Subdomain Creation Failed", description=f"Failed to create DNS record. Cloudflare returned the following error:\n```\n{message}\n```", color=discord.Color.red())
                await interaction.response.edit_message(embed=embed, view=None)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"An unexpected error occurred: {str(e)}", color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)

class RecordContentModal(discord.ui.Modal, title="Enter Record Content"):
    def __init__(self, view: SubdomainCreationView):
        super().__init__()
        self.view = view
        self.add_item(discord.ui.TextInput(label="Subdomain Name", custom_id="name"))
        self.add_item(discord.ui.TextInput(label="Record Content", custom_id="content"))
        
        # Add additional fields based on record type
        if self.view.record_type in RECORD_FEATURES:
            for feature in RECORD_FEATURES[self.view.record_type]:
                self.add_item(discord.ui.TextInput(label=feature.capitalize(), custom_id=feature))

    async def on_submit(self, interaction: discord.Interaction):
        self.view.record_content = f"{self.children[0].value}.{self.view.domain},{self.children[1].value}"
        
        # Store additional features
        for child in self.children[2:]:
            self.view.additional_features[child.custom_id] = child.value
        
        self.view.clear_items()
        self.view.add_item(Select(placeholder="Proxy status", 
                                  options=[discord.SelectOption(label="Proxied", value="True"),
                                           discord.SelectOption(label="DNS only", value="False")],
                                  custom_id="proxy_status_select"))
        
        embed = discord.Embed(title="Subdomain Creation", color=discord.Color.blue())
        embed.add_field(name="Domain", value=self.view.domain, inline=False)
        embed.add_field(name="Record Type", value=self.view.record_type, inline=False)
        embed.add_field(name="Record Content", value=self.view.record_content, inline=False)
        for feature, value in self.view.additional_features.items():
            embed.add_field(name=feature.capitalize(), value=value, inline=False)
        embed.add_field(name="Next Step", value="Choose proxy status", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self.view)

def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            return json.load(f)
    return {"admins": [], "users": {}}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
