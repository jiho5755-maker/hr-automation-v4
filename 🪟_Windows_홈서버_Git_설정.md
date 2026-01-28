# 🪟 Windows 홈서버 Git 설정 가이드

**작성일:** 2026년 1월 28일  
**대상:** Windows 홈서버 관리자

---

## 🎯 목표

Mac에서 개발한 코드를 GitHub를 통해 Windows 홈서버로 자동 배포

```
Mac (개발) → GitHub → Windows (배포) → Docker (운영)
```

---

## 📋 사전 준비

### ✅ 확인할 것

- [ ] Windows PC에 Docker Desktop 설치됨
- [ ] Docker 서비스 실행 중
- [ ] 인터넷 연결 정상
- [ ] 관리자 권한 있음

---

## 🔧 Step 1: Git 설치 확인

### PowerShell 열기

1. **Windows 키** 누르기
2. "PowerShell" 입력
3. **우클릭 → 관리자 권한으로 실행**

### Git 버전 확인

```powershell
git --version
```

**정상 출력 예시:**
```
git version 2.43.0.windows.1
```

### Git이 없다면 설치

**다운로드:**
```
https://git-scm.com/download/win
```

**설치 옵션:**
- ✅ Git Bash Here
- ✅ Git GUI Here
- ✅ Use Git from the Windows Command Prompt
- ✅ Checkout Windows-style, commit Unix-style line endings

**설치 후 PowerShell 재시작!**

---

## 📂 Step 2: 기존 폴더 백업

### 현재 폴더 확인

```powershell
cd C:\HomeServer
ls
```

**예상 출력:**
```
인사팀_자동화_마스터
```

### 백업 생성

```powershell
# 날짜를 포함한 백업 폴더로 이름 변경
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Rename-Item "인사팀_자동화_마스터" "인사팀_자동화_마스터_backup_$date"
```

**확인:**
```powershell
ls
```

**예상 출력:**
```
인사팀_자동화_마스터_backup_20260128_213000
```

---

## 🔑 Step 3: GitHub 접근 설정

### Git 사용자 정보 설정

```powershell
# 이름 설정
git config --global user.name "장지호"

# 이메일 설정 (GitHub 계정 이메일)
git config --global user.email "jiho5755@example.com"

# 확인
git config --list
```

### GitHub Personal Access Token 준비

**Mac에서 사용한 Token을 그대로 사용!**

또는 새로 생성:
1. https://github.com/settings/tokens/new
2. Note: `windows-homeserver`
3. Expiration: `No expiration`
4. ✅ repo (전체 체크)
5. **Generate token** 클릭
6. 토큰 복사 (예: `ghp_xxxx...`)
7. 메모장에 임시 저장

---

## 📥 Step 4: GitHub에서 Clone

### Clone 실행

```powershell
cd C:\HomeServer

git clone https://github.com/jiho5755-maker/hr-automation-v4.git 인사팀_자동화_마스터
```

### GitHub 로그인

**Username 입력:**
```
jiho5755-maker
```

**Password 입력:**
```
(Personal Access Token 붙여넣기)
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Clone 진행 중...

**예상 출력:**
```
Cloning into '인사팀_자동화_마스터'...
remote: Enumerating objects: 165, done.
remote: Counting objects: 100% (165/165), done.
remote: Compressing objects: 100% (156/156), done.
remote: Total 165 (delta 25), reused 165 (delta 25), pack-reused 0
Receiving objects: 100% (165/165), 255.00 KiB | 1.50 MiB/s, done.
Resolving deltas: 100% (25/25), done.
```

**완료! ✅**

---

## 🔧 Step 5: 환경변수 복사

### .env 파일 복사

```powershell
# 백업 폴더에서 .env 파일 찾기
$backupFolder = Get-ChildItem -Directory | Where-Object {$_.Name -like "*backup*"} | Select-Object -First 1
$backupPath = "$($backupFolder.FullName)\.env"
$newPath = "C:\HomeServer\인사팀_자동화_마스터\.env"

# 복사
if (Test-Path $backupPath) {
    Copy-Item $backupPath $newPath
    Write-Host "✅ .env 파일 복사 완료!" -ForegroundColor Green
} else {
    Write-Host "⚠️ .env 파일이 없습니다. env.example.txt를 참고하여 생성하세요." -ForegroundColor Yellow
}
```

### .env 파일 확인

```powershell
cd C:\HomeServer\인사팀_자동화_마스터
cat .env
```

**필수 내용:**
```
# Docker 설정
HOST_IP=192.168.0.43
NGINX_PORT=80

