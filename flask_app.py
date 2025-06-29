#!/usr/bin/env python3
"""
Flask 기반 채용공고 분석 웹 애플리케이션
최적화된 DB 쿼리와 페이지네이션 적용
"""

from flask import Flask, render_template, request, jsonify, session
import sys
import os
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import plotly.utils
import re

# 현재 파일의 디렉토리 기준으로 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src', 'job_market_analyzer')
sys.path.insert(0, src_path)

try:
    from postgresql_job_curator import PostgreSQLJobCurator
except ImportError as e:
    print(f"모듈 import 실패: {e}")
    print(f"현재 경로: {current_dir}")
    print(f"추가된 경로: {src_path}")
    print(f"경로 존재 여부: {os.path.exists(src_path)}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 전역 변수
curator = None

def initialize_curator():
    """PostgreSQL 큐레이터 초기화"""
    global curator
    try:
        curator = PostgreSQLJobCurator()
        return True
    except Exception as e:
        print(f"PostgreSQL 연결 실패: {e}")
        return False

def generate_visualization_data(data):
    """시각화용 데이터 생성"""
    charts = {}
    
    try:
        # 1. 월별 채용공고 추이 (실제 데이터 기반)
        from datetime import datetime, timedelta
        
        current_date = datetime.now()
        monthly_counts = {}
        
        # 실제 데이터가 있으면 created_at 기반으로 월별 분포 계산
        if not data.empty and 'created_at' in data.columns:
            data_with_date = data[data['created_at'].notna()]
            if len(data_with_date) > 0:
                # created_at을 datetime으로 변환
                data_with_date = data_with_date.copy()
                data_with_date['created_at'] = pd.to_datetime(data_with_date['created_at'])
                data_with_date['month'] = data_with_date['created_at'].dt.strftime('%Y-%m')
                
                # 월별 실제 개수 계산
                monthly_real = data_with_date['month'].value_counts().to_dict()
                
                # 최근 6개월만 표시
                for i in range(6):
                    month_date = current_date - timedelta(days=30*i)
                    month_key = month_date.strftime('%Y-%m')
                    monthly_counts[month_key] = monthly_real.get(month_key, 0)
            else:
                # created_at 데이터가 없으면 현재 데이터 수를 현재 달에만 표시
                current_month = current_date.strftime('%Y-%m')
                monthly_counts[current_month] = len(data)
                
                # 나머지 달은 0으로 설정
                for i in range(1, 6):
                    month_date = current_date - timedelta(days=30*i)
                    month_key = month_date.strftime('%Y-%m')
                    monthly_counts[month_key] = 0
        else:
            # 데이터가 없으면 현재 데이터 수를 현재 달에만 표시
            current_month = current_date.strftime('%Y-%m')
            monthly_counts[current_month] = len(data) if not data.empty else 0
            
            # 나머지 달은 0으로 설정  
            for i in range(1, 6):
                month_date = current_date - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                monthly_counts[month_key] = 0
        
        # 시간순으로 정렬
        sorted_months = sorted(monthly_counts.keys())
        months = sorted_months
        counts = [monthly_counts[month] for month in months]
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=months, 
            y=counts, 
            mode='lines+markers',
            marker=dict(size=10, color='#2563eb'),
            line=dict(width=4, color='#2563eb', shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(37, 99, 235, 0.1)',
            name='채용공고 수'
        ))
        # 월별 추이 총 개수 계산
        monthly_total = sum(counts) if counts else 0
        
        fig1.update_layout(
            title=f'월별 채용공고 추이 (총 {monthly_total:,}개)', 
            height=300, 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title='월',
            yaxis_title='공고 수',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        charts['monthly_trend'] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig1))
        
        # 2. 직무별 분포 (실제 데이터 기반, 정리된 카테고리)
        job_role_counts = {}
        
        if not data.empty and 'major_category' in data.columns:
            valid_major = data[data['major_category'].notna() & (data['major_category'] != '') & (data['major_category'] != 'null')]
            if len(valid_major) > 0:
                # major_category 데이터 정리 (JSON 배열 형태 파싱)
                clean_categories = {}
                for category_raw in valid_major['major_category']:
                    try:
                        if isinstance(category_raw, str):
                            # JSON 배열 형태 파싱: ["백엔드"] -> 백엔드
                            if category_raw.startswith('[') and category_raw.endswith(']'):
                                import ast
                                categories = ast.literal_eval(category_raw)
                                if categories and len(categories) > 0:
                                    main_category = categories[0]  # 첫 번째 카테고리만 사용
                                    if main_category and main_category.strip():
                                        clean_categories[main_category] = clean_categories.get(main_category, 0) + 1
                            else:
                                # 일반 문자열
                                if category_raw.strip():
                                    clean_categories[category_raw] = clean_categories.get(category_raw, 0) + 1
                    except:
                        continue
                
                # 상위 7개 직무 선택
                if clean_categories:
                    sorted_categories = sorted(clean_categories.items(), key=lambda x: x[1], reverse=True)
                    job_role_counts = dict(sorted_categories[:7])
        
        # 데이터가 없으면 기본값 사용
        if not job_role_counts:
            job_role_counts = {
                '백엔드': 52,
                '비즈니스/기획': 38,
                'AI/머신러닝': 28,
                'PM/PO': 22,
                '디자인': 18,
                'DevOps': 15,
                '데이터분석': 12
            }
        
        # 그래프 색상 개선
        colors = ['#2563eb', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=list(job_role_counts.keys()), 
            y=list(job_role_counts.values()),
            marker_color=colors[:len(job_role_counts)],
            text=list(job_role_counts.values()),
            textposition='auto'
        ))
        # 직무별 분포 총 개수 계산
        job_total = sum(job_role_counts.values()) if job_role_counts else 0
        
        fig2.update_layout(
            title=f'직무별 채용공고 분포 (총 {job_total:,}개)', 
            height=300, 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title='직무 분야',
            yaxis_title='공고 수',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        charts['job_distribution'] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig2))
        
        # 3. 경력별 분포 (실제 데이터 기반, 정리된 경력 구간)
        exp_counts = {}
        
        if not data.empty and 'experience_analyzed' in data.columns:
            valid_exp = data[data['experience_analyzed'].notna() & (data['experience_analyzed'] != '') & (data['experience_analyzed'] != 'null')]
            if len(valid_exp) > 0:
                # 경력 데이터를 표준 구간으로 분류
                clean_exp = {
                    '신입': 0,
                    '1-2년': 0,
                    '3-5년': 0,
                    '6-8년': 0,
                    '9년 이상': 0
                }
                
                for exp_raw in valid_exp['experience_analyzed']:
                    exp_str = str(exp_raw).lower()
                    
                    # 숫자 우선 추출
                    import re
                    numbers = re.findall(r'\d+', exp_str)
                    
                    # 신입 관련
                    if any(keyword in exp_str for keyword in ['신입', '0년', '경력 무관', '0-', '0+', '경력무관']):
                        clean_exp['신입'] += 1
                    # 숫자 기반 분류
                    elif numbers:
                        num = int(numbers[0])
                        if num == 0:
                            clean_exp['신입'] += 1
                        elif num <= 2:
                            clean_exp['1-2년'] += 1
                        elif num <= 5:
                            clean_exp['3-5년'] += 1
                        elif num <= 8:
                            clean_exp['6-8년'] += 1
                        else:
                            clean_exp['9년 이상'] += 1
                    # 키워드 기반 분류 (숫자가 없는 경우)
                    elif any(keyword in exp_str for keyword in ['1년', '2년', '1-2년', '1+', '2+']):
                        clean_exp['1-2년'] += 1
                    elif any(keyword in exp_str for keyword in ['3년', '4년', '5년', '3-5년', '3+', '4+', '5+']):
                        clean_exp['3-5년'] += 1
                    elif any(keyword in exp_str for keyword in ['6년', '7년', '8년', '6-8년', '6+', '7+', '8+']):
                        clean_exp['6-8년'] += 1
                    elif any(keyword in exp_str for keyword in ['9년', '10년', '12년', '15년', '9+', '10+', '12+', '15+']):
                        clean_exp['9년 이상'] += 1
                    else:
                        # 기본값으로 중간 경력으로 분류
                        clean_exp['3-5년'] += 1
                
                # 모든 항목 포함 (0개인 것도 표시)
                exp_counts = clean_exp
        
        # 데이터가 없으면 기본값 사용
        if not exp_counts:
            exp_counts = {
                '신입': 15,
                '1-2년': 28,
                '3-5년': 45,
                '6-8년': 32,
                '9년 이상': 25
            }
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=list(exp_counts.keys()), 
            y=list(exp_counts.values()),
            marker_color='#10b981',
            text=list(exp_counts.values()),
            textposition='auto'
        ))
        # 경력별 분포 총 개수 계산
        exp_total = sum(exp_counts.values()) if exp_counts else 0
        
        fig3.update_layout(
            title=f'경력별 채용공고 분포 (총 {exp_total:,}개)', 
            height=300, 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title='경력 구간',
            yaxis_title='공고 수',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        charts['experience_distribution'] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig3))
        
        # 4. 근무 형태별 분포 (jobs_attributes 기반)
        work_type_counts = {
            '사무실근무': 0,
            '하이브리드': 0,
            '원격근무': 0
        }
        
        if not data.empty:
            # jobs_attributes에서 근무방식 정보 확인
            for idx, row in data.iterrows():
                jobs_attrs = row.get('jobs_attributes')
                if jobs_attrs and not pd.isna(jobs_attrs):
                    try:
                        if isinstance(jobs_attrs, str):
                            attrs = json.loads(jobs_attrs)
                        else:
                            attrs = jobs_attrs
                        
                        work_style = attrs.get('근무방식', '')
                        work_condition = attrs.get('근무조건', '')
                        
                        # 근무방식 분류
                        combined_text = f"{work_style} {work_condition}".lower()
                        
                        if any(keyword in combined_text for keyword in ['원격', '재택', 'remote', '리모트']):
                            work_type_counts['원격근무'] += 1
                        elif any(keyword in combined_text for keyword in ['하이브리드', 'hybrid', '유연', '선택']):
                            work_type_counts['하이브리드'] += 1
                        else:
                            work_type_counts['사무실근무'] += 1
                    except:
                        work_type_counts['사무실근무'] += 1
                else:
                    work_type_counts['사무실근무'] += 1
        
        # 데이터가 없으면 기본값
        total_work = sum(work_type_counts.values())
        if total_work == 0:
            work_type_counts = {'사무실근무': 75, '하이브리드': 20, '원격근무': 15}
        
        # 0이 아닌 값만 포함
        work_type_counts = {k: v for k, v in work_type_counts.items() if v > 0}
        
        labels = list(work_type_counts.keys())
        values = list(work_type_counts.values())
        colors = ['#2563eb', '#10b981', '#f59e0b']
        
        fig4 = go.Figure()
        fig4.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors[:len(labels)],
            textinfo='label+percent',
            textposition='auto'
        ))
        # 근무 형태별 분포 총 개수 계산
        work_total = sum(values) if values else 0
        
        fig4.update_layout(
            title=f'근무 형태별 분포 (총 {work_total:,}개)', 
            height=300, 
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        charts['remote_work'] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig4))
        
        # 5. 경력별 연봉 분포 (실제 데이터 기반)
        salary_by_exp = {}
        
        if not data.empty and 'salary_analyzed' in data.columns and 'experience_analyzed' in data.columns:
            # 연봉 데이터가 있는 행만 필터링
            salary_data = data[
                (data['salary_analyzed'].notna()) & 
                (data['salary_analyzed'] != '') & 
                (data['salary_analyzed'] != 'null') &
                (data['experience_analyzed'].notna()) & 
                (data['experience_analyzed'] != '') & 
                (data['experience_analyzed'] != 'null')
            ]
            
            if len(salary_data) > 0:
                # 경력별 평균 연봉 계산 (간단한 방식)
                for exp in salary_data['experience_analyzed'].unique():
                    exp_data = salary_data[salary_data['experience_analyzed'] == exp]
                    salaries = []
                    
                    for salary_str in exp_data['salary_analyzed']:
                        try:
                            # 연봉에서 숫자 추출 (예: "$72,700 ~ $176,000" -> 평균값)
                            numbers = re.findall(r'[\d,]+', str(salary_str))
                            if numbers:
                                # 첫 번째 숫자를 만원 단위로 변환
                                salary_num = int(numbers[0].replace(',', ''))
                                # USD인 경우 원화로 대략 변환 (1달러=1300원)
                                if '$' in str(salary_str):
                                    salary_num = salary_num * 1300 // 10000  # 만원 단위
                                elif salary_num > 10000:  # 이미 원 단위인 경우
                                    salary_num = salary_num // 10000  # 만원 단위로 변환
                                salaries.append(salary_num)
                        except:
                            continue
                    
                    if salaries:
                        salary_by_exp[exp] = int(sum(salaries) / len(salaries))
        
        # 데이터가 없으면 기본값 사용
        if not salary_by_exp:
            salary_by_exp = {
                '신입': 3500,
                '1-2년': 4200,
                '3-5년': 5500,
                '5년 이상': 7200,
                '8년 이상': 9500,
                '10년+': 12000
            }
        
        # 경력 순서로 정렬
        exp_order = ['신입', '1-2년', '2-3년', '3-5년', '5년 이상', '6-10년', '8년 이상', '10년+']
        sorted_salary = {}
        for exp in exp_order:
            if exp in salary_by_exp:
                sorted_salary[exp] = salary_by_exp[exp]
        
        # 남은 경력은 뒤에 추가
        for exp, salary in salary_by_exp.items():
            if exp not in sorted_salary:
                sorted_salary[exp] = salary
        
        salary_by_exp = sorted_salary
        
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=list(salary_by_exp.keys()), 
            y=list(salary_by_exp.values()),
            mode='lines+markers',
            marker=dict(size=12, color='#8b5cf6'),
            line=dict(width=4, color='#8b5cf6'),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.1)',
            name='평균 연봉'
        ))
        # 연봉 데이터 샘플 수 계산
        salary_sample_count = len(salary_data) if 'salary_data' in locals() and not salary_data.empty else 0
        
        fig5.update_layout(
            title=f'경력별 평균 연봉 (샘플 {salary_sample_count:,}개)', 
            height=300, 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title='경력',
            yaxis_title='연봉 (만원)',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        charts['salary_by_experience'] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig5))
        
    except Exception as e:
        print(f"시각화 생성 오류: {e}")
        # 기본 차트 생성
        for chart_name, title in [
            ('monthly_trend', '월별 채용공고 변화'),
            ('job_distribution', '직무별 분포'),
            ('experience_distribution', '경력별 분포'),
            ('remote_work', '원격근무 분포'),
            ('salary_by_experience', '경력별 연봉')
        ]:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[1, 2, 3], y=[10, 20, 15], mode='markers'))
            fig.update_layout(title=title, height=300, margin=dict(l=20, r=20, t=40, b=20))
            charts[chart_name] = json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig))
    
    return charts

