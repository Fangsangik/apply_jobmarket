#!/bin/bash

# Flask `� tX � �l��
echo "=� Starting Flask Job Market Analyzer..."

#  �X� \1T ( ݬm)
# source venv/bin/activate

# X�� \�
export FLASK_APP=flask_app.py
export FLASK_ENV=development

# Flask `� tX �
python3 flask_app.py

echo " Flask application started successfully!"
echo "=� Access the application at: http://localhost:5008"