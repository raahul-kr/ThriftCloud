terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["137112412989"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_security_group" "thriftcloud_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH + web traffic for ThriftCloud"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "HTTP: Nginx proxy"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Frontend Dev/Prod"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Backend API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

resource "aws_instance" "thriftcloud_host" {
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true
  key_name                    = var.key_pair_name
  vpc_security_group_ids      = [aws_security_group.thriftcloud_sg.id]
  user_data                   = file("${path.module}/user_data.sh")

  tags = {
    Name = "${var.project_name}-host"
  }
}

resource "aws_eip" "thriftcloud_static_ip" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }
}

resource "aws_eip_association" "thriftcloud_eip_assoc" {
  allocation_id = aws_eip.thriftcloud_static_ip.id
  instance_id   = aws_instance.thriftcloud_host.id
}

output "static_public_ip" {
  description = "Static public IP for ThriftCloud"
  value       = aws_eip.thriftcloud_static_ip.public_ip
}

output "app_url" {
  description = "HTTP URL for ThriftCloud"
  value       = "http://${aws_eip.thriftcloud_static_ip.public_ip}:3000"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i <path-to-key.pem> ec2-user@${aws_eip.thriftcloud_static_ip.public_ip}"
}
