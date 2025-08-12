# Optimized Steam Discord Bot

A production-ready Discord bot for Steam API integration with advanced features including intelligent caching, rate limiting, comprehensive error handling, and performance monitoring.

## 🚀 Features

### Core Features
- **Steam Profile Lookup**: Get detailed user profiles, game libraries, and achievements
- **Game Information**: Fetch game details, player counts, and news
- **Social Features**: Compare users, view friends lists, and recent activity
- **Real-time Data**: Current player counts and live game statistics

### Performance Optimizations
- **Intelligent Caching**: Multi-level caching with TTL and LRU eviction
- **Async Processing**: Non-blocking operations for better responsiveness
- **Rate Limiting**: Advanced rate limiting with sliding window algorithm
- **Circuit Breaker**: Automatic failure detection and recovery
- **Connection Pooling**: Optimized HTTP connections with keep-alive

### Security & Reliability
- **Environment Variables**: Secure configuration management
- **Input Validation**: Comprehensive validation for all user inputs
- **Error Handling**: Graceful error handling with detailed logging
- **Health Monitoring**: Real-time health checks and alerting
- **Backup & Recovery**: Automatic data backup and recovery mechanisms

### Monitoring & Analytics
- **Structured Logging**: JSON-formatted logs with detailed metrics
- **Performance Tracking**: Response time monitoring and optimization
- **Error Tracking**: Comprehensive error reporting and analysis
- **Usage Analytics**: Command usage statistics and trends
- **Health Dashboard**: Real-time bot health and performance metrics

## 📋 Requirements

- Python 3.8+
- Discord Bot Token
- Steam API Key
- 512MB RAM minimum (1GB recommended)
- Stable internet connection

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd steam-discord-bot
```

### 2. Install Dependencies
```bash
pip install -r optimized_requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root:

```env
# Required Configuration
DISCORD_TOKEN=your_discord_bot_token_here
STEAM_API_KEY=your_steam_api_key_here

# Optional Configuration
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
RETRY_ATTEMPTS=3
RETRY_DELAY=1.0

# Cache Settings
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=300
CACHE_PROFILE_TTL=300
CACHE_GAME_TTL=3600
CACHE_PLAYER_COUNT_TTL=120

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=15
RATE_LIMIT_WINDOW=60

# Security Settings
ALLOWED_GUILDS=123456789,987654321
ADMIN_USER_IDS=123456789,987654321
DEBUG_MODE=false

# Feature Flags
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
ENABLE_ANALYTICS=true

# Logging
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=true
```

### 4. Get API Keys

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable required intents (Message Content, Server Members)

#### Steam API Key
1. Go to [Steam API Key Registration](https://steamcommunity.com/dev/apikey)
2. Register for a free API key
3. Copy the key to your `.env` file

### 5. Run the Bot
```bash
python optimized_discord_bot.py
```

## 🎮 Commands

### Profile Commands
- `!profile <steamid>` - Get user profile information
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

### Admin Commands
- `!stats` - Bot statistics and performance metrics
- `!cache info` - Cache information
- `!cache clear` - Clear cache
- `!ping` - Check bot latency

## 🔧 Configuration

### Performance Tuning

#### Cache Configuration
```env
# Increase cache size for high-traffic servers
CACHE_MAX_SIZE=2000

# Adjust TTL based on data freshness requirements
CACHE_PROFILE_TTL=600    # 10 minutes
CACHE_GAME_TTL=7200      # 2 hours
CACHE_PLAYER_COUNT_TTL=60 # 1 minute
```

#### Rate Limiting
```env
# Adjust rate limits based on server size
RATE_LIMIT_MAX_REQUESTS=20
RATE_LIMIT_WINDOW=60
```

#### Concurrent Requests
```env
# Increase for high-performance servers
MAX_CONCURRENT_REQUESTS=20
REQUEST_TIMEOUT=45
```

### Security Configuration

#### Guild Restrictions
```env
# Restrict bot to specific servers
ALLOWED_GUILDS=123456789,987654321
```

#### Admin Users
```env
# Grant admin privileges to specific users
ADMIN_USER_IDS=123456789,987654321
```

## 📊 Monitoring

### Log Files
The bot creates several log files in the `logs/` directory:

- `steam_bot_all.log` - All log messages
- `steam_bot_errors.log` - Error messages only
- `steam_bot_api.log` - API call logs
- `steam_bot_commands.log` - Command execution logs
- `steam_bot_performance.log` - Performance metrics

### Metrics Dashboard
Use the `!stats` command to view:
- Bot uptime and performance
- Cache usage and hit rates
- API call statistics
- Error rates and response times
- Recent performance trends

### Health Checks
The bot automatically performs health checks every 2 minutes:
- Cache health monitoring
- Response time analysis
- Error rate tracking
- Resource usage monitoring

## 🚨 Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check if the bot is online in Discord
2. Verify the bot token is correct
3. Ensure the bot has proper permissions
4. Check logs for error messages

#### API Rate Limiting
1. Reduce concurrent requests: `MAX_CONCURRENT_REQUESTS=5`
2. Increase rate limit window: `RATE_LIMIT_WINDOW=120`
3. Enable caching to reduce API calls

#### High Memory Usage
1. Reduce cache size: `CACHE_MAX_SIZE=500`
2. Enable cache cleanup: `CACHE_CLEANUP_INTERVAL=300`
3. Monitor with `!stats` command

#### Slow Response Times
1. Check internet connection
2. Verify Steam API status
3. Enable caching for frequently accessed data
4. Monitor response times with `!ping`

### Debug Mode
Enable debug mode for detailed logging:
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 🔒 Security Best Practices

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique tokens
- Rotate tokens regularly
- Use different tokens for development and production

### Access Control
- Restrict bot to specific guilds
- Grant admin privileges only to trusted users
- Monitor command usage for suspicious activity

### API Security
- Keep Steam API key secure
- Monitor API usage for unusual patterns
- Implement rate limiting to prevent abuse

## 📈 Performance Optimization

### Caching Strategy
- Profile data: 5 minutes (frequently changing)
- Game data: 1 hour (rarely changes)
- Player counts: 2 minutes (real-time data)

### Rate Limiting
- Per-user rate limiting prevents abuse
- Sliding window algorithm for fair distribution
- Automatic backoff on API errors

### Connection Optimization
- HTTP connection pooling
- Keep-alive connections
- DNS caching
- Automatic retry with exponential backoff

## 🧪 Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Performance Tests
```bash
pytest tests/performance/ -v
```

## 📝 Development

### Code Style
The project uses:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking

```bash
# Format code
black .

# Check types
mypy .

# Lint code
flake8 .
```

### Adding New Commands
1. Create a new method in `OptimizedSteamCommands`
2. Add rate limiting decorator: `@rate_limit_check()`
3. Implement proper error handling
4. Add logging and metrics
5. Update documentation

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

### Documentation
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Steam Web API Documentation](https://developer.valvesoftware.com/wiki/Steam_Web_API)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)

### Community
- Discord Server: [Link to your Discord server]
- GitHub Issues: [Repository issues page]
- Wiki: [Project wiki]

### Professional Support
For enterprise deployments and custom features, contact: [your-email@domain.com]

## 🔄 Changelog

### Version 2.0.0 (Current)
- Complete rewrite with async architecture
- Advanced caching system
- Comprehensive error handling
- Performance monitoring
- Security improvements
- Modular code structure

### Version 1.0.0
- Basic Steam API integration
- Simple Discord commands
- Basic error handling

---

**Note**: This bot is designed for production use with high availability and performance requirements. For development or testing, consider using the simplified version in the `legacy/` directory.