# Task List: 인사팀 자동화 시스템 통합

## Quick Reference (Extracted from PRD & Blueprint)

### Ownership Rules
*Source: PRD §7 + Blueprint §2.1*

| Artifact | Created By | App's Role | DO NOT |
|----------|------------|------------|--------|
| hr_master.db | App | Create + Manage | DO NOT depend on external DB server |
| employees 테이블 레코드 | App | Create + Update + Delete | DO NOT use JSON files |
| work_logs 테이블 레코드 | App | Create | DO NOT manually insert |
| payroll_history 테이블 레코드 | App | Create | DO NOT keep calculation results only in memory |
| 급여명세서 PDF | App | Create + Deliver | DO NOT save to server disk |
| 급여대장 Excel | App | Create + Deliver | DO NOT save to server disk |
| 출산육아 정부 서식 PDF | App | Create + Deliver | DO NOT save to server disk |
| system_logs 테이블 레코드 | App | Create | DO NOT skip logging |
| session_state | App | Create + Maintain + Destroy | DO NOT leak sessions |

### State Variables
*Source: PRD §8 + Blueprint §3*

| State Variable | Initial Value | Created When | Cleared When | Persists Across |
|----------------|---------------|--------------|--------------|------------------|
| session_state.logged_in | False | 로그인 성공 | 로그아웃 또는 세션 종료 | 페이지 전환 |
| session_state.user | None | 로그인 성공 | 로그아웃 | 페이지 전환 |
| session_state.current_employee | None | 직원 선택 | 다른 직원 선택 또는 로그아웃 | 페이지 전환 (유지) |
| session_state.payroll_temp_data | {} | 급여 계산 시작 | 급여 저장 완료 또는 페이지 이탈 | 급여관리 페이지 내만 |
| session_state.show_employee_form | False | "새 직원 추가/수정" 클릭 | 저장/취소 클릭 | 직원 관리 페이지 내만 |
| session_state.current_page | "대시보드" | 앱 시작 | 페이지 전환 시 새 페이지명으로 | 페이지 전환 |

### Critical Boundaries
*Source: Blueprint §2.3*

- ❌ DO NOT: 직원 데이터를 JSON 파일(employees_data.json)에 저장. hr_master.db만 사용
- ❌ DO NOT: 다운로드 파일(PDF, Excel)을 서버 디스크에 저장. 메모리(BytesIO)에서 생성 후 즉시 다운로드
- ❌ DO NOT: 중요 액션(로그인, 데이터 변경, 계산)에서 system_logs 기록 생략
- ❌ DO NOT: 로그아웃 시 session_state 일부만 제거. st.session_state.clear() 호출 필수
- ❌ DO NOT: 급여 계산 결과를 메모리에만 유지. payroll_history 테이블에 저장 필수
- ✅ MUST: 모든 직원 CRUD 작업은 shared.database 모듈의 API 사용 (get_all_employees, add_employee, update_employee, delete_employee)
- ✅ MUST: 급여 계산 → 명세서 생성 파이프라인 끊김 없이 연결 (calculate_payroll → format_payslip → generate_pdf)
- ✅ MUST: 페이지 전환 시 공통 상태(logged_in, user, current_employee)는 유지, 페이지별 임시 상태는 초기화

### User Visibility Rules
*Source: PRD §6*

| User Action | User Sees | User Does NOT See | Timing |
|-------------|-----------|-------------------|--------|
| 로그인 성공 | "환영합니다, [사용자명]님!" 토스트 | DB 쿼리, 세션 생성 과정 | < 1초 |
| 사이드바 메뉴 선택 | 선택 메뉴 하이라이트 + 페이지 로드 | session_state 업데이트, 리렌더링 | < 1초 |
| 직원 정보 저장 | "✅ 저장 완료!" 토스트 | SQL INSERT 쿼리, DB 커밋 | < 1초 |
| 직원 선택 (다른 모듈) | 선택 직원의 모든 정보 자동 로드 | DB 조회, session_state 동기화 | < 1초 |
| 급여 계산 시작 | "계산 중..." 로딩 스피너 | 4대보험, 소득세 개별 계산 로직 | 1-3초 |
| 급여 계산 완료 | "✅ 계산 완료!" + 결과 요약 | DB 저장, 명세서 데이터 준비 | 즉시 |
| 급여명세서 미리보기 | 명세서 전체 내용 표시 (모든 항목 포함) | 명세서 포맷팅, PDF 렌더링 준비 | < 1초 |
| 급여명세서 PDF 다운로드 | "PDF 생성 중..." → "✅ 다운로드 완료!" | PDF 라이브러리 실행, 파일 생성 | 2-5초 |

---

## Requirements Traceability

**Every requirement MUST map to at least one task. Nothing should be lost.**

