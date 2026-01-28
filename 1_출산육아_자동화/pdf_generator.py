"""
임신 관련 서식 PDF 완벽 재현 생성기
원본 서식과 100% 동일하게 구현 - 최종 버전
"""

from io import BytesIO
from datetime import date, datetime
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import calendar

import constants as C


# ============================================================
# 한글 폰트 설정
# ============================================================

def register_korean_fonts():
    """한글 폰트 등록"""
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', '/System/Library/Fonts/Supplemental/AppleGothic.ttf'))
        return 'NanumGothic'
    except:
        try:
            pdfmetrics.registerFont(TTFont('Malgun', 'malgun.ttf'))
            return 'Malgun'
        except:
            return 'Helvetica'


# ============================================================
# 1. 임신기 근로시간 단축 신청서
# ============================================================

def create_application_form_pdf(employee_info: Dict, employer_info: Dict, 
                                pregnancy_data: Dict, childbirth_data: Dict) -> BytesIO:
    """임신기 근로시간 단축 신청서 PDF 생성 (원본과 100% 일치)"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    font_name = register_korean_fonts()
    
    # 제목
    c.setFont(font_name, 18)
    c.drawCentredString(width / 2, height - 50, "임신기 근로시간 단축 신청서")
    
    # 신청인 정보 테이블
    y_pos = height - 85
    table_width = 155*mm
    table_start_x = 28*mm
    
    c.setFont(font_name, 10)
    
    # 테이블 외곽선
    row_height = 10*mm
    
    # 상단 테이블 (2행)
    c.rect(table_start_x, y_pos - row_height*2, table_width, row_height*2)
    
    # 가로선
    c.line(table_start_x, y_pos - row_height, table_start_x + table_width, y_pos - row_height)
    
    # 세로선들
    col1 = 23*mm
    col2 = 43*mm
    col3 = 88*mm
    col4 = 113*mm
    
    c.line(table_start_x + col1, y_pos - row_height*2, table_start_x + col1, y_pos)
    c.line(table_start_x + col2, y_pos - row_height*2, table_start_x + col2, y_pos)
    c.line(table_start_x + col3, y_pos - row_height*2, table_start_x + col3, y_pos)
    c.line(table_start_x + col4, y_pos - row_height*2, table_start_x + col4, y_pos)
    
    # 신청인 (세로 병합)
    c.drawString(table_start_x + 6*mm, y_pos - 12*mm, "신청인")
    
    # 첫째 행 내용
    c.drawString(table_start_x + col1 + 7*mm, y_pos - 6*mm, "성명")
    c.drawString(table_start_x + col2 + 9*mm, y_pos - 6*mm, employee_info["이름"])
    c.drawString(table_start_x + col3 + 4*mm, y_pos - 6*mm, "생년월일")
    birth = employee_info["주민등록번호"][:6]
    c.drawString(table_start_x + col4 + 7*mm, y_pos - 6*mm, birth)
    
    # 둘째 행 내용
    c.drawString(table_start_x + col1 + 4*mm, y_pos - 16*mm, "소속(부서)")
    c.drawString(table_start_x + col2 + 9*mm, y_pos - 16*mm, employee_info["부서"])
    c.drawString(table_start_x + col3 + 4*mm, y_pos - 16*mm, "직위(직급)")
    c.drawString(table_start_x + col4 + 7*mm, y_pos - 16*mm, employee_info["직급"])
    
    # 임신기간 중 근로시간 단축 테이블
    y_pos = y_pos - row_height*2 - 5*mm
    
    due_date = childbirth_data["출산예정일"]
    start_date = pregnancy_data["시작일"]
    end_date = pregnancy_data["종료일"]
    work_start = pregnancy_data['근무시간']['시작']
    work_end = pregnancy_data['근무시간']['종료']
    
    # 큰 테이블 그리기
    table_height = 50*mm
    c.rect(table_start_x, y_pos - table_height, table_width, table_height)
    
    # 왼쪽 첫 번째 열 (임신기간 중 근로시간 단축) - 세로 병합
    c.line(table_start_x + col1, y_pos - table_height, table_start_x + col1, y_pos)
    c.setFont(font_name, 9)
    c.drawString(table_start_x + 2*mm, y_pos - 18*mm, "임신기간 중")
    c.drawString(table_start_x + 3*mm, y_pos - 23*mm, "근로시간")
    c.drawString(table_start_x + 6*mm, y_pos - 28*mm, "단축")
    c.setFont(font_name, 10)
    
    # 출산예정일 행
    row1_y = 12*mm
    c.line(table_start_x, y_pos - row1_y, table_start_x + table_width, y_pos - row1_y)
    c.line(table_start_x + 68*mm, y_pos - row1_y, table_start_x + 68*mm, y_pos)
    c.drawString(table_start_x + 38*mm, y_pos - 7*mm, "출산예정일")
    c.drawString(table_start_x + 78*mm, y_pos - 7*mm, 
                 f"{due_date.year}년 {due_date.month:02d}월 {due_date.day:02d}일")
    
    # 12주(84일) 이내 섹션
    row2_y = 26*mm
    c.line(table_start_x, y_pos - row2_y, table_start_x + table_width, y_pos - row2_y)
    
    # 12주(84일)/이내 세로선
    c.line(table_start_x + 38*mm, y_pos - row2_y, table_start_x + 38*mm, y_pos - row1_y)
    # 개시예정일/종료예정일 세로선
    c.line(table_start_x + 68*mm, y_pos - row2_y, table_start_x + 68*mm, y_pos - row1_y)
    
    # 12주(84일) 이내 좌측 셀을 가로로 나누기
    c.line(table_start_x + col1, y_pos - 19*mm, table_start_x + 38*mm, y_pos - 19*mm)
    
    c.setFont(font_name, 9)
    c.drawString(table_start_x + 28*mm, y_pos - 16*mm, "12주")
    c.drawString(table_start_x + 26*mm, y_pos - 18.5*mm, "(84일)")
    c.drawString(table_start_x + 28*mm, y_pos - 23*mm, "이내")
    c.setFont(font_name, 10)
    
    c.drawString(table_start_x + 46*mm, y_pos - 16*mm, "개시 예정일")
    c.drawString(table_start_x + 46*mm, y_pos - 23*mm, "종료 예정일")
    
    # 32주(246일) 이후 섹션
    row3_y = 38*mm
    c.line(table_start_x, y_pos - row3_y, table_start_x + table_width, y_pos - row3_y)
    
    # 32주(246일)/이후 세로선
    c.line(table_start_x + 38*mm, y_pos - row3_y, table_start_x + 38*mm, y_pos - row2_y)
    # 개시예정일/종료예정일 세로선
    c.line(table_start_x + 68*mm, y_pos - row3_y, table_start_x + 68*mm, y_pos - row2_y)
    
    # 32주(246일) 이후 좌측 셀을 가로로 나누기
    c.line(table_start_x + col1, y_pos - 32*mm, table_start_x + 38*mm, y_pos - 32*mm)
    
    c.setFont(font_name, 9)
    c.drawString(table_start_x + 28*mm, y_pos - 29*mm, "32주")
    c.drawString(table_start_x + 26*mm, y_pos - 31.5*mm, "(246일)")
    c.drawString(table_start_x + 28*mm, y_pos - 35*mm, "이후")
    c.setFont(font_name, 10)
    
    c.drawString(table_start_x + 46*mm, y_pos - 29*mm, "개시 예정일")
    c.drawString(table_start_x + 78*mm, y_pos - 29*mm,
                 f"{start_date.year}.{start_date.month:02d}.{start_date.day:02d}")
    
    c.drawString(table_start_x + 46*mm, y_pos - 35*mm, "종료 예정일")
    c.drawString(table_start_x + 78*mm, y_pos - 35*mm,
                 f"{end_date.year}.{end_date.month:02d}.{end_date.day:02d}")
    
    # 근무 개시 시각 및 종료 시각
    c.line(table_start_x + 68*mm, y_pos - table_height, table_start_x + 68*mm, y_pos - row3_y)
    
    c.setFont(font_name, 9)
    c.drawString(table_start_x + 26*mm, y_pos - 42*mm, "근무 개시 시각")
    c.drawString(table_start_x + 26*mm, y_pos - 46*mm, "및 종료 시각")
    
    # 근무시간을 중앙에 크게 표시
    c.setFont(font_name, 11)
    work_time_text = f"{work_start}  ~  {work_end}"
    c.drawString(table_start_x + 85*mm, y_pos - 44*mm, work_time_text)
    c.setFont(font_name, 10)
    
    # 주의사항
    y_pos = y_pos - table_height - 4*mm
    c.setFont(font_name, 8)
    c.drawString(table_start_x, y_pos, "※ 개시 및 종료일정은 출산 일정에 따라 변동 될 수 있음.")
    
    # 신청 문구
    y_pos = y_pos - 18*mm
    c.setFont(font_name, 11)
    c.drawCentredString(width / 2, y_pos, "위 본인은 『근로기준법』제74조 제7항에 따라")
    y_pos -= 6*mm
    c.drawCentredString(width / 2, y_pos, "위와 같이 근로시간 단축을 신청합니다.")
    
    # 날짜 및 서명
    y_pos -= 18*mm
    today = datetime.now()
    c.drawCentredString(width / 2, y_pos, f"{today.year}년     {today.month}월     {today.day}일")
    
    y_pos -= 10*mm
    c.drawCentredString(width / 2, y_pos, f"신청인  {employee_info['이름']}  (서명 또는 인)")
    
    # 첨부
    y_pos -= 18*mm
    c.setFont(font_name, 9)
    c.drawString(table_start_x, y_pos, "첨부  임신 사실을 증명하는 의사의 진단서(임신주수 확인용)")
    
    # 제출처 - 하단에 고정
    y_pos = 60*mm
    employer_name = employer_info.get('대표자명', employer_info.get('회사명', '사업주'))
    c.drawString(table_start_x, y_pos, f"{employer_name} 귀하")
    
    c.save()
    buffer.seek(0)
    return buffer


# ============================================================
# 2. 임신사유 근로시간 단축 확인서
# ============================================================

def create_confirmation_form_pdf(employee_info: Dict, employer_info: Dict, 
                                 pregnancy_data: Dict, childbirth_data: Dict) -> BytesIO:
    """임신사유 근로시간 단축 확인서 PDF 생성 (원본과 100% 일치)"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    font_name = register_korean_fonts()
    
    # 서식 번호
    c.setFont(font_name, 7)
    c.drawString(18*mm, height - 15*mm, "■ 고용창출장려금·고용안정장려금의 신청 및 지급에 관한 규정 [별지 제22호의2 서식]")
    
    # 제목
    c.setFont(font_name, 14)
    c.drawCentredString(width / 2, height - 28*mm, "임신사유 근로시간 단축에 대한 근로자 확인서")
    
    # 동의 문구
    y_pos = height - 38*mm
    c.setFont(font_name, 7)
    c.drawString(18*mm, y_pos, "※ 본인은 임신 사유로 근로시간을 단축한 사실을 아래와 같이 확인하며,")
    y_pos -= 3.5*mm
    c.drawString(21*mm, y_pos, "위라밸일자리 장려금(소정근로시간 단축제) 지원을 위한 자료로 활용하는 것에 대해 동의합니다.")
    
    # 기본 정보 테이블
    y_pos -= 8*mm
    table_x = 18*mm
    table_width = 174*mm
    row_h = 10*mm
    
    c.rect(table_x, y_pos - row_h, table_width, row_h)
    
    # 세로선
    c.line(table_x + 27*mm, y_pos - row_h, table_x + 27*mm, y_pos)
    c.line(table_x + 85*mm, y_pos - row_h, table_x + 85*mm, y_pos)
    c.line(table_x + 105*mm, y_pos - row_h, table_x + 105*mm, y_pos)
    c.line(table_x + 140*mm, y_pos - row_h, table_x + 140*mm, y_pos)
    c.line(table_x + 155*mm, y_pos - row_h, table_x + 155*mm, y_pos)
    
    c.setFont(font_name, 8)
    
    # 성명 (생년월일)
    c.drawString(table_x + 6*mm, y_pos - 3.5*mm, "성  명")
    c.drawString(table_x + 3*mm, y_pos - 7*mm, "(생년월일)")
    
    # 생년월일 포맷팅 - 괄호 안에 넣기
    birth_str = employee_info["주민등록번호"][:6]
    if birth_str[0] in ['0', '1', '2']:
        birth_year = f"20{birth_str[:2]}"
    else:
        birth_year = f"19{birth_str[:2]}"
    birth_formatted = f"({birth_year}.{birth_str[2:4]}.{birth_str[4:6]})"
    
    # 이름과 생년월일을 함께 표시
    c.drawString(table_x + 30*mm, y_pos - 5*mm, f"{employee_info['이름']} {birth_formatted}")
    
    # 연락처
    c.drawString(table_x + 90*mm, y_pos - 5*mm, "연락처")
    phone = employee_info.get("연락처", "010-xxxx-xxxx")
    c.drawString(table_x + 110*mm, y_pos - 5*mm, phone)
    
    # 임신일
    c.drawString(table_x + 143*mm, y_pos - 5*mm, "임신일")
    # 임신확인일 데이터 가져오기
    pregnancy_confirm = childbirth_data.get("임신확인일")
    if pregnancy_confirm and isinstance(pregnancy_confirm, date):
        pregnancy_date_str = f"{pregnancy_confirm.strftime('%y.%m.%d')}"
    else:
        pregnancy_date_str = "00.00.00"
    c.setFont(font_name, 7)
    c.drawString(table_x + 158*mm, y_pos - 5*mm, pregnancy_date_str)
    c.setFont(font_name, 8)
    
    # 충 단축 기간 (세로 병합)
    y_pos -= row_h
    c.rect(table_x + 140*mm, y_pos - row_h, 34*mm, row_h*2)
    c.drawString(table_x + 141*mm, y_pos + 2*mm, "충 단축 기간")
    
    start = pregnancy_data["시작일"]
    end = pregnancy_data["종료일"]
    c.setFont(font_name, 7)
    c.drawString(table_x + 157*mm, y_pos - 2*mm, f"{start.strftime('%y.%m.%d')}~")
    c.drawString(table_x + 157*mm, y_pos - 7*mm, f"{end.strftime('%y.%m.%d')}")
    c.setFont(font_name, 8)
    
    # 단축 근로 시간 및 이행 테이블
    y_pos -= 8*mm
    detail_height = 115*mm
    c.rect(table_x, y_pos - detail_height, table_width, detail_height)
    
    # 왼쪽 헤더 (세로 병합)
    c.line(table_x + 16*mm, y_pos - detail_height, table_x + 16*mm, y_pos)
    c.drawString(table_x + 4*mm, y_pos - 6*mm, "단축")
    c.drawString(table_x + 4*mm, y_pos - 10*mm, "근로")
    c.drawString(table_x + 4*mm, y_pos - 14*mm, "시간")
    c.drawString(table_x + 5*mm, y_pos - 18*mm, "및")
    c.drawString(table_x + 4*mm, y_pos - 22*mm, "이행")
    
    # 내용 시작
    c.setFont(font_name, 7)
    c.drawString(table_x + 18*mm, y_pos - 4*mm, 
                 "○ 근로시간 단축 기간 내 아래와 같이 근로시간을 단축하였음을 확인합니다.")
    
    # 1회차
    y_pos -= 10*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.setFont(font_name, 8)
    c.drawString(table_x + 18*mm, y_pos - 4*mm, f"1회차) {start.year}년 {start.month:02d}월")
    
    # 해당월 단축 사용 기간
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.line(table_x + 85*mm, y_pos, table_x + 85*mm, y_pos + 18*mm)
    c.setFont(font_name, 7)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 해당월 단축 사용 기간")
    _, last_day_1 = calendar.monthrange(start.year, start.month)
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, 
                 f"{start.year}. {start.month:02d}. {start.day:02d}. ~ {start.year}. {start.month:02d}. {last_day_1}.")
    
    # 단축 후 주당 근로시간
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 단축 후 주당 근로시간")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "주당 30시간")
    
    # 단축 후 근로시간 준수 여부
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 단축 후 근로시간 준수 여부")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "준수( O ), 미준수(    )")
    
    # 2회차
    y_pos -= 8*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.setFont(font_name, 8)
    c.drawString(table_x + 18*mm, y_pos - 4*mm, f"2회차) {end.year}년 {end.month:02d}월")
    
    # 해당월 단축 사용 기간
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.line(table_x + 85*mm, y_pos, table_x + 85*mm, y_pos + 18*mm)
    c.setFont(font_name, 7)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 해당월 단축 사용 기간")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, 
                 f"{end.year}. {end.month:02d}. 01. ~ {end.year}. {end.month:02d}. {end.day:02d}.")
    
    # 단축 후 주당 근로시간
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 단축 후 주당 근로시간")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "주당 30시간")
    
    # 단축 후 근로시간 준수 여부
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 단축 후 근로시간 준수 여부")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "준수( O ), 미준수(    )")
    
    # 3회차 (빈 칸)
    y_pos -= 8*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.setFont(font_name, 8)
    c.drawString(table_x + 18*mm, y_pos - 4*mm, "3회차) 2020년 00월")
    
    # 해당월 단축 사용 기간
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.line(table_x + 85*mm, y_pos, table_x + 85*mm, y_pos + 18*mm)
    c.setFont(font_name, 7)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 해당월 단축 사용 기간")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "2020. 00. 00. ~ 2020. 00. 00.")
    
    # 단축 후 주당 근로시간
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 단축 후 주당 근로시간")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "주당 00시간")
    
    # 단축 후 근로시간 준수 여부
    y_pos -= 6*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.drawString(table_x + 21*mm, y_pos - 3.5*mm, "• 단축 후 근로시간 준수 여부")
    c.drawString(table_x + 90*mm, y_pos - 3.5*mm, "준수(  ), 미준수(  )")
    
    # 작성방법
    y_pos -= 8*mm
    c.line(table_x, y_pos, table_x + table_width, y_pos)
    c.setFont(font_name, 6.5)
    c.drawString(table_x + 18*mm, y_pos - 3*mm, "✧ 작성방법")
    y_pos -= 4*mm
    c.drawString(table_x + 18*mm, y_pos - 2*mm, 
                 "① 1일부터 말일까지를 월 단위로 매월 작성합니다.")
    y_pos -= 3*mm
    c.drawString(table_x + 18*mm, y_pos - 2*mm, 
                 "② 단축 후 주당 근로시간: 단축 후 근로계약서 또는 근로시간 단축 신청서 상의 (주당)근로시간을 작성합니다.")
    y_pos -= 3*mm
    c.drawString(table_x + 21*mm, y_pos - 2*mm, 
                 "* 주15시간 미만, 주30시간을 초과하는 경우 장려금을 지원하지 않음")
    y_pos -= 3*mm
    c.drawString(table_x + 18*mm, y_pos - 2*mm, 
                 "③ 단축 후의 근로시간을 초과하여 근무한 날이 있는 월은 미준수에 체크(√)합니다.")
    y_pos -= 3*mm
    c.drawString(table_x + 21*mm, y_pos - 2*mm, 
                 "* 사업주의 업무지시 또는 연장근로 승인에 따라 단축 후 근무시간을 초과하여 근무한 경우를 말하며,")
    y_pos -= 3*mm
    c.drawString(table_x + 23*mm, y_pos - 2*mm, 
                 "미준수한 월은 해당월의 장려금을 지원하지 않음")
    
    # 부정수급 경고
    y_pos -= 8*mm
    c.setFont(font_name, 7)
    c.drawString(table_x, y_pos, 
                 "○ 만약 거짓이나 그 밖의 부정한 방법으로 위라밸일자리 장려금(소정근로시간단축제)을 지급 받고자 사")
    y_pos -= 3.5*mm
    c.drawString(table_x + 3*mm, y_pos, 
                 "업주와 공모한 경우에는 해당 근로자도 고용보험법령에 의해 처벌될 수 있음을 확인합니다.")
    
    # 부정수급 처벌 경고
    y_pos -= 5*mm
    c.setFont(font_name, 6)
    c.drawString(table_x, y_pos,
                 "※ 부정수급 적발시 경우, 「고용보험법」 제116조제1항에 따라 사업주와 공모하여 거짓이나 그 밖의 부")
    y_pos -= 3*mm
    c.drawString(table_x + 3*mm, y_pos,
                 "정한 방법으로 다음 고용안정사업의 지원금 또는 급여를 받은 자와 공모한 사업주는 각각 5년 이하")
    y_pos -= 3*mm
    c.drawString(table_x + 3*mm, y_pos,
                 "의 징역 또는 5천만원 이하의 벌금 가능")
    
    # 동의 문구
    y_pos -= 7*mm
    c.setFont(font_name, 7)
    c.drawString(table_x, y_pos, "위 내용에 동의하며 기재 내용이 모두 사실임을 확인합니다.")
    
    # 근로자 서명
    y_pos -= 8*mm
    today = datetime.now()
    c.setFont(font_name, 9)
    c.drawRightString(width - 25*mm, y_pos, f"{today.year}년     {today.month:02d}월     {today.day:02d}일")
    
    y_pos -= 6*mm
    c.drawRightString(width - 20*mm, y_pos, f"확인자(근로자)  {employee_info['이름']}  (서명 또는 인)")
    
    # 사업주 제출 문구
    y_pos -= 8*mm
    c.setFont(font_name, 7)
    c.drawString(table_x, y_pos, 
                 "「고용창출장려금·고용안정장려금의 신청 및 지급에 관한 규정」에 따라")
    y_pos -= 3.5*mm
    c.drawString(table_x, y_pos, 
                 "위와 같이 근로자로부터 확인받았으며, 동 확인서를 제출합니다.")
    
    # 사업주 서명
    y_pos -= 8*mm
    c.setFont(font_name, 9)
    c.drawRightString(width - 25*mm, y_pos, f"{today.year}년     {today.month:02d}월     {today.day:02d}일")
    
    y_pos -= 6*mm
    employer_name = employer_info.get('대표자명', employer_info.get('회사명', '사업주'))
    c.drawRightString(width - 20*mm, y_pos, f"신청인(사업주)  {employer_name}  (서명 또는 인)")
    
    # 제출처
    y_pos -= 8*mm
    c.setFont(font_name, 9)
    c.drawString(table_x, y_pos, "○○지방고용노동청(○○지청)장 귀하")
    
    c.save()
    buffer.seek(0)
    return buffer


