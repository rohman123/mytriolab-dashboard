# ============================================
# MyTrioLab Setup - Ringkasan Perintah CLI
# Tanggal: 14 Juni 2026
# Domain: mytriolab.my.id
# ============================================

## 1. CLOUDFLARE TUNNEL SETUP

# Cek NS domain
dig NS mytriolab.my.id

# Install cloudflared (Mac)
brew install cloudflared

# Login ke Cloudflare (buka link di browser)
cloudflared tunnel login

# Buat tunnel
cloudflared tunnel create oman-laptop

# Catat Tunnel ID: affab27e-7a17-4874-b2e1-95d13dd3a26a

# Hubungkan domain ke tunnel
cloudflared tunnel route dns oman-laptop mytriolab.my.id

# Jalankan tunnel (foreground)
cloudflared tunnel run oman-laptop

# Install tunnel sebagai service (Mac - launchd)
sudo cloudflared service install
sudo launchctl start com.cloudflare.cloudflared

# Cek tunnel list
cloudflared tunnel list

# Cek tunnel info
cloudflared tunnel info oman-laptop


## 2. WEB SERVER (MacBook)

# Jalankan Python HTTP server sementara
cd /Users/rohmannurhaqiqi && python3 -m http.server 8080

# Jalankan server custom (dengan JSON API)
cd /Users/rohmannurhaqiqi && python3 server.py

# Download file dari GitHub
curl -sL "https://raw.githubusercontent.com/rohman123/mytriolab-dashboard/main/index.html" -o ~/index.html
curl -sL "https://raw.githubusercontent.com/rohman123/mytriolab-dashboard/main/server.py" -o ~/server.py

# Matikan semua Python server
pkill -f python3


## 3. CLOUDFLARE CONFIG (~/.cloudflared/config.yml)

tunnel: affab27e-7a17-4874-b2e1-95d13dd3a26a
credentials-file: /Users/rohmannurhaqiqi/.cloudflared/affab27e-7a17-4874-b2e1-95d13dd3a26a.json

ingress:
  - hostname: mytriolab.my.id
    service: http://localhost:8080
  - hostname: www.mytriolab.my.id
    service: http://localhost:8080
  - hostname: ssh.mytriolab.my.id
    service: ssh://localhost:22
  - service: http_status:404


## 4. CLOUDFLARE ZERO TRUST (Dashboard: one.dash.cloudflare.com)

# --- Aplication 1: MyLab (Web) ---
# Access → Applications → Add application → Self-hosted
# Name: MyLab
# Domain: mytriolab.my.id
# Policy: Allow-Oman → Email: rohmandev95@gmail.com → Allow

# --- Application 2: MyLab-SSH ---
# Access → Applications → Add application → Self-hosted
# Name: MyLab-SSH
# Domain: ssh.mytriolab.my.id
# Policy: Allow-Hermes-Agent → Service Token: Hermes-Agent → Allow

# --- Service Token ---
# Access → Service Auth → Service Tokens → Create
# Name: Hermes-Agent
# Client ID: bb76af361a55b6e7a016d8fad4cfff11.access
# Client Secret: (tersimpan di dashboard)


## 5. DNS RECORDS (Cloudflare Dashboard → DNS)

# CNAME mytriolab.my.id → affab27e-7a17-4874-b2e1-95d13dd3a26a.cfargotunnel.com (Proxied)
# CNAME www → mytriolab.my.id (Proxied)
# CNAME ssh → mytriolab.my.id (Proxied)


## 6. SSH SETUP (MacBook)

# Aktifkan SSH
sudo systemsetup -setremotelogin on

# Cek SSH status
sudo launchctl list | grep ssh

# SSH dari MacBook ke MacBook (test)
ssh localhost

# SSH via tunnel (dari server)
ssh -o ProxyCommand="cloudflared access ssh --hostname %h" rohmannurhaqiqi@ssh.mytriolab.my.id

# Login cloudflared untuk SSH (server)
cloudflared access ssh --hostname ssh.mytriolab.my.id


## 7. SERVICE TOKEN TEST

# Test akses HTTP dengan Service Token
curl -s -o /dev/null -w "%{http_code}" \
  -H "CF-Access-Client-Id: bb76af361a55b6e7a016d8fad4cfff11.access" \
  -H "CF-Access-Client-Secret: (client_secret)" \
  https://mytriolab.my.id

# Expected: 200


## 8. GITHUB

# Repo: https://github.com/rohman123/mytriolab-dashboard
# Token: simpan di gh CLI

# Login gh CLI
unset GITHUB_TOKEN
echo 'ghp_TOKEN' | gh auth login --with-token

# Clone & push
cd /tmp && git clone https://github.com/rohman123/mytriolab-dashboard.git
cd mytriolab-dashboard
# ... edit files ...
git add .
git commit -m "Update files"
git push


## 9. TROUBLESHOOTING

# Error 521: Web server belum jalan → jalankan python3 server.py
# Error 522: Tunnel mati → jalankan cloudflared tunnel run oman-laptop
# Error 1016: A Record masih pakai IP → ganti ke CNAME tunnel
# 302 redirect: Cloudflare Access policy belum allow
# 403: Service Token belum di-allow di policy

# Cek tunnel status
cloudflared tunnel run oman-laptop

# Cek config
cat ~/.cloudflared/config.yml

# Hapus lock file cloudflared
rm -f ~/.cloudflared/*.lock ~/.cloudflared/*.url


## 10. CREDENTIALS (SIMPAN AMAN!)

# Tunnel ID: affab27e-7a17-4874-b2e1-95d13dd3a26a
# Tunnel Name: oman-laptop
# Service Token Client ID: bb76af361a55b6e7a016d8fad4cfff11.access
# GitHub Repo: rohman123/mytriolab-dashboard
# Email: rohmandev95@gmail.com
