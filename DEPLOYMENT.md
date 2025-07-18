# Deployment Guide for Polkadot Grant Analyzer

This guide provides step-by-step instructions for deploying your Polkadot Grant Analyzer to various platforms.

## Prerequisites

1. **GitHub Token**: You'll need a GitHub personal access token for the app to fetch data
2. **OpenAI API Key** (Optional): For AI evaluation features
3. **Git Repository**: Your code should be in a Git repository

## Deployment Options

### 1. Streamlit Cloud (Recommended - Free & Easy)

**Steps:**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and set:
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a custom subdomain (optional)
6. Add environment variables:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
7. Click "Deploy"

**Advantages:**

- Free tier available
- Automatic deployments from Git
- Built for Streamlit apps
- Easy environment variable management

### 2. Heroku

**Steps:**

1. Install Heroku CLI: `brew install heroku/brew/heroku`
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set GITHUB_TOKEN=your_github_token
   heroku config:set OPENAI_API_KEY=your_openai_key
   ```
5. Deploy: `git push heroku main`

**Advantages:**

- Custom domains
- Good free tier
- Easy scaling

### 3. Railway

**Steps:**

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in the Railway dashboard:
   - `GITHUB_TOKEN`
   - `OPENAI_API_KEY`
6. Deploy automatically

**Advantages:**

- Modern platform
- Good free tier
- Automatic deployments

### 4. Docker + Any Cloud Platform

**Steps:**

1. Build Docker image:
   ```bash
   docker build -t polkadot-grant-analyzer .
   ```
2. Run locally to test:
   ```bash
   docker run -p 8501:8501 -e GITHUB_TOKEN=your_token polkadot-grant-analyzer
   ```
3. Deploy to your preferred cloud platform (AWS, GCP, Azure, etc.)

## Environment Variables

Set these environment variables in your deployment platform:

- `GITHUB_TOKEN`: Your GitHub personal access token (required)
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for AI features)

## Data Management

### For Production Deployment:

1. **Database**: The app uses SQLite by default. For production:

   - Consider using PostgreSQL or MySQL
   - Set up automated backups
   - Use environment variables for database connection

2. **Data Refresh**:

   - Set up a cron job or scheduled task to refresh data periodically
   - Consider using GitHub Actions for automated data updates

3. **Caching**:
   - The app caches data in memory
   - Consider implementing Redis for better caching

## Troubleshooting

### Common Issues:

1. **Port Issues**: Ensure the app runs on the port specified by the platform (usually `$PORT`)
2. **Memory Limits**: Some platforms have memory limits. Consider optimizing data loading
3. **Timeout Issues**: Large data operations might timeout. Consider implementing progress bars
4. **API Rate Limits**: GitHub API has rate limits. Implement proper error handling

### Debug Commands:

```bash
# Test locally
streamlit run streamlit_app.py

# Check environment variables
echo $GITHUB_TOKEN

# Test GitHub API
python test_github_api.py

# Check database
python check_data.py
```

## Security Considerations

1. **API Keys**: Never commit API keys to Git
2. **Database**: Use environment variables for database credentials
3. **HTTPS**: Ensure your deployment uses HTTPS
4. **Rate Limiting**: Implement rate limiting for public deployments

## Monitoring

1. **Logs**: Monitor application logs for errors
2. **Performance**: Track response times and memory usage
3. **Data Freshness**: Monitor when data was last updated
4. **API Usage**: Track GitHub API usage to avoid rate limits

## Cost Optimization

1. **Free Tiers**: Start with free tiers and upgrade as needed
2. **Data Storage**: Use efficient data storage and compression
3. **Caching**: Implement proper caching to reduce API calls
4. **Scheduled Updates**: Update data during off-peak hours

## Support

If you encounter issues:

1. Check the logs in your deployment platform
2. Test locally first
3. Verify environment variables are set correctly
4. Check GitHub API rate limits
