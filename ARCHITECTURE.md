# BioNexus Co-scientists - Architecture

## 🎯 프로젝트 목표

arXiv 논문에서 과학적 가설을 자동 생성하는 멀티에이전트 시스템.

## 🏗️ 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  Modern Glassmorphism UI | TailwindCSS + shadcn/ui          │
│  실시간 스트리밍 | WebSocket | 가설 카드 시각화              │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Claude Agent SDK Agent Teams (3-Agent System)      │    │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │    │
│  │  │ Generator  │  │  Validator  │  │    Ranker    │ │    │
│  │  │ (Opus 4-6) │  │ (Sonnet 4-5)│  │ (Haiku 4-6)  │ │    │
│  │  └────────────┘  └─────────────┘  └──────────────┘ │    │
│  │       │                 │                 │         │    │
│  │       └─────────────────┴─────────────────┘         │    │
│  │                    Debate Layer                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐   │
│  │            Hypothesis Processing Pipeline             │   │
│  │  1. arXiv Query → 2. RAG → 3. Graph RAG →            │   │
│  │  4. Debate → 5. Clustering → 6. Ranking              │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼────────┐
│  Qdrant        │           │    Neo4j        │
│  (Vector DB)   │           │  (Graph DB)     │
│  - Embeddings  │           │  - Entities     │
│  - Semantic    │           │  - Relations    │
│    Search      │           │  - Knowledge    │
└────────────────┘           └─────────────────┘
```

## 🔧 기술 스택

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (비동기 처리)
- **AI SDK:** Claude Agent SDK Agent Teams
- **Models:**
  - Generator: Claude Opus 4-6 (창의성)
  - Validator: Claude Sonnet 4-5 (균형)
  - Ranker: Claude Haiku 4-6 (속도)
- **Vector DB:** Qdrant (임베딩 저장)
- **Graph DB:** Neo4j (지식 그래프)
- **Queue:** Redis (작업 큐)
- **Cache:** Redis (RAG 캐시)

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Styling:** TailwindCSS + shadcn/ui
- **Animation:** Framer Motion
- **State:** Zustand (경량 상태 관리)
- **WebSocket:** Socket.IO Client
- **Icons:** Lucide Icons

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes (k8s)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana

## 📂 디렉토리 구조

```
bionexus-co-scientists/
├── backend/
│   ├── app/
│   │   ├── agents/              # Claude Agent SDK 에이전트
│   │   │   ├── generator.py     # 가설 생성 에이전트
│   │   │   ├── validator.py     # 검증 에이전트
│   │   │   ├── ranker.py        # 순위 에이전트
│   │   │   ├── debate.py        # 토론 시스템
│   │   │   └── orchestrator.py  # Agent Teams 오케스트레이터
│   │   ├── rag/                 # RAG 시스템
│   │   │   ├── vector_store.py  # Qdrant 연동
│   │   │   ├── graph_rag.py     # Neo4j 그래프 RAG
│   │   │   ├── embeddings.py    # 임베딩 생성
│   │   │   └── retrieval.py     # 검색 로직
│   │   ├── arxiv/               # arXiv 연동
│   │   │   ├── client.py        # arXiv API 클라이언트
│   │   │   ├── parser.py        # 논문 파싱
│   │   │   └── downloader.py    # PDF 다운로드
│   │   ├── clustering/          # 가설 클러스터링
│   │   │   ├── kmeans.py        # KMeans 기본
│   │   │   └── evaluator.py     # 클러스터 평가
│   │   ├── api/                 # FastAPI 라우터
│   │   │   ├── hypotheses.py    # 가설 생성 API
│   │   │   ├── papers.py        # 논문 검색 API
│   │   │   ├── websocket.py     # WebSocket 핸들러
│   │   │   └── health.py        # 헬스체크
│   │   ├── models/              # Pydantic 모델
│   │   │   ├── hypothesis.py    # 가설 데이터 모델
│   │   │   ├── paper.py         # 논문 데이터 모델
│   │   │   └── agent.py         # 에이전트 상태
│   │   ├── hooks/               # SDK Hooks
│   │   │   ├── pre_tool.py      # PreToolUse 훅
│   │   │   ├── post_tool.py     # PostToolUse 훅
│   │   │   └── monitor.py       # 실시간 모니터링
│   │   ├── core/                # 핵심 로직
│   │   │   ├── config.py        # 설정 관리
│   │   │   ├── logging.py       # 로깅
│   │   │   └── cache.py         # Redis 캐시
│   │   └── main.py              # FastAPI 엔트리포인트
│   ├── tests/
│   │   ├── unit/                # 유닛 테스트
│   │   ├── integration/         # 통합 테스트
│   │   └── e2e/                 # E2E 테스트
│   ├── pyproject.toml           # Poetry 의존성
│   ├── Dockerfile               # Backend 컨테이너
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── page.tsx         # 홈페이지
│   │   │   ├── hypotheses/      # 가설 생성 페이지
│   │   │   │   └── page.tsx
│   │   │   ├── papers/          # 논문 검색 페이지
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx       # 루트 레이아웃
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui 컴포넌트
│   │   │   ├── hypothesis/      # 가설 관련 컴포넌트
│   │   │   │   ├── HypothesisCard.tsx
│   │   │   │   ├── HypothesisStream.tsx
│   │   │   │   └── DebateView.tsx
│   │   │   ├── paper/           # 논문 관련 컴포넌트
│   │   │   │   ├── PaperSearch.tsx
│   │   │   │   └── PaperCard.tsx
│   │   │   └── layout/          # 레이아웃 컴포넌트
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   ├── lib/                 # 유틸리티
│   │   │   ├── api.ts           # API 클라이언트
│   │   │   ├── websocket.ts     # WebSocket 클라이언트
│   │   │   └── utils.ts         # 헬퍼 함수
│   │   ├── store/               # Zustand 스토어
│   │   │   ├── hypothesis.ts
│   │   │   └── paper.ts
│   │   └── styles/
│   │       └── globals.css      # 글로벌 스타일
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── README.md
│
├── infra/
│   ├── docker/
│   │   └── docker-compose.yml   # 로컬 개발 환경
│   ├── k8s/
│   │   ├── backend/             # Backend k8s 매니페스트
│   │   ├── frontend/            # Frontend k8s 매니페스트
│   │   ├── neo4j/               # Neo4j 매니페스트
│   │   ├── qdrant/              # Qdrant 매니페스트
│   │   └── redis/               # Redis 매니페스트
│   └── scripts/                 # 배포 스크립트
│
├── docs/
│   ├── api/                     # API 문서
│   ├── architecture/            # 아키텍처 다이어그램
│   └── guides/                  # 가이드
│
├── .github/
│   └── workflows/               # CI/CD 워크플로우
│
├── README.md                    # 프로젝트 루트 README
├── ARCHITECTURE.md              # 이 파일
├── ROADMAP.md                   # 개발 로드맵
└── LICENSE                      # 라이선스
```

## 🔄 데이터 플로우

### 가설 생성 파이프라인

```
1. 사용자 입력 (키워드/논문 URL)
   │
   ▼