| Source | Requirement | Mapped To Task |
|--------|-------------|----------------|
| PRD §5.1.1 | 사이드바 메뉴 표시 | Task 1.2 |
| PRD §5.1.2 | 메뉴 선택 시 1초 이내 페이지 전환 | Task 1.3 |
| PRD §5.1.3 | 현재 선택 메뉴 강조 | Task 1.3 |
| PRD §5.1.4 | 미로그인 사용자 리다이렉트 | Task 1.3 |
| PRD §5.2.1 | 직원 목록 테이블 표시 | Task 2.2 |
| PRD §5.2.2 | "새 직원 추가" 버튼 | Task 2.2 |
| PRD §5.2.3 | 필수 정보 입력 | Task 2.3 |
| PRD §5.2.4 | 선택 정보 입력 | Task 2.3 |
| PRD §5.2.5 | hr_master.db 저장 + 토스트 | Task 2.4 |
| PRD §5.2.6 | 직원 정보 수정 시 모든 모듈 반영 | Task 2.4, Task 6.1 |
| PRD §5.2.7 | 직원 삭제 시 소프트 삭제 | Task 2.5 |
| PRD §5.3.1~§5.3.5 | 홈 대시보드 기능 | Task 1.4 |
| PRD §5.4.1~§5.4.5 | 출산육아 모듈 통합 | Task 3.3, Task 3.4 |
| PRD §5.5.1~§5.5.4 | 출산육아 데이터 마이그레이션 | Task 3.1, Task 3.2 |
| PRD §5.6.1~§5.6.4 | 재택근무 모듈 통합 | Task 4.1, Task 4.2 |
| PRD §5.7.1~§5.7.3 | 급여관리 모듈 통합 | Task 5.4 |
| PRD §5.8.1~§5.8.7 | 급여 계산 → 명세서 자동 반영 | Task 5.2, Task 5.5, Task 5.6, Task 5.7 |
| PRD §5.9.1~§5.9.6 | 급여 계산 로직 검증 | Task 5.1 |
| PRD §5.10.1~§5.10.6 | 급여관리 UI/UX 개선 | Task 5.8 |
| PRD §5.11.1~§5.11.5 | 실시간 데이터 동기화 | Task 6.1 |
| PRD §5.12.1~§5.12.5 | 출산육아 검증 | Task 3.4 |
| PRD §5.13.1~§5.13.5 | 재택근무 검증 | Task 4.2 |
| PRD §5.14.1~§5.14.10 | 급여관리 검증 (Critical) | Task 5.9 |
| PRD §6.1 V-1~V-12 | 사용자 가시성 규칙 | 모든 UI 관련 Task (User Sees 필드) |
| PRD §6.2 T-1~T-10 | 타이밍 및 피드백 | 모든 UI 관련 Task (Timing 주석) |
| PRD §7.1 O-1~O-11 | 아티팩트 소유권 | Quick Reference + 모든 생성 Task (Ownership 필드) |
| PRD §7.3 | 파생 소유권 규칙 | Quick Reference (DO NOTs) |
| PRD §8.1 SI-1~SI-4 | 상태 격리 | Task 6.2, 모든 상태 관련 Task (State Change 필드) |
| PRD §8.2 SL-1~SL-9 | 상태 생명주기 | Quick Reference + 모든 상태 관련 Task (State Change 필드) |
| Blueprint §2.1 | 아티팩트 소유권 강제 | Quick Reference (Ownership Rules) |
| Blueprint §2.3 | 경계 규칙 | Quick Reference (DO NOTs) |
| Blueprint §3.1~§3.7 | 상태 전환 | 모든 Parent Task Pre/Post 조건 |
| Blueprint §4.1~§4.3 | 통합 와이어링 | IC-1, IC-2, IC-3 |
| Blueprint §8 | 구현 단계 | Task 그룹핑 (Phase 0~7) |

---

## Overview

이 작업 목록은 인사팀 자동화 시스템의 6개 독립 모듈을 단일 포트 8000의 통합 대시보드로 완전히 통합하는 프로젝트를 위한 것입니다. 현재 각각 다른 포트(8501-8505)에서 실행되는 Streamlit 앱들을 Multipage App 패턴으로 재구성하고, 중앙 데이터베이스(hr_master.db)를 통한 실시간 데이터 동기화를 구현합니다. 특히 급여관리 모듈은 계산 결과가 명세서에 자동으로 반영되도록 전면 개선됩니다. 모든 작업은 PRD §1-§10와 Technical Blueprint §1-§11에 명시된 요구사항을 1:1로 구현합니다. 단계별 통합과 실제 데이터 기반 검증을 통해 안정적인 통합을 보장합니다.

## Relevant Files

- `0_통합_대시보드/app.py` – 메인 앱 진입점, st.navigation 설정
- `0_통합_대시보드/pages/home.py` – 홈 대시보드 페이지
- `0_통합_대시보드/pages/employee_management.py` – 직원 관리 페이지 (신규)
- `0_통합_대시보드/pages/maternity.py` – 출산육아 페이지 (리팩토링)
- `0_통합_대시보드/pages/remote_work.py` – 재택근무 페이지 (리팩토링)
- `0_통합_대시보드/pages/payroll.py` – 급여관리 페이지 (리팩토링 + 개선)
- `0_통합_대시보드/pages/settings.py` – 설정 페이지
- `shared/database.py` – 통합 DB API (기존, 수정 없음)
- `shared/auth.py` – 인증 모듈 (기존, 수정 없음)
- `shared/design.py` – 디자인 시스템 (기존, 수정 없음)
- `shared/utils.py` – 유틸리티 (기존, 수정 없음)
- `1_출산육아_자동화/engine.py` – 출산육아 비즈니스 로직
- `1_출산육아_자동화/pdf_generator.py` – 출산육아 PDF 생성
- `1_출산육아_자동화/employees_data.json` – 마이그레이션 후 삭제 예정
- `3_재택근무_관리시스템/app.py` – 재택근무 로직 (리팩토링 예정)
- `5_급여관리_자동화/calculator.py` – 급여 계산 로직 (개선 필요)
- `5_급여관리_자동화/database.py` – 급여 특화 테이블 관리
- `scripts/migrate_json_to_db.py` – 마이그레이션 스크립트 (신규)
- `scripts/verify_migration.py` – 마이그레이션 검증 (신규)
- `START_HERE.sh` – 시스템 시작 스크립트 (수정 필요)
- `tests/test_payroll_calculator.py` – 급여 계산 단위 테스트 (신규)
- `tests/test_integration.py` – 통합 테스트 (신규)

---

## Tasks

### 0.0 준비 작업 (Phase 0)

**Pre-condition:** 프로젝트가 안정적으로 실행 중

#### Sub-Tasks:

- [ ] 0.1 Review context: PRD 전체, Blueprint 전체
  - **Relevant Sections:** PRD §1 (Overview), Blueprint §1.7 (Improvements)
  - **Key Decisions:** 단계별 통합(출산육아 → 재택 → 급여), 실제 데이터 검증, JSON 제거
  - **Watch Out For:** 급여관리는 가장 신중하게, 실제 급여 데이터 검증 필수

- [ ] 0.2 프로젝트 전체 백업 생성
  - **Input:** 현재 프로젝트 전체
  - **Output:** `_backups/backup_[YYYYMMDD_HHMMSS]_pre_integration/` 폴더
  - **Implements:** Blueprint §11.5 (Rollback Strategy)

- [ ] 0.3 Git 브랜치 생성
  - **Input:** main 브랜치
  - **Output:** `feature/hr-integration` 브랜치
  - **Implements:** Best Practice

- [ ] 0.4 개발 환경 확인
  - **Input:** N/A
  - **Output:** Python 3.8+, Streamlit 1.32.0+, 필수 패키지 설치 확인
  - **Implements:** Blueprint §11.1 (Environment Requirements)

