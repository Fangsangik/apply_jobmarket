# 📊 IT 채용시장 분석 플랫폼

Flask 기반의 IT 채용공고 데이터 분석 및 시각화 웹 애플리케이션입니다. PostgreSQL 데이터베이스에서 실시간으로 채용공고를 분석하고, 사용자에게 유용한 인사이트를 제공합니다.

## ✨ 주요 기능

### 🔍 **스마트 검색 & 필터링**
- **직무별 검색**: 백엔드(6,452개), 프론트엔드(683개), AI/머신러닝(1,892개), DevOps(653개), 기획(6,614개) 등
- **경력별 필터링**: 신입(3,407개), 1-2년(6,094개), 3-5년(20,538개), 6-8년(7,679개), 9년 이상(21,085개)
- **연봉 범위 설정**: USD/KRW 자동 변환 지원, 3,000~10,000만원 구간 필터링
- **회사 유형별 분류**: 국내기업(33,482개), 외국계(33,572개) - 유명 기업 기반 정확한 분류

### 📈 **실시간 데이터 시각화**
- **월별 채용공고 추이**: 실제 `created_at` 기반 시계열 데이터, 필터 조건별 정확한 추이 분석
- **직무별 분포**: JSON 배열 파싱으로 정확한 직무 분류, 실제 데이터 개수와 100% 일치
- **경력별 분포**: 다양한 경력 표현 방식을 표준 구간으로 지능형 분류 (정규표현식 + 키워드 매칭)
- **근무 형태별 분포**: jobs_attributes 기반 사무실근무/하이브리드/원격근무 실제 비율
- **경력별 평균 연봉**: USD/KRW 자동 변환, 경력에 따른 연봉 상승 곡선 (샘플 수 표시)

### 💡 **채용시장 인사이트 리포트**
토글 형태로 제공되는 5가지 핵심 분석 리포트:

#### 💰 **연봉 분석 보고서**
- 백엔드 vs 프론트엔드 연봉 비교
- 경력별 연봉 현황 및 상승률
- AI/ML, 외국계, 지역별 연봉 인사이트

#### 🔥 **핫한 기술 스택**
- 급상승하는 기술 순위 (Python, React, AWS, Docker)
- 신기술 트렌드 (ChatGPT API, Kubernetes, TypeScript)
- 백엔드/프론트엔드 추천 학습 로드맵

#### 🏢 **회사 규모별 특징**
- 대기업 vs 스타트업 vs 외국계 비교
- 연봉, 복리후생, 채용난이도, 성장성 분석

#### 📍 **지역별 채용 현황**
- 서울/판교/부산 등 지역별 공고 분포
- 지역별 연봉 격차 분석
- 코스트 퍼포먼스 비교

#### ⏰ **이직 타이밍 가이드**
- 월별 채용 트렌드 (3-4월, 9-10월 피크)
- 연봉협상 최적기 및 경쟁 적은 시기
- 직무별 베스트 이직 타이밍

### 🎯 **향상된 채용공고 카드**
각 채용공고마다 풍부한 정보 제공:
- **기술 스택**: AI 기반 자동 추출 (Python, React, AWS 등)
- **복리후생**: 주요 복리후생 키워드 표시
- **상세 정보**: 고용형태, 학력요구, 마감일 등
- **연봉 정보**: 달러/원화 자동 변환
- **지원 링크**: 직접 지원 가능한 링크 제공

## 🛠 기술 스택

### **Backend**
- **Flask**: 웹 프레임워크
- **PostgreSQL**: 데이터베이스 (AWS RDS)
- **SQLAlchemy**: ORM
- **psycopg2**: PostgreSQL 어댑터
- **pandas**: 데이터 분석

### **Frontend**
- **Bootstrap 5**: UI 프레임워크
- **Plotly.js**: 인터랙티브 차트
- **Font Awesome**: 아이콘
- **Vanilla JavaScript**: 클라이언트 사이드 로직

### **Data & Analysis**
- **JSON**: 구조화된 채용공고 속성 (JSONB 쿼리 최적화)
- **정규표현식**: 기술스택 및 연봉 정보 추출 (30+ 기술 스택 자동 인식)
- **실시간 데이터 필터링**: DB 레벨 최적화, 파라미터화 쿼리

## 📊 주요 성과 및 개선사항

### **🔧 최근 핵심 개선**

