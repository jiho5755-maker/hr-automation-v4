# 🐳 HR 자동화 v4.0 - Docker 빠른 시작

> **Windows 홈서버에서 5분 만에 시작하기**

---

## ⚡ 초간단 시작 (3단계)

### 1️⃣ Docker Desktop 실행 확인

- 시스템 트레이에서 Docker 아이콘 확인
- "Docker Desktop is running" 표시되어야 함

### 2️⃣ PowerShell 관리자 권한으로 실행

```powershell
# 프로젝트 디렉토리로 이동
cd C:\HomeServer\인사팀_자동화_마스터

# 시작!
.\docker-start.ps1
```

### 3️⃣ 브라우저에서 접속

```
http://localhost
```

**로그인:**
- ID: `admin`
- PW: `admin1234`

---

## 🛠️ 주요 명령어

| 작업 | 명령어 | 설명 |
|------|--------|------|
| **시작** | `.\docker-start.ps1` | 전체 시스템 시작 |
| **중지** | `.\docker-stop.ps1` | 전체 시스템 중지 |
| **재시작** | `.\docker-restart.ps1` | 시스템 재시작 |
| **상태** | `.\docker-status.ps1` | 상태 및 리소스 확인 |
| **로그** | `.\docker-logs.ps1` | 로그 확인 |
| **로그(실시간)** | `.\docker-logs.ps1 -Follow` | 실시간 로그 스트림 |

---

## 📂 프로젝트 구조

```
인사팀_자동화_마스터/
├── 0_통합_대시보드/          ← v4.0 메인 앱
│   ├── app.py                ← 진입점
│   ├── pages/                ← 모든 페이지
│   │   ├── 1_👥_직원_관리.py
│   │   ├── 2_👶_출산육아.py
│   │   ├── 3_🏠_재택근무.py
│   │   ├── 4_💰_급여관리.py
│   │   └── 5_⚙️_설정.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── shared/                   ← 공유 모듈
│   ├── database.py          ← 통합 DB 관리
│   ├── auth.py              ← 인증
│   ├── design.py            ← 디자인 시스템
│   └── utils.py             ← 유틸리티
│
├── nginx/
│   └── nginx.conf           ← 리버스 프록시 설정
│
├── docker-compose.yml       ← Docker 구성
├── .env                     ← 환경 변수 (직접 설정 필요)
├── hr_master.db             ← 통합 데이터베이스
│
└── 🪟_Windows_Docker_배포_가이드.md  ← 상세 가이드
```

---

## 🔧 초기 설정 (최초 1회만)

### 1. 환경 변수 설정

```powershell
# .env 파일 생성
copy env.example.txt .env

# 메모장으로 편집
notepad .env
```

**필수 수정 항목:**

```ini
# 홈서버 IP 확인 (PowerShell에서)
ipconfig
# → IPv4 주소 확인 (예: 192.168.0.100)

# .env 파일에서 수정
HOST_IP=192.168.0.100    # ← 실제 IP
ADMIN_PASSWORD=새비밀번호  # ← 보안을 위해 변경
SECRET_KEY=랜덤한긴문자열   # ← 반드시 변경
```

### 2. 데이터베이스 초기화

```powershell
# Python 설치되어 있으면
python scripts/init_system.py

# 또는 Docker 컨테이너에서 자동 실행됨
# (첫 실행 시 자동 초기화)
```

---

## 🚀 실행 방법

### 방법 1: PowerShell 스크립트 (권장)

```powershell
# 관리자 권한 PowerShell에서
.\docker-start.ps1
```

### 방법 2: 수동 실행

```powershell
# 빌드 + 시작 (최초)
docker-compose up -d --build

# 시작만 (이후)
docker-compose up -d
```

---

## 🔍 확인 및 모니터링

### 상태 확인

```powershell
# 전체 상태
.\docker-status.ps1

# 또는
docker-compose ps
```

**정상 상태:**
```
NAME            STATE     HEALTH        PORTS
hr-dashboard    Up        healthy       0.0.0.0:8000->8000/tcp
hr-nginx        Up        healthy       0.0.0.0:80->80/tcp
```

### 로그 확인

```powershell
# 실시간 로그
.\docker-logs.ps1 -Follow

# 최근 100줄
.\docker-logs.ps1

# 대시보드만
.\docker-logs.ps1 -Service dashboard
```

### 리소스 모니터링

```powershell
# 실시간 리소스 사용량
docker stats
```

---

## 🌐 접속 방법

### 로컬 (홈서버에서)

```
http://localhost
http://127.0.0.1
http://localhost:8000
```

### 같은 네트워크 (다른 PC/스마트폰)

```
http://192.168.0.100
```
*(실제 홈서버 IP로 변경)*

### 외부 인터넷 (포트포워딩 설정 후)

```
http://[공인IP]
http://mycompany.ddns.net  (DDNS 설정 시)
```

---

## 🔄 일상 운영

### Windows 부팅 시 자동 시작

**방법 1: 작업 스케줄러 (권장)**

1. `Win+R` → `taskschd.msc` → 엔터
2. 기본 작업 만들기
   - 이름: `HR 자동화 시작`
   - 트리거: `컴퓨터를 시작할 때`
   - 동작: `프로그램 시작`
   - 프로그램: `PowerShell.exe`
   - 인수: `-WindowStyle Hidden -File "C:\HomeServer\인사팀_자동화_마스터\docker-start.ps1"`
   - 체크: `가장 높은 수준의 권한으로 실행`

**방법 2: 시작프로그램**