**Post-condition:** 백업 완료, Git 브랜치 생성, 개발 환경 준비 완료

**Verification:**
- [ ] _backups/ 폴더에 최신 백업 존재
- [ ] `git branch`로 feature/hr-integration 브랜치 확인
- [ ] `python3 --version` → 3.8 이상
- [ ] `pip3 list | grep streamlit` → 1.32.0 이상

---

### 1.0 통합 프레임워크 구축 (Phase 1)

**Pre-condition:** 준비 작업 완료

#### Sub-Tasks:

- [ ] 1.1 Review context: PRD §5.1, Blueprint §1.2
  - **Relevant Sections:** PRD §5.1 (사이드바 네비게이션), Blueprint §1.2 (Target Architecture)
  - **Key Decisions:** Streamlit Multipage App 패턴, st.Page + st.navigation, 단일 포트 8000
  - **Watch Out For:** st.set_page_config은 메인 앱에서만 호출, 페이지 함수는 config 호출하지 않음

- [ ] 1.2 메인 앱 리팩토링 (`0_통합_대시보드/app.py`)
  - **Input:** 기존 app.py (링크만 제공)
  - **Output:** st.Page + st.navigation 설정된 메인 앱
  - **State Change:** session_state 초기화 함수 추가 (SL-1~SL-9)
  - **User Sees:** 로그인 페이지 → 로그인 성공 → 사이드바 메뉴
  - **Implements:** PRD §5.1.1, Blueprint §5.1

- [ ] 1.3 사이드바 네비게이션 구현
  - **Input:** 로그인 상태 (session_state.logged_in)
  - **Output:** 사이드바 메뉴 (대시보드, 직원 관리, 출산육아, 재택근무, 급여관리, 설정, 로그아웃)
  - **State Change:** session_state.current_page 업데이트
  - **User Sees:** 선택 메뉴 하이라이트, 페이지 전환 < 1초
  - **Implements:** PRD §5.1.2, §5.1.3, §5.1.4

- [ ] 1.4 홈 대시보드 페이지 구현 (`pages/home.py`)
  - **Input:** session_state.logged_in, session_state.user
  - **Output:** 전체 인사 현황 메트릭 표시
  - **User Sees:** 등록 직원 수, 특별 관리 직원, 근무 로그, 예상 지원금, 회사 정보, 알림
  - **Implements:** PRD §5.3.1~§5.3.5, Blueprint §5.1

- [ ] 1.5 설정 페이지 구현 (`pages/settings.py`)
  - **Input:** session_state.user
  - **Output:** 시스템 정보 표시 (버전, DB 위치, 통계)
  - **Implements:** Blueprint §5.1

**Post-condition:** 포트 8000에서 로그인 → 사이드바 → 홈 대시보드 표시

**Verification:**
- [ ] START_HERE.sh 실행 → http://localhost:8000 접속 가능
- [ ] 로그인 (admin/admin1234) → "환영합니다, admin님!" 토스트 확인 (PRD §5.1.4)
- [ ] 사이드바에 모든 메뉴 표시 확인 (PRD §5.1.1)
- [ ] 메뉴 선택 → 1초 이내 페이지 전환 확인 (PRD §5.1.2)
- [ ] 홈 대시보드에 메트릭 카드 4개 표시 확인 (PRD §5.3.1)

---

### 2.0 통합 직원 관리 페이지 구축 (Phase 2)

**Pre-condition:** 통합 프레임워크 구축 완료

#### Sub-Tasks:

- [ ] 2.1 Review context: PRD §5.2, Blueprint §2.1, §3.3
  - **Relevant Sections:** PRD §5.2 (통합 직원 관리), Blueprint §2.1 (O-2 직원 레코드), §3.3 (직원 정보 저장 상태 전환)
  - **Key Decisions:** hr_master.db만 사용, JSON 파일 금지, 통합 CRUD 페이지
  - **Watch Out For:** 직원 정보 저장 시 반드시 add_system_log() 호출, 모든 모듈에 즉시 반영 확인

- [ ] 2.2 직원 관리 페이지 UI 구현 (`pages/employee_management.py`)
  - **Input:** N/A
  - **Output:** 직원 목록 테이블, 검색/필터링, 추가/수정/삭제 버튼
  - **User Sees:** 직원 목록 (이름, 부서, 직급, 입사일, 상태)
  - **Implements:** PRD §5.2.1, §5.2.2

- [ ] 2.3 직원 입력 폼 구현
  - **Input:** session_state.show_employee_form = True
  - **Output:** 입력 폼 (필수: 이름, 부서, 직급, 입사일 | 선택: 주민등록번호, 성별, 나이, 이메일, 전화번호, 급여 정보, 특수 상태)
  - **State Change:** session_state.show_employee_form = True
  - **User Sees:** 입력 폼 표시
  - **Implements:** PRD §5.2.3, §5.2.4

- [ ] 2.4 직원 CRUD 로직 연결
  - **Input:** 입력 폼 데이터
  - **Output:** hr_master.db에 저장, session_state.current_employee 업데이트
  - **Ownership:** App creates employees 테이블 레코드
  - **State Change:** session_state.current_employee = 저장된 직원 정보, session_state.show_employee_form = False
  - **User Sees:** "✅ 저장 완료!" 토스트 (< 1초)
  - **Integration:** shared.database.add_employee() 또는 update_employee() 호출
  - **Implements:** PRD §5.2.5, §5.2.6, Blueprint §3.3, IC-1

- [ ] 2.5 직원 삭제 기능 구현
  - **Input:** 선택된 직원 emp_id
  - **Output:** is_active = 0 (소프트 삭제)
  - **Ownership:** App updates employees 테이블
  - **User Sees:** 확인 다이얼로그 → "✅ 삭제 완료!"
  - **Integration:** shared.database.delete_employee(emp_id, hard_delete=False)
  - **Implements:** PRD §5.2.7

**Post-condition:** 직원 추가/수정/삭제 → DB 반영 → session_state.current_employee 업데이트

**Verification:**
- [ ] "새 직원 추가" 클릭 → 입력 폼 표시 (PRD §5.2.2)
- [ ] 필수 정보 입력 후 저장 → "✅ 저장 완료!" 토스트 (PRD §5.2.5)
- [ ] `sqlite3 hr_master.db "SELECT * FROM employees WHERE name='테스트직원'"` → 레코드 확인
- [ ] 직원 목록에 새 직원 표시 확인 (PRD §5.2.5)
- [ ] 직원 수정 → 모든 페이지에서 최신 정보 표시 확인 (PRD §5.2.6) → 이후 Task 6.1에서 재확인

