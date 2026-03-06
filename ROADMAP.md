# BioNexus Co-scientists - Development Roadmap

## 🎯 전체 타임라인: 3-4개월 (풀스펙)

```
Month 1          Month 2          Month 3          Month 4
├───────────────┼───────────────┼───────────────┼───────────────┤
│ Phase 1       │ Phase 2       │ Phase 3       │ Phase 4       │
│ Foundation    │ Core Features │ Frontend      │ Polish        │
└───────────────┴───────────────┴───────────────┴───────────────┘
```

---

## 📅 Phase 1: Foundation (Week 1-4)

### Week 1: 프로젝트 기반 구축

**Backend Setup**
- [x] 프로젝트 구조 생성
- [ ] Poetry 의존성 설정 (`pyproject.toml`)
- [ ] FastAPI 기본 앱 구조
- [ ] Docker 개발 환경 (`docker-compose.yml`)
- [ ] 환경 변수 관리 (`.env` + Pydantic Settings)
- [ ] 로깅 설정 (구조화된 JSON 로그)

**인프라 설정**
- [ ] Neo4j 로컬 실행 (Docker)
- [ ] Qdrant 로컬 실행 (Docker)
- [ ] Redis 설정 (캐시 + 큐)
- [ ] DB 연결 테스트

**체크리스트:**
- [ ] `docker-compose up`으로 전체 스택 실행 가능
- [ ] FastAPI 헬스체크 API 동작 (`GET /health`)
- [ ] Neo4j, Qdrant, Redis 연결 확인

**목표 산출물:**
```
✅ 로컬 환경에서 Backend + DB 전체 스택 실행
✅ API 기본 엔드포인트 1개 (`/health`)
```

---

### Week 2: Claude Agent SDK 통합

**Agent Teams 기본 구현**
- [ ] Claude Agent SDK 설치 및 인증
- [ ] `agents/orchestrator.py`: Agent Teams 기본 쿼리
- [ ] `agents/generator.py`: Generator 에이전트 프롬프트
- [ ] `agents/validator.py`: Validator 에이전트 프롬프트
- [ ] `agents/ranker.py`: Ranker 에이전트 프롬프트
- [ ] POC 리포 참고하여 Hooks 구현
  - `hooks/pre_tool.py`: PreToolUse 훅
  - `hooks/post_tool.py`: PostToolUse 훅
  - `hooks/monitor.py`: 실시간 모니터링

**기본 테스트**
- [ ] Generator 단독 실행 (간단한 프롬프트)
- [ ] Validator 단독 실행
- [ ] Ranker 단독 실행
- [ ] 3개 에이전트 순차 실행 확인

**체크리스트:**
- [ ] `python -m app.agents.orchestrator` 실행 성공
- [ ] 간단한 가설 생성 (예: "양자 컴퓨팅 논문 5편 → 가설 3개")
- [ ] Hooks로 tool_use 이벤트 캡처 확인

**목표 산출물:**
```
✅ Claude Agent SDK Agent Teams 기본 동작
✅ 3개 에이전트 독립 실행 성공
✅ Hooks 기반 모니터링 작동
```

---

### Week 3: arXiv 연동 & 일반 RAG

**arXiv Client 구현**
- [ ] `arxiv/client.py`: arXiv API 연동
  - 키워드 검색
  - 논문 메타데이터 조회
  - PDF 다운로드
- [ ] `arxiv/parser.py`: PDF 텍스트 추출
  - PyMuPDF / pdfplumber 사용
  - 섹션별 파싱 (Abstract, Introduction, Methods, etc.)
- [ ] `arxiv/downloader.py`: 배치 다운로드

**Vector RAG (Qdrant)**
- [ ] `rag/embeddings.py`: OpenAI Embeddings 생성
- [ ] `rag/vector_store.py`: Qdrant 연동
  - Collection 생성
  - 논문 임베딩 저장
  - 의미 기반 검색 (Semantic Search)
- [ ] `rag/retrieval.py`: RAG 검색 로직
  - Top-K 검색
  - Reranking