1. `docker-start.ps1` 우클릭 → 바로가기 만들기
2. `Win+R` → `shell:startup` → 엔터
3. 바로가기 붙여넣기

### 매일 자동 백업

**작업 스케줄러 등록:**

1. 기본 작업 만들기
   - 이름: `HR 자동화 백업`
   - 트리거: `매일 새벽 2시`
   - 동작: `PowerShell.exe`
   - 인수: `-File "C:\HomeServer\인사팀_자동화_마스터\backup-daily.ps1"`

---

## ⚠️ 문제 해결

### 시작 안 됨

```powershell
# 1. Docker 실행 확인
docker info

# 2. 로그 확인
.\docker-logs.ps1

# 3. 강제 재빌드
docker-compose down
docker-compose up -d --build --force-recreate
```

### 포트 충돌 (80번 포트 사용 중)

```powershell
# 80번 포트 사용 중인 프로그램 확인
netstat -ano | findstr :80

# 해결 1: 다른 포트 사용
# .env 파일 수정
NGINX_PORT=8080

# 해결 2: 충돌 프로세스 종료 (작업 관리자)
```

### 데이터베이스 오류

```powershell
# 1. 중지
docker-compose down

# 2. DB 파일 권한 확인
# hr_master.db 우클릭 → 속성 → 보안
# "Users" 그룹에 읽기/쓰기 권한 부여

# 3. 재시작
.\docker-start.ps1
```

### 메모리 부족

```powershell
# Docker Desktop 설정
# Settings → Resources → Memory 증가 (4GB 권장)
```

---

## 🔐 보안 체크리스트

### 최초 설정 시 필수

- [ ] `.env` 파일에서 `ADMIN_PASSWORD` 변경
- [ ] `.env` 파일에서 `SECRET_KEY` 변경 (랜덤 문자열)
- [ ] 기본 admin 계정 비밀번호 변경 (대시보드에서)
- [ ] Windows 방화벽 확인

### 외부 접속 시 권장

- [ ] HTTPS 설정 (Let's Encrypt)
- [ ] 강력한 비밀번호 정책
- [ ] VPN 사용 (포트포워딩 대신)
- [ ] 정기 백업 자동화
- [ ] 로그 정기 검토

---

## 📊 성능 최적화

### Docker Desktop 설정

**Settings → Resources:**

```
CPUs: 4 (또는 전체의 50%)
Memory: 4GB
Swap: 1GB
Disk: 64GB
```

### WSL 2 최적화

**파일:** `%USERPROFILE%\.wslconfig`

```ini
[wsl2]
memory=4GB
processors=4
swap=1GB
localhostForwarding=true
```

**적용:** Docker Desktop 재시작

---

## 🆘 긴급 복구

### 시스템이 완전히 망가졌을 때

```powershell
# 1. 모든 컨테이너 중지 및 삭제
docker-compose down -v

# 2. 이미지 삭제
docker-compose down --rmi all

# 3. 백업에서 DB 복구
copy backups\backup_최신\hr_master.db .\hr_master.db

# 4. 재빌드 및 시작
docker-compose up -d --build --force-recreate
```

---

## 📈 다음 단계

### 현재 (v4.0)
- ✅ 통합 대시보드
- ✅ 직원 관리
- ✅ 재택근무 관리
- 🚧 출산육아 (개발 중)
- 🚧 급여관리 (개선 중)

### 계획 (v4.1+)
- 🔜 영업/마케팅 자동화
- 🔜 회계/재무 자동화
- 🔜 모바일 앱

---

## 💡 유용한 팁

### 빠른 재시작

```powershell
# 코드만 수정한 경우
docker-compose restart dashboard

# DB 스키마 변경한 경우
docker-compose up -d --build --force-recreate dashboard
```

### 데이터 확인

```powershell
# 컨테이너 내부 접속
docker-compose exec dashboard /bin/bash

# Python 쉘 실행
docker-compose exec dashboard python

# DB 직접 확인
docker-compose exec dashboard sqlite3 /app/hr_master.db
```

### 성능 모니터링

```powershell
# CPU/메모리 사용량
docker stats --no-stream

# 디스크 사용량
docker system df
```

---

## 📞 지원 및 문서

- 📖 상세 가이드: [🪟_Windows_Docker_배포_가이드.md](./🪟_Windows_Docker_배포_가이드.md)
- 🏠 홈서버 가이드: [🏠_홈서버_배포_가이드.md](./🏠_홈서버_배포_가이드.md)
- 🚀 일반 실행: [README.md](./README.md)

---

## 🎯 요약

```powershell
# 시작
.\docker-start.ps1

# 확인
.\docker-status.ps1

# 접속
http://localhost

# 중지
.\docker-stop.ps1
```

**이게 전부입니다! 🎉**

---

## ⚙️ 고급 설정

### 외부 접속 허용

1. **공유기 포트포워딩**
   - 외부 포트: 80
   - 내부 IP: 192.168.0.100
   - 내부 포트: 80

2. **DDNS 설정**
   - No-IP, DuckDNS 등 사용
   - 도메인: `mycompany.ddns.net`

3. **접속**
   ```
   http://mycompany.ddns.net
   ```

### HTTPS 설정 (Let's Encrypt)

```powershell
# Certbot 컨테이너 추가
# docker-compose.yml 수정 필요
# 상세 가이드는 🪟_Windows_Docker_배포_가이드.md 참조
```

---

**더 자세한 내용은 [🪟_Windows_Docker_배포_가이드.md](./🪟_Windows_Docker_배포_가이드.md)를 참조하세요!**