# 보안 설정
SECRET_KEY=your-secret-key-here
```

없으면 생성:
```powershell
notepad .env
```

---

## 📦 Step 6: 데이터베이스 복사 (선택사항)

### 기존 DB 백업이 있다면

```powershell
# 백업 폴더에서 DB 복사
$backupFolder = Get-ChildItem -Directory | Where-Object {$_.Name -like "*backup*"} | Select-Object -First 1

# hr_master.db 복사
Copy-Item "$($backupFolder.FullName)\hr_master.db" "C:\HomeServer\인사팀_자동화_마스터\hr_master.db"

# work_logs.db 복사
Copy-Item "$($backupFolder.FullName)\3_재택근무_관리시스템\work_logs.db" "C:\HomeServer\인사팀_자동화_마스터\3_재택근무_관리시스템\work_logs.db"

Write-Host "✅ 데이터베이스 복사 완료!" -ForegroundColor Green
```

---

## 🐳 Step 7: Docker 재시작

### 기존 컨테이너 정리

```powershell
cd C:\HomeServer\인사팀_자동화_마스터

# 기존 컨테이너 정지 및 삭제
docker-compose down -v
```

### Docker 이미지 빌드 및 시작

```powershell
# 이미지 빌드 (최초 1회 또는 코드 변경 시)
docker-compose build --no-cache

# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 대시보드 준비 대기

**로그에서 이 메시지를 기다리세요:**
```
hr-dashboard  | You can now view your Streamlit app in your browser.
hr-dashboard  | URL: http://0.0.0.0:8000
```

**Ctrl + C** 로 로그 보기 종료

---

## 🔄 Step 8: 데이터베이스 초기화

### init_system.py 실행

```powershell
# 컨테이너 내부에서 스크립트 실행
docker exec -it hr-dashboard python scripts/init_system.py
```

**예상 출력:**
```
✅ 데이터베이스 초기화 완료
✅ 관리자 계정 생성 완료
   - 아이디: admin
   - 비밀번호: admin123
✅ 회사 정보 생성 완료
```

---

## ✅ Step 9: 접속 테스트

### 웹 브라우저 열기

```
http://192.168.0.43
```

또는

```
http://localhost
```

### 로그인

- **아이디:** `admin`
- **비밀번호:** `admin123`

### 확인사항

- ✅ 대시보드 페이지 로드됨
- ✅ 사이드바 메뉴 정상 작동
- ✅ 직원 관리 페이지 접근 가능
- ✅ 오류 없음

---

## 🚀 Step 10: 자동 배포 스크립트 테스트

### git-deploy.ps1 실행

```powershell
cd C:\HomeServer\인사팀_자동화_마스터
.\git-deploy.ps1
```

**스크립트가 자동으로:**
1. ✅ Docker 컨테이너 정지
2. ✅ GitHub에서 최신 코드 받기 (`git pull`)
3. ✅ Docker 이미지 재빌드
4. ✅ 컨테이너 시작
5. ✅ 상태 확인

**예상 출력:**
```
=================================
  🔄 HR 자동화 시스템 배포 시작
=================================

1. Docker 컨테이너 정지 중...
✅ 컨테이너 정지 완료

2. Git에서 최신 코드 받기...
Already up to date.
✅ 코드 업데이트 완료

3. Docker 이미지 빌드...
✅ 이미지 빌드 완료

4. Docker 컨테이너 시작...
✅ 컨테이너 시작 완료

5. 상태 확인...
NAME           STATUS
hr-dashboard   Up
hr-nginx       Up

=================================
  ✅ 배포 완료!
=================================

접속: http://192.168.0.43
```

---

## 🧪 Step 11: 전체 워크플로우 테스트

### Mac에서 변경사항 만들기

```bash
cd ~/Documents/인사팀_자동화_마스터

# 테스트 파일 생성
echo "# 배포 테스트 $(date)" >> DEPLOY_TEST.md

# Git 커밋 및 푸시
git add DEPLOY_TEST.md
git commit -m "🧪 배포 파이프라인 테스트"
git push
```

### Windows에서 배포

```powershell
cd C:\HomeServer\인사팀_자동화_마스터
.\git-deploy.ps1
```

### 확인

브라우저 새로고침 → 변경사항 반영 확인!

---

## 🔧 문제 해결

### 문제 1: "git: command not found"