---

### 3.0 출산육아 모듈 통합 (Phase 3)

**Pre-condition:** 통합 직원 관리 페이지 완료

#### Sub-Tasks:

- [ ] 3.1 Review context: PRD §5.4, §5.5, Blueprint §2.3, §6.2
  - **Relevant Sections:** PRD §5.4 (출산육아 통합), §5.5 (마이그레이션), Blueprint §2.3 (JSON 금지 규칙), §6.2 (Session State Schema)
  - **Key Decisions:** employees_data.json → hr_master.db 마이그레이션, JSON 파일 의존성 완전 제거
  - **Watch Out For:** 마이그레이션 전 백업 필수, 마이그레이션 후 데이터 검증 필수 (건수 + 내용)

- [ ] 3.2 마이그레이션 스크립트 작성 (`scripts/migrate_json_to_db.py`)
  - **Input:** `1_출산육아_자동화/employees_data.json`
  - **Output:** hr_master.db employees 테이블에 INSERT, 마이그레이션 로그
  - **Ownership:** App creates employees 레코드 (from JSON)
  - **User Sees:** "마이그레이션 진행 중... [진행률]" → "✅ [N]건 마이그레이션 완료!"
  - **Integration:** shared.database.add_employee() 반복 호출
  - **Implements:** PRD §5.5.1, §5.5.4, Blueprint §5.3

- [ ] 3.3 마이그레이션 실행 및 검증 (`scripts/verify_migration.py`)
  - **Input:** hr_master.db (마이그레이션 후)
  - **Output:** 검증 리포트 (건수 비교, 샘플 데이터 비교)
  - **User Sees:** "검증 중..." → "✅ 검증 완료: [N]건 일치"
  - **Implements:** PRD §5.5.2, §5.5.3, NFR-8

- [ ] 3.4 출산육아 페이지 리팩토링 (`pages/maternity.py`)
  - **Input:** `1_출산육아_자동화/app.py` (기존 코드)
  - **Output:** `0_통합_대시보드/pages/maternity.py` (페이지 함수)
  - **State Change:** session_state.current_employee 사용
  - **User Sees:** 직원 선택 드롭다운 → 모든 정보 자동 로드
  - **Integration:** shared.database.get_all_employees(), get_employee_by_id()
  - **Implements:** PRD §5.4.1~§5.4.5, Blueprint §5.1

- [ ] 3.5 출산육아 기능 테스트
  - **Input:** 마이그레이션된 직원 데이터
  - **Output:** 재택근무 로그, 지원금 계산, 정부 서식 PDF
  - **User Sees:** 계산 결과, PDF 다운로드
  - **Implements:** PRD §5.4.4, §5.12.1~§5.12.5

**Post-condition:** 출산육아 페이지에서 직원 선택 → 모든 정보 자동 로드 → 모든 기능 정상 작동

**Verification:**
- [ ] `python3 scripts/migrate_json_to_db.py` 실행 → 성공 메시지 (PRD §5.5.1)
- [ ] `python3 scripts/verify_migration.py` 실행 → 100% 일치 (PRD §5.5.2, §5.5.3)
- [ ] 출산육아 페이지 이동 → 직원 드롭다운에 모든 직원 표시 (PRD §5.4.2)
- [ ] 직원 선택 → 모든 정보 자동 로드 확인 (PRD §5.4.3)
- [ ] 재택근무 로그 생성 → 정상 작동 (PRD §5.12.2)
- [ ] 지원금 계산 → 정확한 금액 (PRD §5.12.3)
- [ ] 정부 서식 PDF 생성 → 다운로드 성공 (PRD §5.12.4)

---

### 4.0 재택근무 모듈 통합 (Phase 4)

**Pre-condition:** 출산육아 모듈 통합 완료

#### Sub-Tasks:

- [ ] 4.1 Review context: PRD §5.6, Blueprint §5.1, §6.1
  - **Relevant Sections:** PRD §5.6 (재택근무 통합), Blueprint §5.1 (Components), §6.1 (work_logs 테이블)
  - **Key Decisions:** 재택근무는 이미 hr_master.db 사용, 큰 변경 없음
  - **Watch Out For:** work_logs 테이블 저장 확인, 통합 대시보드에서 조회 가능 확인

- [ ] 4.2 재택근무 페이지 리팩토링 (`pages/remote_work.py`)
  - **Input:** `3_재택근무_관리시스템/app.py` (기존 코드)
  - **Output:** `0_통합_대시보드/pages/remote_work.py` (페이지 함수)
  - **State Change:** session_state.current_employee 사용
  - **User Sees:** 직원 선택 → 일정 관리, 근무 기록, 월간 리포트
  - **Integration:** shared.database.get_employee_by_id()
  - **Implements:** PRD §5.6.1~§5.6.4, Blueprint §5.1

- [ ] 4.3 재택근무 기능 테스트
  - **Input:** 선택된 직원
  - **Output:** 일정 등록, 근무 기록 저장, 리포트 생성
  - **Ownership:** App creates work_logs 레코드
  - **User Sees:** "✅ 근무 로그 저장 완료!"
  - **Implements:** PRD §5.13.1~§5.13.5

**Post-condition:** 재택근무 페이지에서 직원 선택 → 일정 관리 → 근무 기록 → 리포트 생성

**Verification:**
- [ ] 재택근무 페이지 이동 → 직원 선택 → 정보 자동 로드 (PRD §5.6.2)
- [ ] 일정 등록 → 정상 작동 (PRD §5.13.2)
- [ ] 근무 기록 추적 → work_logs 테이블 저장 확인 (PRD §5.6.4, §5.13.3)
- [ ] 월간 리포트 생성 → 다운로드 성공 (PRD §5.13.4)

---

### 5.0 급여관리 모듈 통합 및 전면 개선 (Phase 5 - Critical)

**Pre-condition:** 재택근무 모듈 통합 완료

#### Sub-Tasks:

- [ ] 5.1 Review context: PRD §5.7~§5.10, §5.14, Blueprint §4.2, §7.2
  - **Relevant Sections:** PRD §5.8 (급여 → 명세서 자동 반영 Critical), §5.9 (계산 로직 검증), §5.10 (UI/UX), §5.14 (실제 데이터 검증), Blueprint §4.2 (Integration Wiring), §7.2 (Payroll Data Flow Contract)
  - **Key Decisions:** 급여 계산 → 명세서 완전 자동화 파이프라인, 2026년 법령 기준, 실제 급여 데이터 3건 검증
  - **Watch Out For:** 계산 결과 → payroll_temp_data → 명세서 연결 끊김 없이, 모든 항목 100% 반영, 실수령액 100% 일치

- [ ] 5.2 급여 계산 로직 개선 (`5_급여관리_자동화/calculator.py`)
  - **Input:** employee 정보, year_month
  - **Output:** payroll_data 표준화된 딕셔너리 (Blueprint §7.2 구조)
  - **State Change:** N/A (순수 계산 함수)
  - **Implements:** PRD §5.8.1~§5.8.5, §5.9.1~§5.9.6, Blueprint §7.2
  - **상세:**
    - [ ] 5.2.1 calculate_payroll() 메서드 반환값 표준화
      - { basic_salary, allowances:{overtime, night, holiday, annual_leave}, deductions:{national_pension, health_insurance, long_term_care, employment_insurance, income_tax, local_tax}, total_payment, total_deduction, net_payment }
    - [ ] 5.2.2 2026년 국민연금 요율 4.5% 확인
    - [ ] 5.2.3 2026년 건강보험 요율 3.545% + 장기요양 12.81% 확인
    - [ ] 5.2.4 2026년 고용보험 요율 0.9% 확인
    - [ ] 5.2.5 2026년 소득세율 구간 확인
    - [ ] 5.2.6 최저임금 10,030원 검증 로직 확인

- [ ] 5.3 명세서 생성 로직 재구축
  - **Input:** payroll_data (표준화된 구조)
  - **Output:** payslip_data (명세서 표시용 구조)
  - **Implements:** PRD §5.8.6, Blueprint §7.2
  - **상세:**
    - [ ] 5.3.1 format_payslip(payroll_data) 함수 작성
    - [ ] 5.3.2 모든 지급 항목 포함 확인 (기본급, 모든 수당)
    - [ ] 5.3.3 모든 공제 항목 포함 확인 (4대보험, 소득세, 지방소득세)
    - [ ] 5.3.4 실수령액 계산 검증 (total_payment - total_deduction)

- [ ] 5.4 PDF 생성 로직 개선
  - **Input:** payslip_data (명세서 데이터)
  - **Output:** BytesIO PDF
  - **Ownership:** App creates PDF in memory (DO NOT save to disk)
  - **User Sees:** "PDF 생성 중..." → "✅ 다운로드 완료!"
  - **Implements:** PRD §5.8.7, Blueprint §2.1 O-5, §2.3

- [ ] 5.5 급여관리 페이지 리팩토링 (`pages/payroll.py`)
  - **Input:** `5_급여관리_자동화/app.py` (기존 코드)
  - **Output:** `0_통합_대시보드/pages/payroll.py` (페이지 함수)
  - **State Change:** session_state.current_employee 사용, session_state.payroll_temp_data 관리
  - **User Sees:** 급여 계산 → 명세서 미리보기 → PDF 다운로드 플로우
  - **Implements:** PRD §5.7.1~§5.7.3, Blueprint §5.1

- [ ] 5.6 급여 계산 → 명세서 파이프라인 연결
  - **Input:** 직원 정보, 년월
  - **Output:** 계산 완료 → payroll_temp_data 저장 → 명세서 생성 준비
  - **Ownership:** App creates payroll_history 레코드
  - **State Change:** session_state.payroll_temp_data = payroll_data
  - **User Sees:** "계산 중..." → "✅ 계산 완료! 실수령액: ₩X,XXX,XXX"
  - **Integration:** PayrollCalculator.calculate_payroll(), save_payroll_history()
  - **Implements:** PRD §5.8.1~§5.8.5, Blueprint §4.2, IC-2

- [ ] 5.7 명세서 미리보기 기능 구현
  - **Input:** session_state.payroll_temp_data
  - **Output:** 명세서 HTML 렌더링
  - **User Sees:** 명세서 전체 내용 표시 (모든 항목 자동 반영됨!)
  - **Implements:** PRD §5.8.6, Blueprint §4.2

- [ ] 5.8 PDF 다운로드 기능 구현
  - **Input:** payslip_data
  - **Output:** PDF 파일 다운로드
  - **Ownership:** App creates PDF in memory
  - **User Sees:** "PDF 생성 중..." → "✅ 다운로드 완료!" (2-5초)
  - **Implements:** PRD §5.8.7, Blueprint §4.2

- [ ] 5.9 급여관리 UI/UX 개선
  - **Input:** N/A
  - **Output:** 개선된 UI (플로우 시각화, 안내 문구, 로딩 인디케이터, 오류 메시지)
  - **User Sees:** 계산 플로우 시각화, 명확한 안내
  - **Implements:** PRD §5.10.1~§5.10.6

- [ ] 5.10 실제 급여 데이터 검증 (Critical)
  - **Input:** 실제 지급한 급여 명세서 3건
  - **Output:** 검증 리포트 (계산 결과 vs 실제 급여 비교)
  - **User Sees:** 검증 결과 리포트
  - **Implements:** PRD §5.14.1~§5.14.10, Blueprint §10.3
  - **상세:**
    - [ ] 5.10.1 직원 A 데이터 입력 (기본급 3,000,000원, 연장수당 500,000원)
    - [ ] 5.10.2 급여 계산 실행
    - [ ] 5.10.3 국민연금 계산 결과 vs 실제 급여 비교 → 100% 일치 확인
    - [ ] 5.10.4 건강보험 계산 결과 vs 실제 급여 비교 → 100% 일치 확인
    - [ ] 5.10.5 고용보험 계산 결과 vs 실제 급여 비교 → 100% 일치 확인
    - [ ] 5.10.6 소득세/지방소득세 계산 결과 vs 실제 급여 비교 → 100% 일치 확인
    - [ ] 5.10.7 시간외 수당 계산 결과 vs 실제 급여 비교 → 100% 일치 확인
    - [ ] 5.10.8 실수령액 계산 결과 vs 실제 급여 비교 → 100% 일치 확인
    - [ ] 5.10.9 명세서 PDF 생성 → 모든 항목 정확히 표시 확인
    - [ ] 5.10.10 직원 B, C에 대해 5.10.1~5.10.9 반복
    - [ ] 5.10.11 불일치 발견 시 → 원인 분석 → 코드 수정 → 재검증