2. arXiv Query
   │ (arxiv/client.py)
   ▼
3. 논문 다운로드 & 파싱
   │ (arxiv/parser.py)
   ▼
4. Vector RAG (Qdrant)
   │ - 논문 임베딩
   │ - 의미 기반 검색
   ▼
5. Graph RAG (Neo4j)
   │ - 엔티티 추출 (NER)
   │ - 관계 추출 (Relation Extraction)
   │ - 지식 그래프 쿼리
   ▼
6. Agent Teams 실행
   │ ┌─────────────────────────────────┐
   │ │ Generator (Opus 4-6)            │
   │ │ - RAG 컨텍스트 기반 가설 생성  │
   │ │ - 3-5개 후보 가설               │
   │ └────────┬────────────────────────┘
   │          │
   │          ▼
   │ ┌─────────────────────────────────┐
   │ │ Validator (Sonnet 4-5)          │
   │ │ - 과학적 타당성 검증            │
   │ │ - 논리적 오류 체크              │
   │ │ - 점수 부여 (0-100)             │
   │ └────────┬────────────────────────┘
   │          │
   │          ▼
   │ ┌─────────────────────────────────┐
   │ │ Debate Layer                    │
   │ │ - Generator vs Validator 토론   │
   │ │ - 반박/수정 3라운드             │
   │ │ - 합의 도출                     │
   │ └────────┬────────────────────────┘
   │          │
   │          ▼
   │ ┌─────────────────────────────────┐
   │ │ Ranker (Haiku 4-6)              │
   │ │ - 최종 순위 결정                │
   │ │ - 참신성/실현가능성 평가        │
   │ └────────────────────────────────┘
   ▼
