"""
채용공고 키워드 분석기
기존 분석 결과를 바탕으로 한 키워드 매핑
"""

from company_keywords import CompanyKeywords
import re

class JobKeywordsAnalyzer:
    """채용공고 키워드 분석기"""

    def __init__(self):
        """키워드 데이터 초기화"""
        self.job_role_keywords = {
            '🎨 프론트엔드': [
                'frontend', 'front-end', '프론트엔드', 'react', 'vue', 'angular',
                'javascript', 'typescript', 'html', 'css', 'ui', 'ux',
                'next.js', 'nuxt.js', 'svelte', 'webpack', 'vite',
                'frontend engineer', 'front-end engineer', 'ui engineer', 'web developer',
                'senior frontend', 'lead frontend', 'principal frontend'
            ],
            '🔧 백엔드': [
                # 한국어 키워드 (확장)
                'backend', 'back-end', '백엔드', '백앤드', 'server', '서버', '서버개발', '서버 개발',
                '서버 개발자', '서버개발자', '서버 엔지니어', '서버엔지니어', 'BE개발자', 'BE 개발자',
                '백엔드 개발자', '백엔드개발자', '백엔드 엔지니어', '시스템개발', '시스템 개발',
                'API개발', 'API 개발', 'API 개발자', 'API개발자', '웹 서버', '웹서버',
                
                # 영어 키워드 (대폭 확장 - 외국 기업용)
                'backend engineer', 'back-end engineer', 'server engineer', 'backend developer',
                'backend dev', 'server developer', 'server dev', 'systems engineer', 'system engineer',
                'software engineer', 'software development engineer', 'senior software engineer', 
                'principal engineer', 'staff engineer', 'principal software engineer', 'staff software engineer',
                'software engineer ii', 'software engineer iii', 'sde', 'sde ii', 'sde iii',
                'senior sde', 'principal sde', 'software development engineer ii', 'software development engineer iii',
                'backend software engineer', 'server software engineer', 'distributed systems engineer',
                'server side engineer', 'server-side engineer', 'api engineer', 'platform engineer',
                'infrastructure software engineer', 'systems software engineer', 'backend architect',
                
                # 기술 스택 기반 (회사별 흔한 표현)
                'java engineer', 'python engineer', 'go engineer', 'kotlin engineer', 'scala engineer',
                'spring developer', 'django developer', 'node.js engineer', 'microservices engineer',
                'distributed systems', 'scalability engineer', 'performance engineer',
                
                # 기술 키워드 (실제 DB 데이터 기반 확장)
                'spring', 'spring boot', 'django', 'flask', 'express', 'node.js', 'nodejs',
                'java', 'python', 'php', 'go', 'golang', 'kotlin', 'scala', 'ruby', 'rails',
                '.net', 'dotnet', 'c#', 'microservice', 'microservices', 'api development',
                'rest api', 'graphql', 'grpc', 'database', '데이터베이스', 'cloud engineer',
                
                # DB 분석에서 발견된 실제 키워드들 추가
                'api', 'server', 'database', 'mysql', 'postgresql', 'mongodb', 'redis',
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'unix',
                'restful', 'microservice', 'architecture', 'design patterns', 'algorithms',
                'data structures', 'system design', 'scalability', 'performance',
                'tcp/ip', 'http', 'https', 'ssl', 'security'
            ],
            '🤖 AI/머신러닝': [
                'ai', 'ml', '머신러닝', '인공지능', 'machine learning', 'deep learning',
                'data scientist', '데이터사이언티스트', 'nlp', 'computer vision',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
                'machine learning engineer', 'ml engineer', 'ai engineer', 'data science engineer',
                'senior data scientist', 'lead data scientist', 'principal data scientist',
                'ai specialist', 'ml specialist', 'computer vision engineer'
            ],
            '📱 모바일': [
                'mobile', '모바일', 'android', 'ios', 'swift', 'kotlin', 'flutter',
                'react native', 'xamarin', '앱개발', 'app development'
            ],
            '📊 데이터 분석': [
                '데이터분석', 'data analyst', 'business analyst', 'bi', 'analytics',
                'tableau', 'power bi', '데이터 애널리스트', 'sql', '통계', 'statistics'
            ],
            '🛠️ DevOps': [
                'devops', 'sre', 'infrastructure', '인프라', 'cloud', 'aws', 'azure',
                'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform'
            ],
            '🎮 게임 개발': [
                'game', '게임', 'unity', 'unreal', 'c#', 'c++', '게임개발',
                'game development', '게임엔진'
            ],
            '💼 기획/PM': [
                'pm', 'product manager', '기획', '프로덕트매니저', 'project manager',
                '서비스기획', '상품기획', 'planning',
                'engineering manager', 'engineering program manager', 'technical program manager',
                'senior product manager', 'lead product manager', 'program manager',
                'product owner', 'scrum master', 'project coordinator'
            ],
            '🎨 디자인': [
                'design', '디자인', 'ui design', 'ux design', 'graphic design',
                'figma', 'sketch', 'adobe', 'photoshop', 'illustrator'
            ],
            '💼 비즈니스': [
                'business', '비즈니스', 'marketing', '마케팅', 'sales', '영업',
                'strategy', '전략', 'consulting', '컨설팅'
            ],
            '👥 고객지원': [
                'customer success', 'customer support', 'account manager', 'client success',
                'customer service', 'technical support', 'support specialist', 'success manager',
                '고객지원', '고객성공', '고객서비스', 'customer experience'
            ],
            '💰 재무/회계': [
                'finance', 'financial analyst', 'accounting', 'finance assistant',
                'financial planning', 'budget analyst', 'controller', 'treasurer',
                '재무', '회계', '경리', 'financial operations'
            ],
            '🧑‍💼 인사/HR': [
                'hr', 'human resources', 'talent acquisition', 'recruiter', 'people operations',
                'hr specialist', 'hr manager', 'talent manager', '인사', '채용',
                'people partner', 'hr business partner'
            ],
            '⚖️ 법무/컴플라이언스': [
                'legal', 'legal counsel', 'compliance', 'legal affairs', 'attorney',
                'compliance officer', 'legal specialist', '법무', '컴플라이언스',
                'regulatory affairs', 'legal operations'
            ]
        }

        self.tech_stack_categories = {
            '언어': {
                'JavaScript': ['javascript', 'js', 'node.js', 'nodejs'],
                'TypeScript': ['typescript', 'ts'],
                'Python': ['python', 'py'],
                'Java': ['java'],
                'React': ['react', 'reactjs', 'react.js'],
                'Vue': ['vue', 'vuejs', 'vue.js'],
                'Angular': ['angular', 'angularjs'],
                'Spring': ['spring', 'spring boot', 'springboot'],
                'Django': ['django'],
                'Flask': ['flask'],
                'Express': ['express', 'expressjs'],
                'PHP': ['php'],
                'Go': ['go', 'golang'],
                'Kotlin': ['kotlin'],
                'Swift': ['swift'],
                'C++': ['c++', 'cpp'],
                'C#': ['c#', 'csharp'],
                'Ruby': ['ruby', 'rails'],
                'Scala': ['scala']
            },
            '데이터베이스': {
                'MySQL': ['mysql'],
                'PostgreSQL': ['postgresql', 'postgres'],
                'MongoDB': ['mongodb', 'mongo'],
                'Redis': ['redis'],
                'Oracle': ['oracle'],
                'SQL Server': ['sql server', 'sqlserver', 'mssql'],
                'MariaDB': ['mariadb'],
                'Elasticsearch': ['elasticsearch', 'elastic'],
                'DynamoDB': ['dynamodb']
            },
            '클라우드/인프라': {
                'AWS': ['aws', 'amazon web services'],
                'Azure': ['azure', 'microsoft azure'],
                'GCP': ['gcp', 'google cloud'],
                'Docker': ['docker'],
                'Kubernetes': ['kubernetes', 'k8s'],
                'Jenkins': ['jenkins'],
                'GitLab': ['gitlab'],
                'Terraform': ['terraform'],
                'Ansible': ['ansible']
            },
            'AI/ML': {
                'TensorFlow': ['tensorflow'],
                'PyTorch': ['pytorch'],
                'Keras': ['keras'],
                'Scikit-learn': ['scikit-learn', 'sklearn'],
                'Pandas': ['pandas'],
                'NumPy': ['numpy'],
                'Jupyter': ['jupyter'],
                'R': ['r language', 'r programming'],
                'Spark': ['apache spark', 'spark']
            }
        }

        self.experience_levels = {
            '신입': [
                '신입', 'junior', '주니어', '0년', '0-1년', '경력없음',
                'entry-level', 'entry level', 'new grad', 'fresh graduate',
                'college hire', 'university graduate', '0-2 years', '0 to 2 years',
                'recent graduate', 'graduate level'
            ],
            '1-2년': [
                '1년', '2년', '1-2년', '1~2년', '1 year', '2 years',
                '1-2 years', '1 to 2 years', '2+ years', 'associate level',
                '1+ years', 'minimum 1 year', 'at least 1 year'
            ],
            '3-5년': [
                '3년', '4년', '5년', '3-5년', '3~5년', 'mid', '미드',
                '3 years', '4 years', '5 years', '3-5 years', '3 to 5 years',
                '3+ years', '4+ years', '5+ years', 'mid-level', 'mid level',
                'minimum 3 years', 'at least 3 years'
            ],
            '6-10년': [
                '6년', '7년', '8년', '9년', '10년', '6-10년', 'senior', '시니어',
                '6 years', '7 years', '8 years', '9 years', '10 years',
                '6-10 years', '6 to 10 years', '6+ years', '7+ years', '8+ years',
                '9+ years', '10+ years', 'senior level', 'experienced'
            ],
            '10년+': [
                '10년+', '10년 이상', '시니어+', 'staff', 'principal', 'lead',
                '10+ years', 'more than 10 years', 'over 10 years',
                'staff level', 'principal level', 'lead level', 'expert level',
                'minimum 10 years', 'at least 10 years', '15+ years'
            ]
        }

        self.salary_ranges_usd = {
            '60K-80K': (60000, 80000),
            '80K-100K': (80000, 100000),
            '100K-120K': (100000, 120000),
            '120K-150K': (120000, 150000),
            '150K-200K': (150000, 200000),
            '200K+': (200000, 999999)
        }

        self.salary_ranges_krw = {
            '3000만원-4000만원': (30000000, 40000000),
            '4000만원-5000만원': (40000000, 50000000),
            '5000만원-6000만원': (50000000, 60000000),
            '6000만원-7000만원': (60000000, 70000000),
            '7000만원-8000만원': (70000000, 80000000),
            '8000만원+': (80000000, 999999999)
        }

        self.company_classifier = CompanyKeywords()

    # === 개선된 직무 분류 로직 ===
    def classify_job_role(self, text, company_name=None):
        if not text:
            return '기타'
        
        text_lower = text.lower().strip()
        
        # 비개발 직무 제외 (우선 확인)
        non_dev_keywords = [
            '연구기획', 'r&d', '생산', '현장직', '제조', '품질관리', 'qa', '영업', '마케팅',
            '인사', 'hr', '재무', '회계', '경리', '법무', '구매', '조달', '물류',
            '신규사업담당', '사업기획', '경영기획', '전략기획', '기획팀',
            '배터리시스템', '차량 성능개발', '친환경차', '자동차', '기계',
            'operations technician', 'data center operations', 'hardware systems'
        ]
        
        for keyword in non_dev_keywords:
            if keyword in text_lower:
                # 개발 관련 키워드가 함께 있지 않으면 제외
                dev_keywords = ['engineer', 'developer', 'programming', 'software', 'backend', 'frontend']
                has_dev = any(dev_kw in text_lower for dev_kw in dev_keywords)
                if not has_dev:
                    return '기타'
        
        # 기업 유형 판단
        is_korean = self.company_classifier.is_korean_company(company_name) if company_name else True
        is_foreign = self.company_classifier.is_foreign_company(company_name) if company_name else False
        
        # 직무별 키워드 매칭 (가중치 적용)
        role_scores = {}
        
        for role, keywords in self.job_role_keywords.items():
            score = 0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    # 정확한 단어 매치에 더 높은 점수
                    if keyword_lower == text_lower or f' {keyword_lower} ' in f' {text_lower} ':
                        score += 3
                    else:
                        score += 1
            
            if score > 0:
                role_scores[role] = score
        
        # 특별 패턴 매칭 (외국 기업 직무)
        if is_foreign:
            english_patterns = {
                '🔧 백엔드': ['software engineer', 'backend engineer', 'server engineer', 'sde', 'backend developer', 'data engineer'],
                '🎨 프론트엔드': ['frontend engineer', 'front-end engineer', 'ui engineer', 'frontend developer'],
                '🤖 AI/머신러닝': ['machine learning engineer', 'ml engineer', 'data scientist', 'ai engineer'],
                '📱 모바일': ['mobile engineer', 'ios engineer', 'android engineer', 'mobile developer'],
                '💼 기획/PM': ['product manager', 'program manager', 'technical program manager', 'engineering manager'],
                '🛠️ DevOps': ['devops engineer', 'site reliability engineer', 'infrastructure engineer', 'cloud engineer'],
                '👥 고객지원': ['customer success', 'customer support', 'technical support', 'support engineer']
            }
            
            for role, patterns in english_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        if role in role_scores:
                            role_scores[role] += 5  # 외국 기업 특화 패턴에 높은 점수
                        else:
                            role_scores[role] = 5
        
        # 개발자 직무 우선 처리 ('engineer', 'developer' 키워드가 있는 경우)
        if any(kw in text_lower for kw in ['engineer', 'developer', 'programmer']):
            # 백엔드 우선 점수 부여
            if any(kw in text_lower for kw in ['software', 'backend', 'server', 'api', 'database']):
                if '🔧 백엔드' in role_scores:
                    role_scores['🔧 백엔드'] += 2
                else:
                    role_scores['🔧 백엔드'] = 2
        
        # 최고 점수 직무 반환
        if role_scores:
            best_role = max(role_scores.items(), key=lambda x: x[1])[0]
            return best_role
        
        return '기타'

    def _get_english_job_role(self, korean_role):
        """한국어 직무명을 영어로 변환 (현재는 사용하지 않음)"""
        mapping = {
            "🎨 프론트엔드": "🎨 Frontend",
            "🔧 백엔드": "🔧 Backend", 
            "🤖 AI/머신러닝": "🤖 AI/ML",
            "📱 모바일": "📱 Mobile",
            "📊 데이터 분석": "📊 Data Analysis",
            "🛠️ DevOps": "🛠️ DevOps",
            "🎮 게임 개발": "🎮 Game Dev",
            "💼 기획/PM": "💼 PM/Product",
            "🎨 디자인": "🎨 Design",
            "💼 비즈니스": "💼 Business",
            "👥 고객지원": "👥 Customer Support",
            "💰 재무/회계": "💰 Finance/Accounting",
            "🧑‍💼 인사/HR": "🧑‍💼 HR",
            "⚖️ 법무/컴플라이언스": "⚖️ Legal/Compliance"
        }
        return mapping.get(korean_role, "기타")

    def get_job_role_filter_options(self):
        return list(self.job_role_keywords.keys())

    def get_tech_stack_options(self, job_role=None):
        if job_role and job_role in self.job_role_keywords:
            role_keywords = self.job_role_keywords[job_role]
            relevant_techs = []
            for category, techs in self.tech_stack_categories.items():
                for tech, keywords in techs.items():
                    if any(keyword in ' '.join(role_keywords).lower() for keyword in keywords):
                        relevant_techs.append(tech)
            if '🎨 프론트엔드' in job_role:
                relevant_techs.extend(['React', 'Vue', 'Angular', 'JavaScript', 'TypeScript'])
            elif '🔧 백엔드' in job_role:
                relevant_techs.extend(['Spring', 'Django', 'Node.js', 'Java', 'Python'])
            elif '🤖 AI' in job_role:
                relevant_techs.extend(['TensorFlow', 'PyTorch', 'Python', 'Pandas', 'NumPy'])
            elif '📱 모바일' in job_role:
                relevant_techs.extend(['React Native', 'Flutter', 'Swift', 'Kotlin'])
            elif '🛠️ DevOps' in job_role:
                relevant_techs.extend(['AWS', 'Docker', 'Kubernetes', 'Jenkins'])
            return list(set(relevant_techs))
        all_techs = []
        for category, techs in self.tech_stack_categories.items():
            all_techs.extend(techs.keys())
        return all_techs

    def get_experience_options(self):
        return list(self.experience_levels.keys())

    def get_salary_ranges(self, currency='USD'):
        if currency == 'KRW':
            return self.salary_ranges_krw
        return self.salary_ranges_usd

    def extract_tech_stacks(self, text):
        text_lower = text.lower() if text else ""
        found_techs = []
        for category, techs in self.tech_stack_categories.items():
            for tech, keywords in techs.items():
                if any(keyword.lower() in text_lower for keyword in keywords):
                    found_techs.append(tech)
        return found_techs

    def classify_experience(self, text):
        if not text or not str(text).strip():
            return '정보 없음'
            
        text_lower = str(text).lower().strip()
        
        # 1순위: 직접적인 키워드 매칭
        for level, keywords in self.experience_levels.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                return level
        
        # 2순위: 숫자 패턴 매칭 (더 포괄적으로)
        patterns = [
            r'(\d+)\+?\s*years?\s*(of\s*)?experience',
            r'(\d+)\s*to\s*(\d+)\s*years',
            r'(\d+)-(\d+)\s*years',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?',
            r'(\d+)\s*years?\s*minimum',
            r'(\d+)\s*년\s*이상',
            r'(\d+)\s*년차',
            r'(\d+)년\s*경력',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    if isinstance(matches[0], tuple):
                        years = int(matches[0][0]) if matches[0][0] else int(matches[0][1])
                    else:
                        years = int(matches[0])
                    
                    if years == 0:
                        return '신입'
                    elif 1 <= years <= 2:
                        return '1-2년'
                    elif 3 <= years <= 5:
                        return '3-5년'
                    elif 6 <= years <= 10:
                        return '6-10년'
                    else:
                        return '10년+'
                except (ValueError, IndexError):
                    continue
        
        # 3순위: 일반적인 숫자 찾기
        numbers = re.findall(r'\d+', text_lower)
        if numbers:
            try:
                years = int(numbers[0])
                if years == 0:
                    return '신입'
                elif 1 <= years <= 2:
                    return '1-2년'
                elif 3 <= years <= 5:
                    return '3-5년'
                elif 6 <= years <= 10:
                    return '6-10년'
                else:
                    return '10년+'
            except (ValueError, IndexError):
                pass
        
        # 4순위: 특별 키워드 기반 추론
        if any(kw in text_lower for kw in ['junior', '주니어', 'entry', 'graduate', '졸업']):
            return '1-2년'
        elif any(kw in text_lower for kw in ['senior', '시니어', 'lead', '리드', 'principal', '수석']):
            return '6-10년'
        elif any(kw in text_lower for kw in ['staff', 'expert', '전문가', 'architect', '아키텍트']):
            return '10년+'
        elif any(kw in text_lower for kw in ['mid', 'middle', '중급', 'intermediate']):
            return '3-5년'
        
        # 5순위: 제목 기반 추론 (더 포괄적으로)
        if any(kw in text_lower for kw in ['intern', '인턴', 'trainee', '신입', 'new grad', 'fresh graduate', 'entry level', 'college hire']):
            return '신입'
        
        # 6순위: 경력무관/무관 키워드가 있으면서 다른 경력 표시가 없는 경우 신입으로 간주
        if any(kw in text_lower for kw in ['경력무관', '경력 무관', '무관', '신입가능', '신입 가능', '신입/경력', '신입 및 경력']):
            # 다른 경력 요구사항이 명시되어 있지 않으면 신입으로 분류
            has_specific_exp = any(pattern in text_lower for pattern in [
                'years', '년', '이상', '년차', 'minimum', 'required', 'experience'
            ])
            if not has_specific_exp:
                return '신입'
        
        return '경력무관'  # "미분류" 대신 "경력무관"으로 변경

    def get_recommended_filters(self, analysis_data=None):
        recommendations = {
            'popular_roles': ['🔧 백엔드', '🎨 프론트엔드', '🤖 AI/머신러닝'],
            'hot_techs': ['React', 'Spring', 'Python', 'JavaScript', 'AWS'],
            'high_demand_experience': ['3-5년', '1-2년'],
            'trending_companies': ['네이버', '카카오', '쿠팡', '토스', '라인']
        }
        return recommendations

    # ===== 회사 분류 함수들 (CompanyKeywords 사용) =====
    def classify_korean_tech_company(self, company_name):
        return self.company_classifier.classify_korean_tech_company(company_name)

    def get_korean_tech_companies_list(self):
        return self.company_classifier.get_korean_tech_companies_list()

    def is_korean_tech_company(self, company_name):
        return self.company_classifier.is_korean_tech_company(company_name) is not None

    def is_korean_company(self, company_name):
        return self.company_classifier.is_korean_company(company_name)

    def is_foreign_company(self, company_name):
        return self.company_classifier.is_foreign_company(company_name)
