# Architecture Overview

## Product objective

ThriftCloud helps engineering and operations teams answer three questions quickly:

1. Where is cloud spend going?
2. How much of that spend is waste or under-optimized?
3. What should we do next, and how confident are we?

## Foundation architecture

### Frontend

- React + TypeScript dashboard
- Zustand for auth session state
- Recharts for spend and trend visualization
- Tailwind CSS for a fast-moving design system

### Backend

- FastAPI for REST endpoints
- JWT auth with role-aware users
- SQLAlchemy models for users and billing data
- Service layer for scoring and recommendations

### Data plane

- PostgreSQL for persistent app data
- Redis reserved for queueing, cache, and future async jobs
- Seeded billing records to keep demos local-first and reproducible

## Phase path

### Phase 1

- app skeleton
- local environment
- auth
- fake data generation

### Phase 2

- provider adapters
- rules engine
- FinOps score evolution
- deeper dashboard workflows

### Phase 3

- forecasting endpoints
- anomaly detection
- vector store
- AI copilot with citations

### Phase 4

- PDF report generation
- metrics and dashboards
- cold-clone setup validation
- portfolio-ready documentation

## Suggested capstone demo story

1. Sign in with a seeded demo account
2. Review cross-cloud spend and the FinOps score
3. Explain why waste is happening using recommendation insights
4. Show the roadmap path to AI copilot and predictive optimization

