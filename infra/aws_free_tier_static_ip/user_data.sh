#!/bin/bash
set -euxo pipefail

# AL2023 uses dnf instead of yum mostly, but yum works as a symlink
dnf update -y
dnf install -y git docker

# Enable and start Docker
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# Install Docker Compose plugin
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Wait for network and clone
cd /home/ec2-user
if [ ! -d "ThriftCloud" ]; then
  git clone https://github.com/raahul-kr/ThriftCloud.git
fi

cd /home/ec2-user/ThriftCloud
# Start the containers
docker compose up -d --build
