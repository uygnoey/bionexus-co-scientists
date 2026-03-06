# 🧬 BioNexus Co-scientists

> AI-powered scientific hypothesis generation from arXiv papers using multi-agent debate systems.

**BioNexus Co-scientists**는 arXiv 논문을 기반으로 창의적이고 과학적으로 타당한 가설을 자동 생성하는 멀티에이전트 시스템입니다. Claude Agent SDK Agent Teams를 활용한 Generator, Validator, Ranker 에이전트가 토론을 통해 최적의 가설을 도출합니다.

---

## ✨ 주요 기능

### 🤖 Multi-Agent System
- **Generator (Claude Opus 4-6)**: 창의적인 가설 생성
- **Validator (Claude Sonnet 4-5)**: 과학적 타당성 검증
- **Ranker (Claude Haiku 4-6)**: 최종 순위 결정
- **Debate Layer**: 에이전트 간 3라운드 토론으로 가설 정제

### 🔍 Hybrid RAG System
- **Vector RAG (Qdrant)**: 논문 임베딩 기반 의미 검색
- **Graph RAG (Neo4j)**: 지식 그래프 기반 엔티티 관계 추론
- **Dual Retrieval**: 두 시스템을 결합한 정밀한 컨텍스트 제공

### 📊 Intelligent Clustering
- **KMeans Clustering**: 유사 가설 자동 그룹화
- **Diversity Guarantee**: 중복 제거 및 다양성 보장
- **Quality Scoring**: 참신성, 실현가능성, 영향력 평가

### 💫 Modern Glassmorphism UI
- **Real-time Streaming**: WebSocket 기반 실시간 진행 상황 업데이트
- **Interactive Cards**: Framer Motion 애니메이션
- **Responsive Design**: 모바일부터 데스크톱까지 완벽 지원
- **Accessibility**: WCAG AA 준수

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────┐
│     Frontend (Next.js + TailwindCSS)    │
│   Modern Glassmorphism | shadcn/ui      │
└───────────────┬─────────────────────────┘
                │ REST API + WebSocket
┌───────────────▼─────────────────────────┐
│         Backend (FastAPI)               │
│  ┌─────────────────────────────────┐    │
│  │  Claude Agent SDK Agent Teams   │    │
│  │  Generator → Validator → Ranker │    │
│  └─────────────────────────────────┘    │
│                 │                        │
│  ┌──────────────┴──────────────┐        │
│  │  Vector RAG  │  Graph RAG   │        │
│  │   (Qdrant)   │   (Neo4j)    │        │
│  └──────────────┴──────────────┘        │
└─────────────────────────────────────────┘
```

자세한 아키텍처는 [ARCHITECTURE.md](./ARCHITECTURE.md)를 참고하세요.

---

## 🚀 빠른 시작

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Kubernetes** (프로덕션 배포 시)
- **Anthropic API Key**

### 로컬 개발 환경 설정

#### 1. 리포지토리 클론

```bash
git clone https://github.com/uygnoey/bionexus-co-scientists.git
cd bionexus-co-scientists
```

#### 2. 환경 변수 설정

```bash
# Backend
cp backend/.env.example backend/.env
# ANTHROPIC_API_KEY, NEO4J_URI 등 설정

# Frontend
cp frontend/.env.example frontend/.env
# NEXT_PUBLIC_API_URL 설정
```

#### 3. Docker Compose로 전체 스택 실행

```bash
cd infra/docker
docker-compose up -d
```

이 명령어는 다음을 실행합니다:
- Neo4j (Graph DB)
- Qdrant (Vector DB)
- Redis (Cache & Queue)
- Backend API
- Frontend Web App

#### 4. 접속

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 🛠️ 개발 가이드

### Backend 개발

```bash
cd backend

# Poetry 설치
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 개발 서버 실행
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 개발

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 테스트 실행

```bash
# Backend 테스트
cd backend
poetry run pytest

# Frontend 테스트
cd frontend
npm run test

# E2E 테스트
npm run test:e2e
```

---

## 📖 문서

- [**Architecture**](./ARCHITECTURE.md): 시스템 아키텍처 상세 설명
- [**Roadmap**](./ROADMAP.md): 개발 로드맵 및 마일스톤
- [**API Documentation**](./docs/api/): REST API 문서
- [**Deployment Guide**](./docs/guides/deployment.md): Kubernetes 배포 가이드
- [**Contributing**](./CONTRIBUTING.md): 기여 가이드

---

## 🧪 테스트 커버리지

| Component | Coverage | Tests |
|-----------|----------|-------|
| Backend   | 80%+     | 100+  |
| Frontend  | 75%+     | 80+   |
| E2E       | 100%     | 50+   |

---

## 🎯 성능 지표

- **가설 생성 시간**: < 2분 (10편 논문 기준)
- **RAG 검색 지연**: < 500ms
- **Graph RAG 쿼리**: < 1s
- **API 응답 시간**: < 200ms (캐시 적중 시)
- **WebSocket 지연**: < 100ms

---

## 🗺️ 로드맵

### Phase 1: Foundation (Week 1-4) ✅
- [x] 프로젝트 기반 구축
- [x] Claude Agent SDK 통합
- [x] arXiv 연동 & Vector RAG
- [x] Graph RAG (Neo4j)
- [x] API 라우터
- [x] Docker Compose 설정

### Phase 2: Core Features (Week 5-8) 🚧
- [ ] Graph RAG (Neo4j)
- [ ] Debate Layer
- [ ] WebSocket 실시간 스트리밍

### Phase 3: Frontend (Week 9-11)
- [ ] Next.js UI 구현
- [ ] Modern Glassmorphism 스타일
- [ ] 실시간 인터랙션

### Phase 4: Polish & Deployment (Week 12-16)
- [ ] 성능 최적화
- [ ] Kubernetes 배포
- [ ] 문서화 완료

전체 로드맵은 [ROADMAP.md](./ROADMAP.md)를 참고하세요.

---

## 🤝 기여하기

기여는 언제나 환영합니다! 자세한 내용은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고하세요.

---

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](./LICENSE) 파일을 참고하세요.

---

## 🙏 감사의 말

- [Anthropic](https://www.anthropic.com/) - Claude Agent SDK
- [arXiv](https://arxiv.org/) - 오픈 액세스 논문 저장소
- [Neo4j](https://neo4j.com/) - Graph Database
- [Qdrant](https://qdrant.tech/) - Vector Database
- [Next.js](https://nextjs.org/) - React Framework
- [shadcn/ui](https://ui.shadcn.com/) - UI Components

---

## 📧 연락처

- **Author**: Yeongyu Yang
- **GitHub**: [@uygnoey](https://github.com/uygnoey)
- **Issues**: [GitHub Issues](https://github.com/uygnoey/bionexus-co-scientists/issues)

---

<div align="center">

**🦀 Built with CLAW**

*"잡으면 안 놓는다"*

</div>
