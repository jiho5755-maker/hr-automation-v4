# 급여관리 자동화 시스템 - 제미나이 검토용 패키지

## 📦 포함된 파일

### 1. 급여관리 자동화 (5_급여관리_자동화/)
- app.py - 메인 애플리케이션
- calculator.py - 급여 계산 로직
- constants.py - 상수 정의
- database.py - 급여 관련 DB 함수
- Dockerfile - Docker 설정
- README.md - 설명서
- requirements.txt - 패키지 의존성

### 2. 공유 모듈 (shared/)
- database.py - 통합 데이터베이스 (직원 정보, 회사 정보 조회)
- design.py - 디자인 시스템
- utils.py - 공통 유틸리티 함수

### 3. 통합대시보드 - 급여 관련 (0_통합_대시보드/)
- app.py - 메인 앱 구조
- pages/4_💰_급여_정보_관리.py - 급여 정보 관리 페이지
- pages/0_📊_홈.py - 홈 페이지 (급여 통계 포함)
- requirements.txt - 의존성

### 4. 프로젝트 개요
- README.md - 전체 프로젝트 설명

## 🔗 주요 연동 관계

1. **통합대시보드 → 급여관리**
   - `4_💰_급여_정보_관리.py`에서 `5_급여관리_자동화/database.py`의 함수들을 직접 import
   - 급여 설정 정보를 입력/수정하는 인터페이스 제공

2. **급여관리 → 공유 모듈**
   - `shared/database.py`: 직원 정보, 회사 정보 조회
   - `shared/design.py`: 디자인 시스템 적용
   - `shared/utils.py`: 공통 유틸리티 함수

3. **데이터베이스**
   - 통합 DB: `hr_master.db` (프로젝트 루트)
   - 급여 관련 테이블: `payroll_settings`, `payroll_history`, `annual_leave`, `overtime_logs` 등

## 📋 검토 요청 사항

1. 코드 품질 및 구조
2. 급여 계산 로직의 정확성 (2026년 기준)
3. 데이터베이스 설계 및 연동
4. 통합대시보드와의 연동 방식
5. 에러 처리 및 예외 상황
6. 보안 및 데이터 무결성

## 🚀 실행 방법

```bash
# 급여관리 앱 실행
cd 5_급여관리_자동화
streamlit run app.py --server.port 8505

# 통합대시보드 실행
cd 0_통합_대시보드
streamlit run app.py --server.port 8500
```

## ⚠️ 주의사항

- 실제 데이터베이스 파일(`hr_master.db`)은 포함되지 않았습니다.
- 가상환경(`venv/`)은 포함되지 않았습니다.
- 실행을 위해서는 `requirements.txt`의 패키지들을 설치해야 합니다.
