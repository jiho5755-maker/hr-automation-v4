# 📘 Git 워크플로우 가이드

> **Mac 개발 → Git → Windows 홈서버 배포**

---

## 🎯 워크플로우 개요

```
Mac (Cursor IDE)
    ↓ 1. 코드 개발
    ↓ 2. 로컬 테스트
    ↓ 3. Git commit/push
    ↓
GitHub/GitLab
    ↓
Windows 홈서버
    ↓ 4. Git pull
    ↓ 5. Docker 재배포
    ✅ 완료
```

---

## 🔧 초기 설정 (1회만)

### Mac에서

#### 1. GitHub 저장소 생성

```bash
# 브라우저에서 GitHub.com 접속
# New Repository 클릭
# 저장소 이름: hr-automation-v4
# Private 선택 (보안)
# README 체크 해제 (이미 있음)
# Create repository
```

#### 2. Git 원격 저장소 연결

```bash
cd ~/Documents/인사팀_자동화_마스터

# GitHub 저장소 URL 연결
git remote add origin https://github.com/username/hr-automation-v4.git

# 또는 SSH (키 설정 필요)
git remote add origin git@github.com:username/hr-automation-v4.git

# 확인
git remote -v

# 첫 푸시
git push -u origin main
```

#### 3. Git 사용자 정보 설정 (아직 안 했다면)

```bash
git config --global user.name "장지호"
git config --global user.email "your.email@example.com"

# 확인
git config --global --list
```

---

### Windows 홈서버에서

#### 1. Git 설치 확인

```powershell
# PowerShell에서
git --version

# 없다면 설치
# https://git-scm.com/download/win
```

#### 2. 기존 폴더 백업

```powershell
cd C:\HomeServer

# 기존 폴더 백업
Rename-Item 인사팀_자동화_마스터 인사팀_자동화_마스터_old
```

#### 3. Git 저장소 클론

```powershell
# GitHub에서 클론
git clone https://github.com/username/hr-automation-v4.git 인사팀_자동화_마스터

cd 인사팀_자동화_마스터
```

#### 4. 환경 설정 복사

```powershell
# 기존 .env와 DB 파일 복사
copy ..\인사팀_자동화_마스터_old\.env .env
copy ..\인사팀_자동화_마스터_old\hr_master.db hr_master.db

# 확인
ls
```

#### 5. Docker 재배포

```powershell
.\docker-restart.ps1
```

---

## 📝 일상 개발 워크플로우

### Mac에서 (개발)

#### 1단계: 코드 수정

```bash
cd ~/Documents/인사팀_자동화_마스터

# Cursor IDE에서 코드 수정
# 예: 급여 계산 로직 추가
```

#### 2단계: 로컬 테스트

```bash
# Mac에서 테스트
./START_HERE.sh

# 브라우저에서 확인
# http://localhost:8000

# 문제 없으면 다음 단계
```

#### 3단계: Git 커밋

```bash
# 변경사항 확인
git status

# 변경 파일 추가
git add .

# 또는 특정 파일만
git add 5_급여관리_자동화/calculator.py

# 커밋 (의미 있는 메시지)
git commit -m "급여 계산 로직 추가

- 기본급 계산 함수 구현
- 4대보험 자동 계산
- 소득세 간이세액표 적용"

# 확인
git log --oneline -1
```

#### 4단계: GitHub에 푸시

```bash
# 푸시
git push origin main

# 또는 (main 브랜치 기본 설정 시)
git push

# 성공 메시지 확인
```

---

### Windows 홈서버에서 (배포)

#### 방법 1: 자동 스크립트 (권장) 🚀

```powershell
cd C:\HomeServer\인사팀_자동화_마스터

# 원클릭 배포
.\git-deploy.ps1

# 끝! (자동으로 pull + docker restart + 브라우저 열기)
```

#### 방법 2: 수동 배포

```powershell
cd C:\HomeServer\인사팀_자동화_마스터

# 1. 최신 코드 가져오기
git pull origin main

# 2. Docker 재배포
.\docker-restart.ps1

# 3. 확인
start http://localhost
```

---

## 🌿 브랜치 전략 (선택사항)

### 간단한 전략 (1인 개발)

```bash
# main 브랜치만 사용
# Mac에서 개발 → 테스트 → push → Windows pull
```

### 고급 전략 (팀 개발)

```bash
# main: 안정 버전 (Windows 홈서버)
# develop: 개발 버전 (Mac 테스트)
# feature/*: 기능 개발

# 새 기능 개발
git checkout -b feature/payroll-improvement
# ... 개발 ...
git push origin feature/payroll-improvement

# 개발 완료 후 merge
git checkout main
git merge feature/payroll-improvement
git push origin main

# Windows에서 배포
.\git-deploy.ps1
```

