# Docker Setup for Your Fork

## Quick Start

This guide will help you build and run your forked version with the advanced filtering features.

### Prerequisites

- Docker installed on your system
- Docker Compose installed

### Step 1: Build Your Custom Docker Image

```bash
# Navigate to your repository
cd Vinted-Notifications

# Build the Docker image
docker compose -f docker-compose.custom.yml build

# This will:
# - Use the Dockerfile to build an image
# - Include all your code changes (required_words filter)
# - Tag it as vinted-notifications-fork:latest
```

### Step 2: Start the Container

```bash
# Start the container in detached mode
docker compose -f docker-compose.custom.yml up -d

# Check if it's running
docker compose -f docker-compose.custom.yml ps

# View logs
docker compose -f docker-compose.custom.yml logs -f
```

### Step 3: Access the Web UI

Open your browser and go to: **http://localhost:8000**

You should see the Vinted Notifications web interface!

### Step 4: Configure Your First Query with Required Words

1. Click on **"Queries"** in the sidebar
2. In the "Add New Query" form:
   - **Vinted search URL**: Paste your Vinted search URL
     ```
     https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first
     ```
   - **Name**: `Rithum Switch` (optional but recommended)
   - **Required Words**: `rithum|||switch` ⭐ NEW FIELD
3. Click **"Add Query"**

#### What the Required Words Field Does

- **Format**: Separate words with `|||` (three pipe characters)
- **Logic**: ALL words must be present (AND logic)
- **Where**: Words can appear in title OR description (OR logic for location)
- **Case**: Case-insensitive matching

#### Examples

| Required Words | Matches | Doesn't Match |
|----------------|---------|---------------|
| `rithum|||switch` | "Rithum Switch Console" | "Nintendo Switch" (missing "rithum") |
| `apple|||magic|||mouse` | "Apple Magic Mouse" | "Magic Mouse 2" (missing "apple") |
| `nintendo|||switch|||oled` | "Nintendo Switch OLED" | "Nintendo Switch Lite" (missing "oled") |

### Step 5: Configure Telegram Notifications (Optional)

1. Click on **"Configuration"** in the sidebar
2. Under **Telegram Settings**:
   - Enable Telegram
   - Enter your Bot Token (get from [@BotFather](https://t.me/botfather))
   - Enter your Chat ID
3. Click **"Save Configuration"**
4. Go back to the Dashboard and click **"Start Telegram Bot"**

### Step 6: View Items and Verify Filtering

1. Click on **"Items"** in the sidebar
2. You'll see all items that match your query AND required words
3. If items don't contain the required words, they won't appear here!

## Common Operations

### Stop the Container

```bash
docker compose -f docker-compose.custom.yml down
```

### Restart the Container

```bash
docker compose -f docker-compose.custom.yml restart
```

### View Logs

```bash
# Follow logs in real-time
docker compose -f docker-compose.custom.yml logs -f

# View last 100 lines
docker compose -f docker-compose.custom.yml logs --tail=100
```

### Update Your Fork and Rebuild

```bash
# Pull latest changes from your fork
git pull

# Rebuild the image
docker compose -f docker-compose.custom.yml build

# Restart with new image
docker compose -f docker-compose.custom.yml up -d
```

### Access the Database

The database is stored in `./data/vinted_notifications.db` (bind mounted from the container).

```bash
# Install SQLite browser (if not installed)
# Linux: sudo apt install sqlitebrowser
# Mac: brew install --cask db-browser-for-sqlite

# Open the database
sqlitebrowser ./data/vinted_notifications.db

# Or use command line
sqlite3 ./data/vinted_notifications.db "SELECT id, query_name, required_words FROM queries;"
```

### Check Required Words for Existing Queries

```bash
sqlite3 ./data/vinted_notifications.db <<EOF
SELECT
    id,
    query_name,
    required_words,
    CASE
        WHEN required_words = '' THEN '❌ No filter'
        ELSE '✅ Filtered'
    END as status
FROM queries;
EOF
```

## Database Migration

If you're upgrading from the original version:

1. **Your existing data is safe!** The migration will automatically add the `required_words` column.

2. When you first start the container, the migration script `migrations/1.0.5.4_1.0.5.5.sql` will run automatically.

3. Existing queries will have empty `required_words` (no filtering = backward compatible).

4. To add required words to existing queries:
   ```bash
   # Enter the container
   docker compose -f docker-compose.custom.yml exec vinted-notifications sh

   # Update queries
   sqlite3 /app/data/vinted_notifications.db
   UPDATE queries SET required_words = 'word1|||word2' WHERE id = 1;
   .exit

   # Exit container
   exit
   ```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose -f docker-compose.custom.yml logs

# Common issues:
# - Ports 8000 or 8080 already in use
# - Permission issues with ./data or ./logs directories
```

### Database Locked

```bash
# Stop the container
docker compose -f docker-compose.custom.yml down

# Remove lock file if it exists
rm -f ./data/.vinted_notifications.db-lock

# Start again
docker compose -f docker-compose.custom.yml up -d
```

### Required Words Not Working

1. **Check the filter is set**:
   ```bash
   sqlite3 ./data/vinted_notifications.db "SELECT id, query_name, required_words FROM queries WHERE id=1;"
   ```

2. **Check for typos**: The separator must be exactly `|||` (three pipes)

3. **Case doesn't matter**: "Switch" matches "switch"

4. **Check logs** for filtered items:
   ```bash
   docker compose -f docker-compose.custom.yml logs | grep "required_words"
   ```

### Web UI Not Accessible

```bash
# Check if container is running
docker compose -f docker-compose.custom.yml ps

# Check port mapping
docker compose -f docker-compose.custom.yml port vinted-notifications 8000

# Try accessing: http://localhost:8000
```

### Want to Use a Different Port?

Edit `docker-compose.custom.yml`:

```yaml
ports:
  - "9000:8000"  # Change 9000 to your preferred port
  - "8080:8080"
```

Then access at: http://localhost:9000

## Advanced Configuration

### Environment Variables

You can add environment variables to the docker-compose file:

```yaml
services:
  vinted-notifications:
    build: .
    environment:
      - QUERY_REFRESH_DELAY=30  # Check every 30 seconds
      - ITEMS_PER_QUERY=50       # Get 50 items per query
    ports:
      - "8000:8000"
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Using a Pre-built Image

If you want to push your image to Docker Hub:

```bash
# Tag your image
docker tag vinted-notifications-fork:latest YOUR_USERNAME/vinted-notifications:latest

# Push to Docker Hub
docker push YOUR_USERNAME/vinted-notifications:latest

# Update docker-compose.custom.yml
# Replace "build: ." with:
# image: YOUR_USERNAME/vinted-notifications:latest
```

## Next Steps

1. ✅ Add queries with required words via the Web UI
2. ✅ Configure Telegram or RSS notifications
3. ✅ Monitor the logs to see filtering in action
4. ✅ Adjust required words as needed to fine-tune results

## Support

- See [ADVANCED_FILTERING.md](./ADVANCED_FILTERING.md) for detailed filtering guide
- See [FORK_CHANGES.md](./FORK_CHANGES.md) for what's different in this fork
- Open an issue on GitHub if you encounter problems

---

**Happy deal hunting with precise filtering!** 🎯
