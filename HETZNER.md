# Hetzner Deployment

This repository now includes a production-oriented Docker Compose stack for a Hetzner VM:

- `docker-compose.hetzner.yml` runs the app plus Caddy
- `docker-compose.nginx.yml` runs the app behind an existing nginx reverse proxy
- `deploy/hetzner/Caddyfile` terminates TLS and proxies:
  - `/` to the Web UI on port `8000`
  - `/rss/` to the RSS server on port `8080`

## Recommended Setup

This path assumes:

- a Hetzner Cloud or dedicated server running Ubuntu/Debian
- a DNS record like `alerts.example.com` pointing to the server
- ports `80` and `443` open in both the Hetzner firewall and the server firewall

### 1. Install Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

### 2. Clone the Repository on the Server

```bash
git clone <your-fork-or-repo-url> vinted-notifications
cd vinted-notifications
```

### 3. Configure the Hostname

```bash
cp .env.hetzner.example .env.hetzner
```

Edit `.env.hetzner` and set:

```dotenv
APP_HOST=alerts.example.com
```

### 4. Prepare Persistent Storage

```bash
mkdir -p data logs
```

### 5. Start the Stack

```bash
docker compose --env-file .env.hetzner -f docker-compose.hetzner.yml up -d --build
```

Once Caddy finishes certificate provisioning, the app should be available at:

```text
https://alerts.example.com
```

## Existing nginx Host

If your Hetzner box already uses nginx on port `80` or has port `8080` occupied, use the nginx-oriented stack instead:

```bash
cp .env.nginx.example .env.nginx
mkdir -p data logs
docker compose --env-file .env.nginx -f docker-compose.nginx.yml up -d --build
```

That compose file binds the app to loopback only:

- Web UI on `127.0.0.1:${VN_WEB_PORT}`
- RSS on `127.0.0.1:${VN_RSS_PORT}`

Then add an nginx server block based on `deploy/nginx/vinted-notifications.nginx.conf.example` and reload nginx.

## First-Boot App Configuration

Open the Web UI, then:

1. Go to `Configuration`
2. Set `Public RSS URL` to `https://alerts.example.com/rss/`
3. Save the configuration
4. Start the RSS process if you want the feed enabled

That setting is important because the app previously assumed `localhost` for RSS, while the Hetzner setup publishes RSS through Caddy at `/rss/`.

## Updating

```bash
git pull
docker compose --env-file .env.hetzner -f docker-compose.hetzner.yml up -d --build
```

## Logs

```bash
docker compose --env-file .env.hetzner -f docker-compose.hetzner.yml logs -f
```

## No-Domain Fallback

If you want the fastest possible public deployment before DNS is ready:

1. Use the existing `docker-compose.yml`
2. Open TCP port `9005` on the server
3. Optionally open TCP port `8080` if you want direct RSS access
4. Visit `http://<server-ip>:9005`

In that mode, the RSS fallback URL will be `http://<server-ip>:8080/`.
