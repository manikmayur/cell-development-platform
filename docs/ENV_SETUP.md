# Environment Setup Guide

## OpenAI API Key Configuration

To use the AI Assistant feature, you need to set up your OpenAI API key. Follow these steps:

### 1. Create a .env file

Create a `.env` file in the root directory of the project with the following content:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here

# Optional: Other environment variables
# STREAMLIT_SERVER_PORT=8501
# STREAMLIT_THEME_BASE=light
```

### 2. Get your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and replace `your_actual_openai_api_key_here` in the .env file

### 3. Install Dependencies

Make sure you have all required dependencies installed:

```bash
pip install -r cell_development_requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

## Security Notes

- **Never commit your .env file to version control**
- The .env file is already included in .gitignore
- Keep your API key secure and don't share it publicly
- Consider using environment variables in production deployments

## Troubleshooting

If you encounter issues:

1. **API Key Error**: Make sure your .env file is in the correct location and contains a valid API key
2. **Module Not Found**: Install python-dotenv: `pip install python-dotenv`
3. **Permission Error**: Ensure the .env file has proper read permissions

## Alternative: Environment Variable

Instead of using a .env file, you can also set the environment variable directly:

```bash
export OPENAI_API_KEY=your_actual_openai_api_key_here
streamlit run app.py
```
