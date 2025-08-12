import re
from typing import Dict, List, Optional
from datetime import datetime

def validate_steam_id(steam_id: str) -> bool:
    """Validate if the provided string is a valid Steam ID"""
    # Steam IDs are 17-digit numbers
    return bool(re.match(r'^\d{17}$', steam_id))

def validate_app_id(app_id: str) -> bool:
    """Validate if the provided string is a valid Steam App ID"""
    # App IDs are numeric
    return bool(re.match(r'^\d+$', app_id))

def format_playtime(minutes: int) -> str:
    """Format playtime in minutes to human-readable format"""
    if minutes < 60:
        return f"{minutes}m"
    elif minutes < 1440:  # less than 24 hours
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}m"
    else:
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days}d"
        else:
            return f"{days}d {remaining_hours}h"

def format_user_profile(profile: Dict) -> str:
    """Format user profile information for display"""
    if not profile:
        return "❌ Profile not found or private"
    
    name = profile.get('personaname', 'Unknown')
    real_name = profile.get('realname', 'Not specified')
    country = profile.get('loccountrycode', 'Not specified')
    status = profile.get('personastate', 0)
    profile_url = profile.get('profileurl', '')
    avatar = profile.get('avatarfull', '')
    
    # Status mapping
    status_map = {
        0: "🟤 Offline",
        1: "🟢 Online",
        2: "🟡 Busy",
        3: "🔴 Away",
        4: "⏸️ Snooze",
        5: "🔍 Looking to trade",
        6: "🎮 Looking to play"
    }
    
    status_text = status_map.get(status, "Unknown")
    
    message = f"🎮 **Steam Profile: {name}**\n\n"
    message += f"👤 **Real Name:** {real_name}\n"
    message += f"🌍 **Country:** {country}\n"
    message += f"📊 **Status:** {status_text}\n"
    message += f"🔗 **Profile:** [View Profile]({profile_url})\n"
    
    if avatar:
        message += f"🖼️ **Avatar:** [View]({avatar})"
    
    return message

def format_game_details(game: Dict) -> str:
    """Format game details for display"""
    if not game:
        return "❌ Game not found"
    
    name = game.get('name', 'Unknown')
    release_date = game.get('release_date', {}).get('date', 'Unknown')
    description = game.get('detailed_description', 'No description available')
    developer = game.get('developers', ['Unknown'])[0] if game.get('developers') else 'Unknown'
    genres = [genre['description'] for genre in game.get('genres', [])]
    price = game.get('price_overview', {})
    
    # Clean description (remove HTML tags)
    import re
    clean_description = re.sub(r'<[^>]+>', '', description)
    clean_description = clean_description[:300] + "..." if len(clean_description) > 300 else clean_description
    
    message = f"🎮 **{name}**\n\n"
    message += f"📅 **Release Date:** {release_date}\n"
    message += f"👨‍💻 **Developer:** {developer}\n"
    
    if genres:
        message += f"🏷️ **Genres:** {', '.join(genres[:3])}\n"
    
    if price and price.get('final'):
        final_price = price['final'] / 100  # Convert cents to dollars
        original_price = price.get('initial', 0) / 100
        if original_price > final_price:
            discount = price.get('discount_percent', 0)
            message += f"💰 **Price:** ${final_price:.2f} (${original_price:.2f} - {discount}% off)\n"
        else:
            message += f"💰 **Price:** ${final_price:.2f}\n"
    else:
        message += f"💰 **Price:** Free\n"
    
    message += f"\n📝 **Description:** {clean_description}"
    
    return message

def format_owned_games(games_data: Dict) -> str:
    """Format owned games list for display"""
    if not games_data or not games_data.get('response', {}).get('games'):
        return "❌ No games found or profile is private"
    
    games = games_data['response']['games']
    total_games = len(games)
    total_playtime = sum(game.get('playtime_forever', 0) for game in games)
    
    message = f"📚 **Owned Games: {total_games}**\n"
    message += f"⏱️ **Total Playtime:** {format_playtime(total_playtime)}\n\n"
    
    # Sort by playtime and show top 10
    sorted_games = sorted(games, key=lambda x: x.get('playtime_forever', 0), reverse=True)
    
    for i, game in enumerate(sorted_games[:10], 1):
        name = game.get('name', 'Unknown')
        playtime = game.get('playtime_forever', 0)
        playtime_formatted = format_playtime(playtime)
        
        message += f"{i}. **{name}** - {playtime_formatted}\n"
    
    if total_games > 10:
        message += f"\n... and {total_games - 10} more games"
    
    return message

def format_recent_games(recent_data: Dict) -> str:
    """Format recently played games for display"""
    if not recent_data or not recent_data.get('response', {}).get('games'):
        return "❌ No recent games found or profile is private"
    
    games = recent_data['response']['games']
    
    message = "🎮 **Recently Played Games**\n\n"
    
    for i, game in enumerate(games, 1):
        name = game.get('name', 'Unknown')
        playtime_2weeks = game.get('playtime_2weeks', 0)
        playtime_forever = game.get('playtime_forever', 0)
        
        message += f"{i}. **{name}**\n"
        if playtime_2weeks > 0:
            message += f"   Last 2 weeks: {format_playtime(playtime_2weeks)}\n"
        message += f"   Total: {format_playtime(playtime_forever)}\n\n"
    
    return message

