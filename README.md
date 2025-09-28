# Vinted-Notifications

A real-time notification system for Vinted listings that works across all Vinted country domains. Get instant alerts
when items matching your search criteria are posted.

![Vinted-Notifications](https://github.com/user-attachments/assets/f2788511-5a8a-4a8d-8198-a4135081a3d8)

---

## ⚡ Quickstart

If you just want to get started fast with Docker Compose:

```bash
curl -O https://raw.githubusercontent.com/Fuyucch1/Vinted-Notifications/main/docker-compose.yml
docker-compose up -d
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📋 Features

- **Web UI**: Manage everything through an intuitive web interface
- **Multi-Country Support**: Works on all Vinted domains regardless of country
- **Real-Time Notifications**: Get instant alerts for new listings
- **Multiple Search Queries**: Monitor multiple search terms simultaneously
- **Country Filtering**: Filter items by seller's country of origin
- **RSS Feed**: Subscribe to your search results with any RSS reader
- **Telegram Integration**: Receive notifications directly in Telegram

---

## 📦 Installation

### Option 1: Docker Run (Simplest)

#### Prerequisites

- Docker installed on your system
- Telegram bot token (for Telegram notifications)

#### Setup with Docker Run

1. **Create directories for persistent data**

   ```bash
   mkdir -p data logs
   ```

2. **Run the container**

   ```bash
   docker run -d \
     --name vinted-notifications \
     -p 8000:8000 \
     -p 8080:8080 \
     -v "$(pwd)/data:/app/data" \
     -v "$(pwd)/logs:/app/logs" \
     --restart unless-stopped \
     fuyucch1/vinted-notifications:latest
   ```

   > **Note**: The volume mounts ensure your data and logs are preserved even if the container is removed or updated.
   The database is stored in the `data` directory, and logs are stored in the `logs` directory.

3. **Access the Web UI**

   Once started, access the Web UI at [http://localhost:8000](http://localhost:8000) to complete the setup.

### Option 2: Docker Compose (Recommended)

#### Prerequisites

- Docker and Docker Compose installed on your system
- Telegram bot token (for Telegram notifications)

#### Setup with Docker Compose

1. **Create a docker-compose.yml file**

   ```yaml
   version: '3.8'

   services:
     vinted-notifications:
       image: fuyucch1/vinted-notifications:latest
       pull_policy: always
       ports:
         - "8000:8000"
         - "8080:8080"
       volumes:
         - VN_data:/app/data
         - VN_logs:/app/logs
       restart: unless-stopped
       read_only: true
       tmpfs:
         - /tmp

   volumes:
     VN_data:
     VN_logs:
   ```

   > **Note**: This configuration uses named volumes (`VN_data` and `VN_logs`) which are managed by Docker. This ensures
   your data and logs are preserved even if the container is removed or updated.

2. **Start the container**

   ```bash
   docker-compose up -d
   ```

3. **Access the Web UI**

   Once started, access the Web UI at [http://localhost:8000](http://localhost:8000) to complete the setup.

### Option 3: Self-Build

#### Prerequisites

- Python 3.11 or higher
- Telegram bot token (for Telegram notifications)

#### Setup

1. **Clone the repository or download the latest release**

   ```bash
   git clone https://github.com/Fuyucch1/Vinted-Notifications.git
   cd Vinted-Notifications
   ```

   Alternatively, download the [latest release](https://github.com/Fuyucch1/Vinted-Notifications/releases/latest) and
   extract it.

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initial Configuration**

   The application can be configured through the Web UI after starting. However, you can also change the Web UI port in
   the
   `configuration_values.py` file directly.

4. **Run the application**

   ```bash
   python vinted_notifications.py
   ```

   Once started, access the Web UI at [http://localhost:8000](http://localhost:8000) to complete the setup.

## 🚀 Usage

### Web UI

The Web UI is the easiest way to manage the application. Access it at [http://localhost:8000](http://localhost:8000)
after starting the application.

Features available in the Web UI:

- **Dashboard**: Overview of application status and recent items
- **Queries Management**: Add, remove, and view search queries
- **Items Viewing**: Browse and filter items found by the application
- **Allowlist Management**: Filter items by seller's country
- **Configuration**: Set up Telegram bot, RSS feed, and other settings
- **Logs**: View application logs directly from the web interface

### Telegram Commands

After configuring your Telegram bot in the Web UI, you can use the following commands:

- `/add_query query` - Add a search query to monitor
- `/remove_query query_number` - Remove a specific query
- `/remove_query all` - Remove all queries
- `/queries` - List all active queries
- `/hello` - Check if the bot is working
- `/create_allowlist` - Create a country allowlist (will slow down processing)
- `/delete_allowlist` - Delete the country allowlist
- `/add_country XX` - Add a country to the allowlist (ISO3166 format)
- `/remove_country XX` - Remove a country from the allowlist
- `/allowlist` - View the current allowlist

### Query Examples

Queries must be added with a whole link. It works with filters.:

   ```
   /add_query https://www.vinted.fr/catalog?search_text=nike%20shoes&price_to=50&currency=EUR&brand_id[]=53
   ```

### RSS Feed

The RSS feed provides an alternative way to receive notifications. After enabling it in the Web UI, access it
at [http://localhost:8080](http://localhost:8080).

## ⚙️ Advanced Configuration

### Proxy Support

The application supports using proxies to avoid rate limits. Those are configured in the configuration tab of the Web
UI.

### Custom Notification Format

You can customize the notification message format:

```python
MESSAGE = '''\
🆕 Title: {title}
💶 Price: {price}
🛍️ Brand: {brand}
<a href='{image}'>&#8205;</a>
'''
```

## 🔄 Updating

### Option 1: Docker Run

1. Pull the latest image:
   ```bash
   docker pull fuyucch1/vinted-notifications:latest
   ```
2. Stop and remove the existing container:
   ```bash
   docker stop vinted-notifications
   docker rm vinted-notifications
   ```
3. Run the container again with the same command as in the installation section:
   ```bash
   docker run -d \
     --name vinted-notifications \
     -p 8000:8000 \
     -p 8080:8080 \
     -v "$(pwd)/data:/app/data" \
     -v "$(pwd)/logs:/app/logs" \
     --restart unless-stopped \
     fuyucch1/vinted-notifications:latest
   ```

   > **Important**: This update method preserves your data because of the volume mounts. Your database and logs will be
   maintained across updates as they are stored in the mounted directories.

### Option 2: Docker Compose

1. Pull the latest image:
   ```bash
   docker pull fuyucch1/vinted-notifications:latest
   ```
2. Restart your container:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

   > **Important**: This update method preserves your data because of the named volumes (`VN_data` and `VN_logs`). Your
   database and logs will be maintained across updates as they are stored in these Docker-managed volumes.

### Option 3: Self-Build

1. Download the latest [release](https://github.com/Fuyucch1/Vinted-Notifications/releases/latest)
2. Back up your `vinted_notifications.db` file
3. Replace all files with the new ones
4. Restart the application

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the [GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE).

## 🙏 Acknowledgements

- Thanks to [@herissondev](https://github.com/herissondev) for maintaining pyVinted, a core dependency of this project.
