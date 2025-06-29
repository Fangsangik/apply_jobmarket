"""
Career Position 매핑 클래스
career_position 테이블 기준으로 jobs.title과 jobs_analyzed.jobs_attributes와 매칭
"""

import psycopg2
import re
from typing import Dict, List, Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class CareerPositionMapper:
    """career_position 기준 직군 매핑 클래스"""
    
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "password")
        }
        
        # career_position 데이터와 매핑 테이블
        self.career_positions = {}
        self.korean_english_mapping = {}
        self.english_korean_mapping = {}
        self.keyword_mapping = {}
        
        self._load_career_positions()
        self._build_mapping_tables()
    
    def _load_career_positions(self):
        """career_position 테이블에서 데이터 로드"""
        try:
            conn = psycopg2.connect(**self.db_config, sslmode='require')
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name FROM career_position ORDER BY id;')
            positions = cursor.fetchall()
            
            for pos_id, name in positions:
                self.career_positions[pos_id] = name
            
            cursor.close()
            conn.close()
            
            print(f"✅ career_position 데이터 로드 완료: {len(self.career_positions)}개")
            
        except Exception as e:
            print(f"❌ career_position 데이터 로드 실패: {e}")


    # TODO : 신입 인턴 같은 분류 / 따로 분류
    def _build_mapping_tables(self):
        """영어↔한국어 매핑 테이블 및 키워드 매핑 구성"""
        
        # 영어↔한국어 매핑 (career_position 기준)
        mapping_rules = {
            # 개발 관련 - Software Engineer는 백엔드로 매핑 (외국 기업 표준)
            'Software Engineer': '백엔드 개발자',
            'Software Development Engineer': '백엔드 개발자',
            'SDE': '백엔드 개발자',
            'Senior Software Engineer': '백엔드 개발자',
            'Principal Software Engineer': '백엔드 개발자',
            'Staff Software Engineer': '백엔드 개발자',
            '소프트웨어 엔지니어': 'Software Engineer',
            'Network Engineer': '네트워크 엔지니어',
            '네트워크 엔지니어': 'Network Engineer',
            'DevOps 엔지니어': 'DevOps Engineer',
            '백엔드 개발자': 'Backend Developer',
            '프론트 개발자': 'Frontend Developer',
            'ios 개발자': 'iOS Developer',
            '안드로이드 개발자': 'Android Developer',
            'RN 개발자': 'React Native Developer',
            '풀스택 개발자': 'Fullstack Developer',
            '게임 개발자': 'Game Developer',
            '블록체인 개발자': 'Blockchain Developer',
            '하드웨어 개발자': 'Hardware Developer',
            
            # 데이터/AI 관련
            '데이터 사이언티스트': 'Data Scientist',
            '데이터 엔지니어': 'Data Engineer',
            '데이터 분석가': 'Data Analyst',
            'AI 엔지니어': 'AI Engineer',
            'ML 엔지니어': 'ML Engineer',
            'Vision 엔지니어': 'Vision Engineer',
            '비전 엔지니어': 'Vision Engineer',
            
            # 기획/관리 관련 - 영어 직무명 추가 매핑
            '프로덕트 매니저': 'Product Manager',
            'PM': '프로덕트 매니저',  # PM → 프로덕트 매니저로 직접 매핑
            'PO': '서비스 기획자',    # PO → 서비스 기획자로 매핑
            'Product Manager': '프로덕트 매니저',
            'Product Owner': '서비스 기획자',
            'Tech PM': 'Technical Product Manager',
            '서비스 기획자': 'Service Planner',
            '프로젝트 매니저': 'Project Manager',
            
            # 운영/시스템 관련
            '시스템 엔지니어': 'System Engineer',
            '운영 엔지니어': 'Operations Engineer',
            '보안 엔지니어': 'Security Engineer',
            'QA 엔지니어': 'QA Engineer',
            'OS 엔지니어': 'OS Engineer',
            'XR 엔지니어': 'XR Engineer',
            
            # 디자인 관련
            '디자이너': 'Designer',
            'UI UX 디자이너': 'UI UX Designer',
            '프로덕트 디자이너': 'Product Designer',
            '콘텐츠 디자이너': 'Content Designer',
            '인테리어 디자이너': 'Interior Designer',
            
            # 비즈니스 관련 - 영어 직무명 추가 매핑
            '마케터': 'Marketer',
            '사업개발': 'Business Development',
            '경영지원': 'Business Support',
            '영업 담당': 'Sales Representative',
            '세일즈': 'Sales',
            '운영 매니저': 'Operations Manager',
            'CX 매니저': 'Customer Experience Manager',
            '그로스 매니저': 'Growth Manager',
            'QA 매니저': 'QA Manager',
            '커뮤니티 매니저': 'Community Manager',
            'MD': '마케터',  # MD → 마케터로 매핑
            
            # 기타 - 영어 직무명 추가 매핑
            'HR': 'HR',  # HR → HR로 유지 (career_position에 HR이 있음)
            'PR': 'PR',  # PR → PR로 유지 (career_position에 PR이 있음)
            'Human Resources': 'HR',
            'Public Relations': 'PR',
            '법무 담당': 'Legal Affairs',
            '재무 담당': 'Finance',
            '회계담당': 'Accounting',
            '연구원': 'Researcher',
            '전문연구요원': 'Professional Research Personnel',
            '퍼블리셔': 'Publisher',
            'SCM 매니저': 'Supply Chain Manager',
            '애자일 코치': 'Agile Coach',
            '투자심사역': 'Investment Analyst',
            'C Level': 'C Level Executive',
            '변호사': 'Lawyer'
        }
        
        # 양방향 매핑 구성
        for key, value in mapping_rules.items():
            if self._is_korean(key):
                self.korean_english_mapping[key] = value
                self.english_korean_mapping[value] = key
            else:
                self.english_korean_mapping[key] = value
                self.korean_english_mapping[value] = key
        
        # 키워드 매핑 (매칭에 사용할 키워드들)
        self._build_keyword_mapping()
        
        print(f"✅ 매핑 테이블 구성 완료")
        print(f"   - 한→영 매핑: {len(self.korean_english_mapping)}개")
        print(f"   - 영→한 매핑: {len(self.english_korean_mapping)}개")
        print(f"   - 키워드 매핑: {len(self.keyword_mapping)}개")
    
    def _build_keyword_mapping(self):
        """키워드 기반 매핑 테이블 구성"""
        
        # career_position의 각 직군에 대해 매칭 키워드 정의
        for pos_id, position_name in self.career_positions.items():
            keywords = []
            
            # 기본 키워드 (직군명 자체)
            keywords.append(position_name.lower())
            
            # 영어↔한국어 매핑이 있으면 추가
            if position_name in self.korean_english_mapping:
                keywords.append(self.korean_english_mapping[position_name].lower())
            if position_name in self.english_korean_mapping:
                keywords.append(self.english_korean_mapping[position_name].lower())
            
            # 직군별 추가 키워드 정의
            additional_keywords = self._get_additional_keywords(position_name)
            keywords.extend(additional_keywords)
            
            # 중복 제거 및 정리
            keywords = list(set([k.strip().lower() for k in keywords if k.strip()]))
            
            self.keyword_mapping[pos_id] = {
                'name': position_name,
                'keywords': keywords
            }
    
    def _get_additional_keywords(self, position_name: str) -> List[str]:
        """직군별 추가 키워드 정의"""
        additional_keywords = []
        
        name_lower = position_name.lower()

        # TODO : 쫌더 정밀하고 폭 넓게 분석 할 수 있는 방법?
        # 개발 관련
        if any(word in name_lower for word in ['개발자', 'developer', 'engineer']):
            if 'backend' in name_lower or '백엔드' in name_lower:
                additional_keywords.extend([
                    'backend', 'server', '서버', 'api', 'backend developer', 'server developer',
                    'software engineer', 'software development engineer', 'sde', 
                    'backend engineer', 'server engineer', 'backend software engineer', 'spring', 'django', 'nodejs', 'java', 'python'
                ])
            elif 'frontend' in name_lower or '프론트' in name_lower:
                additional_keywords.extend(['frontend', 'react', 'vue', 'angular', 'web', 'frontend engineer', 'front-end engineer', 'javascript', 'typescript', 'js', 'css', 'html'])
            elif 'ios' in name_lower:
                additional_keywords.extend(['swift', 'objective-c', 'xcode', 'ios engineer'])
            elif 'android' in name_lower or '안드로이드' in name_lower:
                additional_keywords.extend(['kotlin', 'java android', 'android studio', 'android engineer'])
            elif 'fullstack' in name_lower or '풀스택' in name_lower:
                additional_keywords.extend(['full stack', 'full-stack', 'fullstack engineer'])
            elif 'game' in name_lower or '게임' in name_lower:
                additional_keywords.extend(['unity', 'unreal', '게임엔진', 'game developer'])
            elif 'software' in name_lower or '소프트웨어' in name_lower:
                # Software Engineer는 기본적으로 백엔드로 매핑 (외국 기업에서 흔히 사용)
                additional_keywords.extend([
                    'software engineer', 'software development engineer', 'sde', 'sde ii', 'sde iii',
                    'senior software engineer', 'principal software engineer', 'staff software engineer',
                    'backend', 'server', 'api development', 'system design'
                ])
        
        # 데이터/AI 관련
        elif any(word in name_lower for word in ['데이터', 'data', 'ai', 'ml']):
            if 'scientist' in name_lower or '사이언티스트' in name_lower:
                additional_keywords.extend(['machine learning', 'python', 'r', 'statistics'])
            elif 'engineer' in name_lower and 'data' in name_lower:
                additional_keywords.extend(['etl', 'pipeline', 'bigdata', '빅데이터'])
            elif 'analyst' in name_lower or '분석가' in name_lower:
                additional_keywords.extend(['analytics', 'sql', 'tableau', 'visualization'])
        
        # 기획/관리 관련
        elif any(word in name_lower for word in ['매니저', 'manager', 'pm', 'po']):
            if 'product' in name_lower or '프로덕트' in name_lower:
                additional_keywords.extend(['product management', 'roadmap', 'strategy'])
            elif 'project' in name_lower or '프로젝트' in name_lower:
                additional_keywords.extend(['project management', 'agile', 'scrum'])
        
        # 디자인 관련
        elif any(word in name_lower for word in ['디자이너', 'designer', 'design']):
            if 'ui' in name_lower or 'ux' in name_lower:
                additional_keywords.extend(['figma', 'sketch', 'prototype', 'wireframe'])
            elif 'product' in name_lower:
                additional_keywords.extend(['user experience', 'interaction'])
        
        return additional_keywords
    
    def _is_korean(self, text: str) -> bool:
        """텍스트가 한국어인지 확인"""
        return bool(re.search(r'[가-힣]', text))
    
    def match_with_career_position(self, text: str) -> Optional[Dict]:
        """텍스트에서 career_position과 매칭되는 직군 찾기"""
        if not text:
            return None
        
        text_lower = text.lower()
        best_match = None
        max_score = 0
        
        for pos_id, mapping_info in self.keyword_mapping.items():
            score = 0
            matched_keywords = []
            
            for keyword in mapping_info['keywords']:
                if keyword in text_lower:
                    # 키워드 길이에 따른 가중치 (긴 키워드일수록 높은 점수)
                    keyword_score = len(keyword.split()) * 2 + len(keyword)
                    score += keyword_score
                    matched_keywords.append(keyword)
            
            if score > max_score:
                max_score = score
                best_match = {
                    'career_position_id': pos_id,
                    'career_position_name': mapping_info['name'],
                    'matched_keywords': matched_keywords,
                    'score': score
                }
        
        return best_match if max_score > 0 else None
    
    def get_position_info(self, position_id: int) -> Optional[Dict]:
        """career_position ID로 직군 정보 조회"""
        if position_id not in self.career_positions:
            return None
        
        position_name = self.career_positions[position_id]
        
        # 영어↔한국어 매핑 정보 포함
        english_name = self.korean_english_mapping.get(position_name)
        korean_name = self.english_korean_mapping.get(position_name)
        
        return {
            'id': position_id,
            'name': position_name,
            'english_name': english_name,
            'korean_name': korean_name,
            'keywords': self.keyword_mapping.get(position_id, {}).get('keywords', [])
        }
    
    def get_all_positions(self) -> Dict[int, str]:
        """모든 career_position 반환"""
        return self.career_positions.copy()

if __name__ == "__main__":
    # 테스트
    mapper = CareerPositionMapper()
    
    # 테스트 케이스
    test_cases = [
        "백엔드 개발자 모집",
        "Software Engineer Position",
        "데이터 사이언티스트 신입 채용",
        "React 프론트엔드 개발자",
        "Product Manager (PM) 경력직",
        "UI/UX 디자이너 채용"
    ]
    
    print("\n=== 매칭 테스트 ===")
    for test_text in test_cases:
        match_result = mapper.match_with_career_position(test_text)
        if match_result:
            print(f"입력: {test_text}")
            print(f"  → 매칭: {match_result['career_position_name']} (ID: {match_result['career_position_id']})")
            print(f"  → 키워드: {match_result['matched_keywords']}")
            print(f"  → 점수: {match_result['score']}")
        else:
            print(f"입력: {test_text} → 매칭 없음")
        print("---")