**API 엔드포인트**
- [ ] `POST /api/papers/search`: arXiv 논문 검색
- [ ] `GET /api/papers/{arxiv_id}`: 논문 상세 조회
- [ ] `POST /api/papers/embed`: 논문 임베딩 저장

**체크리스트:**
- [ ] arXiv에서 논문 10편 검색 및 다운로드 성공
- [ ] Qdrant에 임베딩 저장 확인
- [ ] RAG 검색 결과 Top-5 정확도 체크 (수동)

**목표 산출물:**
```
✅ arXiv 논문 자동 수집 파이프라인
✅ Qdrant Vector RAG 동작
✅ API로 논문 검색 가능
```

---

### Week 4: 통합 테스트 & Week 1-3 버그 수정

**통합 테스트 작성**
- [ ] `tests/integration/test_arxiv_rag.py`
  - arXiv 검색 → 임베딩 → RAG 검색 전체 플로우
- [ ] `tests/integration/test_agent_teams.py`
  - Agent Teams 3개 에이전트 실행
- [ ] `tests/unit/` 유닛 테스트 (커버리지 목표 60%+)

**버그 수정 & 리팩토링**
- [ ] Week 1-3에서 발견된 버그 수정
- [ ] 코드 리뷰 및 리팩토링
- [ ] 문서 업데이트 (README, API 문서)

**CI/CD 기본 설정**
- [ ] GitHub Actions 워크플로우 생성
  - `pytest` 자동 실행
  - 코드 커버리지 체크
  - Docker 이미지 빌드

**체크리스트:**
- [ ] 통합 테스트 5개 이상 PASS
- [ ] CI/CD 파이프라인 동작 확인
- [ ] 코드 커버리지 60% 이상

**목표 산출물:**
```
✅ Phase 1 완료 (Foundation)
✅ Backend 핵심 기능 동작 (arXiv + RAG + Agent Teams)
✅ 테스트 자동화 기반 구축
```

---

## 📅 Phase 2: Core Features (Week 5-8)

### Week 5: Graph RAG (Neo4j) 구현

**엔티티 추출 (NER)**
- [ ] `rag/graph_rag.py`: Neo4j 연동
- [ ] NER 모델 통합 (spaCy / LLM 기반)
  - PERSON, ORGANIZATION, CONCEPT, METHOD 추출
- [ ] Neo4j에 엔티티 저장

**관계 추출 (Relation Extraction)**
- [ ] 엔티티 간 관계 추출
  - "X uses Y"
  - "X is related to Y"
  - "X is a type of Y"
- [ ] Neo4j에 관계 저장

**그래프 쿼리**
- [ ] Cypher 쿼리 작성
  - 2-hop 연결 검색
  - 공통 엔티티 발견
  - 클러스터 감지

**체크리스트:**
- [ ] 논문 10편에서 엔티티 100개 이상 추출
- [ ] Neo4j 그래프 시각화 확인 (Neo4j Browser)
- [ ] Graph RAG 검색 결과 유의미성 체크

**목표 산출물:**
```
✅ Neo4j Graph RAG 동작
✅ 논문 간 지식 그래프 구축
✅ 그래프 기반 검색 가능
```

---

### Week 6: Debate Layer & Clustering

**에이전트 토론 시스템**
- [ ] `agents/debate.py`: 토론 오케스트레이션
  - Generator vs Validator 3라운드
  - 반박 → 수정 → 합의 프로세스
- [ ] 토론 결과 저장 (PostgreSQL / JSON)

**가설 클러스터링**
- [ ] `clustering/kmeans.py`: KMeans 기본 구현
  - 가설 임베딩 생성
  - 최적 클러스터 수 자동 결정 (Elbow Method)
- [ ] `clustering/evaluator.py`: 클러스터 품질 평가
  - Silhouette Score
  - Diversity Score

**API 엔드포인트**
- [ ] `POST /api/hypotheses/generate`: 가설 생성 (전체 파이프라인)
  - arXiv 검색
  - RAG + Graph RAG
  - Agent Teams 실행
  - 토론
  - 클러스터링
