# Steam Discord Bot

A comprehensive Discord bot that integrates with the Steam Web API to provide various Steam-related features and information. This is a conversion of the original Telegram bot to Discord using `discord.py`.

## 🚀 Features

### Profile & Games
- **Profile Information**: Get detailed Steam user profiles
- **Game Library**: View owned games with playtime statistics
- **Recent Games**: See recently played games
- **Achievements**: Track game achievements and progress
- **Steam Level**: Check user's Steam level
- **Badges**: View user's Steam badges

### Game Information
- **Game Details**: Comprehensive game information and statistics
- **Player Counts**: Real-time player counts for games
- **Game News**: Latest news and updates for games
- **Top Games**: Trending games on Steam
- **Random Games**: Discover new games randomly

### Social Features
- **Friends List**: View user's Steam friends
- **User Comparison**: Compare two Steam users' libraries

### Admin & Utility
- **Debug Information**: Bot statistics and system information
- **Ping Test**: Check bot latency
- **Help System**: Comprehensive command help

## 📋 Requirements

- Python 3.8+
- Discord Bot Token
- Steam Web API Key
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd steam-discord-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   STEAM_API_KEY=your_steam_api_key_here
   ```

4. **Get your Discord Bot Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Create a bot and copy the token
   - Enable the following intents:
     - Message Content Intent
     - Server Members Intent

5. **Get your Steam API Key**:
   - Go to [Steam Web API](https://steamcommunity.com/dev/apikey)
   - Generate a new API key

## 🚀 Running the Bot

### Option 1: Direct Execution
```bash
python discord_main.py
```

### Option 2: Using the Install Script
```bash
chmod +x install.sh
./install.sh
```

## 📝 Commands

### Basic Commands
- `!start` - Welcome message and command overview
- `!help` - Show help information
- `!ping` - Check bot latency
- `!info` - Show bot information
- `!debug` - Show debug information

### Profile Commands
- `!profile <steamid>` - Get Steam user profile info
- `!library <steamid>` - List owned games
- `!recent <steamid>` - Recently played games
- `!achievements <steamid> <appid>` - Game achievements
- `!level <steamid>` - Steam level
- `!badges <steamid>` - User badges

### Game Commands
- `!game <appid>` - Game details
- `!playercount <appid>` - Current players
- `!news <appid>` - Game news
- `!topgames` - Trending games
- `!randomgame` - Random game suggestion

### Social Commands
- `!friends <steamid>` - Friends list
- `!compare <steamid1> <steamid2>` - Compare users

## 🔧 Configuration

The bot uses environment variables for configuration. Key settings in `config.py`:

```python
# Bot Tokens
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

# Steam API Base URLs
STEAM_API_BASE = "https://api.steampowered.com"
STEAM_STORE_BASE = "https://store.steampowered.com"
STEAM_COMMUNITY_BASE = "https://steamcommunity.com"

# Cache settings
CACHE_DURATION = 300  # 5 minutes in seconds

# Rate limiting
RATE_LIMIT_DELAY = 1  # seconds between API calls
```

## 🏗️ Architecture

### Modular Design
The Discord bot is organized into modular components:

1. **Main Bot Class** (`SteamDiscordBot`):
   - Handles bot initialization and lifecycle
   - Manages global error handling
   - Runs background tasks

2. **Command Cogs**:
   - `SteamCommands`: All Steam-related commands
   - `AdminCommands`: Utility and admin commands

3. **Supporting Modules**:
   - `steam_api.py`: Steam Web API integration
   - `utils.py`: Utility functions and formatting
   - `config.py`: Configuration management
   - `logging_config.py`: Logging setup

### Key Features

#### Async/Await Support
All commands and API calls are properly async to avoid blocking the event loop:

```python
@commands.command(name='profile')
@commands.cooldown(1, 5, commands.BucketType.user)
async def profile_command(self, ctx, steam_id: str):
    # Async command implementation
```

#### Error Handling
Comprehensive error handling with user-friendly messages:

```python
async def on_command_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
    # ... more error types
```

#### Rate Limiting
Commands have cooldowns to prevent spam:

```python
@commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
```

#### Rich Embeds
Responses use Discord embeds for better formatting:

```python
embed = discord.Embed(
    title=f"🎮 Steam Profile: {profile.get('personaname', 'Unknown')}",
    description=message,
    color=discord.Color.green(),
    url=profile.get('profileurl', '')
)
```

## 🔍 Logging

The bot includes comprehensive logging:

- **Console Output**: Real-time bot status
- **File Logs**: Rotating log files for debugging
- **Error Logs**: Separate error tracking
- **API Logs**: Steam API call monitoring

Log files are stored in the `logs/` directory:
- `steam_bot.log` - General bot logs
- `steam_bot_errors.log` - Error logs
- `steam_bot_api.log` - API call logs

## 🚀 Deployment

### Local Development
```bash
python discord_main.py
```

### Production Deployment
1. **VPS/Cloud Setup**:
   ```bash
   # Install Python and dependencies
   sudo apt update
   sudo apt install python3 python3-pip
   pip3 install -r requirements.txt
   
   # Set up environment variables
   export DISCORD_TOKEN="your_token"
   export STEAM_API_KEY="your_key"
   
   # Run the bot
   python3 discord_main.py
   ```

2. **Using PM2 (Recommended)**:
   ```bash
   npm install -g pm2
   pm2 start discord_main.py --name "steam-discord-bot" --interpreter python3
   pm2 save
   pm2 startup
   ```

3. **Docker Deployment**:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "discord_main.py"]
   ```

## 🔧 Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check if the bot token is correct
   - Verify the bot has proper permissions
   - Ensure Message Content Intent is enabled

2. **Commands not working**:
   - Check command prefix (default: `!`)
   - Verify bot permissions in the server
   - Check command cooldowns

3. **Steam API errors**:
   - Verify Steam API key is valid
   - Check if Steam services are available
   - Review API rate limits

### Debug Commands
- `!debug` - Shows bot statistics and system info
- `!ping` - Tests bot latency
- Check logs in `logs/` directory

## 📊 Performance

### Optimizations
- **Async Operations**: All I/O operations are async
- **Caching**: Steam API responses are cached
- **Rate Limiting**: Prevents API abuse
- **Background Tasks**: Periodic cleanup runs in background

### Monitoring
- Command usage statistics
- Error tracking and reporting
- API call monitoring
- Bot uptime and performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Original Telegram bot implementation
- Discord.py library and community
- Steam Web API documentation
- All contributors and users

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Join our Discord server
- Check the documentation

---

**Note**: This Discord bot maintains full compatibility with the original Telegram bot's functionality while adapting to Discord's API and conventions.