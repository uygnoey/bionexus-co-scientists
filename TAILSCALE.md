# 🌐 Tailscale 원격 접속 설정

Tailscale을 사용하면 어디서든 안전하게 BioNexus에 접속할 수 있습니다.

---

## 설치

### Mac
```bash
brew install tailscale
sudo tailscaled install-system-daemon
tailscale up
```

### 다른 기기
https://tailscale.com/download 에서 다운로드

---

## 서버 설정 (Mac Mini)

### 1. Tailscale 설치 & 로그인
```bash
brew install tailscale
sudo tailscaled install-system-daemon
tailscale up
```

### 2. Tailscale IP 확인
```bash
tailscale ip -4
```
예: `100.64.1.2`

### 3. Backend 실행 (모든 인터페이스에서 접근 가능하게)
```bash
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### 4. Frontend 실행
```bash
cd frontend
npm run dev -- -H 0.0.0.0
```

---

## 클라이언트 설정 (원격 접속)

### 1. 같은 Tailscale 네트워크에 로그인
```bash
tailscale up
```

### 2. 서버 IP 확인
```bash
tailscale status
```

서버의 Tailscale IP를 찾습니다 (예: `100.64.1.2`)

### 3. 브라우저에서 접속

- **Frontend**: `http://100.64.1.2:9001`
- **Backend API**: `http://100.64.1.2:9000`
- **API Docs**: `http://100.64.1.2:9000/docs`

---

## Frontend 환경 변수 수정 (원격 접속용)

원격에서 접속할 때는 Frontend가 Tailscale IP를 사용하도록 설정:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://100.64.1.2:9000
NEXT_PUBLIC_WS_URL=ws://100.64.1.2:9000
```

**주의**: IP는 실제 서버의 Tailscale IP로 변경하세요!

---

## Docker/Podman으로 실행 시

### 1. docker-compose.yml 수정

```yaml
# infra/docker/docker-compose.yml
services:
  backend:
    ports:
      - "0.0.0.0:9000:9000"  # 모든 인터페이스에서 접근 가능
    environment:
      CORS_ORIGINS: '["http://localhost:9001", "http://100.64.1.2:9001"]'
```

### 2. 실행
```bash
podman-compose up -d
```

---

## 보안 팁

### 1. Tailscale ACL 설정
Tailscale 관리자 페이지에서 ACL을 설정하여 특정 디바이스만 접근 허용:

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["your-laptop"],
      "dst": ["mac-mini:9000", "mac-mini:9001"]
    }
  ]
}
```

### 2. 방화벽 설정 (선택)
```bash
# macOS 방화벽에서 9000, 9001 포트만 Tailscale 인터페이스에 허용
```

---

## 문제 해결

### "Connection refused"
- Backend/Frontend가 `0.0.0.0`으로 바인딩되었는지 확인
- 방화벽 설정 확인
- Tailscale 연결 확인: `tailscale status`

### "CORS error"
- Backend의 `CORS_ORIGINS`에 원격 URL 추가
- Frontend의 `.env.local`에 올바른 Backend URL 설정

### Tailscale IP가 바뀜
- Tailscale은 보통 고정 IP를 유지하지만, 재설치 시 변경될 수 있음
- MagicDNS 사용 권장: `http://mac-mini:9000` (디바이스 이름 사용)

---

## MagicDNS 사용 (권장)

Tailscale MagicDNS를 활성화하면 IP 대신 디바이스 이름 사용 가능:

```bash
# 1. Tailscale 관리자 페이지에서 MagicDNS 활성화

# 2. 디바이스 이름으로 접속
http://mac-mini:9001  # Frontend
http://mac-mini:9000  # Backend
```

Frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=http://mac-mini:9000
NEXT_PUBLIC_WS_URL=ws://mac-mini:9000
```

---

**이제 어디서든 안전하게 BioNexus Co-scientists를 사용할 수 있습니다!** 🦀
