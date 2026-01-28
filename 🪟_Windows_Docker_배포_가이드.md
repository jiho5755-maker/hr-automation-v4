# 🪟 Windows Docker 홈서버 배포 가이드

> **HR 자동화 시스템 v4.0 - Windows 환경 완벽 가이드**

---

## 📋 목차

1. [사전 준비](#1-사전-준비)
2. [초기 설정](#2-초기-설정)
3. [Docker 배포](#3-docker-배포)
4. [접속 및 확인](#4-접속-및-확인)
5. [일상 운영](#5-일상-운영)
6. [문제 해결](#6-문제-해결)
7. [백업 및 복구](#7-백업-및-복구)
8. [외부 접속 설정](#8-외부-접속-설정)

---

## 1. 사전 준비

### ✅ 필수 소프트웨어

#### 1.1 Docker Desktop 설치

```powershell
# 다운로드 링크
https://www.docker.com/products/docker-desktop/

# 설치 후 확인
docker --version
docker-compose --version
```

**설치 확인:**
- Docker Desktop 아이콘이 시스템 트레이에 있어야 함
- "Docker Desktop is running" 상태 확인

#### 1.2 Git (선택사항)

```powershell
# Git for Windows
https://git-scm.com/download/win
```

#### 1.3 PowerShell (Windows 기본 탑재)

```powershell
# 버전 확인
$PSVersionTable.PSVersion

# 5.1 이상이면 OK
```

---

## 2. 초기 설정

### 2.1 프로젝트 복사

```powershell
# 홈서버의 원하는 위치로 이동
cd C:\HomeServer\

# 프로젝트 복사 (USB, 네트워크 드라이브 등에서)
# 또는
git clone [repository-url]
```

### 2.2 환경 변수 설정

```powershell
# 프로젝트 디렉토리로 이동
cd C:\HomeServer\인사팀_자동화_마스터

# 환경 변수 파일 생성
copy env.example.txt .env

# .env 파일 편집 (메모장 또는 VS Code)
notepad .env
```

**필수 수정 항목:**

```ini
# 1. 홈서버 IP 확인 및 입력
# PowerShell에서 실행:
ipconfig
# → IPv4 주소를 확인 (예: 192.168.0.100)

HOST_IP=192.168.0.100  # ← 실제 IP로 변경

# 2. 보안 설정 변경 (⚠️ 중요!)
SECRET_KEY=이곳에_랜덤한_문자열_입력
ADMIN_PASSWORD=강력한_비밀번호로_변경

# 3. 회사 정보
COMPANY_NAME=실제_회사명
COMPANY_CEO=대표자명
BUSINESS_NUMBER=사업자번호
```

### 2.3 데이터베이스 초기화

```powershell
# Python이 설치되어 있다면 (선택사항)
python scripts/init_system.py

# 또는 Docker로 초기화 (권장)
# → 첫 실행 시 자동으로 초기화됩니다
```

### 2.4 로그 디렉토리 생성

```powershell
mkdir logs
```

---

## 3. Docker 배포

### 3.1 빠른 시작 🚀

```powershell
# PowerShell 관리자 권한으로 실행
# (시작 메뉴 → PowerShell 우클릭 → "관리자 권한으로 실행")

cd C:\HomeServer\인사팀_자동화_마스터

# 시작 스크립트 실행
.\docker-start.ps1
```

**첫 실행 시:**
- 이미지 다운로드: 약 2-3분
- 빌드: 약 5-10분
- 총 소요 시간: 약 10-15분

**이후 실행 시:**
- 시작 시간: 약 10-30초

### 3.2 수동 실행 (세부 제어)

```powershell
# 1. 빌드 + 시작
docker-compose up -d --build

# 2. 시작만 (빌드 없이)
docker-compose up -d

# 3. 백그라운드 없이 로그 보면서 실행
docker-compose up

# 4. 특정 서비스만 시작
docker-compose up -d dashboard
```

### 3.3 상태 확인

```powershell
# 스크립트로 확인 (권장)
.\docker-status.ps1

# 또는 수동 확인
docker-compose ps
```

**정상 상태:**
```
NAME            STATUS          PORTS
hr-dashboard    Up (healthy)    0.0.0.0:8000->8000/tcp
hr-nginx        Up (healthy)    0.0.0.0:80->80/tcp
```

---

## 4. 접속 및 확인

### 4.1 로컬 접속 (홈서버에서)

```
http://localhost
http://localhost:8000
http://127.0.0.1
```

### 4.2 같은 네트워크에서 접속 (다른 PC/스마트폰)

```
# .env 파일의 HOST_IP 사용
http://192.168.0.100
http://192.168.0.100:8000
```

### 4.3 로그인 정보

**기본 계정:**
```
관리자 계정:
  ID: admin
  PW: admin1234

테스트 계정:
  ID: test
  PW: test1234
```

⚠️ **실제 운영 시 반드시 비밀번호를 변경하세요!**

---

## 5. 일상 운영

### 5.1 시작

```powershell
.\docker-start.ps1
```

또는

```powershell
docker-compose up -d
```

### 5.2 중지

```powershell
.\docker-stop.ps1
```

또는

```powershell
docker-compose down
```

### 5.3 재시작

```powershell
.\docker-restart.ps1
```

또는

```powershell
docker-compose restart
```

### 5.4 로그 확인

```powershell
# 실시간 로그 (Ctrl+C로 종료)
.\docker-logs.ps1 -Follow

# 최근 100줄
.\docker-logs.ps1

# 최근 500줄
.\docker-logs.ps1 -Lines 500

# 대시보드만
.\docker-logs.ps1 -Service dashboard

# Nginx만
.\docker-logs.ps1 -Service nginx
```

### 5.5 상태 모니터링

```powershell
# 전체 상태
.\docker-status.ps1

# 리소스 사용량 실시간
docker stats
```

---

## 6. 문제 해결

### 6.1 컨테이너가 시작 안 됨

```powershell
# 1. 로그 확인
docker-compose logs dashboard

# 2. 강제 재빌드
docker-compose down
docker-compose up -d --build --force-recreate

# 3. 캐시 없이 재빌드
docker-compose build --no-cache
docker-compose up -d
```

### 6.2 포트 충돌 (80번 포트 사용 중)

```powershell
# 현재 80번 포트 사용 중인 프로세스 확인
netstat -ano | findstr :80

# 해결 방법 1: 다른 포트 사용
# .env 파일 수정
NGINX_PORT=8080

# 해결 방법 2: 충돌 프로세스 종료
# 작업 관리자에서 해당 프로세스 종료
```

### 6.3 데이터베이스 오류

```powershell
# 1. 컨테이너 중지
docker-compose down

# 2. DB 파일 권한 확인
# 파일 탐색기에서:
# hr_master.db 우클릭 → 속성 → 보안
# "Everyone" 또는 "Users" 그룹에 읽기/쓰기 권한 부여

# 3. 재시작
docker-compose up -d
```

### 6.4 "출산육아" 페이지 크래시

현재 v4.0에서는 출산육아 기능이 통합 대시보드 내에서 개발 중입니다.
완전한 기능은 v4.1 업데이트 예정입니다.

### 6.5 로그인 오류

```powershell
# 1. 데이터베이스 초기화
python scripts/init_system.py

# 2. 컨테이너 재시작
.\docker-restart.ps1

# 3. 기본 계정으로 로그인 시도
# admin / admin1234
```

### 6.6 Docker Desktop이 느림

```powershell
# WSL 2 설정 최적화
# %USERPROFILE%\.wslconfig 파일 생성

[wsl2]
memory=4GB
processors=2
swap=1GB
```

**Docker Desktop 재시작 필요**

---

## 7. 백업 및 복구

### 7.1 데이터 백업

```powershell
# 백업 디렉토리 생성
mkdir backups

# 현재 날짜로 백업
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\backup_$date"
mkdir $backupDir

# 데이터베이스 백업
docker-compose exec dashboard cp /app/hr_master.db /app/hr_master_backup.db
docker cp hr-dashboard:/app/hr_master_backup.db "$backupDir\hr_master.db"

# 전체 데이터 디렉토리 백업
Copy-Item -Recurse -Path ".\logs" -Destination "$backupDir\logs"
Copy-Item ".env" "$backupDir\.env"

Write-Host "✅ 백업 완료: $backupDir"
```

### 7.2 자동 백업 스크립트

`backup-daily.ps1` 파일을 생성하고 Windows 작업 스케줄러에 등록하세요.

```powershell
# 작업 스케줄러 등록
# 시작 → 작업 스케줄러 → 기본 작업 만들기
# → 트리거: 매일 새벽 2시
# → 동작: 프로그램 시작 → PowerShell.exe
# → 인수: -File "C:\HomeServer\인사팀_자동화_마스터\backup-daily.ps1"
```

### 7.3 복구

```powershell
# 1. 컨테이너 중지
docker-compose down

# 2. 백업에서 복구
$backupDir = "backups\backup_20260128_120000"
Copy-Item "$backupDir\hr_master.db" ".\hr_master.db"
Copy-Item -Recurse "$backupDir\logs" ".\logs"

# 3. 재시작
docker-compose up -d

Write-Host "✅ 복구 완료"
```

---

## 8. 외부 접속 설정

### 8.1 공유기 포트포워딩

**목적:** 외부 인터넷에서도 접속 가능하게 하기

**단계:**

1. **공유기 관리 페이지 접속**
   - 일반적으로 `http://192.168.0.1` 또는 `http://192.168.1.1`
   - 공유기 제조사별로 다를 수 있음

2. **포트포워딩 설정**
   ```
   외부 포트: 80
   내부 IP: 192.168.0.100 (홈서버 IP)
   내부 포트: 80
   프로토콜: TCP
   ```

3. **공인 IP 확인**
   ```
   https://whatismyipaddress.com/
   ```

4. **접속**
   ```
   http://[공인IP]
   ```

### 8.2 DDNS 설정 (선택사항)

**목적:** IP 변경에도 도메인으로 접속

**추천 서비스:**
- No-IP (무료): https://www.noip.com/
- DuckDNS (무료): https://www.duckdns.org/
- Cloudflare (무료): https://www.cloudflare.com/

**예시: No-IP 사용**

1. No-IP 계정 생성
2. 호스트네임 생성 (예: mycompany.ddns.net)
3. No-IP DUC (Dynamic Update Client) 설치
4. 접속: `http://mycompany.ddns.net`

### 8.3 HTTPS 설정 (Let's Encrypt)

**외부 접속 시 보안 강화**

```powershell
# Certbot 컨테이너 추가
# docker-compose.yml에 추가:

certbot:
  image: certbot/certbot
  volumes:
    - ./nginx/certs:/etc/letsencrypt
  command: certonly --webroot --webroot-path=/var/www/html --email your@email.com --agree-tos --no-eff-email -d mycompany.ddns.net
```

**nginx.conf 수정:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/mycompany.ddns.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mycompany.ddns.net/privkey.pem;
    # ...
}
```

---

## 9. 성능 최적화

### 9.1 Docker Desktop 설정

**Settings → Resources:**

```
CPUs: 4 (또는 전체의 50%)
Memory: 4GB (또는 전체의 50%)
Swap: 1GB
Disk image size: 64GB
```

### 9.2 WSL 2 최적화

**파일 생성:** `%USERPROFILE%\.wslconfig`

```ini
[wsl2]
memory=4GB
processors=4
swap=1GB
localhostForwarding=true
```

**적용:** Docker Desktop 재시작

### 9.3 컨테이너 리소스 제한

이미 `docker-compose.yml`에 설정되어 있음:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # CPU 1코어
      memory: 1G       # 메모리 1GB
```

---

## 10. Windows 시작 시 자동 실행

### 10.1 작업 스케줄러 등록

1. **시작 → 작업 스케줄러**

2. **기본 작업 만들기**
   - 이름: `HR 자동화 시스템 시작`
   - 트리거: `컴퓨터를 시작할 때`
   - 동작: `프로그램 시작`
   - 프로그램: `PowerShell.exe`
   - 인수: `-WindowStyle Hidden -File "C:\HomeServer\인사팀_자동화_마스터\docker-start.ps1"`

3. **고급 설정**
   - "가장 높은 수준의 권한으로 실행" 체크
   - "숨김" 체크 (백그라운드 실행)

### 10.2 시작프로그램에 등록 (간단한 방법)

```powershell
# 바로가기 생성
# docker-start.ps1 우클릭 → 바로가기 만들기

# 바로가기를 시작프로그램 폴더로 이동
# Win+R → shell:startup → 엔터
# → 바로가기 붙여넣기
```

---

## 11. 모니터링 및 알림

### 11.1 Discord/Slack 알림 (선택사항)

컨테이너 다운 시 알림 받기:

```powershell
# docker-compose.yml에 watchtower 추가
watchtower:
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  environment:
    - WATCHTOWER_NOTIFICATIONS=slack
    - WATCHTOWER_NOTIFICATION_SLACK_HOOK_URL=your_webhook_url
```

### 11.2 Uptime Kuma (권장)

```powershell
# docker-compose.yml에 추가
uptime-kuma:
  image: louislam/uptime-kuma:1
  container_name: uptime-kuma
  volumes:
    - ./uptime-kuma-data:/app/data
  ports:
    - "3001:3001"
  restart: always
```

**접속:** `http://localhost:3001`

---

## 12. 업데이트 방법

### 12.1 코드 업데이트

```powershell
# 1. 백업 (안전을 위해)
.\backup-now.ps1

# 2. 코드 업데이트
git pull
# 또는 새 파일 복사

# 3. 재배포
docker-compose down
docker-compose up -d --build

Write-Host "✅ 업데이트 완료"
```

### 12.2 데이터는 그대로 유지

Docker Compose는 **볼륨**을 사용하므로:
- 컨테이너 재생성 시에도 데이터 보존
- `hr_master.db`는 호스트에 저장됨
- 안전하게 업데이트 가능

---

## 13. 보안 체크리스트

### ✅ 필수 보안 조치

- [ ] `.env` 파일에서 `SECRET_KEY` 변경
- [ ] `.env` 파일에서 `ADMIN_PASSWORD` 변경
- [ ] 기본 admin 계정 비밀번호 변경
- [ ] Windows 방화벽 설정 확인
- [ ] 외부 접속 시 HTTPS 사용
- [ ] 정기 백업 자동화
- [ ] Docker Desktop 자동 업데이트 활성화

### ✅ 권장 보안 조치

- [ ] VPN을 통한 외부 접속 (포트포워딩 대신)
- [ ] fail2ban 또는 Cloudflare 사용
- [ ] 로그 정기 검토
- [ ] 데이터베이스 암호화

---

## 14. 유용한 명령어 모음

### 컨테이너 관리

```powershell
# 전체 중지
docker-compose down

# 전체 삭제 (데이터 포함 ⚠️)
docker-compose down -v

# 특정 컨테이너 재시작
docker-compose restart dashboard

# 컨테이너 내부 접속
docker-compose exec dashboard /bin/bash

# 컨테이너 내부에서 Python 실행
docker-compose exec dashboard python
```

### 로그 관리

```powershell
# 전체 로그
docker-compose logs

# 실시간 로그
docker-compose logs -f

# 최근 50줄
docker-compose logs --tail=50

# 특정 시간 이후 로그
docker-compose logs --since="2026-01-28T10:00:00"

# 에러만 필터링
docker-compose logs | Select-String "ERROR"
```

### 리소스 정리

```powershell
# 사용하지 않는 이미지 삭제
docker image prune -a

# 사용하지 않는 볼륨 삭제
docker volume prune

# 전체 정리 (⚠️ 주의)
docker system prune -a --volumes
```

---

## 15. 트러블슈팅 FAQ

### Q1: Docker Desktop이 시작 안 됨
**A:** 
- WSL 2 업데이트: `wsl --update`
- Hyper-V 활성화 확인
- BIOS에서 가상화 기능 활성화 확인

### Q2: 빌드가 너무 느림
**A:**
```powershell
# Docker Desktop Settings → Resources
# CPU/Memory 증가

# 또는 이미 빌드된 이미지 사용
docker-compose up -d  # --build 없이
```

### Q3: 외부에서 접속 안 됨
**A:**
1. 공유기 포트포워딩 확인
2. Windows 방화벽 설정 확인
3. 홈서버 IP 고정 (DHCP 설정)

### Q4: 메모리 부족
**A:**
```powershell
# docker-compose.yml에서 리소스 제한 조정
deploy:
  resources:
    limits:
      memory: 512M  # 1G → 512M로 감소
```

### Q5: 컨테이너가 자동 재시작 안 됨
**A:**
```yaml
# docker-compose.yml 확인
restart: always  # unless-stopped 대신
```

---

## 16. 다음 단계 (확장)

### 16.1 영업/마케팅 자동화 추가 예정

```yaml
# docker-compose.yml
sales-marketing:
  build: ./6_영업마케팅_자동화
  container_name: hr-sales
  # ...
```

### 16.2 회계/재무 자동화 추가 예정

```yaml
# docker-compose.yml
accounting:
  build: ./7_회계재무_자동화
  container_name: hr-accounting
  # ...
```

---

## 🎯 핵심 요약

| 작업 | 명령어 |
|------|--------|
| **시작** | `.\docker-start.ps1` |
| **중지** | `.\docker-stop.ps1` |
| **재시작** | `.\docker-restart.ps1` |
| **상태 확인** | `.\docker-status.ps1` |
| **로그 확인** | `.\docker-logs.ps1` |
| **접속** | `http://localhost` |

---

## 📞 지원

문제가 발생하면:

1. 로그 확인: `.\docker-logs.ps1 -Follow`
2. 상태 확인: `.\docker-status.ps1`
3. 재시작 시도: `.\docker-restart.ps1`
4. 강제 재빌드: `docker-compose up -d --build --force-recreate`

---

**🎉 이제 안정적인 24/7 홈서버 운영이 가능합니다!**