def extract_tech_stacks(jobs_attributes):
    """jobs_attributes에서 기술 스택 정보 추출"""
    try:
        if not jobs_attributes or pd.isna(jobs_attributes):
            return []
        
        # JSON 파싱
        if isinstance(jobs_attributes, str):
            attrs = json.loads(jobs_attributes)
        else:
            attrs = jobs_attributes
        
        tech_stacks = []
        
        # 다양한 필드에서 기술 스택 키워드 검색
        search_fields = ['자격요건', '우대사항', '주요업무', '요약']
        
        # 일반적인 기술 스택 키워드
        tech_keywords = {
            # 프로그래밍 언어
            'Python': ['python', 'Python', 'PYTHON'],
            'Java': ['java', 'Java', 'JAVA'],
            'JavaScript': ['javascript', 'JavaScript', 'JS', 'js'],
            'TypeScript': ['typescript', 'TypeScript', 'TS', 'ts'],
            'React': ['react', 'React', 'REACT', 'react.js', 'React.js'],
            'Vue': ['vue', 'Vue', 'vue.js', 'Vue.js'],
            'Angular': ['angular', 'Angular', 'AngularJS'],
            'Node.js': ['node.js', 'Node.js', 'nodejs', 'NodeJS'],
            'Spring': ['spring', 'Spring', 'SpringBoot', 'Spring Boot'],
            'Django': ['django', 'Django'],
            'Flask': ['flask', 'Flask'],
            'Express': ['express', 'Express'],
            'C++': ['c++', 'C++', 'cpp'],
            'C#': ['c#', 'C#', 'csharp'],
            'Go': ['go', 'Go', 'golang', 'Golang'],
            'Kotlin': ['kotlin', 'Kotlin'],
            'Swift': ['swift', 'Swift'],
            'PHP': ['php', 'PHP'],
            'Ruby': ['ruby', 'Ruby', 'rails', 'Rails'],
            # 데이터베이스
            'MySQL': ['mysql', 'MySQL', 'MYSQL'],
            'PostgreSQL': ['postgresql', 'PostgreSQL', 'postgres'],
            'MongoDB': ['mongodb', 'MongoDB', 'mongo'],
            'Redis': ['redis', 'Redis'],
            'Oracle': ['oracle', 'Oracle'],
            'SQL Server': ['sql server', 'SQL Server', 'sqlserver'],
            # 클라우드/인프라
            'AWS': ['aws', 'AWS', 'Amazon Web Services'],
            'Azure': ['azure', 'Azure', 'Microsoft Azure'],
            'GCP': ['gcp', 'GCP', 'Google Cloud'],
            'Docker': ['docker', 'Docker'],
            'Kubernetes': ['kubernetes', 'Kubernetes', 'k8s'],
            'Jenkins': ['jenkins', 'Jenkins'],
            'Git': ['git', 'Git', 'GitHub', 'github'],
            # AI/ML
            'TensorFlow': ['tensorflow', 'TensorFlow'],
            'PyTorch': ['pytorch', 'PyTorch'],
            'Keras': ['keras', 'Keras'],
            'Pandas': ['pandas', 'Pandas'],
            'NumPy': ['numpy', 'NumPy'],
            # 게임 엔진 (샘플 데이터에서 발견)
            'Unity': ['unity', 'Unity'],
            'Unreal': ['unreal', 'Unreal', '언리얼'],
            'Niagara': ['niagara', 'Niagara', '나이아가라']
        }
        
        # 모든 필드에서 기술 스택 검색
        for field in search_fields:
            if field in attrs and attrs[field]:
                content = str(attrs[field]).lower()
                for tech_name, keywords in tech_keywords.items():
                    if any(keyword.lower() in content for keyword in keywords):
                        if tech_name not in tech_stacks:
                            tech_stacks.append(tech_name)
        
        return tech_stacks[:5]  # 최대 5개만 표시
        
    except Exception as e:
        print(f"기술 스택 추출 오류: {e}")
        return []

