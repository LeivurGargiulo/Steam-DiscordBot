# Steam Telegram Bot - Example Usage

This file contains examples of how to use the Steam Telegram Bot commands with sample outputs.

## 🚀 Getting Started

1. **Start the bot**: Send `/start` to your bot
2. **Get help**: Send `/help` for command list

## 📋 Command Examples

### Profile Commands

#### `/profile <steamid>`
**Example**: `/profile 76561197960287930`

**Expected Output**:
```
🎮 Steam Profile: Valve

👤 Real Name: Valve
🌍 Country: US
📊 Status: 🟢 Online
🔗 Profile: View Profile
🖼️ Avatar: View
```

### Game Commands

#### `/game <appid>`
**Example**: `/game 730` (Counter-Strike 2)

**Expected Output**:
```
🎮 Counter-Strike 2

📅 Release Date: 2012-08-21
👨‍💻 Developer: Valve
🏷️ Genres: Action, FPS
💰 Price: Free

📝 Description: Counter-Strike 2 is the largest technical leap forward in Counter-Strike history...
```

#### `/playercount <appid>`
**Example**: `/playercount 730`

**Expected Output**:
```
👥 Counter-Strike 2

🎮 Current Players: 1,234,567
```

#### `/news <appid>`
**Example**: `/news 730`

**Expected Output**:
```
📰 Latest News

1. CS2 Major Update Released (2024-01-15)
   Read More

2. New Operation Announced (2024-01-10)
   Read More
```

### Library Commands

#### `/library <steamid>`
**Example**: `/library 76561197960287930`

**Expected Output**:
```
📚 Owned Games: 150
⏱️ Total Playtime: 45d 12h 30m

1. Counter-Strike 2 - 2d 15h 30m
2. Dota 2 - 1d 8h 45m
3. Team Fortress 2 - 12h 20m
...
```

#### `/recent <steamid>`
**Example**: `/recent 76561197960287930`

**Expected Output**:
```
🎮 Recently Played Games

1. Counter-Strike 2
   Last 2 weeks: 5h 30m
   Total: 2d 15h 30m

2. Dota 2
   Last 2 weeks: 2h 15m
   Total: 1d 8h 45m
```

### Achievement Commands

#### `/achievements <steamid> <appid>`
**Example**: `/achievements 76561197960287930 730`

**Expected Output**:
```
🏆 Achievements: 45/167 (27.0%)

1. First Blood - 2024-01-10
2. Sharpshooter - 2024-01-08
3. Team Player - 2024-01-05
...
```

### Social Commands

#### `/friends <steamid>`
**Example**: `/friends 76561197960287930`

**Expected Output**:
```
👥 Friends: 25

1. 76561198012345678 - Friends since 2023-05-15
2. 76561198087654321 - Friends since 2023-03-20
...
```

#### `/compare <steamid1> <steamid2>`
**Example**: `/compare 76561197960287930 76561198012345678`

**Expected Output**:
```
📊 User Comparison

🎮 Games Owned:
   User 1 (76561197960287930): 150 games
   User 2 (76561198012345678): 89 games

⏱️ Total Playtime:
   User 1: 45d 12h 30m
   User 2: 23d 8h 15m

🤝 Common Games: 45
```

### Game Discovery Commands

#### `/topgames`
**Example**: `/topgames`

**Expected Output**:
```
🔥 Top Games on Steam

1. Counter-Strike 2 (ID: 730)
2. Dota 2 (ID: 570)
3. PUBG: BATTLEGROUNDS (ID: 578080)
...
```

#### `/randomgame`
**Example**: `/randomgame`

**Expected Output**:
```
🎮 Random Game: Portal 2

📅 Release Date: 2011-04-19
👨‍💻 Developer: Valve
🏷️ Genres: Puzzle, Adventure
💰 Price: $9.99

📝 Description: Portal 2 draws from the award-winning formula of innovative gameplay...
```

### User Stats Commands

#### `/level <steamid>`
**Example**: `/level 76561197960287930`

**Expected Output**:
```
📊 Steam Level

👤 User: Valve
⭐ Level: 42
```

#### `/badges <steamid>`
**Example**: `/badges 76561197960287930`

**Expected Output**:
```
🏅 Badges: 15

1. Community Ambassador (Level 5) - 2023-12-15
2. Game Collector (Level 3) - 2023-11-20
...
```

### Advanced Commands

#### `/recommend <steamid>`
**Example**: `/recommend 76561197960287930`

**Expected Output**:
```
🎯 Game Recommendations

1. Team Fortress 2 (ID: 440)
2. Left 4 Dead 2 (ID: 550)
3. Portal (ID: 400)
...
```

## ⚠️ Common Issues

### Private Profiles
If a Steam profile is private, you'll see messages like:
```
❌ Profile not found or private
❌ No games found or profile is private
```

### Invalid Steam IDs
Steam IDs must be 17-digit numbers:
```
❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.
```

### Invalid App IDs
App IDs must be numeric:
```
❌ Invalid App ID format. App IDs are numeric.
```

## 🎯 Tips for Best Results

1. **Use public Steam profiles** for best results
2. **Steam IDs are 17 digits** - you can find them in Steam profile URLs
3. **App IDs are numeric** - you can find them in Steam store URLs
4. **Popular games work best** for player count and news
5. **Be patient** - some API calls may take a few seconds

## 🔗 Useful Resources

- **Find Steam ID**: Use Steam profile URL or Steam ID finder websites
- **Find App ID**: Look in Steam store URL (e.g., `store.steampowered.com/app/730/`)
- **Steam API Documentation**: https://developer.valvesoftware.com/wiki/Steam_Web_API