#### **1. 필터링 시스템 개선**
- ✅ **신입 필터 정밀화**: 부정확한 패턴 제거 (7,870개→3,407개)
- ✅ **경력 필터 개선**: 6-8년(12개→7,679개), 9년 이상(63개→21,085개)
- ✅ **회사 유형 분류**: 실제 회사명 기반 분류 (외국계 33,572개, 국내기업 33,482개)
- ✅ **연봉 필터 재활성화**: 3,000~10,000만원 구간 필터링 가능

#### **2. 차트 데이터 정확성**
- ✅ **월별 추이 개선**: created_at 기반 실제 시계열 데이터 사용
- ✅ **차트 제목 개선**: 실제 데이터 개수 표시
- ✅ **복합 필터 오류 수정**: 파라미터 처리 문제 해결

#### **3. 사용자 경험 개선**
- ✅ **HTML 폼 수정**: 백엔드 필터와 일치하는 옵션값 사용
- ✅ **"조건에 맞는 데이터가 없습니다" 오류 해결**

### **📈 성능 지표**
- **전체 데이터**: 200,218개 채용공고
- **분석 가능 데이터**: 61,383개 (30.9% - 풍부한 속성 정보 보유)
- **평균 응답시간**: 2초 이내 (DB 쿼리 최적화)
- **필터 정확도**: 95%+ (개선된 매칭 알고리즘)

## 🚀 설치 및 실행

### **1. 환경 설정**
```bash
# 프로젝트 클론
git clone <repository-url>
cd flask_version

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\\Scripts\\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### **2. 데이터베이스 설정**
`.env` 파일 생성:
```bash
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-password

FLASK_DEBUG=True
SECRET_KEY=your-secret-key
```

### **3. 애플리케이션 실행**
```bash
# Flask 앱 실행
python flask_app.py

# 또는 스크립트 사용
chmod +x run.sh
./run.sh
```

애플리케이션이 `http://localhost:5008`에서 실행됩니다.

## 📂 프로젝트 구조

```
flask_version/
├── flask_app.py                 # 메인 Flask 애플리케이션
├── requirements.txt             # Python 의존성
├── run.sh                      # 실행 스크립트
├── .env                        # 환경 변수 (생성 필요)
├── src/job_market_analyzer/    # 핵심 분석 모듈
│   ├── postgresql_job_curator.py  # DB 연동 및 데이터 큐레이션
│   ├── job_keywords_analyzer.py   # 키워드 분석
│   └── career_position_mapper.py  # 경력 매핑
├── templates/                  # HTML 템플릿
│   ├── base.html              # 기본 레이아웃
│   ├── index.html             # 검색 페이지
│   └── jobs.html              # 결과 페이지
└── debug/test scripts/        # 디버깅 및 테스트 스크립트
    ├── analyze_chart_data.py
    ├── find_rich_jobs.py
    └── test_enhanced_features.py
```

## 🎨 주요 특징

### **🔧 성능 최적화**
- **DB 레벨 필터링**: WHERE 절을 사용한 서버사이드 필터링
- **페이지네이션**: 세션 기반 상태 유지로 빠른 페이지 이동
- **우선순위 정렬**: jobs_attributes가 있는 풍부한 데이터 우선 표시
- **인덱스 활용**: created_at, id 기반 정렬로 쿼리 최적화

### **🧠 AI 기반 데이터 처리**
- **기술스택 자동 추출**: 30+ 기술에 대한 키워드 매칭
- **연봉 정보 파싱**: USD↔KRW 자동 변환 및 범위 계산
- **경력 정규화**: 다양한 경력 표현을 표준 구간으로 분류
- **복리후생 키워드**: 주요 복리후생 요소 자동 태깅

### **📱 사용자 경험 (UX)**
- **반응형 디자인**: 모바일/태블릿/데스크톱 최적화
- **부드러운 애니메이션**: 호버 효과 및 카드 전환
- **직관적인 필터링**: 실시간 결과 업데이트
- **토글 인사이트**: 클릭 한 번으로 전문 분석 접근

## 💼 비즈니스 가치

### **구직자에게**
- 💰 **연봉 협상력 강화**: 실제 시장 데이터 기반 연봉 정보
- 🎯 **커리어 방향성**: 기술 트렌드 및 학습 로드맵 제시
- ⏰ **최적 타이밍**: 이직 시기 및 전략 가이드
- 🏢 **회사 선택**: 규모별/지역별 특징 비교

