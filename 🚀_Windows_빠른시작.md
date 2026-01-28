# 🚀 Windows 홈서버 빠른 시작 (30초)

**Windows 관리자용 치트시트**

---

## 🔧 최초 1회 설정

### 1. Git 설치 확인

```powershell
git --version
```

없으면: https://git-scm.com/download/win

---

### 2. 기존 폴더 백업

```powershell
cd C:\HomeServer
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Rename-Item "인사팀_자동화_마스터" "인사팀_자동화_마스터_backup_$date"
```

---

### 3. GitHub Clone

```powershell
git clone https://github.com/jiho5755-maker/hr-automation-v4.git 인사팀_자동화_마스터
```

**로그인:**
- Username: `jiho5755-maker`
- Password: `(Personal Access Token)`

---

### 4. 환경변수 복사

```powershell
cd C:\HomeServer
$backup = Get-ChildItem -Directory | Where-Object {$_.Name -like "*backup*"} | Select-Object -First 1
Copy-Item "$($backup.FullName)\.env" "인사팀_자동화_마스터\.env"
```

---

### 5. Docker 시작

```powershell
cd 인사팀_자동화_마스터
docker-compose down -v
docker-compose up -d
```

---

### 6. DB 초기화

```powershell
docker exec -it hr-dashboard python scripts/init_system.py
```

---

### 7. 접속 테스트

```
http://192.168.0.43
```

**로그인:**
- 아이디: `admin`
- 비밀번호: `admin123`

---

## 🔄 일상적인 배포 (10초)

### Mac에서 코드 푸시 받았을 때

```powershell
cd C:\HomeServer\인사팀_자동화_마스터
.\git-deploy.ps1
```

**끝!** 🎉

---

## 🚨 문제 해결 (1줄)

### 접속 안 됨

```powershell
cd C:\HomeServer\인사팀_자동화_마스터
docker-compose restart
```

### DB 오류

```powershell
docker-compose down -v && docker-compose up -d
docker exec -it hr-dashboard python scripts/init_system.py
```

### 완전 재시작

```powershell
.\docker-restart.ps1
```

---

## 📊 상태 확인

```powershell
# 컨테이너 상태
docker-compose ps

# 로그 보기
docker-compose logs -f

# 포트 확인
netstat -ano | findstr :80
```

---

## 🎯 핵심 명령어 3개

```powershell
# 1. 배포
.\git-deploy.ps1

# 2. 재시작
.\docker-restart.ps1

# 3. 상태 확인
.\docker-status.ps1
```

---

**끝! 이것만 알면 됩니다!** 🚀
