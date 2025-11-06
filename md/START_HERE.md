# 🎉 Read-a-Thon System - Quick Start Guide

Your Read-a-Thon reporting system is ready to use!

## ✅ What's Already Done

1. ✅ Database initialized with **409 students** across 19 classes
2. ✅ Two teams configured: **Kitsko** and **Staub**
3. ✅ Grade rules set up (K-5) with daily minimums
4. ✅ Sample data files created for testing
5. ✅ Flask web application ready to run

## 🚀 Start Using the System (3 Steps)

### Step 1: Start the Application

Open Terminal and run:

```bash
cd /Users/stevesouza/my/data/readathon
python3 app.py
```

You should see:
```
============================================================
READ-A-THON REPORTING SYSTEM
============================================================

Starting web server...
Open your browser and go to: http://localhost:5000
```

### Step 2: Open Your Browser

Navigate to: **http://localhost:5000**

You'll see the dashboard with all your stats!

### Step 3: Try Uploading Sample Data

1. Click **"Upload Data"** in the navigation
2. Select date: **October 10, 2025**
3. Upload the files:
   - **Minutes File**: `sample_minutes.csv`
   - **Donations File**: `sample_donations.csv`
4. Click **"Upload Data"**

The sample files contain data for 20 students to test the system.

## 📊 Next Steps

### View Reports
1. Click **"Reports"** in the navigation
2. Select any report from the list
3. Click **"Run Report"**
4. Use **"Copy to Clipboard"** or **"Export CSV"** buttons

### Run Workflows
1. Click **"Workflows"** in the navigation
2. Choose **"Daily Slide Update"** or **"Cumulative Workflow"**
3. View all reports in sequence

## 📁 Your Real Data

When you're ready to use your actual daily data:

1. Export your data from your tracking system as CSV
2. Make sure CSV files have these columns:
   - **Minutes file**: `Reader Name`, `Minutes`
   - **Donations file**: `Reader Name`, `Donations`
3. Upload through the web interface

Student names must match the roster exactly!

## 🔧 Troubleshooting

### Port Already in Use?
If you see an error about port 5000, edit `app.py` line 197 to use a different port:
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Reset Everything?
If you need to start fresh:
```bash
rm readathon.db
python3 init_data.py
```

### Stop the Server
Press `CTRL+C` in the Terminal window

## 📖 Full Documentation

See `README.md` for:
- Complete report descriptions
- Business logic details
- File structure
- Advanced features

## 🎯 Daily Workflow

Your typical daily routine will be:

1. Start the app: `python3 app.py`
2. Upload today's minutes and donations CSV files
3. Run reports or workflows
4. Copy results to your slideshow or export to Excel
5. Stop the server when done: `CTRL+C`

## 💡 Tips

- The system is **completely local** - no internet required (except for first load)
- All data stays on your Mac in `readathon.db`
- You can run reports as many times as you want
- Prize drawings (Q4) are random each time you run them
- Export any report to CSV for Excel analysis

## 📞 Need Help?

Check the README.md file for detailed documentation on:
- All 11 available reports
- Data upload requirements
- Business logic explanations
- Technical details

---

**Ready to start?** Run `python3 app.py` and open http://localhost:5000 🚀

Good luck with your read-a-thon! 📚✨
