#!/usr/bin/env python3
"""
모든 필터 하나씩 테스트
"""

import sys
import os
sys.path.insert(0, 'src/job_market_analyzer')
from postgresql_job_curator import PostgreSQLJobCurator

def test_all_filters():
    """모든 필터 테스트"""
    print("🔍 모든 필터 테스트 시작...")
    
    curator = PostgreSQLJobCurator()
    
    print("\n=== 1. 기본 데이터 확인 ===")
    total = curator.get_jobs_count(table_name="jobs", filters={})
    print(f"전체 데이터: {total:,}개")
    
    print("\n=== 2. 직무별 필터 테스트 ===")
    job_roles = ['백엔드', '프론트엔드', 'AI/머신러닝', 'DevOps', '기획']
    
    for job_role in job_roles:
        filters = {'job_role': job_role}
        count = curator.get_jobs_count(table_name="jobs", filters=filters)
        print(f"  {job_role}: {count:,}개")
    
    print("\n=== 3. 경력별 필터 테스트 ===")
    experiences = ['신입', '1-2년', '3-5년', '6-8년', '9년 이상']
    
    for exp in experiences:
        filters = {'experience': exp}
        count = curator.get_jobs_count(table_name="jobs", filters=filters)
        print(f"  {exp}: {count:,}개")
    
    print("\n=== 4. 회사 유형별 필터 테스트 ===")
    company_types = ['외국계', '국내기업']
    
    for company_type in company_types:
        filters = {'company_type': company_type}
        count = curator.get_jobs_count(table_name="jobs", filters=filters)
        print(f"  {company_type}: {count:,}개")
    
    print("\n=== 5. 연봉 필터 테스트 (제거된 상태) ===")
    print("  연봉 필터는 현재 비활성화됨")
    
    print("\n=== 6. 복합 필터 테스트 ===")
    complex_filters = [
        {'job_role': '백엔드', 'experience': '3-5년'},
        {'job_role': 'AI/머신러닝', 'experience': '신입'},
        {'company_type': '외국계', 'job_role': '백엔드'}
    ]
    
    for i, filters in enumerate(complex_filters, 1):
        count = curator.get_jobs_count(table_name="jobs", filters=filters)
        filter_desc = " + ".join([f"{k}={v}" for k, v in filters.items()])
        print(f"  복합{i} ({filter_desc}): {count:,}개")
    
    print("\n=== 7. 실제 데이터 샘플 조회 ===")
    print("백엔드 + 3-5년 경력 데이터 샘플:")
    data = curator.get_jobs_data(
        table_name="jobs", 
        filters={'job_role': '백엔드', 'experience': '3-5년'}, 
        limit=3
    )
    
    if not data.empty:
        for idx, row in data.iterrows():
            print(f"  - {row['company']}: {row['title']}")
            print(f"    경력: {row.get('experience_analyzed', 'N/A')}")
            print(f"    직군: {row.get('major_category', 'N/A')}")
    else:
        print("  조회된 데이터 없음")

if __name__ == "__main__":
    test_all_filters()