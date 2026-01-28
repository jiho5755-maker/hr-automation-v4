"""
TAX-EASY AI - 주택 관련 항목 전용 파서
전세자금 대출, 주택청약저축 등을 파싱합니다.
"""

import re
from typing import Dict, List


def parse_jeonse_loan(text: str) -> Dict:
    """
    전세자금 대출 원리금 상환액 파싱
    
    Returns:
        {
            'found': bool,
            'total_repayment': int,
            'details': List[Dict]
        }
    """
    result = {
        'found': False,
        'total_repayment': 0,
        'details': []
    }
    
    if '주택임차차입금' not in text and '전세자금' not in text:
        return result
    
    # 주택임차차입금 섹션 추출
    section_start = text.find('주택임차차입금')
    if section_start == -1:
        section_start = text.find('전세자금')
    
    if section_start == -1:
        return result
    
    section_end = text.find('주택마련저축', section_start)
    if section_end == -1:
        section_end = text.find('주택청약', section_start)
    if section_end == -1:
        section_end = len(text)
    
    section_text = text[section_start:section_end]
    
    amount_pattern = r'(\d{1,3}(?:,\d{3})*)'
    lines = section_text.split('\n')
    
    for line in lines:
        if '합 계' in line or ('합계' in line and '상환액' in section_text[:section_text.find(line)+1000]):
            amounts = re.findall(amount_pattern, line)
            if amounts:
                amount_str = amounts[-1].replace(',', '')
                try:
                    amount = int(amount_str)
                    if amount > 100000:
                        result['found'] = True
                        result['total_repayment'] = amount
                        break
                except ValueError:
                    continue
    
    return result


def parse_housing_subscription(text: str) -> Dict:
    """
    주택청약저축 납입액 파싱
    
    Returns:
        {
            'found': bool,
            'total_payment': int,
            'account_details': List[Dict]
        }
    """
    result = {
        'found': False,
        'total_payment': 0,
        'account_details': []
    }
    
    if '주택마련저축' not in text and '주택청약' not in text:
        return result
    
    # 주택마련저축 섹션 추출
    section_start = text.find('주택마련저축')
    if section_start == -1:
        section_start = text.find('주택청약저축')
    if section_start == -1:
        section_start = text.find('청약종합저축')
    
    if section_start == -1:
        return result
    
    section_end = text.find('의료비', section_start)
    if section_end == -1:
        section_end = text.find('신용카드', section_start)
    if section_end == -1:
        section_end = len(text)
    
    section_text = text[section_start:section_end]
    
    amount_pattern = r'(\d{1,3}(?:,\d{3})*)'
    lines = section_text.split('\n')
    
    for line in lines:
        if '합 계' in line or ('합계' in line and '납입' in section_text[:section_text.find(line)+1000]):
            amounts = re.findall(amount_pattern, line)
            if amounts:
                amount_str = amounts[-1].replace(',', '')
                try:
                    amount = int(amount_str)
                    if amount > 1000:
                        result['found'] = True
                        result['total_payment'] = amount
                        break
                except ValueError:
                    continue
    
    return result


def parse_housing_data(text: str) -> Dict:
    """
    주택 관련 모든 데이터 파싱
    
    Returns:
        {
            'jeonse_loan': Dict,
            'housing_subscription': Dict
        }
    """
    return {
        'jeonse_loan': parse_jeonse_loan(text),
        'housing_subscription': parse_housing_subscription(text)
    }