---

## 📊 자주 사용하는 Git 명령어

### 상태 확인

```bash
# 현재 상태
git status

# 변경사항 확인
git diff

# 커밋 히스토리
git log --oneline -10

# 특정 파일 히스토리
git log --follow -- 0_통합_대시보드/app.py
```

### 변경사항 되돌리기

```bash
# 파일 수정 취소 (커밋 전)
git checkout -- 파일명

# 스테이징 취소
git reset HEAD 파일명

# 마지막 커밋 취소 (로컬만)
git reset --soft HEAD~1

# 특정 커밋으로 되돌리기
git revert <commit-hash>
```

### 동기화

```bash
# 원격 저장소 상태 확인
git fetch origin

# 원격과 로컬 차이 확인
git log HEAD..origin/main --oneline

# 원격 변경사항 가져오기
git pull origin main
```

---

## 🚨 문제 해결

### 충돌 발생 시

#### Mac에서:

```bash
# 1. 원격 변경사항 확인
git fetch origin

# 2. Merge 시도
git merge origin/main

# 3. 충돌 파일 확인
git status

# 4. 충돌 해결 (Cursor IDE에서)
# <<<<<<< HEAD
# 내 변경사항
# =======
# 원격 변경사항
# >>>>>>> origin/main

# 5. 해결 후 커밋
git add .
git commit -m "Merge conflict resolved"
git push
```

#### Windows에서:

```bash
# 로컬 변경사항 임시 저장
git stash

# Pull
git pull origin main

# 임시 저장 복원
git stash pop

# 충돌 해결 후
git add .
git commit -m "Conflict resolved"
```

### .env 파일 실수로 커밋한 경우

```bash
# Git 히스토리에서 제거
git rm --cached .env

# .gitignore에 추가 (이미 있어야 함)
echo ".env" >> .gitignore

# 커밋
git commit -m "Remove .env from tracking"
git push
```

### 큰 파일 (DB) 커밋 방지

```bash
# .gitignore 확인
cat .gitignore | grep "\.db"

# 이미 추적 중이면 제거
git rm --cached *.db
git commit -m "Remove database files from tracking"
```

---

## 💡 팁과 모범 사례

### 커밋 메시지 작성법

**좋은 예:**
```
급여 계산 로직 개선

- 2026년 최저임금 반영
- 4대보험률 업데이트
- 소득세 계산 버그 수정
```

**나쁜 예:**
```
수정
fix
급여관리 작업
```

### 커밋 주기

```
✅ 기능 단위로 커밋
✅ 테스트 통과 후 커밋
✅ 하루 작업 끝에 커밋
❌ 너무 큰 변경사항 한번에 커밋
❌ 동작 안 하는 코드 커밋
```

### 브랜치 네이밍

```
feature/payroll-calculation   # 기능 개발
bugfix/login-error            # 버그 수정
hotfix/critical-security      # 긴급 수정
improve/ui-design             # 개선
```

---

## 📋 체크리스트

### Mac에서 개발 완료 후

- [ ] 로컬 테스트 완료 (`./START_HERE.sh`)
- [ ] 모든 기능 정상 작동 확인
- [ ] 의미 있는 커밋 메시지 작성
- [ ] `.env` 파일 제외 확인
- [ ] `git push` 완료
- [ ] Windows 팀에 배포 요청

### Windows에서 배포 전

- [ ] 현재 서비스 정상 작동 중
- [ ] 백업 완료 (자동)
- [ ] `.env` 파일 백업 확인
- [ ] `hr_master.db` 백업 확인
- [ ] `git pull` 또는 `.\git-deploy.ps1` 실행
- [ ] 배포 후 접속 테스트

---

## 🎯 빠른 참조

### Mac 개발자용

```bash
# 일상 워크플로우
git status              # 상태 확인
git add .              # 변경사항 추가
git commit -m "메시지"  # 커밋
git push               # 푸시
```

### Windows 운영자용

```powershell
# 배포
.\git-deploy.ps1       # 원클릭 배포

# 상태 확인
.\docker-status.ps1    # Docker 상태
git log -1             # 최신 커밋 확인
```

---

## 🔗 유용한 링크

- Git 공식 문서: https://git-scm.com/doc
- GitHub 가이드: https://guides.github.com/
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf

---

## 🎉 완료!

이제 전문적인 Git 워크플로우로 개발하고 배포할 수 있습니다!

**Mac에서 개발 → GitHub → Windows 배포** 🚀
