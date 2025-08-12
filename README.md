# Steam Telegram Bot 🎮

A comprehensive Telegram bot that integrates with the Steam Web API to provide various Steam-related features and information. This bot offers 20 different commands to help users explore Steam profiles, games, achievements, and more.

## 🌟 Features

### Profile & Games
- **`/profile <steamid>`** - Fetch and display user's Steam profile info (avatar, nickname, real name, country, status, profile URL)
- **`/library <steamid>`** - List all games owned by a user with total playtime stats
- **`/recent <steamid>`** - Show last 5 recently played games with playtime
- **`/achievements <steamid> <appid>`** - Show user's achievement progress for a game
- **`/level <steamid>`** - Show Steam level
- **`/badges <steamid>`** - Show Steam badges for a user

### Game Information
- **`/game <appid>`** - Fetch Steam game details (name, release date, description, developer, genre, price)
- **`/playercount <appid>`** - Show current global player count for a game
- **`/news <appid>`** - Fetch latest news for a game
- **`/topgames`** - Show trending or top-selling Steam games
- **`/randomgame`** - Suggest a random Steam game

### Social Features
- **`/friends <steamid>`** - List a user's Steam friends (public only)
- **`/compare <steamid1> <steamid2>`** - Compare two users' stats (playtime, achievements)

### Advanced Features
- **`/wishlist <steamid>`** - Show user's Steam wishlist (placeholder - requires public profile)
- **`/recommend <steamid>`** - Recommend games based on user library
- **`/pricehistory <appid>`** - Show price history for a game (placeholder - requires third-party API)

### Placeholder Features (Future Implementation)
- **`/salealerts`** - Steam sale alerts (placeholder)
- **`/leaderboard`** - Game hours leaderboard in group chat (placeholder)
- **`/newreleases`** - New release alerts based on genre preferences (placeholder)
- **`/tradeoffers`** - Trade offer notifications (placeholder)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Steam API Key (get from [Steam Community](https://steamcommunity.com/dev/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SteamTelegram-Bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   STEAM_API_KEY=your_steam_api_key_here
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## 🔧 Setup Instructions

### Getting a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided by BotFather

### Getting a Steam API Key

1. Go to [Steam Community Developer](https://steamcommunity.com/dev/apikey)
2. Sign in with your Steam account
3. Accept the terms and conditions
4. Enter a domain name (can be any valid domain)
5. Copy the API key

## 📖 Usage Examples

### Basic Commands
```
/profile 76561198000000000    # Get profile info
/game 730                     # Get CS2 details
/playercount 730              # Get CS2 player count
/topgames                     # Get trending games
```

### Advanced Commands
```
/library 76561198000000000    # Get user's game library
/achievements 76561198000000000 730  # Get achievements for CS2
/compare 76561198000000000 76561198000000001  # Compare two users
/recommend 76561198000000000  # Get game recommendations
```

## 🏗️ Project Structure

```
SteamTelegram-Bot/
├── main.py              # Main entry point
├── bot.py               # Main bot class with command handlers
├── steam_api.py         # Steam API client
├── utils.py             # Utility functions and formatters
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## 🔧 Configuration

The bot uses environment variables for configuration. Key settings include:

- `TELEGRAM_TOKEN`: Your Telegram bot token
- `STEAM_API_KEY`: Your Steam API key
- `CACHE_DURATION`: Cache duration in seconds (default: 300)
- `RATE_LIMIT_DELAY`: Delay between API calls in seconds (default: 1)

## 🛠️ Technical Details

### Dependencies
- `python-telegram-bot`: Telegram Bot API wrapper
- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management
- `aiohttp`: Async HTTP client (optional)

### API Integration
- **Steam Web API**: For user profiles, games, achievements, etc.
- **Steam Store API**: For game details and featured games
- **Rate Limiting**: Built-in rate limiting to respect API limits
- **Error Handling**: Comprehensive error handling for API failures

### Features Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Profile Info | ✅ Complete | Full Steam profile data |
| Game Details | ✅ Complete | Store API integration |
| Library | ✅ Complete | Owned games with playtime |
| Recent Games | ✅ Complete | Recently played games |
| Achievements | ✅ Complete | Achievement progress |
| Player Count | ✅ Complete | Real-time player count |
| News | ✅ Complete | Game news feed |
| Friends | ✅ Complete | Public friends list |
| Top Games | ✅ Complete | Featured games |
| Recommendations | ✅ Complete | Basic recommendation system |
| User Comparison | ✅ Complete | Compare two users |
| Steam Level | ✅ Complete | User level display |
| Badges | ✅ Complete | User badges |
| Random Game | ✅ Complete | Random game suggestion |
| Wishlist | ⚠️ Placeholder | Requires web scraping |
| Price History | ⚠️ Placeholder | Requires third-party API |
| Sale Alerts | ⚠️ Placeholder | Future implementation |
| Leaderboard | ⚠️ Placeholder | Future implementation |
| New Releases | ⚠️ Placeholder | Future implementation |
| Trade Offers | ⚠️ Placeholder | Future implementation |

## 🚨 Limitations

1. **Private Profiles**: Some features require public Steam profiles
2. **API Rate Limits**: Steam API has rate limits that the bot respects
3. **Wishlist Access**: Steam doesn't provide public API for wishlists
4. **Price History**: Requires third-party service integration
5. **Real-time Features**: Some features require additional infrastructure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Steam Web API](https://developer.valvesoftware.com/wiki/Steam_Web_API) for providing the API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram integration
- Steam Community for the API access

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🔄 Updates

The bot is actively maintained and updated with new features. Check the repository regularly for updates and improvements.

---

**Happy Gaming! 🎮**