**Post-condition:** 급여 계산 → 명세서 자동 반영 100%, 실제 급여 데이터 3건 100% 일치

**Verification:**
- [ ] 급여관리 페이지 이동 → 직원 선택 → 정보 자동 로드 (PRD §5.7.2)
- [ ] "급여 계산" 버튼 클릭 → "계산 중..." → "✅ 계산 완료!" (PRD §5.8.1~§5.8.5)
- [ ] 계산 결과 요약 표시 확인 (지급액, 공제액, 실수령액) (PRD §5.8.5)
- [ ] "명세서 미리보기" 클릭 → 모든 항목 자동 반영 확인 (PRD §5.8.6)
- [ ] PDF 다운로드 → 파일 열어서 내용 확인 (PRD §5.8.7)
- [ ] 실제 급여 데이터 3건 → 100% 일치 확인 (PRD §5.14.1~§5.14.10)

---

### 6.0 데이터 동기화 및 통합 테스트 (Phase 6)

**Pre-condition:** 모든 모듈 통합 완료

#### Sub-Tasks:

- [ ] 6.1 Review context: PRD §5.11, Blueprint §3.6
  - **Relevant Sections:** PRD §5.11 (실시간 데이터 동기화), Blueprint §3.6 (페이지 전환 상태 전환)
  - **Key Decisions:** 페이지 전환 시 공통 상태 유지, 임시 상태 초기화
  - **Watch Out For:** current_employee는 페이지 전환 시 유지, payroll_temp_data는 급여관리 페이지만

- [ ] 6.2 실시간 데이터 동기화 검증
  - **Input:** 직원 정보 수정
  - **Output:** 모든 페이지에서 최신 정보 표시
  - **State Change:** session_state.current_employee 업데이트
  - **User Sees:** 페이지 새로고침 없이 즉시 반영
  - **Implements:** PRD §5.11.1~§5.11.5, Blueprint §4.3, IC-3

- [ ] 6.3 session_state 생명주기 테스트
  - **Input:** 로그인 → 작업 → 페이지 전환 → 로그아웃
  - **Output:** 상태 생성 → 유지 → 초기화 확인
  - **State Change:** 모든 SL-1~SL-9 상태 확인
  - **Implements:** PRD §8.2, Blueprint §3.1~§3.7

- [ ] 6.4 통합 테스트 시나리오 실행
  - **Input:** 여러 시나리오
  - **Output:** 모든 시나리오 통과
  - **Implements:** Blueprint §10.2
  - **상세:**
    - [ ] 6.4.1 시나리오 1: 신규 직원 추가 → 모든 모듈에서 사용
    - [ ] 6.4.2 시나리오 2: 기존 직원 정보 수정 → 모든 모듈에서 즉시 반영
    - [ ] 6.4.3 시나리오 3: 급여 계산 → 명세서 생성 → PDF 다운로드 (End-to-End)
    - [ ] 6.4.4 시나리오 4: 여러 사용자 동시 접속 (세션 격리 확인)

**Post-condition:** 모든 데이터 동기화 정상 작동, 통합 테스트 100% 통과

**Verification:**
- [ ] 직원 관리에서 직원 정보 수정 → 출산육아 페이지 이동 → 최신 정보 표시 (PRD §5.11.2)
- [ ] 재택근무 페이지 이동 → 최신 정보 표시 (PRD §5.11.3)
- [ ] 급여관리 페이지 이동 → 최신 정보 표시 (PRD §5.11.4)
- [ ] 페이지 새로고침 없이 즉시 반영 확인 (PRD §5.11.5)
- [ ] 로그인 → 상태 생성 확인 (SL-1, SL-2)
- [ ] 페이지 전환 → 공통 상태 유지 확인 (SL-3)
- [ ] 로그아웃 → 모든 상태 제거 확인 (st.session_state.clear())
- [ ] 통합 테스트 시나리오 모두 통과 (Blueprint §10.2)

---

### 7.0 포트 통합 및 배포 준비 (Phase 7)

**Pre-condition:** 모든 모듈 통합 및 테스트 완료

#### Sub-Tasks:

- [ ] 7.1 Review context: PRD §4.1 FR-1, Blueprint §11
  - **Relevant Sections:** PRD FR-1 (단일 포트 통합), Blueprint §11 (Deployment)
  - **Key Decisions:** 포트 8000만 실행, 다른 포트 실행 스크립트 deprecated
  - **Watch Out For:** START_HERE.sh만 수정, 기존 독립 실행 스크립트는 보존 (롤백 대비)

- [ ] 7.2 START_HERE.sh 수정
  - **Input:** 기존 START_HERE.sh (포트 8000 실행)
  - **Output:** 업데이트된 스크립트 (Blueprint §11.4 버전)
  - **User Sees:** "통합 대시보드 시작!" + 새로운 기능 안내
  - **Implements:** Blueprint §11.4

- [ ] 7.3 기존 독립 실행 스크립트 정리
  - **Input:** 각 모듈의 🚀_실행하기.command
  - **Output:** deprecated 표시 또는 주석 처리
  - **Implements:** Blueprint §11 (Note)

- [ ] 7.4 README.md 업데이트
  - **Input:** 기존 README.md
  - **Output:** 업데이트된 문서 (포트 8000만 사용 안내)
  - **Implements:** Best Practice

- [ ] 7.5 최종 테스트
  - **Input:** START_HERE.sh
  - **Output:** 포트 8000에서만 접속 가능 확인
  - **User Sees:** 통합 대시보드 정상 실행
  - **Implements:** PRD M-1

**Post-condition:** START_HERE.sh → 포트 8000만 실행 → 모든 기능 접근 가능

