# Security & API Key Setup

## 🔐 Protecting Your API Keys

This project uses environment variables to keep API keys secure. **Never commit your `.env` file to version control!**

## Setup Instructions

### 1. Copy the Example Environment File

```bash
cp .env.example event_horizon/.env
```

### 2. Add Your API Keys

Open `event_horizon/.env` and replace the placeholder values with your actual API keys:

```bash
# OpenAI API Key - Get yours from https://platform.openai.com/api-keys
OPENAI_API_KEY=your-actual-openai-api-key-here

# Gemini API Key (optional) - Get yours from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3. Verify .gitignore

The `.gitignore` file already includes `.env` to prevent accidental commits of sensitive data. Always verify before pushing:

```bash
git status
```

If you see `.env` listed, **DO NOT COMMIT IT!**

## 🚨 What to Do If You Accidentally Commit API Keys

If you accidentally commit API keys to GitHub:

1. **Immediately revoke the exposed keys** on the provider's dashboard:
   - OpenAI: https://platform.openai.com/api-keys
   - Gemini: https://makersuite.google.com/app/apikey

2. **Generate new API keys** and update your local `.env` file

3. **Remove the keys from Git history:**
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   # See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
   ```

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file

### Gemini API Key (Optional)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

## Best Practices

✅ **DO:**
- Use environment variables for all sensitive data
- Keep `.env` in `.gitignore`
- Share `.env.example` with placeholder values
- Rotate API keys regularly
- Use separate keys for development and production

❌ **DON'T:**
- Hardcode API keys in source code
- Commit `.env` files to version control
- Share API keys in public channels
- Use production keys in development
- Leave unused API keys active

## File Structure

```
AI Agent Cup/
├── .env.example          # Template with placeholder values (SAFE TO COMMIT)
├── .gitignore            # Excludes .env from version control
└── event_horizon/
    └── .env              # Your actual API keys (NEVER COMMIT)
```

## Questions?

If you need help setting up your API keys, please refer to:
- [OpenAI Documentation](https://platform.openai.com/docs/quickstart)
- [Google AI Documentation](https://ai.google.dev/tutorials/setup)
