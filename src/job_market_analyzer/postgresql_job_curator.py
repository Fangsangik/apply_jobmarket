"""
PostgreSQL 채용정보 큐레이터
AWS RDS PostgreSQL 데이터베이스 연동
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')
import psycopg2.extras
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class PostgreSQLJobCurator:
    """PostgreSQL 채용정보 큐레이터"""

    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "password")
        }

        try:
            # SQLAlchemy 엔진 생성
            connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            self.engine = create_engine(
                connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
            
            # 테이블 목록 가져오기
            self.available_tables = self._get_available_tables()
            print(f"✅ PostgreSQL 연결 성공! 사용 가능한 테이블: {len(self.available_tables)}개")
            
        except Exception as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            self.engine = None
            self.available_tables = []

    def _get_available_tables(self):
        """사용 가능한 테이블 목록 조회"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                return tables
        except Exception as e:
            print(f"❌ 테이블 목록 조회 실패: {e}")
            return []

    def get_jobs_data(self, limit: Optional[int] = 50, table_name: str = None,
                     job_role: str = None, experience_range: str = None, offset: int = 0, 
                     filters: dict = None):
        """채용공고 데이터 조회 (jobs_analyzed와 조인) - 최적화된 버전"""
        if not self.engine or not table_name or table_name == "no_tables":
            return pd.DataFrame()

        try:
            if table_name not in self.available_tables:
                print(f"❌ 테이블 '{table_name}'을 찾을 수 없습니다.")
                return pd.DataFrame()
            
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                sslmode='require'
            )
            
            # jobs_analyzed 테이블이 있는지 확인하고 조인 쿼리 구성
            if 'jobs_analyzed' in self.available_tables and table_name == 'jobs':
                # 필터 조건 구성
                where_conditions = []
                params = []
                
                if filters:
                    # 직무 필터 - 더 유연한 매칭
                    if filters.get('job_role') and filters['job_role'] != '전체':
                        job_role = filters['job_role']
                        if job_role == '백엔드':
                            where_conditions.append("(ja.jobs_attributes->>'직군 대분류' LIKE '%백엔드%' OR ja.jobs_attributes->>'직무' LIKE '%백엔드%' OR j.content LIKE '%백엔드%')")
                        elif job_role == 'AI/머신러닝':
                            where_conditions.append("(ja.jobs_attributes->>'직군 대분류' LIKE '%AI%' OR ja.jobs_attributes->>'직군 대분류' LIKE '%ML%' OR ja.jobs_attributes->>'직군 대분류' LIKE '%머신러닝%')")
                        else:
                            where_conditions.append("(ja.jobs_attributes->>'직군 대분류' LIKE %s OR ja.jobs_attributes->>'직무' LIKE %s)")
                            params.extend([f'%{job_role}%', f'%{job_role}%'])
                    
                    # 경력 필터 - 간단하고 안전한 매칭  
                    if filters.get('experience') and filters['experience'] != '전체':
                        exp = filters['experience']
                        if exp == '신입':
                            where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%신입%' OR ja.jobs_attributes->>'경력연차' LIKE '%무관%' OR ja.jobs_attributes->>'경력연차' = '0년' OR ja.jobs_attributes->>'경력연차' = '0')")
                        elif exp == '1-2년':
                            where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%1년%' OR ja.jobs_attributes->>'경력연차' LIKE '%2년%' OR ja.jobs_attributes->>'경력연차' LIKE '%1+%' OR ja.jobs_attributes->>'경력연차' LIKE '%2+%' OR ja.jobs_attributes->>'경력연차' LIKE '%1-2%')")
                        elif exp == '3-5년':
                            where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%3년%' OR ja.jobs_attributes->>'경력연차' LIKE '%4년%' OR ja.jobs_attributes->>'경력연차' LIKE '%5년%' OR ja.jobs_attributes->>'경력연차' LIKE '%3+%' OR ja.jobs_attributes->>'경력연차' LIKE '%4+%' OR ja.jobs_attributes->>'경력연차' LIKE '%5+%' OR ja.jobs_attributes->>'경력연차' LIKE '%3-5%')")
                        elif exp == '6-8년':
                            where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%6년%' OR ja.jobs_attributes->>'경력연차' LIKE '%7년%' OR ja.jobs_attributes->>'경력연차' LIKE '%8년%' OR ja.jobs_attributes->>'경력연차' LIKE '%6+%' OR ja.jobs_attributes->>'경력연차' LIKE '%7+%' OR ja.jobs_attributes->>'경력연차' LIKE '%8+%')")
                        elif exp == '9년 이상':
                            where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%9년%' OR ja.jobs_attributes->>'경력연차' LIKE '%10년%' OR ja.jobs_attributes->>'경력연차' LIKE '%9+%' OR ja.jobs_attributes->>'경력연차' LIKE '%10+%' OR ja.jobs_attributes->>'경력연차' LIKE '%이상%')")
                        else:
                            where_conditions.append(f"ja.jobs_attributes->>'경력연차' LIKE '%{exp}%'")
                    
                    # 연봉 필터 (간단한 패턴 매칭)
                    if filters.get('min_salary'):
                        min_sal = filters['min_salary']
                        where_conditions.append(f"(ja.jobs_attributes->>'연봉정보' ~ '[0-9]' AND ja.jobs_attributes->>'연봉정보' ~ '{min_sal}')")
                    
                    # 회사 유형 필터 (실제 회사명 기반)
                    if filters.get('company_type') and filters['company_type'] != '전체':
                        company_type = filters['company_type']
                        if company_type == '외국계':
                            # 잘 알려진 외국 회사들
                            foreign_companies = ['google', 'microsoft', 'amazon', 'meta', 'apple', 'netflix', 'airbnb', 'uber', 'zoom', 'adobe', 'salesforce', 'oracle', 'ibm', 'intel', 'nvidia', 'tesla', 'spotify', 'slack', 'github', 'atlassian']
                            conditions = [f"j.company LIKE '%{company}%'" for company in foreign_companies]
                            where_conditions.append(f"({' OR '.join(conditions)})")
                        elif company_type == '국내기업':
                            # 잘 알려진 한국 회사들
                            korean_companies = ['samsung', 'lg', 'naver', 'kakao', 'coupang', 'baemin', 'toss', 'line', 'nexon', 'ncsoft', 'hyundai', 'sk', 'kt', 'lotte', 'doosan', 'hanwha', 'posco']
                            conditions = [f"j.company LIKE '%{company}%'" for company in korean_companies]
                            where_conditions.append(f"({' OR '.join(conditions)})")
                
                where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                # 최적화된 쿼리 - jobs_attributes가 있는 것을 우선으로 정렬
                base_query = f"""
                    SELECT j.id, j.title, j.company, j.url, j.content, j.category, j.position,
                           j.created_at, j.updated_at, j.html,
                           ja.jobs_attributes,
                           ja.jobs_attributes->>'직군 대분류' as major_category,
                           ja.jobs_attributes->>'직군 소분류' as minor_category,
                           ja.jobs_attributes->>'직무' as job_role_analyzed,
                           ja.jobs_attributes->>'경력연차' as experience_analyzed,
                           ja.jobs_attributes->>'연봉정보' as salary_analyzed,
                           ja.jobs_attributes->>'근무지역' as location_analyzed,
                           ja.jobs_attributes->>'회사명' as company_analyzed
                    FROM jobs j
                    LEFT JOIN jobs_analyzed ja ON j.id = ja.jobs_id
                    {where_clause}
                    ORDER BY 
                        CASE WHEN ja.jobs_attributes IS NOT NULL AND ja.jobs_attributes != 'null' THEN 0 ELSE 1 END,
                        j.created_at DESC, j.id DESC
                """
                
                if limit is not None:
                    main_query = base_query + f" LIMIT {limit} OFFSET {offset}"
                    print(f"🔄 페이지네이션 데이터 조회 중 (LIMIT {limit}, OFFSET {offset})...")
                else:
                    main_query = base_query
                    print(f"🔄 전체 데이터 조회 중 (필터 적용)...")
            else:
                # 기존 로직 (fallback)
                main_query = f"SELECT * FROM {table_name} ORDER BY created_at DESC"
                if limit is not None:
                    main_query += f" LIMIT {limit} OFFSET {offset}"
                print(f"🔄 기본 테이블 조회 중...")
            
            if params:
                df = pd.read_sql_query(main_query, conn, params=params)
            else:
                df = pd.read_sql_query(main_query, conn)
            conn.close()
            print(f"✅ {len(df)}개 행 조회 완료")
            return df

        except Exception as e:
            print(f"❌ 데이터 조회 실패: {e}")
            return pd.DataFrame()

    def get_jobs_count(self, table_name: str = "jobs", filters: dict = None):
        """필터 조건에 맞는 총 채용공고 수 조회 (페이지네이션용)"""
        if not self.engine or not table_name or table_name == "no_tables":
            return 0

        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                sslmode='require'
            )
            
            # 필터 조건 구성
            where_conditions = []
            params = []
            
            if filters:
                # 직무 필터 - 더 유연한 매칭
                if filters.get('job_role') and filters['job_role'] != '전체':
                    job_role = filters['job_role']
                    if job_role == '백엔드':
                        where_conditions.append("(ja.jobs_attributes->>'직군 대분류' LIKE '%백엔드%' OR ja.jobs_attributes->>'직무' LIKE '%백엔드%' OR j.content LIKE '%백엔드%')")
                    elif job_role == 'AI/머신러닝':
                        where_conditions.append("(ja.jobs_attributes->>'직군 대분류' LIKE '%AI%' OR ja.jobs_attributes->>'직군 대분류' LIKE '%ML%' OR ja.jobs_attributes->>'직군 대분류' LIKE '%머신러닝%')")
                    else:
                        where_conditions.append("(ja.jobs_attributes->>'직군 대분류' LIKE %s OR ja.jobs_attributes->>'직무' LIKE %s)")
                        params.extend([f'%{job_role}%', f'%{job_role}%'])
                
                # 경력 필터 - 간단하고 안전한 매칭  
                if filters.get('experience') and filters['experience'] != '전체':
                    exp = filters['experience']
                    if exp == '신입':
                        where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%신입%' OR ja.jobs_attributes->>'경력연차' LIKE '%무관%' OR ja.jobs_attributes->>'경력연차' = '0년' OR ja.jobs_attributes->>'경력연차' = '0')")
                    elif exp == '1-2년':
                        where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%1년%' OR ja.jobs_attributes->>'경력연차' LIKE '%2년%' OR ja.jobs_attributes->>'경력연차' LIKE '%1+%' OR ja.jobs_attributes->>'경력연차' LIKE '%2+%' OR ja.jobs_attributes->>'경력연차' LIKE '%1-2%')")
                    elif exp == '3-5년':
                        where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%3년%' OR ja.jobs_attributes->>'경력연차' LIKE '%4년%' OR ja.jobs_attributes->>'경력연차' LIKE '%5년%' OR ja.jobs_attributes->>'경력연차' LIKE '%3+%' OR ja.jobs_attributes->>'경력연차' LIKE '%4+%' OR ja.jobs_attributes->>'경력연차' LIKE '%5+%' OR ja.jobs_attributes->>'경력연차' LIKE '%3-5%')")
                    elif exp == '6-8년':
                        where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%6년%' OR ja.jobs_attributes->>'경력연차' LIKE '%7년%' OR ja.jobs_attributes->>'경력연차' LIKE '%8년%' OR ja.jobs_attributes->>'경력연차' LIKE '%6+%' OR ja.jobs_attributes->>'경력연차' LIKE '%7+%' OR ja.jobs_attributes->>'경력연차' LIKE '%8+%')")
                    elif exp == '9년 이상':
                        where_conditions.append("(ja.jobs_attributes->>'경력연차' LIKE '%9년%' OR ja.jobs_attributes->>'경력연차' LIKE '%10년%' OR ja.jobs_attributes->>'경력연차' LIKE '%9+%' OR ja.jobs_attributes->>'경력연차' LIKE '%10+%' OR ja.jobs_attributes->>'경력연차' LIKE '%이상%')")
                    else:
                        where_conditions.append(f"ja.jobs_attributes->>'경력연차' LIKE '%{exp}%'")
                
                # 연봉 필터 (간단한 패턴 매칭)
                if filters.get('min_salary'):
                    min_sal = filters['min_salary']
                    where_conditions.append(f"(ja.jobs_attributes->>'연봉정보' ~ '[0-9]' AND ja.jobs_attributes->>'연봉정보' ~ '{min_sal}')")
                
                # 회사 유형 필터 (실제 회사명 기반)
                if filters.get('company_type') and filters['company_type'] != '전체':
                    company_type = filters['company_type']
                    if company_type == '외국계':
                        # 잘 알려진 외국 회사들
                        foreign_companies = ['google', 'microsoft', 'amazon', 'meta', 'apple', 'netflix', 'airbnb', 'uber', 'zoom', 'adobe', 'salesforce', 'oracle', 'ibm', 'intel', 'nvidia', 'tesla', 'spotify', 'slack', 'github', 'atlassian']
                        conditions = [f"j.company LIKE '%{company}%'" for company in foreign_companies]
                        where_conditions.append(f"({' OR '.join(conditions)})")
                    elif company_type == '국내기업':
                        # 잘 알려진 한국 회사들
                        korean_companies = ['samsung', 'lg', 'naver', 'kakao', 'coupang', 'baemin', 'toss', 'line', 'nexon', 'ncsoft', 'hyundai', 'sk', 'kt', 'lotte', 'doosan', 'hanwha', 'posco']
                        conditions = [f"j.company LIKE '%{company}%'" for company in korean_companies]
                        where_conditions.append(f"({' OR '.join(conditions)})")
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            count_query = f"""
                SELECT COUNT(*)
                FROM jobs j
                LEFT JOIN jobs_analyzed ja ON j.id = ja.jobs_id
                {where_clause}
            """
            
            cursor = conn.cursor()
            if params:
                cursor.execute(count_query, params)
            else:
                cursor.execute(count_query)
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return count
            
        except Exception as e:
            print(f"❌ 개수 조회 실패: {e}")
            return 0

    def test_connection(self):
        """연결 테스트"""
        if not self.engine:
            return False
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"❌ 연결 테스트 실패: {e}")
            return False

    def get_table_info(self, table_name: str):
        """테이블 정보 조회"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """))
                columns = [(row[0], row[1]) for row in result]
                return {'columns': columns}
        except Exception as e:
            print(f"❌ 테이블 정보 조회 실패: {e}")
            return None

if __name__ == "__main__":
    # 테스트 코드
    curator = PostgreSQLJobCurator()
    
    if curator.test_connection():
        print("✅ 연결 테스트 성공")
        
        # 테이블 목록 출력
        print(f"사용 가능한 테이블: {curator.available_tables}")
        
        # 샘플 데이터 조회
        if 'jobs' in curator.available_tables:
            sample_data = curator.get_jobs_data(table_name="jobs", limit=5)
            print(f"샘플 데이터 조회: {len(sample_data)}개 행")
            if not sample_data.empty:
                print(f"컬럼: {list(sample_data.columns)}")
    else:
        print("❌ 연결 테스트 실패")