7. 클러스터링 (KMeans)
   │ - 유사 가설 그룹화
   │ - 다양성 보장
   ▼
8. 결과 반환
   │ - WebSocket 실시간 스트리밍
   │ - REST API 최종 결과
   ▼
9. Frontend 렌더링
   - Modern Glassmorphism UI
   - 애니메이션 효과
   - 인터랙티브 카드
```

## 🧠 Claude Agent SDK Agent Teams 설계

### Agent 구성

```python
# agents/orchestrator.py
from anthropic import AnthropicClient

client = AnthropicClient(api_key=settings.ANTHROPIC_API_KEY)

# Generator Agent
generator_prompt = """
당신은 과학 논문에서 창의적인 가설을 생성하는 연구원입니다.
주어진 RAG 컨텍스트를 바탕으로 3-5개의 참신한 가설을 제안하세요.

평가 기준:
- 참신성 (Novelty): 기존 연구와 차별화
- 실현 가능성 (Feasibility): 검증 가능한 방법론
- 영향력 (Impact): 학문적 기여도
"""

# Validator Agent
validator_prompt = """
당신은 과학적 엄밀함을 검증하는 비평가입니다.
Generator가 제안한 가설의 타당성을 평가하세요.

체크리스트:
1. 논리적 일관성
2. 증거 기반 추론
3. 편향 검사
4. 실험 설계 가능성

각 가설에 점수(0-100)와 피드백을 제공하세요.
"""

# Ranker Agent
ranker_prompt = """
당신은 최종 순위를 결정하는 심사위원장입니다.
토론 결과를 바탕으로 가설의 최종 순위를 매기세요.

고려 사항:
- Generator의 창의성
- Validator의 검증 결과
- 토론 과정에서의 합의
- 실제 연구 가치
"""

# Agent Teams 실행
async def generate_hypotheses(papers: List[Paper]) -> List[Hypothesis]:
    # RAG 컨텍스트 준비
    rag_context = await prepare_rag_context(papers)
    
    # Agent Teams query 실행
    result = client.query(
        model="claude-opus-4-6",
        prompt=f"{generator_prompt}\n\nContext:\n{rag_context}",
        hooks={
            "PreToolUse": pre_tool_hook,
            "PostToolUse": post_tool_hook,
            "TeammateIdle": teammate_idle_hook
        }
    )
    
    # 스트리밍 결과 처리
    async for event in result.stream():
        if event.type == "tool_use":
            await handle_tool_use(event)
        elif event.type == "assistant":
            await stream_to_frontend(event.text)
    
    return parse_hypotheses(result.result)
```

### Debate Layer 구현

```python
# agents/debate.py
async def run_debate(
    generator_hypotheses: List[Hypothesis],
    validator_feedback: List[Feedback]
) -> List[Hypothesis]:
    """
    Generator와 Validator 간 3라운드 토론
    """
    for round_num in range(1, 4):
        # Round 1-3: 반박과 수정
        generator_response = await generator_agent.respond_to_critique(
            validator_feedback
        )
        
        validator_rebuttal = await validator_agent.re_evaluate(
            generator_response
        )
        
        # 합의 체크
        if is_consensus_reached(generator_response, validator_rebuttal):
            break
    
    # 최종 합의된 가설 반환
    return finalize_hypotheses(generator_response, validator_rebuttal)
```

## 🗄️ 데이터베이스 스키마

### Neo4j (Graph DB)

```cypher
// Node Types
(:Paper {
  id: String,
  title: String,
  authors: [String],
  abstract: Text,
  arxiv_id: String,
  published_date: DateTime
})

(:Entity {
  id: String,
  name: String,
  type: String,  // PERSON, ORGANIZATION, CONCEPT, METHOD
  mention_count: Integer
})

(:Hypothesis {
  id: String,
  text: Text,
  score: Float,
  novelty_score: Float,
  feasibility_score: Float,
  created_at: DateTime
})

