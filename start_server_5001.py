#!/usr/bin/env python3
"""Start the Flask app on port 5001 in debug mode"""
from app import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("READ-A-THON REPORTING SYSTEM (Port 5001)")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5001")
    print("\nPress CTRL+C to stop the server\n")
    app.run(debug=True, host='127.0.0.1', port=5001)