# ============================================================
# 통합 PDF 생성 함수
# ============================================================

def generate_pregnancy_forms(employee_info: Dict, employer_info: Dict, 
                            pregnancy_data: Dict = None, childbirth_data: Dict = None) -> Dict[str, BytesIO]:
    """
    임신 관련 모든 서식을 한번에 생성 (완벽한 재현)
    
    Args:
        employee_info: 근로자 정보 (이름, 주민등록번호, 부서, 직급, 연락처)
        employer_info: 사업주 정보 (대표자명, 회사명 등)
        pregnancy_data: 임신기 근로시간 단축 데이터 (시작일, 종료일, 근무시간)
        childbirth_data: 출산 정보 (출산예정일, 임신확인일 등)
    
    Returns:
        서식명을 키로 하는 PDF BytesIO 딕셔너리
    """
    # 데이터가 없으면 constants에서 가져오기
    if pregnancy_data is None:
        pregnancy_data = C.PREGNANCY_SHORT_WORK
    
    if childbirth_data is None:
        childbirth_data = C.CHILDBIRTH_INFO
    
    forms = {}
    
    # 1. 임신기 근로시간 단축 신청서
    forms["임신기_근로시간_단축_신청서"] = create_application_form_pdf(
        employee_info, employer_info, pregnancy_data, childbirth_data
    )
    
    # 2. 임신사유 근로시간 단축 확인서
    forms["임신사유_근로시간_단축_확인서"] = create_confirmation_form_pdf(
        employee_info, employer_info, pregnancy_data, childbirth_data
    )
    
    return forms
