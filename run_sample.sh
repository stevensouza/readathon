#!/bin/bash
# Launch Read-a-Thon app with SAMPLE database
# This script forces the use of sample data regardless of config file

echo "🚀 Starting Read-a-Thon Management System with SAMPLE database..."
python3 app.py --db sample