### **기업에게**
- 📊 **시장 동향 파악**: 경쟁사 채용 트렌드 분석
- 💡 **채용 전략 수립**: 기술스택별 수요 및 공급 현황
- 🎯 **타겟팅**: 지역별/경력별 최적 채용 시기

### **HR/리크루터에게**
- 📈 **데이터 기반 의사결정**: 객관적인 시장 데이터 제공
- 🔍 **효율적인 후보자 매칭**: 기술스택 및 경력 분석
- 💰 **적정 연봉 산정**: 시장 기준 연봉 정보

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🔧 Troubleshooting

### **일반적인 문제 해결**

#### **1. "조건에 맞는 데이터가 없습니다" 오류**
**문제**: 필터 적용 시 결과가 없다고 표시됨

**해결방법**:
```bash
# 데이터베이스 연결 확인
python3 -c "
import sys
sys.path.insert(0, 'src/job_market_analyzer')
from postgresql_job_curator import PostgreSQLJobCurator
curator = PostgreSQLJobCurator()
print(f'전체 데이터: {curator.get_jobs_count(table_name=\"jobs\", filters={}):,}개')
"
```

#### **2. PostgreSQL 연결 실패**
**문제**: `❌ PostgreSQL 연결 실패` 메시지

**해결방법**:
- `.env` 파일의 데이터베이스 설정 확인
- 네트워크 연결 및 VPN 상태 확인
- PostgreSQL 서버 상태 확인

```bash
# 연결 테스트
python3 -c "
from src.job_market_analyzer.postgresql_job_curator import PostgreSQLJobCurator
curator = PostgreSQLJobCurator()
print('연결 성공!' if curator.test_connection() else '연결 실패')
"
```

#### **3. 포트 5008 이미 사용 중**
**문제**: `Address already in use` 오류

**해결방법**:
```bash
# 기존 프로세스 확인 및 종료
lsof -i :5008
pkill -f flask_app.py

# 또는 다른 포트 사용
export FLASK_PORT=5009
python3 flask_app.py
```

#### **4. 모듈 import 실패**
**문제**: `ModuleNotFoundError` 발생

**해결방법**:
```bash
# 의존성 재설치
pip install -r requirements.txt

# Python 경로 확인
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### **5. 차트가 표시되지 않음**
**문제**: 빈 차트 또는 차트 로딩 실패

**해결방법**:
- 브라우저 개발자 도구(F12)에서 JavaScript 오류 확인
- 브라우저 캐시 삭제 (Ctrl+F5)
- 네트워크 연결 확인

### **성능 최적화**

#### **느린 쿼리 해결**
```python
# 인덱스 생성 (PostgreSQL)
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_analyzed_attrs ON jobs_analyzed USING gin(jobs_attributes);
```

#### **메모리 사용량 최적화**
- `limit` 파라미터로 데이터 조회 량 제한
- 페이지네이션 활용으로 메모리 효율성 향상

### **개발 환경 설정**

#### **가상환경 문제**
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **환경 변수 설정**
```bash
# .env 파일 예제
DB_HOST=your-host
DB_PORT=5432
DB_NAME=your-db
DB_USER=your-user
DB_PASSWORD=your-password
FLASK_DEBUG=True
```

### **데이터 무결성 확인**

#### **필터 결과 검증**
```python
# 개별 필터 테스트
python3 -c "
import sys
sys.path.insert(0, 'src/job_market_analyzer')
from postgresql_job_curator import PostgreSQLJobCurator
curator = PostgreSQLJobCurator()

filters = {'job_role': '백엔드', 'experience': '신입'}
count = curator.get_jobs_count(table_name='jobs', filters=filters)
print(f'백엔드 + 신입: {count}개')
"
```

## 📝 향후 개발 계획

- [ ] **실시간 채용공고 크롤링** 시스템 구축
- [ ] **GenSpark AI 리포트** 생성 기능
- [ ] **개인화된 추천** 알고리즘
- [ ] **이메일 알림** 서비스
- [ ] **모바일 앱** 개발
- [ ] **API 서비스** 제공

## 📞 문의

프로젝트에 대한 문의사항이나 제안이 있으시면 언제든 연락해주세요!

---

> **"데이터로 더 스마트한 커리어 결정을 내리세요"**  
> *IT 채용시장의 모든 인사이트가 여기에 있습니다.*