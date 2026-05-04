#!/usr/bin/env bash
# Install 1Password CLI on Debian/Ubuntu (devcontainer). Official server pattern.
# See: https://developer.1password.com/docs/cli/install-server/

set -euo pipefail

if command -v op >/dev/null 2>&1; then
  echo "op already installed: $(op --version)"
  exit 0
fi

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq curl ca-certificates gnupg

curl -sS https://downloads.1password.com/linux/keys/1password.asc | sudo gpg --dearmor -o /usr/share/keyrings/1password-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | sudo tee /etc/apt/sources.list.d/1password.list >/dev/null
sudo mkdir -p /etc/debsig/policies/AC2D62742012EA22/
curl -sS https://downloads.1password.com/linux/debsig/1password.policy | sudo tee /etc/debsig/policies/AC2D62742012EA22/1password.policy >/dev/null

sudo apt-get update -qq
sudo apt-get install -y -qq 1password-cli

echo "Installed: $(op --version)"