def extract_job_link_from_html(job):
    """HTML에서 채용공고 링크 추출"""
    try:
        html_content = job.get('html', '')
        if not html_content or pd.isna(html_content):
            return None
            
        # 링크 패턴 추출
        patterns = [
            r'href=["\']([^"\']*apply[^"\']*)["\']',
            r'href=["\']([^"\']*job[^"\']*)["\']',
            r'href=["\']([^"\']*career[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    return match
        
        # 패턴 매칭 실패 시 회사명으로 검색 링크 생성
        company = job.get('company', '')
        title = job.get('title', '')
        if company and company != 'N/A':
            search_query = f"{company} {title} 채용".replace(' ', '+')
            return f"https://www.google.com/search?q={search_query}"
            
        return None
        
    except Exception as e:
        print(f"링크 추출 오류: {e}")
        return None

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_jobs():
    """채용공고 분석 - 최적화된 버전"""
    global curator
    
    if not curator:
        if not initialize_curator():
            return jsonify({'error': 'PostgreSQL 연결 실패'}), 500
    
    try:
        # 폼 데이터 가져오기
        job_role = request.form.get('job_role', '전체')
        experience = request.form.get('experience', '전체')
        min_salary = request.form.get('min_salary')
        max_salary = request.form.get('max_salary')
        company_type = request.form.get('company_type', '전체')
        
        print(f"📊 분석 요청: 직무={job_role}, 경력={experience}, 연봉={min_salary}~{max_salary}, 회사유형={company_type}")
        print(f"🔍 원본 폼 데이터: {dict(request.form)}")
        
        # 필터 조건 구성
        filters = {}
        print(f"🔍 받은 파라미터: job_role={job_role}, experience={experience}, company_type={company_type}")
        
        if job_role != '전체':
            filters['job_role'] = job_role
        if experience != '전체':
            filters['experience'] = experience
        if min_salary:
            try:
                filters['min_salary'] = float(min_salary)
            except ValueError:
                pass
        if max_salary:
            try:
                filters['max_salary'] = float(max_salary)
            except ValueError:
                pass
        if company_type != '전체':
            filters['company_type'] = company_type
        
        print(f"🔍 구성된 필터: {filters}")
        
        # 총 개수 조회 (페이지네이션용)
        total_count = curator.get_jobs_count(table_name="jobs", filters=filters)
        
        if total_count == 0:
            print(f"❌ 필터 조건: {filters}")
            print(f"❌ 총 개수가 0입니다. 필터 조건을 확인해주세요.")
            return jsonify({'error': '조건에 맞는 데이터가 없습니다.'}), 404
        
        print(f"🔍 필터링된 데이터: 총 {total_count}개")
        
        # 세션에 필터 정보 저장 (페이지네이션 시 사용)
        session['current_filters'] = filters
        session['total_count'] = total_count
        
        # 첫 페이지로 리다이렉트
        return jsonify({
            'success': True,
            'total_jobs': total_count,
            'redirect': '/jobs?page=1'
        })
        
    except Exception as e:
        print(f"❌ 분석 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs')
def show_jobs():
    """채용공고 목록 표시 (최적화된 페이지네이션)"""
    global curator
    
    if not curator:
        if not initialize_curator():
            return render_template('jobs.html', 
                                 jobs=[], 
                                 page=1, 
                                 total_pages=0, 
                                 total_jobs=0,
                                 error="데이터베이스 연결 실패")
    
    # 페이지네이션 파라미터
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 페이지당 항목 수
    
    # 세션에서 필터 정보 가져오기
    filters = session.get('current_filters', {})
    total_count = session.get('total_count', 0)
    
    if total_count == 0:
        return render_template('jobs.html', 
                             jobs=[], 
                             page=1, 
                             total_pages=0, 
                             total_jobs=0,
                             error="분석할 데이터가 없습니다. 먼저 분석을 실행하세요.")
    
    total_pages = (total_count + per_page - 1) // per_page
    
    # 페이지 범위 검증
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    # 현재 페이지 데이터 DB에서 직접 조회
    offset = (page - 1) * per_page
    page_data = curator.get_jobs_data(
        table_name="jobs",
        limit=per_page,
        offset=offset,
        filters=filters
    )
    
    if page_data.empty:
        return render_template('jobs.html', 
                             jobs=[], 
                             page=page, 
                             total_pages=total_pages, 
                             total_jobs=total_count,
                             error="해당 페이지에 데이터가 없습니다.")
    
    # 데이터프레임을 딕셔너리 리스트로 변환
    jobs_list = []
    
    for idx, (_, job) in enumerate(page_data.iterrows()):
        # 우선 url 컬럼 사용
        job_link = job.get('url', None)
        
        # url이 없으면 HTML에서 추출 시도
        if not job_link or pd.isna(job_link):
            job_link = extract_job_link_from_html(job) if 'html' in job.index else None
            
        # 링크가 없으면 기본값
        if not job_link or pd.isna(job_link):
            job_link = '#'
        
        # jobs_attributes에서 기술 스택 추출
        tech_stacks = extract_tech_stacks(job.get('jobs_attributes'))
        
        # 추가 정보 추출
        attrs = {}
        if job.get('jobs_attributes') and not pd.isna(job.get('jobs_attributes')):
            try:
                if isinstance(job['jobs_attributes'], str):
                    attrs = json.loads(job['jobs_attributes'])
                else:
                    attrs = job['jobs_attributes']
            except Exception as e:
                attrs = {}
        
        # 복리후생 정보 추출
        benefits = []
        if attrs.get('복리후생'):
            benefits_text = str(attrs['복리후생'])
            # 간단한 복리후생 키워드 추출
            benefit_keywords = ['연차', '휴가', '보험', '교육비', '간식', '점심', '야식', '휴게실', '카페', '헬스장', '도서구입비', '성과급', '스톡옵션']
            for keyword in benefit_keywords:
                if keyword in benefits_text:
                    benefits.append(keyword)
        
        job_dict = {
            'id': offset + idx + 1,
            'company': job.get('company', 'N/A'),
            'title': job.get('title', 'N/A'),
            'job_role': job.get('job_role_analyzed', job.get('major_category', job.get('position', ''))),
            'experience': job.get('experience_analyzed', ''),
            'location': job.get('location_analyzed', job.get('category', '')),
            'salary': job.get('salary_analyzed', ''),
            'tech_stacks': tech_stacks,
            'link': job_link,
            'url': job.get('url', '#'),
            'benefits': benefits[:3],  # 최대 3개 복리후생
            'employment_type': attrs.get('고용형태', ''),
            'education': attrs.get('요구학력', ''),
            'work_type': attrs.get('근무방식', ''),
            'deadline': attrs.get('지원마감일', '')
        }
        jobs_list.append(job_dict)
    
    # 시각화 데이터 생성 (첫 페이지에서만)
    charts = None
    if page == 1:
        charts = generate_visualization_data(page_data)
    
    return render_template('jobs.html',
                         jobs=jobs_list,
                         page=page,
                         total_pages=total_pages,
                         total_jobs=total_count,
                         start_idx=offset + 1,
                         end_idx=min(offset + per_page, total_count),
                         per_page=per_page,
                         charts=charts)

if __name__ == '__main__':
    print("Flask 웹 애플리케이션 시작...")
    print("http://localhost:5008 에서 접속 가능")
    app.run(debug=True, host='0.0.0.0', port=5008)