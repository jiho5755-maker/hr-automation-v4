# 🔄 Mac → Windows 홈서버 전송 가이드

> **개발 Mac에서 Windows Docker 홈서버로 프로젝트 배포하기**

---

## 📋 전송 방법 (4가지)

### 방법 1: USB 드라이브 (가장 간단) 💾

#### Mac에서:

```bash
# 1. 프로젝트 압축
cd ~/Documents
zip -r 인사팀_자동화_마스터.zip 인사팀_자동화_마스터 \
  -x "*/.*" \
  -x "*/__pycache__/*" \
  -x "*/logs/*" \
  -x "*/*.db-shm" \
  -x "*/*.db-wal"

# 2. USB에 복사
cp 인사팀_자동화_마스터.zip /Volumes/USB드라이브명/
```

#### Windows에서:

```powershell
# 1. USB에서 복사
Copy-Item "D:\인사팀_자동화_마스터.zip" "C:\HomeServer\"

# 2. 압축 해제
cd C:\HomeServer
Expand-Archive -Path "인사팀_자동화_마스터.zip" -DestinationPath "."

# 3. 이동
cd 인사팀_자동화_마스터
```

---

### 방법 2: 네트워크 공유 폴더 (가장 빠름) 🌐

#### Windows에서 공유 폴더 설정:

```powershell
# 1. 폴더 생성
mkdir C:\HomeServer\Shared

# 2. 우클릭 → 속성 → 공유 → 고급 공유
# → "이 폴더 공유" 체크
# → 권한: Everyone - 모든 권한

# 3. 네트워크 경로 확인
\\192.168.0.100\Shared
```

#### Mac에서:

```bash
# 1. Finder → 이동 → 서버에 연결 (Cmd+K)
smb://192.168.0.100/Shared

# 2. 프로젝트 복사
cp -R ~/Documents/인사팀_자동화_마스터 /Volumes/Shared/
```

#### Windows에서:

```powershell
# 공유 폴더에서 작업 위치로 복사
Copy-Item -Recurse "C:\HomeServer\Shared\인사팀_자동화_마스터" "C:\HomeServer\"
```

---

### 방법 3: Git (버전 관리 가능) 📦

#### Mac에서:

```bash
cd ~/Documents/인사팀_자동화_마스터

# Git 초기화 (최초 1회)
git init
git add .
git commit -m "HR 자동화 v4.0 초기 커밋"

# GitHub/GitLab에 푸시
git remote add origin https://github.com/username/hr-automation.git
git push -u origin main
```

#### Windows에서:

```powershell
cd C:\HomeServer

# 클론
git clone https://github.com/username/hr-automation.git 인사팀_자동화_마스터
cd 인사팀_자동화_마스터

# 이후 업데이트
git pull
```

**장점:**
- ✅ 버전 관리
- ✅ 변경 이력 추적
- ✅ 롤백 가능
- ✅ 어디서든 접근

---

### 방법 4: SCP (SSH 사용 가능 시) 🔐

#### Windows에서 OpenSSH 서버 설정:

```powershell
# PowerShell 관리자 권한
# OpenSSH 서버 설치
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 서비스 시작
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 방화벽 규칙 (자동 생성됨)
```

#### Mac에서:

```bash
# 프로젝트 전송
cd ~/Documents
scp -r 인사팀_자동화_마스터 사용자명@192.168.0.100:/C:/HomeServer/

# 또는 rsync (증분 전송)
rsync -avz --progress 인사팀_자동화_마스터/ \
  사용자명@192.168.0.100:/C:/HomeServer/인사팀_자동화_마스터/
```

---

## 🎯 권장 워크플로우

### 개발 (Mac) → 배포 (Windows)

```bash
# ===== Mac에서 (개발) =====
cd ~/Documents/인사팀_자동화_마스터

# 1. 코드 수정

# 2. 테스트
./START_HERE.sh

# 3. Git 커밋
git add .
git commit -m "급여 계산 로직 개선"
git push
```

```powershell
# ===== Windows에서 (배포) =====
cd C:\HomeServer\인사팀_자동화_마스터

# 1. 최신 코드 받기
git pull

# 2. 재배포
.\docker-restart.ps1

# 끝!
```

---

## 📦 전송 시 제외할 파일

### 불필요한 파일 (용량 절약)

```
제외:
- _backups/           (백업 폴더)
- __pycache__/        (Python 캐시)
- *.pyc, *.pyo        (컴파일된 파일)
- .DS_Store           (Mac 메타데이터)
- logs/               (로그는 새로 생성)
- *.db-shm, *.db-wal  (DB 임시 파일)
- .git/               (Git 히스토리, 필요시만)

반드시 포함:
- hr_master.db        (통합 데이터베이스)
- .env (또는 env.example.txt)
- shared/             (공유 모듈)
- 0_통합_대시보드/     (메인 앱)
- docker-compose.yml
- nginx/
- scripts/
- *.ps1               (PowerShell 스크립트)
```

### 압축 시 제외 (Mac)

```bash
zip -r 인사팀_자동화_마스터.zip 인사팀_자동화_마스터 \
  -x "*/.*" \
  -x "*/__pycache__/*" \
  -x "*/logs/*" \
  -x "*/*.db-shm" \
  -x "*/*.db-wal" \
  -x "*/_backups/*" \
  -x "*/node_modules/*"
```

---

## ✅ 전송 후 체크리스트

Windows 홈서버에서 확인:

- [ ] 프로젝트 파일 모두 복사되었는지 확인
- [ ] `hr_master.db` 파일 존재 확인
- [ ] `.env` 파일 생성 및 설정
- [ ] PowerShell 스크립트 실행 권한 확인
- [ ] Docker Desktop 실행 중
- [ ] `.\docker-start.ps1` 실행
- [ ] `http://localhost` 접속 확인
- [ ] admin 계정 로그인 확인
- [ ] 각 페이지 정상 작동 확인

---

## 🔄 업데이트 워크플로우

### 일반 업데이트 (코드만)

```powershell
# Windows 홈서버에서
git pull  # 또는 파일 재복사
.\docker-restart.ps1
```

### 메이저 업데이트 (DB 스키마 변경 등)

```powershell
# 1. 백업!
.\backup-daily.ps1

# 2. 중지
docker-compose down

# 3. 업데이트
git pull

# 4. DB 마이그레이션 (필요시)
python scripts/migrate_data.py

# 5. 재빌드
docker-compose up -d --build

# 6. 확인
.\docker-status.ps1
```

---

## 🎯 빠른 참조

### 기본 명령어

```powershell
.\docker-start.ps1      # 시작
.\docker-stop.ps1       # 중지
.\docker-restart.ps1    # 재시작
.\docker-status.ps1     # 상태 확인
.\docker-logs.ps1       # 로그 확인
```

### 접속 URL

```
로컬:           http://localhost
네트워크:       http://192.168.0.100
외부 (DDNS):    http://mycompany.ddns.net
```

### 로그인

```
관리자: admin / admin1234
테스트: test / test1234
```

---

## 🆘 긴급 연락

문제 발생 시:

1. **로그 확인:** `.\docker-logs.ps1 -Follow`
2. **상태 확인:** `.\docker-status.ps1`
3. **재시작:** `.\docker-restart.ps1`
4. **강제 재빌드:** `docker-compose up -d --build --force-recreate`

---

**🎉 이제 Mac에서 개발하고 Windows 홈서버에 배포하는 완벽한 환경이 준비되었습니다!**
