# 🚀 Quick Start Guide - Steam Discord Bot

Get your Steam Discord bot running in 5 minutes!

## 📋 Prerequisites

- Python 3.8+
- Discord Bot Token
- Steam Web API Key

## ⚡ Quick Setup

### 1. Get Your Tokens

**Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application
3. Go to "Bot" section
4. Create Bot and copy the token
5. Enable "Message Content Intent"

**Steam API Key:**
1. Go to [Steam Web API](https://steamcommunity.com/dev/apikey)
2. Generate a new API key

### 2. Install & Run

```bash
# Clone or download the files
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DISCORD_TOKEN=your_discord_token_here" > .env
echo "STEAM_API_KEY=your_steam_api_key_here" >> .env

# Run the bot
python discord_main.py
```

### 3. Invite Bot to Server

1. Go to Discord Developer Portal → OAuth2 → URL Generator
2. Select "bot" scope
3. Select permissions: Send Messages, Read Message History, Use Slash Commands
4. Use the generated URL to invite bot to your server

## 🎮 Test Commands

Once the bot is running, try these commands in your Discord server:

```
!start          - Welcome message and help
!profile 76561198000000000  - Get Steam profile
!game 730       - Get CS2 game info
!playercount 730 - Current CS2 players
!debug          - Bot statistics
!ping           - Test bot latency
```

## 🔧 Troubleshooting

**Bot not responding?**
- Check if token is correct
- Verify bot has proper permissions
- Ensure Message Content Intent is enabled

**Commands not working?**
- Check command prefix (default: `!`)
- Verify bot permissions in server
- Check command cooldowns

**Need help?**
- Run `!debug` for bot status
- Check logs in `logs/` directory
- Review full documentation in `DISCORD_README.md`

## 📚 Next Steps

- Read `DISCORD_README.md` for full documentation
- Check `CONVERSION_SUMMARY.md` for technical details
- Customize bot settings in `config.py`
- Add your own commands!

---

**That's it! Your Steam Discord bot is ready to use!** 🎉