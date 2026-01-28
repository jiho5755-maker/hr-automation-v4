# 🚀 배포 가이드

**인사팀 자동화 시스템 v3.0**  
**Windows 홈서버 배포 매뉴얼**

---

## 📋 배포 준비

### **맥북에서 (개발 환경)**

#### 1. 최종 확인 및 테스트

```bash
cd ~/Documents/인사팀_자동화_마스터

# 통합 대시보드 테스트
cd 0_통합_대시보드
streamlit run app.py --server.port 8000

# 각 앱 개별 테스트
cd ../1_출산육아_자동화
streamlit run app.py --server.port 8501
```

#### 2. Git 저장소 설정

```bash
cd ~/Documents/인사팀_자동화_마스터

# Git 초기화
git init

# .gitignore 확인
cat .gitignore

# 커밋
git add .
git commit -m "Initial commit: HR Automation System v3.0"

# GitHub 저장소 생성 후
git remote add origin https://github.com/your-username/hr-automation.git
git branch -M main
git push -u origin main
```

---

## 🖥️ Windows 홈서버 설정

### **1. 필수 프로그램 설치**

#### Docker Desktop for Windows
```
1. https://www.docker.com/products/docker-desktop/ 다운로드
2. 설치 후 재부팅
3. WSL2 설치 (자동으로 설치됨)
4. Docker Desktop 실행 확인
```

#### Git for Windows
```
1. https://git-scm.com/download/win 다운로드
2. 설치
3. PowerShell에서 확인: git --version
```

### **2. 프로젝트 다운로드**

```powershell
# PowerShell 관리자 권한으로 실행

# 작업 디렉토리 생성
cd C:\
mkdir hr_automation
cd hr_automation

# Git에서 다운로드
git clone https://github.com/your-username/hr-automation.git .

# 또는 수동으로 파일 복사
# 맥북에서 USB나 네트워크 공유로 전송
```

### **3. 환경 설정**

```powershell
# .env 파일 생성
copy .env.example .env

# .env 파일 수정 (메모장으로)
notepad .env
```

**.env 파일 설정**:
```
HOST_IP=192.168.0.XXX  # Windows 홈서버 IP로 변경
ADMIN_PASSWORD=strong_password_here
SECRET_KEY=random_secret_key_here
```

### **4. 방화벽 설정**

```powershell
# Windows 방화벽에서 포트 열기
New-NetFirewallRule -DisplayName "HR System - HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HR System - Apps" -Direction Inbound -Protocol TCP -LocalPort 8000-8504 -Action Allow
```

---

## 🐳 Docker로 배포

### **방법 1: Docker Compose (권장)**

```powershell
cd C:\hr_automation

# 이미지 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 상태 확인
docker-compose ps

# 중지
docker-compose down
```

### **방법 2: 개별 Docker 실행**

```powershell
# 통합 대시보드만 실행
docker build -t hr-dashboard ./0_통합_대시보드
docker run -d -p 8000:8000 -v ${PWD}/hr_master.db:/app/hr_master.db hr-dashboard

# 나머지 앱들도 동일하게...
```

---

## 🌐 접속 방법

### **Windows 홈서버에서**
```
http://localhost
http://localhost:8000  (통합 대시보드)
http://localhost:8501  (출산육아)
http://localhost:8502  (연말정산)
http://localhost:8503  (재택근무)
http://localhost:8504  (정부지원금)
```

### **회사 내부 네트워크에서**
```
http://192.168.0.XXX
http://192.168.0.XXX:8000
```

### **외부 인터넷에서 (DDNS 설정 후)**
```
https://your-domain.ddns.net
```

---

## 🔧 문제 해결

### Q1. Docker 컨테이너가 시작되지 않아요

```powershell
# 로그 확인
docker-compose logs dashboard

# 재시작
docker-compose restart dashboard

# 완전 재빌드
docker-compose down
docker-compose up -d --build --force-recreate
```

### Q2. 포트 충돌 오류

```powershell
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료 (PID 확인 후)
taskkill /PID [PID번호] /F
```

### Q3. DB 파일을 찾을 수 없어요

```powershell
# DB 파일 확인
ls hr_master.db

# 없으면 초기화
python scripts/init_system.py
```

### Q4. 외부에서 접속이 안돼요

1. **공유기 설정**:
   - 포트포워딩: 외부 80 → 내부 192.168.0.XXX:80
   - DMZ 호스트 설정 (선택)

2. **DDNS 설정**:
   - No-IP: https://www.noip.com/
   - DuckDNS: https://www.duckdns.org/

3. **방화벽 확인**:
   - Windows Defender 방화벽 규칙 확인
   - 공유기 방화벽 설정 확인

---

## 📊 모니터링

### **Docker 상태 확인**

```powershell
# 실행 중인 컨테이너
docker ps

# 리소스 사용량
docker stats

# 특정 컨테이너 로그
docker logs -f hr-dashboard
```

### **시스템 로그**

```powershell
# 시스템 로그 확인
sqlite3 hr_master.db "SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 20;"
```

---

## 🔄 업데이트

### **새 버전 배포**

```powershell
cd C:\hr_automation

# Git에서 최신 코드 받기
git pull origin main

# 컨테이너 재빌드
docker-compose down
docker-compose up -d --build

# DB 마이그레이션 (필요시)
docker exec -it hr-dashboard python /app/../scripts/migrate_data.py
```

---

## 💾 백업

### **자동 백업 스크립트** (Windows Task Scheduler)

```powershell
# backup.ps1
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "C:\hr_backup\backup_$timestamp"

# 파일 백업
Copy-Item -Path "C:\hr_automation" -Destination $backupPath -Recurse

# DB 백업
Copy-Item -Path "C:\hr_automation\hr_master.db" -Destination "$backupPath\hr_master.db"

# 오래된 백업 삭제 (30일 이상)
Get-ChildItem "C:\hr_backup" -Directory | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Recurse -Force

Write-Host "✅ 백업 완료: $backupPath"
```

**Task Scheduler 등록**:
```
1. 작업 스케줄러 실행
2. "기본 작업 만들기"
3. 트리거: 매일 02:00 AM
4. 동작: backup.ps1 실행
```

---

## 🔐 보안 권장사항

1. **기본 비밀번호 변경**
   ```powershell
   # .env 파일에서 수정
   ADMIN_PASSWORD=strong_password_here
   ```

2. **HTTPS 설정** (Let's Encrypt)
   ```powershell
   # Certbot 설치 및 인증서 발급
   # nginx 설정에서 SSL 활성화
   ```

3. **IP 화이트리스트** (필요시)
   ```nginx
   # nginx.conf에 추가
   allow 192.168.0.0/24;
   deny all;
   ```

4. **VPN 사용** (강력 권장)
   - Tailscale (무료, 간편)
   - WireGuard
   - OpenVPN

---

## 📞 지원

**문제 발생 시**:
1. 로그 확인: `docker-compose logs`
2. GitHub Issues 생성
3. 백업에서 복원: `_backups/` 폴더 참조

---

**🎉 배포 완료!**

Windows 홈서버에서 안정적으로 운영하세요!
