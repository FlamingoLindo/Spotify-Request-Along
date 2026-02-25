# SSL Certificates Directory

This directory should contain your Cloudflare Origin Certificates.

## Required Files

- `cloudflare.crt` - The Origin Certificate from Cloudflare
- `cloudflare.key` - The Private Key from Cloudflare

## How to Install

1. Copy the **Origin Certificate** from Cloudflare and save it as `cloudflare.crt`
2. Copy the **Private Key** from Cloudflare and save it as `cloudflare.key`

Example on Raspberry Pi:
```bash
cd ~/Spotify-Resquest-Along/nginx/ssl

# Create certificate file
nano cloudflare.crt
# Paste the certificate, save with Ctrl+O, exit with Ctrl+X

# Create key file
nano cloudflare.key
# Paste the private key, save with Ctrl+O, exit with Ctrl+X

# Set proper permissions
chmod 644 cloudflare.crt
chmod 600 cloudflare.key
```

## Security Note

These files are ignored by Git (see `.gitignore`) and should never be committed to version control.