- [ ] `GET /api/hypotheses/{id}`: 가설 상세 조회

**체크리스트:**
- [ ] 토론 3라운드 정상 동작
- [ ] 가설 클러스터링 결과 시각화 (수동)
- [ ] 전체 파이프라인 E2E 테스트 1개 성공

**목표 산출물:**
```
✅ Agent Teams 토론 시스템 동작
✅ 가설 클러스터링 구현
✅ 가설 생성 전체 파이프라인 완성
```

---

### Week 7: WebSocket & 실시간 스트리밍

**WebSocket 구현**
- [ ] `api/websocket.py`: Socket.IO 서버
  - 클라이언트 연결 관리
  - 룸(Room) 기반 이벤트 전송
- [ ] Agent Teams Hooks → WebSocket 연동
  - `tool_use` 이벤트 실시간 전송
  - `assistant` 텍스트 스트리밍
  - 진행 상황 업데이트 (0-100%)

**이벤트 스키마**
- [ ] `ws:hypothesis:start`: 가설 생성 시작
- [ ] `ws:hypothesis:progress`: 진행률 업데이트
- [ ] `ws:hypothesis:agent`: 에이전트 상태 변경
- [ ] `ws:hypothesis:result`: 최종 결과

**체크리스트:**
- [ ] WebSocket 연결 성공
- [ ] 실시간 진행 상황 수신 확인
- [ ] 10초마다 진행률 업데이트 수신

**목표 산출물:**
```
✅ WebSocket 실시간 스트리밍
✅ Agent Teams 실행 상태 실시간 전송
```

---

### Week 8: Backend 최적화 & 테스트

**성능 최적화**
- [ ] Redis 캐싱 도입
  - RAG 검색 결과 캐시 (TTL: 1시간)
  - 논문 메타데이터 캐시
- [ ] 비동기 처리 최적화
  - `asyncio.gather()` 활용
  - 병렬 RAG 검색
- [ ] DB 쿼리 최적화
  - Neo4j 인덱스 추가
  - Qdrant 검색 파라미터 튜닝

**테스트 확장**
- [ ] 통합 테스트 100개 작성
  - API 엔드포인트별 테스트
  - 에러 핸들링 테스트
  - Edge Case 테스트
- [ ] Property-based Tests (pytest-hypothesis)
  - 가설 생성 입력 범위 테스트
  - RAG 검색 경계 조건

**체크리스트:**
- [ ] 가설 생성 시간 < 2분 (10편 논문 기준)
- [ ] RAG 검색 < 500ms
- [ ] 통합 테스트 커버리지 80% 이상

**목표 산출물:**
```
✅ Phase 2 완료 (Core Features)
✅ Backend 모든 기능 완성
✅ 성능 목표 달성
✅ 테스트 커버리지 80%+
```

---

## 📅 Phase 3: Frontend (Week 9-11)

### Week 9: Next.js 프로젝트 기반 구축

**프로젝트 초기화**
- [ ] Next.js 14+ 프로젝트 생성 (App Router)
- [ ] TailwindCSS 설정
- [ ] shadcn/ui 컴포넌트 설치
  - Button, Card, Input, Badge, etc.
- [ ] Framer Motion 설치
- [ ] Zustand 스토어 설정

**레이아웃 구조**
- [ ] `app/layout.tsx`: 루트 레이아웃
  - Header
  - Sidebar (네비게이션)
  - Footer
- [ ] `components/layout/Header.tsx`
- [ ] `components/layout/Sidebar.tsx`
- [ ] `components/layout/Footer.tsx`

**API 클라이언트**
- [ ] `lib/api.ts`: Axios 기반 API 클라이언트
  - Base URL 설정
  - 에러 핸들링
  - 타입 정의
- [ ] `lib/websocket.ts`: Socket.IO 클라이언트

**체크리스트:**
- [ ] Next.js 개발 서버 실행 (`npm run dev`)
- [ ] 기본 레이아웃 렌더링 확인
- [ ] Backend API 호출 테스트 (헬스체크)

