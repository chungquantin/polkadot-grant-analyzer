# Quick Deployment Guide

## 🚀 Fastest Way to Deploy

### Option 1: Streamlit Cloud (Recommended - 5 minutes)

1. **Push to GitHub** (if not already done):

   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set **Main file path**: `streamlit_app.py`
   - Add environment variables:
     - `GITHUB_TOKEN`: Your GitHub token
     - `OPENAI_API_KEY`: Your OpenAI key (optional)
   - Click "Deploy"

### Option 2: Use the Deployment Script

Run the interactive deployment script:

```bash
./deploy.sh
```

This will guide you through:

- Testing locally
- Building Docker image
- Deploying to Heroku
- Preparing for Streamlit Cloud

## 🔧 Environment Variables

You'll need to set these in your deployment platform:

- `GITHUB_TOKEN`: Your GitHub personal access token (required)
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for AI features)

## 📊 What You Get

Your deployed app will include:

- ✅ Real-time grant proposal analysis
- ✅ Interactive visualizations
- ✅ AI-powered evaluation
- ✅ Curator analytics
- ✅ Program-specific insights
- ✅ Stale proposal detection
- ✅ Detailed proposal data

## 🆘 Need Help?

1. **Check the logs** in your deployment platform
2. **Test locally first**: `streamlit run streamlit_app.py`
3. **Verify environment variables** are set correctly
4. **Check GitHub API rate limits**

## 📈 Next Steps

After deployment:

1. Set up automated data refresh
2. Configure monitoring
3. Add custom domain (optional)
4. Set up backups

For detailed instructions, see `DEPLOYMENT.md`
