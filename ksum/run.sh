#!/bin/bash

echo "🎬 Starting AI ShortStory Studio..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f "requirements_installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch requirements_installed
fi

# Run the Streamlit app
echo "🚀 Launching Streamlit interface..."
streamlit run frontend.py

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi 