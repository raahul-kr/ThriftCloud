# 🚀 ThriftCloud

ThriftCloud is a DevOps-focused multi-cloud cost intelligence platform supporting both AWS and Azure billing analysis.

It implements a provider abstraction layer (Strategy Pattern) to detect optimization opportunities, calculate efficiency scores, and simulate projected savings.

Designed with production-style cloud deployment in mind.

---

## 🧠 Core Capabilities

- Multi-Cloud Provider Abstraction (AWS + Azure)
- Cost Explorer (Service-wise breakdown)
- Optimization Insights (Severity-based waste detection)
- Efficiency Scoring Engine
- Monthly & 6-Month Savings Simulation
- REST API Architecture
- Containerized Microservices (Docker Compose)
- Reverse Proxy using Nginx
- Ready for AWS ECS Fargate deployment via Terraform

---

## 🏗 Architecture (Local Mode)

Browser  
→ Nginx  
→ React Frontend  
→ Flask API  
→ Provider Engine  
→ PostgreSQL  
→ Worker Service  

---

## ⚙ Tech Stack

- React
- Flask
- PostgreSQL
- Docker & Docker Compose
- Nginx
- Strategy Pattern (Provider Abstraction)
- Terraform (Planned for AWS Deployment)

---

## 🎯 Project Vision

ThriftCloud is built as a cloud-native, DevOps-first system rather than a simple application.  
It simulates production-grade architecture locally and is designed for seamless deployment on AWS ECS Fargate.

---

Built to demonstrate cloud engineering, DevOps automation, and multi-cloud cost intelligence design.
