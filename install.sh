#!/bin/bash

# Steam Telegram Bot Installation Script
# This script helps you set up the Steam Telegram Bot

echo "🎮 Steam Telegram Bot - Installation Script"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 detected"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys:"
    echo "   1. Get a Telegram bot token from @BotFather"
    echo "   2. Get a Steam API key from https://steamcommunity.com/dev/apikey"
    echo "   3. Add them to the .env file"
else
    echo "✅ .env file already exists"
fi

# Test the installation
echo ""
echo "🧪 Testing installation..."
python3 test_bot.py

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run 'python3 main.py' to start the bot"
echo "3. Send /start to your bot in Telegram"
echo ""
echo "📖 For more information, see README.md"