**목표 산출물:**
```
✅ Next.js 프로젝트 기반 구축
✅ shadcn/ui 컴포넌트 통합
✅ API 클라이언트 동작
```

---

### Week 10: 핵심 UI 컴포넌트 개발

**가설 관련 컴포넌트**
- [ ] `components/hypothesis/HypothesisCard.tsx`
  - Modern Glassmorphism 스타일
  - 호버 애니메이션 (Framer Motion)
  - 가설 점수 시각화 (Progress Bar)
- [ ] `components/hypothesis/HypothesisStream.tsx`
  - WebSocket 실시간 스트리밍
  - 진행 상황 표시
  - 에이전트 상태 아이콘
- [ ] `components/hypothesis/DebateView.tsx`
  - Generator vs Validator 토론 타임라인
  - 말풍선 스타일
  - 애니메이션 전환

**논문 관련 컴포넌트**
- [ ] `components/paper/PaperSearch.tsx`
  - 검색 인풋 (debounce)
  - 자동완성 (추천 키워드)
- [ ] `components/paper/PaperCard.tsx`
  - 논문 메타데이터 표시
  - 선택/해제 체크박스
  - arXiv 링크

**공통 컴포넌트**
- [ ] `components/ui/LoadingSpinner.tsx`
- [ ] `components/ui/EmptyState.tsx`
- [ ] `components/ui/ErrorBoundary.tsx`

**체크리스트:**
- [ ] HypothesisCard 렌더링 확인
- [ ] 호버 애니메이션 부드럽게 동작
- [ ] WebSocket 연결 및 스트리밍 확인

**목표 산출물:**
```
✅ 가설 카드 UI 완성
✅ 실시간 스트리밍 컴포넌트
✅ 토론 시각화 컴포넌트
```

---

### Week 11: 페이지 구현 & 통합

**페이지 구현**
- [ ] `app/page.tsx`: 홈페이지
  - 프로젝트 소개
  - CTA 버튼 ("가설 생성 시작")
  - 데모 비디오 / GIF
- [ ] `app/hypotheses/page.tsx`: 가설 생성 페이지
  - 논문 검색 인터페이스
  - 가설 생성 버튼
  - 실시간 스트리밍 뷰
  - 결과 카드 그리드
- [ ] `app/papers/page.tsx`: 논문 검색 페이지
  - arXiv 검색 폼
  - 검색 결과 목록
  - 필터링 (날짜, 저자, 카테고리)

**Zustand 스토어**
- [ ] `store/hypothesis.ts`
  - 가설 목록 상태
  - WebSocket 이벤트 핸들러
- [ ] `store/paper.ts`
  - 선택된 논문 목록
  - 검색 결과

**라우팅 & 네비게이션**
- [ ] Sidebar 링크 연결
- [ ] 페이지 전환 애니메이션

**체크리스트:**
- [ ] 모든 페이지 접근 가능
- [ ] 논문 검색 → 가설 생성 E2E 동작
- [ ] WebSocket 실시간 업데이트 확인

**목표 산출물:**
```
✅ Phase 3 완료 (Frontend)
✅ 모든 페이지 구현 완료
✅ Backend ↔ Frontend 통합 성공
```

---

## 📅 Phase 4: Polish & Deployment (Week 12-16)

### Week 12: UI 세련미 향상

**Glassmorphism 스타일 고도화**
- [ ] 커스텀 CSS 변수 정의 (`globals.css`)
- [ ] 그라데이션 배경 (Mesh Gradient)
- [ ] 반투명 카드 효과 강화
- [ ] 섬세한 그림자 (Soft Shadows)

**애니메이션 추가**
- [ ] 페이지 전환 애니메이션 (Framer Motion)
- [ ] 가설 카드 등장 애니메이션 (Stagger Effect)
- [ ] 로딩 스켈레톤 (Skeleton Loader)
- [ ] 성공/실패 토스트 (Sonner)

**반응형 디자인**
- [ ] 모바일 레이아웃 (375px ~ 768px)
- [ ] 태블릿 레이아웃 (768px ~ 1024px)
- [ ] 데스크톱 레이아웃 (1024px+)

