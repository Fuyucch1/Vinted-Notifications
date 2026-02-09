# Installation and Setup Guide

## Overview

This guide will help you set up and run your forked version of Vinted-Notifications with advanced filtering capabilities.

## Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)

## Step-by-Step Installation

### 1. Clone Your Forked Repository

```bash
# Clone your fork (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/Vinted-Notifications.git
cd Vinted-Notifications
```

### 2. Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:

```bash
pip install requests sqlite3
```

### 3. Run Initial Setup

```bash
# Run the application once to create the database structure
python vinted_notifications.py
```

This will:
- Create the `data/` directory
- Initialize the SQLite database
- Apply all migrations (including the new `required_words` feature)

### 4. Configure Notifications

You have several options for receiving notifications:

#### Option A: Telegram Bot (Recommended)

1. Create a Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your bot token and chat ID
3. Update the configuration:

```python
import db

# Enable Telegram
db.set_parameter('telegram_enabled', 'True')
db.set_parameter('telegram_token', 'YOUR_BOT_TOKEN')
db.set_parameter('telegram_chat_id', 'YOUR_CHAT_ID')
```

#### Option B: RSS Feed

1. Enable the RSS feed:

```python
import db

db.set_parameter('rss_enabled', 'True')
db.set_parameter('rss_port', '8080')  # Choose your port
```

2. Access the RSS feed at: `http://localhost:8080/feed`

### 5. Add Your First Query with Required Words

#### Method 1: Using Python Script

Create a file called `add_query.py`:

```python
import core

# Add your query with required words
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first",
    name="Rithum Switch",
    required_words="rithum|||switch"  # Both words must be present
)

print("Query added successfully!")
```

Run it:
```bash
python add_query.py
```

#### Method 2: Using SQLite Directly

```bash
# Open the database
sqlite3 data/vinted_notifications.db

# Add a query
INSERT INTO queries (query, query_name, required_words)
VALUES (
    'https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first',
    'Rithum Switch',
    'rithum|||switch'
);

# Exit
.exit
```

### 6. Start the Application

```bash
python vinted_notifications.py
```

The application will:
1. Check Vinted every 60 seconds (configurable)
2. Filter items based on your required words
3. Send notifications via your configured method

## Configuration Options

### Adjust Refresh Interval

```python
import db

# Check Vinted every 30 seconds
db.set_parameter('query_refresh_delay', '30')
```

### Add Banwords (Negative Filter)

```python
import db

# Exclude items with these words
db.set_parameter('banwords', 'replica|||fake|||broken|||damaged')
```

### Configure Country Allowlist

```python
import db

# Only get notifications from Dutch and Belgian sellers
db.add_to_allowlist('NL')
db.add_to_allowlist('BE')
```

### Adjust Newness Threshold

By default, only items posted in the last 20 minutes trigger notifications. To change this, edit `core.py`:

```python
# In the process_items() function, change:
data = [item for item in all_items if item.is_new_item(minutes=30)]  # 30 minutes
```

## Running in the Background

### Linux/macOS (using systemd)

1. Create a service file: `/etc/systemd/system/vinted-notifications.service`

```ini
[Unit]
Description=Vinted Notifications Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/Vinted-Notifications
ExecStart=/usr/bin/python3 /path/to/Vinted-Notifications/vinted_notifications.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vinted-notifications
sudo systemctl start vinted-notifications
```

3. Check status:

```bash
sudo systemctl status vinted-notifications
```

### Linux/macOS (using screen/tmux)

```bash
# Using screen
screen -S vinted
python vinted_notifications.py
# Press Ctrl+A, then D to detach

# To reattach
screen -r vinted

# Using tmux
tmux new -s vinted
python vinted_notifications.py
# Press Ctrl+B, then D to detach

# To reattach
tmux attach -t vinted
```

### Windows (using nssm)

1. Download [NSSM](https://nssm.cc/download)
2. Install the service:

```cmd
nssm install VintedNotifications "C:\Python39\python.exe" "C:\path\to\Vinted-Notifications\vinted_notifications.py"
nssm start VintedNotifications
```

## Upgrading from Original Version

If you already have the original Vinted-Notifications installed:

1. **Backup your database:**

```bash
cp data/vinted_notifications.db data/vinted_notifications.db.backup
```

2. **Replace the code with your fork:**

```bash
# Add your fork as a new remote
git remote add fork https://github.com/YOUR_USERNAME/Vinted-Notifications.git

# Fetch and checkout the fork
git fetch fork
git checkout fork/main
```

3. **Run the application to apply migrations:**

```bash
python vinted_notifications.py
```

The migration `1.0.5.4_1.0.5.5.sql` will automatically add the `required_words` column to existing queries.

4. **Update your queries with required words:**

```bash
sqlite3 data/vinted_notifications.db

# Add required words to existing queries
UPDATE queries SET required_words = 'rithum|||switch' WHERE id = 1;
UPDATE queries SET required_words = 'apple|||mouse' WHERE id = 2;

.exit
```

## Verifying Installation

### Check Database Schema

```bash
sqlite3 data/vinted_notifications.db

# Show queries table structure
.schema queries

# You should see the required_words column
# Output should include: required_words TEXT DEFAULT ''

.exit
```

### Check Logs

```bash
# If logging is enabled
tail -f logs/vinted_notifications.log
```

### Test a Query

```python
import core
from pyVintedVN import Vinted

# Test searching
vinted = Vinted()
items = vinted.items.search(
    "https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first",
    nbr_items=5
)

# Print results
for item in items:
    print(f"Title: {item.title}")
    print(f"Description: {item.description}")
    print(f"Price: {item.price} {item.currency}")
    print("---")
```

## Troubleshooting

### "No module named 'pyVintedVN'"

```bash
# Make sure you're in the correct directory
cd Vinted-Notifications

# Install dependencies
pip install -r requirements.txt
```

### "Database is locked"

Another instance of the application is running. Stop it first:

```bash
# Find the process
ps aux | grep vinted_notifications.py

# Kill it
kill -9 <PID>
```

### "Items not being filtered correctly"

1. Check your required_words setting:
```bash
sqlite3 data/vinted_notifications.db
SELECT id, query_name, required_words FROM queries;
.exit
```

2. Verify the separator is `|||` (three pipes)

3. Test the filter manually:
```python
from core import contains_required_words

# Test cases
print(contains_required_words("Nintendo Switch", "Great condition", "nintendo|||switch"))  # Should be True
print(contains_required_words("Apple Mouse", "Magic Mouse", "magic|||mouse"))  # Should be True
print(contains_required_words("Random Item", "Nothing relevant", "specific|||words"))  # Should be False
```

### Permission Denied

```bash
# Make sure the data directory is writable
chmod -R 755 data/
```

## Getting Help

- Check the [ADVANCED_FILTERING.md](./ADVANCED_FILTERING.md) guide
- Review the [original project's README](./README.md)
- Open an issue on GitHub

## Next Steps

Once installed:

1. ✅ Add queries with required words (see [ADVANCED_FILTERING.md](./ADVANCED_FILTERING.md))
2. ✅ Configure banwords to exclude unwanted items
3. ✅ Set up country allowlist if needed
4. ✅ Run in the background using systemd/screen/tmux
5. ✅ Monitor logs to ensure it's working correctly

Happy deal hunting! 🎉