// Relationships
(:Paper)-[:MENTIONS]->(:Entity)
(:Entity)-[:RELATED_TO {relation_type: String, confidence: Float}]->(:Entity)
(:Hypothesis)-[:DERIVED_FROM]->(:Paper)
(:Hypothesis)-[:INVOLVES]->(:Entity)
```

### Qdrant (Vector DB)

```python
# Collection Schema
{
    "collection_name": "papers",
    "vectors": {
        "size": 1536,  # OpenAI text-embedding-3-small
        "distance": "Cosine"
    },
    "payload_schema": {
        "arxiv_id": "keyword",
        "title": "text",
        "abstract": "text",
        "authors": "keyword[]",
        "published_date": "datetime",
        "chunk_index": "integer"  # 논문을 청크로 나눈 경우
    }
}
```

## 🎨 UI/UX 디자인 원칙

### Modern Glassmorphism 스타일

```css
/* 핵심 디자인 토큰 */
:root {
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-blur: 20px;
  
  /* Colors */
  --primary: #6366f1;      /* Indigo */
  --secondary: #8b5cf6;    /* Purple */
  --accent: #06b6d4;       /* Cyan */
  --success: #10b981;      /* Green */
  --warning: #f59e0b;      /* Amber */
  --error: #ef4444;        /* Red */
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --gradient-mesh: radial-gradient(at 40% 20%, #6366f1 0px, transparent 50%),
                   radial-gradient(at 80% 0%, #8b5cf6 0px, transparent 50%),
                   radial-gradient(at 0% 50%, #06b6d4 0px, transparent 50%);
}

/* 가설 카드 */
.hypothesis-card {
  backdrop-filter: blur(var(--glass-blur));
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hypothesis-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(99, 102, 241, 0.2);
}
```

### 애니메이션 원칙

```typescript
// Framer Motion 공통 variants
export const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" }
  }
};

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

export const glassShine = {
  initial: { x: "-100%" },
  animate: {
    x: "100%",
    transition: {
      repeat: Infinity,
      duration: 3,
      ease: "linear"
    }
  }
};
```

## 🧪 테스트 전략

### 테스트 피라미드

```
        ┌─────────────┐
        │  E2E Tests  │  ← 50개 (핵심 시나리오)
        │   Manual    │
        └─────────────┘
       ┌───────────────┐
       │ Integration   │  ← 100개 (API + DB + Agents)
       │    Tests      │
       └───────────────┘
      ┌─────────────────┐
      │   Unit Tests    │  ← 자동 생성 (커버리지 80%+)
      │   Automated     │
      └─────────────────┘
```

### 테스트 범위

**Backend (Python):**
- **Unit Tests (pytest):** 각 모듈별 단위 테스트
- **Integration Tests:** FastAPI + Qdrant + Neo4j 통합
- **Agent Tests:** Claude Agent SDK 모킹 테스트
- **Property-based Tests (hypothesis):** 엣지 케이스 자동 생성

**Frontend (TypeScript):**
- **Unit Tests (Jest + React Testing Library):** 컴포넌트 단위
- **Integration Tests (Playwright):** E2E 시나리오
- **Visual Regression Tests (Chromatic):** UI 변경 감지

## 🚀 배포 전략

### 로컬 개발

```bash
# Docker Compose로 전체 스택 실행
docker-compose -f infra/docker/docker-compose.yml up
```

### Kubernetes 배포

```yaml
# k8s 배포 순서
1. Namespace 생성
2. Persistent Volume (Neo4j, Qdrant)
3. ConfigMap (환경 변수)
4. Secret (API 키)
5. Services (Neo4j, Qdrant, Redis)
6. Deployments (Backend, Frontend)
7. Ingress (외부 접근)
```

## 📊 모니터링 & 로깅

```python
# Prometheus 메트릭
hypothesis_generation_duration = Histogram(
    "hypothesis_generation_duration_seconds",
    "Time spent generating hypotheses"
)

agent_tool_use_count = Counter(
    "agent_tool_use_total",
    "Total number of tool uses by agent",
    ["agent_type", "tool_name"]
)

rag_retrieval_latency = Summary(
    "rag_retrieval_latency_seconds",
    "RAG retrieval latency"
)
```

## 🔐 보안 고려사항

1. **API 키 관리:** Kubernetes Secrets
2. **Rate Limiting:** FastAPI Limiter (Redis)
3. **Input Validation:** Pydantic 모델 검증
4. **CORS:** 프로덕션 도메인만 허용
5. **WebSocket 인증:** JWT 토큰 기반

## 🎯 성능 목표

- **가설 생성 시간:** < 2분 (10편 논문 기준)
- **RAG 검색:** < 500ms
- **Graph RAG:** < 1s
- **API 응답:** < 200ms (캐시 적중 시)
- **WebSocket 지연:** < 100ms

---

**작성일:** 2026-03-07  
**작성자:** CLAW 🦀  
**버전:** 1.0