**접근성 (a11y)**
- [ ] 키보드 네비게이션
- [ ] ARIA 라벨
- [ ] 색상 대비 (WCAG AA)

**체크리스트:**
- [ ] Lighthouse 점수 90+ (Performance, Accessibility)
- [ ] 모바일에서 정상 동작 확인
- [ ] 키보드만으로 모든 기능 사용 가능

**목표 산출물:**
```
✅ Liner보다 세련된 UI 완성
✅ 반응형 디자인 완벽 지원
✅ 접근성 기준 충족
```

---

### Week 13: 성능 최적화 & SEO

**Frontend 성능 최적화**
- [ ] Next.js 이미지 최적화 (`next/image`)
- [ ] 코드 스플리팅 (Dynamic Import)
- [ ] 폰트 최적화 (`next/font`)
- [ ] 번들 크기 분석 (`@next/bundle-analyzer`)

**Backend 성능 최적화**
- [ ] Gunicorn + Uvicorn 멀티 워커
- [ ] Connection Pooling (DB)
- [ ] 응답 압축 (gzip)

**SEO**
- [ ] 메타 태그 (OG, Twitter Card)
- [ ] `sitemap.xml`
- [ ] `robots.txt`
- [ ] Structured Data (JSON-LD)

**체크리스트:**
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3.0s
- [ ] 번들 크기 < 500KB (gzipped)
- [ ] Google 검색 결과에 OG 이미지 표시

**목표 산출물:**
```
✅ Frontend 성능 목표 달성
✅ SEO 최적화 완료
```

---

### Week 14: 통합 테스트 & E2E 테스트

**E2E 테스트 (Playwright)**
- [ ] `tests/e2e/test_hypothesis_generation.spec.ts`
  - 논문 검색 → 가설 생성 → 결과 확인
- [ ] `tests/e2e/test_paper_search.spec.ts`
  - arXiv 검색 → 논문 선택
- [ ] `tests/e2e/test_debate_view.spec.ts`
  - 토론 타임라인 렌더링 확인

**Visual Regression Tests (Chromatic)**
- [ ] HypothesisCard 스냅샷
- [ ] DebateView 스냅샷
- [ ] 페이지별 스냅샷

**Backend E2E 테스트**
- [ ] `tests/e2e/test_full_pipeline.py`
  - 전체 파이프라인 10회 실행
  - 성공률 100% 확인

**체크리스트:**
- [ ] E2E 테스트 50개 작성 및 PASS
- [ ] Visual Regression 테스트 통과
- [ ] CI/CD에 E2E 테스트 통합

**목표 산출물:**
```
✅ E2E 테스트 50개 PASS
✅ Visual Regression 테스트 설정
✅ 품질 보증 완료
```

---

### Week 15: Docker & Kubernetes 배포

**Docker 이미지**
- [ ] `backend/Dockerfile`: Multi-stage Build
- [ ] `frontend/Dockerfile`: Next.js Standalone 빌드
- [ ] Docker Compose 통합 테스트

**Kubernetes 매니페스트**
- [ ] `infra/k8s/backend/deployment.yaml`
- [ ] `infra/k8s/frontend/deployment.yaml`
- [ ] `infra/k8s/neo4j/statefulset.yaml`
- [ ] `infra/k8s/qdrant/statefulset.yaml`
- [ ] `infra/k8s/redis/deployment.yaml`
- [ ] `infra/k8s/ingress.yaml` (NGINX Ingress)

