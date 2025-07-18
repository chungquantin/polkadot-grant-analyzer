#!/bin/bash

# Polkadot Grant Analyzer Deployment Script
# This script helps you deploy your app to various platforms

set -e

echo "🚀 Polkadot Grant Analyzer Deployment Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Error: streamlit_app.py not found. Please run this script from the project root."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check environment variables
check_env_vars() {
    echo "🔍 Checking environment variables..."
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "⚠️  Warning: GITHUB_TOKEN not set"
        echo "   You'll need to set this in your deployment platform"
    else
        echo "✅ GITHUB_TOKEN is set"
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️  Warning: OPENAI_API_KEY not set (optional for AI features)"
    else
        echo "✅ OPENAI_API_KEY is set"
    fi
}

# Function to test locally
test_local() {
    echo "🧪 Testing locally..."
    if command_exists streamlit; then
        echo "Starting local test (Ctrl+C to stop)..."
        streamlit run streamlit_app.py --server.port=8501
    else
        echo "❌ Streamlit not found. Install with: pip install streamlit"
    fi
}

# Function to build Docker image
build_docker() {
    echo "🐳 Building Docker image..."
    if command_exists docker; then
        docker build -t polkadot-grant-analyzer .
        echo "✅ Docker image built successfully"
        echo "   Run with: docker run -p 8501:8501 -e GITHUB_TOKEN=your_token polkadot-grant-analyzer"
    else
        echo "❌ Docker not found. Install Docker first."
    fi
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    if command_exists heroku; then
        # Check if app exists
        if heroku apps:info --app polkadot-grant-analyzer >/dev/null 2>&1; then
            echo "Updating existing Heroku app..."
            git push heroku main
        else
            echo "Creating new Heroku app..."
            heroku create polkadot-grant-analyzer
            git push heroku main
        fi
        
        echo "✅ Deployed to Heroku"
        echo "   Set environment variables:"
        echo "   heroku config:set GITHUB_TOKEN=your_token"
        echo "   heroku config:set OPENAI_API_KEY=your_key"
    else
        echo "❌ Heroku CLI not found. Install with: brew install heroku/brew/heroku"
    fi
}

# Function to prepare for Streamlit Cloud
prepare_streamlit_cloud() {
    echo "☁️  Preparing for Streamlit Cloud..."
    
    # Check if git repository exists
    if [ ! -d ".git" ]; then
        echo "❌ Not a git repository. Initialize git first:"
        echo "   git init"
        echo "   git add ."
        echo "   git commit -m 'Initial commit'"
        echo "   git remote add origin your-github-repo-url"
        echo "   git push -u origin main"
        return
    fi
    
    # Check if remote exists
    if ! git remote get-url origin >/dev/null 2>&1; then
        echo "❌ No remote repository configured. Add your GitHub repo:"
        echo "   git remote add origin your-github-repo-url"
        echo "   git push -u origin main"
        return
    fi
    
    echo "✅ Repository ready for Streamlit Cloud"
    echo "   Push your changes: git push origin main"
    echo "   Then deploy at: https://share.streamlit.io"
}

# Function to show deployment options
show_options() {
    echo ""
    echo "📋 Deployment Options:"
    echo "1. Test locally"
    echo "2. Build Docker image"
    echo "3. Deploy to Heroku"
    echo "4. Prepare for Streamlit Cloud"
    echo "5. Check environment variables"
    echo "6. Show all options"
    echo "0. Exit"
    echo ""
}

# Main menu
while true; do
    show_options
    read -p "Choose an option (0-6): " choice
    
    case $choice in
        1)
            test_local
            ;;
        2)
            build_docker
            ;;
        3)
            deploy_heroku
            ;;
        4)
            prepare_streamlit_cloud
            ;;
        5)
            check_env_vars
            ;;
        6)
            echo ""
            echo "📚 All Deployment Options:"
            echo ""
            echo "🌐 Streamlit Cloud (Recommended):"
            echo "   - Free and easy"
            echo "   - Go to https://share.streamlit.io"
            echo "   - Connect your GitHub repo"
            echo "   - Set environment variables"
            echo ""
            echo "🚀 Heroku:"
            echo "   - Good free tier"
            echo "   - Custom domains"
            echo "   - Run: ./deploy.sh and choose option 3"
            echo ""
            echo "🛤️  Railway:"
            echo "   - Modern platform"
            echo "   - Go to https://railway.app"
            echo "   - Connect GitHub repo"
            echo ""
            echo "🐳 Docker:"
            echo "   - Maximum portability"
            echo "   - Run: ./deploy.sh and choose option 2"
            echo "   - Deploy to any cloud platform"
            echo ""
            echo "📖 For detailed instructions, see DEPLOYMENT.md"
            ;;
        0)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 0-6."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done 