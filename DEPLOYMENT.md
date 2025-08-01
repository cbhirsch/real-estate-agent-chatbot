# Deployment Guide

This guide will help you deploy your Real Estate Agent Chatbot to various platforms.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended for Beginners)

1. **Prepare your repository:**
   - Make sure all files are committed to GitHub
   - Ensure your `.env` file is NOT in the repository (add to .gitignore)

2. **Deploy to Railway:**
   - Go to [Railway.app](https://railway.app/)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect it's a Python app

3. **Set Environment Variables:**
   - In Railway dashboard, go to "Variables" tab
   - Add all variables from your `.env` file:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     API_KEY=your_api_key_here
     LANGCHAIN_API_KEY=your_langsmith_api_key_here
     LANGCHAIN_PROJECT=real-estate-agent
     ```

4. **Deploy:**
   - Railway will automatically deploy your app
   - You'll get a URL like: `https://your-app-name.railway.app`

### Option 2: Render

1. **Prepare your repository:**
   - Same as Railway

2. **Deploy to Render:**
   - Go to [Render.com](https://render.com/)
   - Sign up with GitHub
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service:**
   - **Name**: `real-estate-agent` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables:**
   - Add the same environment variables as above

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy your app

### Option 3: Heroku

1. **Install Heroku CLI:**
   ```bash
   # Windows
   winget install --id=Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key_here
   heroku config:set API_KEY=your_api_key_here
   heroku config:set LANGCHAIN_API_KEY=your_langsmith_api_key_here
   heroku config:set LANGCHAIN_PROJECT=real-estate-agent
   ```

5. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## 🔧 Environment Variables

Make sure to set these in your deployment platform:

```bash
OPENAI_API_KEY=your_openai_api_key_here
API_KEY=your_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=real-estate-agent
```

## 🌐 Custom Domain (Optional)

### Railway
1. Go to your project settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### Render
1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records

## 🔍 Testing Your Deployment

Once deployed, test your API:

```bash
# Test health endpoint
curl https://your-app-url.railway.app/health

# Test chat endpoint
curl -X POST "https://your-app-url.railway.app/chat" \
     -H "Authorization: Bearer your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "session_id": "test-123"}'
```

## 📊 Monitoring

- **Railway**: Built-in logs and metrics
- **Render**: Built-in logs and uptime monitoring
- **Heroku**: Heroku logs and add-ons

## 🚨 Troubleshooting

### Common Issues:

1. **Port issues**: Make sure you're using `$PORT` environment variable
2. **Missing dependencies**: Check that `requirements.txt` is complete
3. **Environment variables**: Ensure all required variables are set
4. **Memory limits**: Some platforms have memory restrictions

### Debug Commands:

```bash
# Check logs
heroku logs --tail  # Heroku
railway logs        # Railway

# Check environment variables
heroku config       # Heroku
railway variables   # Railway
```

## 🔒 Security Considerations

1. **Never commit `.env` files** to your repository
2. **Use strong API keys** for production
3. **Enable HTTPS** (automatic on most platforms)
4. **Set up proper CORS** if needed
5. **Monitor usage** and set up alerts

## 📈 Next Steps After Deployment

1. **Update your API documentation** with the new URL
2. **Test all endpoints** thoroughly
3. **Set up monitoring** and alerts
4. **Configure custom domain** if desired
5. **Set up CI/CD** for automatic deployments 