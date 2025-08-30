# FashionRAG: 이미지 기반 스타일링 어시스턴트

FashionRAG는 패션 관련 이미지와 텍스트 데이터를 사용하여 사용자에게 개인화된 스타일링 조언을 제공하는 멀티모달 RAG(Retrieval-Augmented Generation) 어시스턴트 시스템입니다.

## 주요 기능

- **이미지 검색**: 텍스트 질문을 기반으로 HuggingFace Fashionpedia 데이터셋에서 관련 이미지 검색
- **벡터 기반 검색**: OpenCLIPEmbeddingFunction을 사용한 이미지 벡터화 및 ChromaDB를 통한 유사도 검색
- **멀티모달 AI 연동**: GPT-4o를 사용한 이미지 분석 및 종합적인 패션 스타일링 추천
- **다국어 지원**: 한국어 질문을 영어로 번역하여 처리 후 한국어로 응답
- **웹 애플리케이션**: Streamlit을 사용한 사용자 친화적 웹 인터페이스

## 기술 스택

- **ChromaDB**: 벡터 데이터베이스
- **HuggingFace Fashionpedia**: 패션 이미지 데이터셋
- **OpenAI GPT-4o**: 멀티모달 언어 모델
- **LangChain**: RAG 파이프라인 프레임워크
- **Streamlit**: 웹 애플리케이션 프레임워크
- **OpenCLIP**: 이미지 임베딩 모델

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 사용법

### 터미널 기반 실행

```bash
python langchain-fashion-multimodal-script.py
```

### 웹 애플리케이션 실행

```bash
streamlit run langchain-fashion-multimodal-streamlit.py
```

## 프로젝트 구조

```
FashionRAG/
├── Information.md                    # 프로젝트 상세 정보
├── requirements.txt                  # Python 의존성
├── env_example.txt                   # 환경 변수 예시
├── langchain-fashion-multimodal-script.py    # 터미널 기반 스크립트
├── langchain-fashion-multimodal-streamlit.py # Streamlit 웹 앱
├── fashion_dataset/                  # 저장된 패션 이미지 (자동 생성)
└── img_vdb/                         # ChromaDB 벡터 데이터베이스 (자동 생성)
```

## 작동 원리

1. **데이터 준비**: Fashionpedia 데이터셋에서 패션 이미지를 다운로드하여 로컬에 저장
2. **벡터화**: OpenCLIP을 사용하여 이미지를 벡터로 변환하고 ChromaDB에 저장
3. **질문 처리**: 사용자의 한국어 질문을 영어로 번역
4. **이미지 검색**: 번역된 질문을 기반으로 관련 이미지를 벡터 데이터베이스에서 검색
5. **멀티모달 분석**: 검색된 이미지와 질문을 GPT-4o에 전달하여 스타일링 조언 생성
6. **응답 번역**: 생성된 영어 응답을 한국어로 번역하여 사용자에게 제공

## 예시 질문

- "하늘색 계열의 캐주얼한 여름 코디 추천해줘"
- "비즈니스 캐주얼 룩 어떻게 구성하면 좋을까?"
- "검은색 드레스에 어울리는 액세서리 추천해줘"
- "남성용 겨울 코트 스타일링 방법 알려줘"

## 주의사항

- OpenAI API 키가 필요합니다
- 첫 실행 시 데이터셋 다운로드와 벡터 데이터베이스 구축에 시간이 걸릴 수 있습니다
- GPT-4o 모델 사용 시 API 비용이 발생할 수 있습니다

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