**해결:**
```powershell
# Git 설치 여부 확인
winget list --name Git

# 없으면 설치
winget install --id Git.Git -e --source winget

# PowerShell 재시작
```

---

### 문제 2: "Permission denied (publickey)"

**해결:** Personal Access Token 사용
```powershell
# HTTPS URL 사용 (SSH 아님!)
git clone https://github.com/jiho5755-maker/hr-automation-v4.git
```

---

### 문제 3: "docker: command not found"

**해결:**
1. Docker Desktop 설치 확인
2. Docker Desktop 실행
3. PowerShell 재시작
4. 다시 시도

---

### 문제 4: "Port 80 is already in use"

**해결:**
```powershell
# 포트를 사용 중인 프로세스 찾기
netstat -ano | findstr :80

# PID 확인 후 종료
Stop-Process -Id <PID> -Force

# 또는 다른 포트 사용 (docker-compose.yml 수정)
```

---

### 문제 5: "Database is locked"

**해결:**
```powershell
# 모든 컨테이너 정지
docker-compose down -v

# 볼륨까지 완전 삭제
docker volume prune

# 재시작
docker-compose up -d

# DB 재초기화
docker exec -it hr-dashboard python scripts/init_system.py
```

---

## 📚 유용한 명령어

### Git 관련

```powershell
# 현재 상태 확인
git status

# 최신 코드 받기
git pull

# 변경사항 취소
git reset --hard origin/main

# 브랜치 확인
git branch

# 커밋 히스토리
git log --oneline -10
```

### Docker 관련

```powershell
# 컨테이너 상태
docker-compose ps

# 로그 보기
docker-compose logs -f

# 컨테이너 재시작
docker-compose restart

# 완전 재시작
docker-compose down -v && docker-compose up -d

# 리소스 정리
docker system prune -a
```

### 시스템 관리

```powershell
# 포트 사용 확인
netstat -ano | findstr :80
netstat -ano | findstr :8000

# Docker 상태
docker info

# 디스크 사용량
docker system df
```

---

## 🎯 일상적인 배포 프로세스

### Mac 개발자가 코드 푸시했을 때

**Windows 관리자가 할 일:**

```powershell
# 1. 프로젝트 폴더로 이동
cd C:\HomeServer\인사팀_자동화_마스터

# 2. 배포 스크립트 실행
.\git-deploy.ps1

# 3. 브라우저 확인
# http://192.168.0.43
```

**끝! 3단계만!** 🚀

---

## 🔄 자동화 (선택사항)

### 작업 스케줄러로 자동 배포

#### 1. 배포 스크립트 경로 복사

```
C:\HomeServer\인사팀_자동화_마스터\git-deploy.ps1
```

#### 2. 작업 스케줄러 열기

- Windows 키
- "작업 스케줄러" 검색
- 실행

#### 3. 작업 만들기

- **이름:** `HR 자동화 자동 배포`
- **트리거:** 매일 새벽 3시
- **작업:** PowerShell
- **인수:** `-File "C:\HomeServer\인사팀_자동화_마스터\git-deploy.ps1"`
- **권한:** 가장 높은 수준의 권한으로 실행

---

## ✅ 완료 체크리스트

### 초기 설정

- [ ] Git 설치 완료
- [ ] Git 사용자 정보 설정
- [ ] 기존 폴더 백업
- [ ] GitHub Clone 완료
- [ ] .env 파일 복사
- [ ] Docker 이미지 빌드
- [ ] 컨테이너 시작
- [ ] DB 초기화
- [ ] 접속 테스트 성공

### 배포 파이프라인

- [ ] git-deploy.ps1 테스트 성공
- [ ] Mac → GitHub → Windows 워크플로우 확인
- [ ] 전체 배포 프로세스 검증

---

## 🎊 완료!

이제 Windows 홈서버가 GitHub와 완벽하게 연동되었습니다!

**Mac에서 개발 → GitHub 푸시 → Windows에서 git-deploy.ps1 실행 → 배포 완료!** 🚀

---

## 📞 다음 단계

1. **Mac 개발자에게 알리기**
   - GitHub 푸시 후 알려달라고 요청

2. **정기 점검**
   - 주 1회 `git-deploy.ps1` 실행
   - Docker 로그 확인
   - 디스크 공간 확인

3. **백업 설정**
   - 매일 자동 백업 설정
   - `backup-daily.ps1` 실행

---

**설정 완료!** 🎉
