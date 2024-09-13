# DomainForge

<p align="center">
  <img src="path_to_your_logo.png" alt="DomainForge Logo" width="200"/>
</p>

DomainForge is a powerful Discord bot that simplifies subdomain management directly from your Discord server. With an intuitive interface and robust features, DomainForge makes it easy to create, manage, and organize subdomains without leaving your Discord environment.

## Features

- **Easy Subdomain Creation**: Set up new subdomains with simple Discord commands.
- **Multiple Record Types**: Support for A, AAAA, CNAME, MX, TXT, and more!
- **User-Friendly Interface**: Intuitive Discord-based controls accessible to all users.
- **Admin Controls**: Powerful management tools for server administrators.
- **Cloudflare Integration**: Seamless connection with Cloudflare for reliable DNS management.

## Getting Started

1. [Invite DomainForge](https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2147483648&scope=bot%20applications.commands) to your Discord server.
2. Use the `/create-subdomain` command to start creating subdomains.
3. Follow the interactive prompts to specify domain, record type, and other details.

## Commands

- `/create-subdomain`: Start the subdomain creation process.
- `/list`: Display all subdomains created by the user.
- `/remove`: Remove a specified subdomain.
- `/userinfo`: (Admin only) View information about a user's subdomains.
- `/ban`: (Admin only) Ban a user and remove their subdomains.
- `/whois`: (Admin only) Look up the owner of a specific subdomain.

## Setup for Development

1. Clone this repository:
 ```bash 
git clone https://github.com/your-username/domainforge.git
```
2. Install dependencies:
 ```bash
cd domainforge
pip install -r requirements.txt
```
3. Set up your `.env` file with the following variables:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token 
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token

# API OF CLOUDFLAE IS LIKE  ( Token name -  Edit zone DNS	) ( Permissions - Zone.DNS,Zone.DNS) ( Resources -	All zones )
# https://dash.cloudflare.com/profile/api-tokens
```

4. Run the bot:
```bash 
python bot.py
```

## Contributing

We welcome contributions to DomainForge! Please feel free to submit issues, fork the repository and send pull requests!

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

If you need help or have any questions, please join our [support server](https://discord.gg/your-support-server-invite).

---

<p align="center">
Made with ❤ by LegendYt4k
</p>