def format_achievements(achievements_data: Dict, schema_data: Dict = None) -> str:
    """Format achievements for display"""
    if not achievements_data or not achievements_data.get('playerstats', {}).get('achievements'):
        return "❌ No achievements found or game doesn't support achievements"
    
    achievements = achievements_data['playerstats']['achievements']
    unlocked = sum(1 for ach in achievements if ach.get('achieved', 0) == 1)
    total = len(achievements)
    
    message = f"🏆 **Achievements: {unlocked}/{total}** ({unlocked/total*100:.1f}%)\n\n"
    
    # Show recently unlocked achievements
    unlocked_achievements = [ach for ach in achievements if ach.get('achieved', 0) == 1]
    unlocked_achievements.sort(key=lambda x: x.get('unlocktime', 0), reverse=True)
    
    for i, achievement in enumerate(unlocked_achievements[:5], 1):
        name = achievement.get('apiname', 'Unknown')
        unlock_time = achievement.get('unlocktime', 0)
        
        if unlock_time > 0:
            unlock_date = datetime.fromtimestamp(unlock_time).strftime('%Y-%m-%d')
            message += f"{i}. **{name}** - {unlock_date}\n"
        else:
            message += f"{i}. **{name}**\n"
    
    if len(unlocked_achievements) > 5:
        message += f"\n... and {len(unlocked_achievements) - 5} more achievements"
    
    return message

def format_friends_list(friends_data: Dict) -> str:
    """Format friends list for display"""
    if not friends_data or not friends_data.get('friendslist', {}).get('friends'):
        return "❌ No friends found or profile is private"
    
    friends = friends_data['friendslist']['friends']
    
    message = f"👥 **Friends: {len(friends)}**\n\n"
    
    for i, friend in enumerate(friends[:10], 1):
        steam_id = friend.get('steamid', 'Unknown')
        relationship = friend.get('relationship', 'Unknown')
        friend_since = friend.get('friend_since', 0)
        
        if friend_since > 0:
            friend_date = datetime.fromtimestamp(friend_since).strftime('%Y-%m-%d')
            message += f"{i}. **{steam_id}** - Friends since {friend_date}\n"
        else:
            message += f"{i}. **{steam_id}**\n"
    
    if len(friends) > 10:
        message += f"\n... and {len(friends) - 10} more friends"
    
    return message

def format_badges(badges_data: Dict) -> str:
    """Format badges for display"""
    if not badges_data or not badges_data.get('response', {}).get('badges'):
        return "❌ No badges found or profile is private"
    
    badges = badges_data['response']['badges']
    
    message = f"🏅 **Badges: {len(badges)}**\n\n"
    
    for i, badge in enumerate(badges[:10], 1):
        name = badge.get('badgeid', 'Unknown')
        level = badge.get('level', 1)
        completion_time = badge.get('completion_time', 0)
        
        if completion_time > 0:
            completion_date = datetime.fromtimestamp(completion_time).strftime('%Y-%m-%d')
            message += f"{i}. **{name}** (Level {level}) - {completion_date}\n"
        else:
            message += f"{i}. **{name}** (Level {level})\n"
    
    if len(badges) > 10:
        message += f"\n... and {len(badges) - 10} more badges"
    
    return message

def format_news(news_data: Dict) -> str:
    """Format game news for display"""
    if not news_data or not news_data.get('appnews', {}).get('newsitems'):
        return "❌ No news found for this game"
    
    news_items = news_data['appnews']['newsitems']
    
    message = "📰 **Latest News**\n\n"
    
    for i, news in enumerate(news_items[:5], 1):
        title = news.get('title', 'No title')
        url = news.get('url', '')
        date = news.get('date', 0)
        
        if date > 0:
            news_date = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
            message += f"{i}. **{title}** ({news_date})\n"
            if url:
                message += f"   [Read More]({url})\n\n"
        else:
            message += f"{i}. **{title}**\n"
            if url:
                message += f"   [Read More]({url})\n\n"
    
    return message

def format_comparison(user1_data: Dict, user2_data: Dict, user1_id: str, user2_id: str) -> str:
    """Format user comparison for display"""
    message = f"📊 **User Comparison**\n\n"
    
    # Compare owned games
    user1_games = user1_data.get('response', {}).get('games', [])
    user2_games = user2_data.get('response', {}).get('games', [])
    
    user1_total_playtime = sum(game.get('playtime_forever', 0) for game in user1_games)
    user2_total_playtime = sum(game.get('playtime_forever', 0) for game in user2_games)
    
    message += f"🎮 **Games Owned:**\n"
    message += f"   User 1 ({user1_id}): {len(user1_games)} games\n"
    message += f"   User 2 ({user2_id}): {len(user2_games)} games\n\n"
    
    message += f"⏱️ **Total Playtime:**\n"
    message += f"   User 1: {format_playtime(user1_total_playtime)}\n"
    message += f"   User 2: {format_playtime(user2_total_playtime)}\n\n"
    
    # Find common games
    user1_app_ids = {game['appid'] for game in user1_games}
    user2_app_ids = {game['appid'] for game in user2_games}
    common_games = user1_app_ids.intersection(user2_app_ids)
    
    message += f"🤝 **Common Games:** {len(common_games)}"
    
    return message