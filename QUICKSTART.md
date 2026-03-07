# 🚀 빠른 시작 가이드

## 포트 정보
- **Backend API**: http://localhost:9000
- **Frontend**: http://localhost:9001
- **Neo4j**: http://localhost:7474
- **Qdrant**: http://localhost:6333
- **Redis**: localhost:6379

---

## 1️⃣ Backend 실행 (로컬)

```bash
# 1. Backend 폴더로 이동
cd backend

# 2. 환경 변수 설정
cp .env.example .env

# 3. .env 파일 편집 (필수!)
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here

# 4. 의존성 설치 (처음만)
pip3 install poetry
poetry install

# 5. 서버 실행
poetry run uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

✅ **Backend 실행 완료!**  
→ http://localhost:9000/docs 에서 API 확인

---

## 2️⃣ Frontend 실행 (로컬)

```bash
# 새 터미널 열기

# 1. Frontend 폴더로 이동
cd frontend

# 2. 의존성 설치 (처음만)
npm install

# 3. 환경 변수 설정
cp .env.example .env.local

# 4. 서버 실행
npm run dev
```

✅ **Frontend 실행 완료!**  
→ http://localhost:9001 에서 확인

---

## 3️⃣ 전체 스택 실행 (Podman)

```bash
# 1. Podman 설치
brew install podman podman-compose

# 2. Podman 초기화
podman machine init
podman machine start

# 3. 환경 변수 설정
cd infra/docker
cp .env.example .env
# .env 파일에 API 키 설정!

# 4. 전체 스택 실행
podman-compose up -d

# 5. 로그 확인
podman-compose logs -f backend
```

✅ **전체 스택 실행 완료!**

---

## 4️⃣ 테스트

```bash
cd backend
poetry run pytest tests/ -v
```

---

## 5️⃣ 중지

### Backend/Frontend 중지
- 터미널에서 `Ctrl+C`

### Podman 스택 중지
```bash
cd infra/docker
podman-compose down
```

---

## 🎯 주요 엔드포인트

| 서비스 | URL | 설명 |
|--------|-----|------|
| Frontend | http://localhost:9001 | 웹 UI |
| Backend API | http://localhost:9000 | REST API |
| API Docs | http://localhost:9000/docs | Swagger UI |
| Neo4j Browser | http://localhost:7474 | Graph DB |
| Qdrant Dashboard | http://localhost:6333/dashboard | Vector DB |

---

## ⚡ 빠른 테스트

### 1. Health Check
```bash
curl http://localhost:9000/health
```

### 2. Paper Search
```bash
curl "http://localhost:9000/api/papers/search?query=quantum+computing&max_results=5"
```

### 3. Hypothesis Generation (예시)
```bash
curl -X POST http://localhost:9000/api/hypotheses/generate \
  -H "Content-Type: application/json" \
  -d '{
    "paper_ids": ["2301.12345"],
    "max_hypotheses": 3
  }'
```

---

## 🔧 문제 해결

### Backend가 안 뜬다
- `.env` 파일에 API 키 확인
- Poetry 설치 확인: `poetry --version`
- 포트 충돌 확인: `lsof -i :9000`

### Frontend가 안 뜬다
- `npm install` 재실행
- `.env.local` 파일 확인
- 포트 충돌 확인: `lsof -i :9001`

### Podman 에러
```bash
podman machine stop
podman machine start
```

---

**Built with CLAW 🦀**
