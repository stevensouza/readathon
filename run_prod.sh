#!/bin/bash
# Launch Read-a-Thon app with PRODUCTION database
# This script forces the use of production data regardless of config file

echo "⚠️  Starting Read-a-Thon Management System with PRODUCTION database..."
echo "   (Contains real student data)"
python3 app.py --db prod