**ConfigMap & Secrets**
- [ ] 환경 변수 ConfigMap
- [ ] API 키 Secrets
- [ ] TLS 인증서 (Let's Encrypt)

**배포 스크립트**
- [ ] `infra/scripts/deploy.sh`
- [ ] `infra/scripts/rollback.sh`

**체크리스트:**
- [ ] 로컬 Kubernetes (Minikube / k3s) 배포 성공
- [ ] Ingress로 외부 접근 확인
- [ ] 무중단 배포 (Rolling Update) 테스트

**목표 산출물:**
```
✅ Docker 이미지 최적화 완료
✅ Kubernetes 배포 성공
✅ 프로덕션 환경 준비 완료
```

---

### Week 16: 문서화 & 최종 점검

**문서 작성**
- [ ] `README.md`: 프로젝트 소개, 빠른 시작 가이드
- [ ] `docs/api/`: API 문서 (Swagger / ReDoc)
- [ ] `docs/architecture/`: 아키텍처 다이어그램
- [ ] `docs/guides/deployment.md`: 배포 가이드
- [ ] `docs/guides/development.md`: 개발 가이드
- [ ] `CONTRIBUTING.md`: 기여 가이드
- [ ] `CHANGELOG.md`: 변경 이력

**코드 리뷰 & 리팩토링**
- [ ] 전체 코드 리뷰
- [ ] 중복 코드 제거
- [ ] 타입 힌트 보완 (Python)
- [ ] TypeScript strict 모드 적용

**최종 테스트**
- [ ] 전체 테스트 스위트 실행 (Backend + Frontend)
- [ ] 성능 벤치마크
- [ ] 보안 감사 (Snyk, Dependabot)

**체크리스트:**
- [ ] 모든 문서 작성 완료
- [ ] 전체 테스트 PASS (200개+)
- [ ] 보안 취약점 0개

**목표 산출물:**
```
✅ Phase 4 완료 (Polish & Deployment)
✅ 프로덕션 배포 가능 상태
✅ 문서화 완료
```

---

## 📊 마일스톤 체크포인트

| Phase | 기간 | 핵심 산출물 | 성공 기준 |
|-------|------|-------------|-----------|
| **Phase 1: Foundation** | Week 1-4 | Backend 기반, Agent Teams, arXiv RAG | `docker-compose up` → 전체 스택 동작 |
| **Phase 2: Core Features** | Week 5-8 | Graph RAG, Debate, WebSocket | 가설 생성 E2E 테스트 PASS |
| **Phase 3: Frontend** | Week 9-11 | Next.js UI, 실시간 스트리밍 | Frontend ↔ Backend 통합 성공 |
| **Phase 4: Polish** | Week 12-16 | UI 세련미, 배포, 문서 | Kubernetes 배포 성공 |

---

## 🚨 리스크 & 대응 계획

### 리스크 1: Claude Agent SDK 불안정

**가능성:** 중  
**영향:** 높음

**대응:**
- POC 리포 참고하여 안정적인 패턴 사용
- Hooks 미동작 시 디스크 IPC 폴링으로 대체
- 최악의 경우 Langchain Agent Teams로 전환

### 리스크 2: Graph RAG 성능 이슈

**가능성:** 중  
**영향:** 중

**대응:**
- Neo4j 인덱스 최적화
- 엔티티 수 제한 (Top-100)
- 성능 미달 시 Vector RAG만 사용 (Graph RAG 선택 기능화)

### 리스크 3: UI 구현 지연

**가능성:** 낮음  
**영향:** 중

**대응:**
- shadcn/ui 컴포넌트 최대 활용
- 애니메이션 단순화
- MVP 버전 먼저 완성 후 폴리싱

---

## 🎯 정의된 성공 기준

### 기능적 성공

- [ ] 10편 논문에서 5개 가설 생성 (< 2분)
- [ ] 가설 품질 평가 (Validator 점수 평균 70+)
- [ ] 클러스터링으로 다양성 보장 (중복 < 20%)

### 기술적 성공

- [ ] 테스트 커버리지 80%+
- [ ] API 응답 시간 < 200ms (캐시 적중)
- [ ] Frontend Lighthouse 점수 90+

### 사용자 경험

- [ ] 실시간 진행 상황 업데이트 (WebSocket)
- [ ] 반응형 디자인 완벽 지원
- [ ] 접근성 WCAG AA 준수

---

**작성일:** 2026-03-07  
**작성자:** CLAW 🦀  
**버전:** 1.0  
**다음 업데이트:** Phase 1 완료 시