**Verification:**
- [ ] START_HERE.sh 실행 → http://localhost:8000 접속 (PRD M-1)
- [ ] http://localhost:8501 접속 → 연결 불가 (PRD M-1)
- [ ] http://localhost:8502 접속 → 연결 불가 (PRD M-1)
- [ ] http://localhost:8503 접속 → 연결 불가 (PRD M-1)
- [ ] http://localhost:8504 접속 → 연결 불가 (PRD M-1)
- [ ] http://localhost:8505 접속 → 연결 불가 (PRD M-1)
- [ ] 포트 8000에서 모든 기능 접근 가능 (PRD M-1)

---

## Integration-Critical Tasks
*Source: Blueprint §4 - Integration Wiring*

These tasks have specific wiring requirements that must be followed exactly. Deviating from the specified sequence can cause bugs.

### IC-1: 직원 정보 저장 플로우
*Maps to: Blueprint §4.1*

**Critical Sequence:**
```
1. validate_employee_data(employee_form_data) // REQUIRED: 필수 필드 검증 (이름, 부서, 직급)
2. add_employee(employee_data) OR update_employee(emp_id, employee_data) // Creates: employees 테이블 레코드
3. add_system_log(username, "직원 추가", "employee_management") // Creates: system_logs 레코드
4. session_state.current_employee = get_employee_by_id(employee_id) // Updates: SL-3 state
5. session_state.show_employee_form = False // Clears: SL-8 state
6. show_success("✅ 저장 완료!") // Displays: V-3 visibility
```

**Ownership Rules (from PRD §7):**
- employees 테이블 레코드는 App이 생성 — External System이 생성하지 않음
- system_logs 레코드는 App이 생성 — 모든 중요 액션마다 필수

**User Visibility (from PRD §6):**
- User sees: "✅ 저장 완료!" 토스트, 직원 목록에 새 직원 추가
- User does NOT see: SQL INSERT 쿼리, 데이터베이스 커밋 과정

**State Changes (from Blueprint §3):**
- Before: current_employee=None (또는 이전 직원), show_employee_form=True
- After: current_employee={새 직원 정보}, show_employee_form=False

**Common Mistakes to Avoid (from Blueprint §2.3):**
- ❌ add_system_log() 생략: 감사 추적 불가능, 문제 발생 시 원인 파악 어려움
- ❌ session_state.current_employee 업데이트 안 함: 다른 페이지에서 선택 직원 잘못 표시
- ❌ show_employee_form을 False로 안 바꿈: 폼이 계속 표시되어 UX 혼란

**Verification:**
- [ ] `sqlite3 hr_master.db "SELECT * FROM employees WHERE name='[직원명]'"` → 레코드 존재
- [ ] `sqlite3 hr_master.db "SELECT * FROM system_logs WHERE action LIKE '%직원 추가%' ORDER BY timestamp DESC LIMIT 1"` → 로그 존재
- [ ] 다른 페이지(출산육아, 재택근무, 급여관리) 이동 → 새 직원 드롭다운에 표시

**Maps to Task:** 2.4

---

### IC-2: 급여 계산 → 명세서 생성 파이프라인
*Maps to: Blueprint §4.2*

**Critical Sequence:**
```
1. validate_employee_payroll_data(employee) // REQUIRED: 급여 정보 존재 확인
2. payroll_calculator.calculate_payroll(employee, year_month) // Returns: payroll_data
   ├─ calculate_national_pension() → 4.5%
   ├─ calculate_health_insurance() → 3.545% + 장기요양 12.81%
   ├─ calculate_employment_insurance() → 0.9%
   ├─ calculate_income_tax() → 누진세율
   ├─ calculate_overtime_allowances()
   └─ RETURN: payroll_data {basic, allowances, deductions, totals, net}
3. save_payroll_history(employee_id, year_month, payroll_data) // Creates: payroll_history 레코드
4. session_state.payroll_temp_data = payroll_data // Updates: SL-7 state
5. show_success(f"✅ 계산 완료! 실수령액: {format_currency(net_payment)}") // Displays: V-7

WHEN USER CLICKS "명세서 미리보기":
6. payslip_data = format_payslip(payroll_data) // Transforms: 모든 항목 100% 반영
7. display_payslip_preview(payslip_data) // Displays: V-8

WHEN USER CLICKS "PDF 다운로드":
8. pdf_bytes = generate_payslip_pdf(payslip_data) // Creates: BytesIO PDF in memory
9. st.download_button("다운로드", pdf_bytes, file_name="...") // Delivers: V-9
```

**Ownership Rules (from PRD §7):**
- payroll_history 레코드는 App이 생성 — 계산 결과를 메모리에만 유지하면 안 됨
- 급여명세서 PDF는 App이 메모리(BytesIO)에서 생성 — 서버 디스크에 저장하면 안 됨

**User Visibility (from PRD §6):**
- User sees (V-6): "계산 중..." 로딩 스피너 (1-3초)
- User sees (V-7): "✅ 계산 완료!" + 결과 요약 (지급액, 공제액, 실수령액)
- User sees (V-8): 명세서 전체 내용 (모든 지급/공제 항목 자동 반영됨!)
- User sees (V-9): "PDF 생성 중..." → "✅ 다운로드 완료!" (2-5초)
- User does NOT see: 4대보험/소득세 개별 계산 로직, DB 저장, PDF 라이브러리 실행

**State Changes (from Blueprint §3):**
- Before: payroll_temp_data={} (empty)
- After: payroll_temp_data={전체 계산 결과}

**Common Mistakes to Avoid (from Blueprint §2.3):**
- ❌ save_payroll_history() 생략: 계산 결과가 DB에 저장 안 되어 급여대장에 누락
- ❌ payroll_data 구조가 표준화 안 됨: format_payslip()에서 항목 누락 가능
- ❌ format_payslip()에서 일부 항목만 반영: 명세서 불완전, 수동 재입력 필요
- ❌ PDF를 서버 디스크에 저장: 디스크 공간 낭비, 보안 위험

**Verification:**
- [ ] 급여 계산 실행 → payroll_temp_data에 모든 키 존재 (basic_salary, allowances, deductions, net_payment)
- [ ] `sqlite3 hr_master.db "SELECT * FROM payroll_history ORDER BY id DESC LIMIT 1"` → 최신 계산 결과 저장 확인
- [ ] 명세서 미리보기 → 모든 지급 항목 표시 (기본급, 연장수당, 야간수당, 휴일수당, 연차수당)
- [ ] 명세서 미리보기 → 모든 공제 항목 표시 (국민연금, 건강보험, 장기요양, 고용보험, 소득세, 지방소득세)
- [ ] 명세서 미리보기 → 실수령액 = 지급액 - 공제액 확인
- [ ] PDF 다운로드 → 파일 열기 → 모든 항목 포함 확인
- [ ] 실제 급여 데이터 3건 → 100% 일치 (PRD §5.14)

