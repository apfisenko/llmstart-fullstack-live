#!/usr/bin/env bash
# Установка Docker Engine и Compose plugin (v2) на Debian / Ubuntu. Идемпотентно.
# Запуск: sudo ./bootstrap-debian-ubuntu.sh
# Не выполняет docker login и не кладёт секреты в систему.
set -euo pipefail

if [ "${EUID:-}" -ne 0 ]; then
  echo "Запустите с правами root: sudo $0" >&2
  exit 1
fi

. /etc/os-release

case "${ID}" in
  debian) DOCKER_DIST="debian" ;;
  ubuntu) DOCKER_DIST="ubuntu" ;;
  *)
    echo "Ожидается ID=debian или ID=ubuntu в /etc/os-release, получено: ${ID}" >&2
    exit 1
    ;;
esac

: "${VERSION_CODENAME?Не удалось прочитать VERSION_CODENAME — проверьте /etc/os-release}"

apt_get="apt-get -qq -o Dpkg::Use-Pty=0"

$apt_get update
DEBIAN_FRONTEND=noninteractive $apt_get install -y --no-install-recommends \
  ca-certificates \
  curl

install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
  curl -fsSL "https://download.docker.com/linux/${DOCKER_DIST}/gpg" -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
fi

arch="$(dpkg --print-architecture)"
list="/etc/apt/sources.list.d/docker.list"
repo_line="deb [arch=${arch} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/${DOCKER_DIST} ${VERSION_CODENAME} stable"
if [ ! -f "$list" ] || ! grep -qF "download.docker.com/linux/${DOCKER_DIST}" "$list" 2>/dev/null; then
  echo "$repo_line" > "$list"
fi

$apt_get update
DEBIAN_FRONTEND=noninteractive $apt_get install -y --no-install-recommends \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin \
  git

systemctl enable --now docker

if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
  usermod -aG docker "$SUDO_USER" || true
  echo "Пользователь ${SUDO_USER} добавлен в группу docker. Для сессии SSH выполните: newgrp docker"
  echo "или перелогиньтесь, затем docker compose version без sudo."
fi

echo "OK: $(docker --version), $(docker compose version)"
