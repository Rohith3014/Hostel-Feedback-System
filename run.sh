#!/bin/bash
echo ""
echo " Hostel Feedback System"
echo " ======================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo " ERROR: python3 is not installed."
    echo " Install from https://www.python.org/downloads/"
    exit 1
fi

# Install dependencies
echo " Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo ""
echo " Starting server at http://localhost:5000"
echo " Press Ctrl+C to stop."
echo ""

python3 app.py