**Maps to Task:** 5.6, 5.7, 5.8

---

### IC-3: 페이지 전환 및 데이터 동기화
*Maps to: Blueprint §4.3*

**Critical Sequence:**
```
1. verify_logged_in() // REQUIRED: SI-2 로그인 확인
2. session_state.current_page = page_name // Updates: SL-9
3. clear_page_specific_state(previous_page) // Clears: SI-3 임시 상태
   // Keeps: SL-1 (logged_in), SL-2 (user), SL-3 (current_employee)
4. st.navigation() or st.rerun() // Transitions to new page

IN NEW PAGE: init_page()
5. IF current_employee in session_state:
   ├─ employee = get_employee_by_id(current_employee['emp_id']) // Refreshes from DB
   └─ display_employee_info(employee) // Displays: V-5
   ELSE:
   └─ show_info("직원을 선택해주세요")
```

**Ownership Rules (from PRD §7):**
- session_state는 App이 생성/관리 — 페이지 전환 시 공통 상태는 유지, 임시 상태는 제거

**User Visibility (from PRD §6):**
- User sees (V-2): 선택 메뉴 하이라이트 + 페이지 로드 (< 1초)
- User sees (V-5): 선택 직원의 모든 정보 자동 로드
- User does NOT see: session_state 업데이트, 페이지 리렌더링, DB 조회

**State Changes (from Blueprint §3):**
- Before: current_page="이전 페이지", payroll_temp_data={계산 결과}
- After: current_page="새 페이지", payroll_temp_data={} (cleared), current_employee=유지

**Common Mistakes to Avoid (from Blueprint §2.3):**
- ❌ 페이지 전환 시 current_employee도 제거: 다른 페이지에서 직원 재선택 필요 (UX 저하)
- ❌ 페이지별 임시 상태 안 지움: payroll_temp_data가 다른 페이지에 영향 줌
- ❌ DB에서 최신 정보 안 가져옴: 다른 곳에서 수정된 정보 반영 안 됨

**Verification:**
- [ ] 직원 관리에서 직원 정보 수정 → 출산육아 페이지 이동 → 최신 정보 표시
- [ ] 재택근무 페이지 이동 → 최신 정보 표시
- [ ] 급여관리 페이지 이동 → 최신 정보 표시
- [ ] 급여관리에서 payroll_temp_data 생성 → 다른 페이지 이동 → payroll_temp_data 초기화 확인
- [ ] 페이지 전환 < 1초 (PRD NFR-1)

**Maps to Task:** 6.2

---

## Validation Checklist

Before implementation, verify 1:1 mapping is complete:

### PRD Coverage
- [ ] Every §5 acceptance criterion has a corresponding subtask (§5.1.1~§5.14.10 → Tasks)
- [ ] Every §6 visibility rule has "User Sees" in relevant subtask (V-1~V-12 → User Sees 필드)
- [ ] Every §7 ownership rule is in Quick Reference AND relevant subtask "Ownership" field (O-1~O-11 → Quick Reference + Tasks)
- [ ] Every §8 state requirement has "State Change" in relevant subtask (SL-1~SL-9, SI-1~SI-4 → State Change 필드)

### Blueprint Coverage
- [ ] Every §2 boundary rule is in Critical Boundaries AND enforced in tasks (§2.3 → DO NOTs + Tasks)
- [ ] Every §3 state transition maps to Pre/Post conditions (§3.1~§3.7 → Parent Task Pre/Post)
- [ ] Every §4 integration wiring maps to an Integration-Critical Task (§4.1~§4.3 → IC-1~IC-3)

### Task Quality
- [ ] First subtask of each parent references relevant docs (All Parent Tasks have X.1 Review context)
- [ ] All subtasks are specific and actionable (not vague)
- [ ] All "Implements" fields trace back to PRD/Blueprint sections

---

## Notes

### Development Standards
- 모든 Python 코드는 PEP 8 준수
- 함수/클래스에 docstring 작성 (Google 스타일)
- 타입 힌팅 사용 (Python 3.8+)

### Testing Commands
```bash
# 단위 테스트 실행
pytest tests/test_payroll_calculator.py -v

# 통합 테스트 실행
pytest tests/test_integration.py -v

# 커버리지 확인
pytest --cov=. --cov-report=html
```

### Linting Commands
```bash
# Pylint
pylint shared/ 0_통합_대시보드/

# Flake8
flake8 shared/ 0_통합_대시보드/ --max-line-length=120

# Black (자동 포맷팅)
black shared/ 0_통합_대시보드/
```

### Database Commands
```bash
# DB 초기화
python3 -c "from shared.database import init_master_database; init_master_database()"

# DB 백업
cp hr_master.db _backups/hr_master_$(date +%Y%m%d_%H%M%S).db

# DB 내용 확인
sqlite3 hr_master.db "SELECT * FROM employees LIMIT 5"
sqlite3 hr_master.db "SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10"
```

### Tips
- **Quick Reference 자주 참조**: 구현 중 소유권 규칙, 상태 변수, 경계 규칙을 자주 확인하세요
- **Integration-Critical Tasks 우선순위**: IC-1, IC-2, IC-3는 가장 중요한 통합 지점입니다. 순서를 정확히 따르세요
- **PRD/Blueprint 확인**: "Implements" 필드의 PRD §X 또는 Blueprint §Y를 확인하여 원본 요구사항 이해
- **단계별 검증**: 각 Parent Task의 Verification을 반드시 수행한 후 다음 Task로 진행
- **실제 데이터 검증 필수**: 특히 급여관리는 실제 급여 데이터 3건으로 반드시 검증 (Task 5.10)
- **롤백 준비**: 문제 발생 시 Blueprint §11.5의 롤백 절차 참고

---

*문서 생성 일시: 2026-01-28*  
*프로젝트: 인사팀 자동화 시스템 통합*  
*버전: 1.0*  
*총 Task 수: 70+ subtasks*  
*Critical Tasks: IC-1 (직원 저장), IC-2 (급여 → 명세서), IC-3 (데이터 동기화)*
