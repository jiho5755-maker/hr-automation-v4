# 🚀 HR 자동화 v4.0 - Git 워크플로우 빠른 시작

> **Mac 개발 → GitHub → Windows 홈서버 배포**

---

## ✅ 현재 상태

```
✅ Git 저장소 초기화 완료
✅ .gitignore 설정 완료
✅ 첫 커밋 완료 (2개 커밋)
✅ Windows 자동 배포 스크립트 준비
✅ 완벽한 워크플로우 가이드 작성
```

---

## 🎯 다음 단계 (GitHub 연결)

### 1️⃣ GitHub 저장소 생성

1. 브라우저에서 https://github.com 접속
2. 로그인
3. 우측 상단 `+` → `New repository` 클릭
4. 저장소 설정:
   - Repository name: `hr-automation-v4`
   - Description: `HR 자동화 시스템 v4.0 통합 대시보드`
   - **Private** 선택 (보안상 중요!)
   - README 체크 **해제** (이미 있음)
5. `Create repository` 클릭

---

### 2️⃣ Mac에서 GitHub 연결

터미널 열기 (⌘ + Space → "터미널"):

```bash
cd ~/Documents/인사팀_자동화_마스터

# GitHub 저장소 URL 연결 (username을 실제 이름으로 변경!)
git remote add origin https://github.com/username/hr-automation-v4.git

# 확인
git remote -v

# GitHub에 푸시
git push -u origin main
```

**GitHub 로그인 요청 시:**
- Username: GitHub 사용자명
- Password: **Personal Access Token** (비밀번호 아님!)

**Personal Access Token 생성:**
1. GitHub.com → 우측 상단 프로필 → Settings
2. Developer settings (왼쪽 맨 아래)
3. Personal access tokens → Tokens (classic)
4. Generate new token (classic)
5. Note: `hr-automation`
6. Expiration: `No expiration`
7. Select scopes: `repo` 체크
8. Generate token
9. **토큰 복사** (다시 볼 수 없음!)
10. 터미널에서 Password에 붙여넣기

---

### 3️⃣ Windows 홈서버 설정

#### PowerShell 관리자 권한으로:

```powershell
# 1. 현재 폴더 백업
cd C:\HomeServer
Rename-Item 인사팀_자동화_마스터 인사팀_자동화_마스터_old

# 2. GitHub에서 클론
git clone https://github.com/username/hr-automation-v4.git 인사팀_자동화_마스터

# 3. 폴더 이동
cd 인사팀_자동화_마스터

# 4. 환경 설정 복사
copy ..\인사팀_자동화_마스터_old\.env .env
copy ..\인사팀_자동화_마스터_old\hr_master.db hr_master.db

# 5. Docker 재배포
.\docker-restart.ps1

# 6. 접속 확인
start http://localhost
```

---

## 🎊 완료! 이제 사용법

### Mac에서 개발

```bash
cd ~/Documents/인사팀_자동화_마스터

# 1. 코드 수정 (Cursor IDE)

# 2. 로컬 테스트
./START_HERE.sh

# 3. Git 커밋
git add .
git commit -m "급여 계산 로직 추가"

# 4. GitHub에 푸시
git push
```

### Windows에서 배포

```powershell
cd C:\HomeServer\인사팀_자동화_마스터

# 원클릭 배포 🚀
.\git-deploy.ps1

# 끝!
```

---

## 📚 추가 문서

- **📘_Git_워크플로우_가이드.md** - 완벽한 워크플로우 가이드
- **🪟_Windows_Docker_배포_가이드.md** - Windows 배포 상세 가이드
- **README_DOCKER.md** - Docker 빠른 시작

---

## 💡 핵심 명령어

### Mac (개발)
```bash
git status          # 상태 확인
git add .          # 변경사항 추가
git commit -m "메시지"  # 커밋
git push           # 푸시
```

### Windows (배포)
```powershell
.\git-deploy.ps1   # 자동 배포
.\docker-status.ps1  # 상태 확인
.\docker-logs.ps1    # 로그 확인
```

---

## 🎯 워크플로우 요약

```
Mac에서:
  코드 수정 → 테스트 → git commit → git push

Windows에서:
  .\git-deploy.ps1 실행 → 자동으로 pull + 재배포

끝!
```

---

**🚀 이제 전문적인 Git 워크플로우로 개발할 준비가 완료되었습니다!**
