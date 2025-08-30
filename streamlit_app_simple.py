# streamlit_app_simple.py
# Streamlit Cloud 배포용 간소화된 FashionRAG 애플리케이션

import os
import streamlit as st
from dotenv import load_dotenv
import base64
from datasets import load_dataset
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
import random

# OpenAI API 키 설정
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다. Streamlit Cloud의 Secrets에서 설정해주세요.")
    st.stop()
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

@st.cache_resource
def setup_dataset():
    """
    Fashionpedia 데이터셋을 설정합니다.
    """
    try:
        with st.spinner("데이터셋을 로드하는 중..."):
            dataset = load_dataset("detection-datasets/fashionpedia")
        
        st.success(f"✅ 데이터셋 로드 완료: {len(dataset['train'])} 훈련 이미지, {len(dataset['val'])} 검증 이미지")
        return dataset
    except Exception as e:
        st.error(f"❌ 데이터셋 로드 실패: {str(e)}")
        return None

def get_random_images(dataset, num_images=2):
    """
    데이터셋에서 랜덤하게 이미지를 선택합니다.
    """
    if not dataset:
        return []
    
    # 랜덤 인덱스 선택
    indices = random.sample(range(min(1000, len(dataset['train']))), num_images)
    
    images = []
    for idx in indices:
        try:
            image = dataset['train'][idx]['image']
            # 이미지를 base64로 인코딩
            import io
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            images.append(img_str)
        except Exception as e:
            st.warning(f"이미지 {idx} 로드 실패: {str(e)}")
            continue
    
    return images

@st.cache_data
def translate(text, target_lang):
    """
    텍스트를 번역합니다.
    """
    try:
        translation_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        translation_prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a translator. Translate the following text to {target_lang}."),
            ("user", "{text}")
        ])
        translation_chain = translation_prompt | translation_model | StrOutputParser()
        return translation_chain.invoke({"text": text})
    except Exception as e:
        st.error(f"번역 오류: {str(e)}")
        return text

def setup_vision_chain():
    """
    멀티모달 비전 체인을 설정합니다.
    """
    gpt4 = ChatOpenAI(model="gpt-4o", temperature=0.0)
    parser = StrOutputParser()
    image_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful fashion and styling assistant. Answer the user's question using the given image context with direct references to parts of the images provided. Maintain a more conversational tone, don't make too many lists. Use markdown formatting for highlights, emphasis, and structure."),
        ("user", [
            {"type": "text", "text": "What are some ideas for styling {user_query}?"},
            {"type": "image_url", "image_url": "data:image/png;base64,{image_data_1}"},
            {"type": "image_url", "image_url": "data:image/png;base64,{image_data_2}"},
        ])
    ])
    return image_prompt | gpt4 | parser

def main():
    """
    메인 함수: Streamlit 앱 실행
    """
    st.set_page_config(
        page_title="FashionRAG - 패션 스타일링 어시스턴트",
        page_icon="👗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 사이드바 설정
    st.sidebar.title("🎨 FashionRAG 설정")
    st.sidebar.markdown("**AI 기반 패션 스타일링 어시스턴트**")
    
    # 메인 타이틀
    st.title("👗 FashionRAG: 패션 스타일링 어시스턴트")
    st.markdown("**멀티모달 RAG 기반 패션 스타일링 조언 시스템**")
    
    # 데이터셋 초기화
    if 'dataset_loaded' not in st.session_state:
        with st.spinner("데이터셋을 초기화하는 중입니다..."):
            dataset = setup_dataset()
            if dataset:
                st.session_state.dataset = dataset
                st.session_state.dataset_loaded = True
                st.success("🎉 FashionRAG 초기화 완료!")
            else:
                st.error("❌ 데이터셋 초기화에 실패했습니다.")
                st.stop()
    
    # 사용자 입력 섹션
    st.header("💬 패션 스타일링 질문하기")
    
    # 예시 질문들
    example_questions = [
        "하늘색 계열의 캐주얼한 여름 코디 추천해줘",
        "비즈니스 캐주얼 룩 어떻게 구성하면 좋을까?",
        "검은색 드레스에 어울리는 액세서리 추천해줘",
        "남성용 겨울 코트 스타일링 방법 알려줘",
        "미니멀한 데일리 룩 구성법"
    ]
    
    # 예시 질문 선택
    selected_example = st.selectbox(
        "💡 예시 질문을 선택하거나 직접 입력하세요:",
        ["직접 입력"] + example_questions
    )
    
    if selected_example == "직접 입력":
        query_ko = st.text_input(
            "질문을 입력하세요:",
            placeholder="예: 하늘색 계열의 캐주얼한 여름 코디 추천해줘"
        )
    else:
        query_ko = st.text_input("질문을 입력하세요:", value=selected_example)
    
    # 질문하기 버튼
    if st.button("🚀 질문하기", type="primary", width='stretch'):
        if not query_ko.strip():
            st.warning("⚠️ 질문을 입력해주세요.")
        else:
            with st.spinner("패션 스타일링 조언을 생성하는 중입니다..."):
                try:
                    # 1. 질문 번역 (한글 -> 영어)
                    with st.expander("📝 번역 과정", expanded=False):
                        query_en = translate(query_ko, "English")
                        st.write(f"**원본 질문:** {query_ko}")
                        st.write(f"**번역된 질문:** {query_en}")
                    
                    # 2. 랜덤 이미지 선택
                    images = get_random_images(st.session_state.dataset, num_images=2)
                    
                    if len(images) < 2:
                        st.error("❌ 이미지를 불러올 수 없습니다.")
                        return
                    
                    # 3. 비전 체인 설정
                    vision_chain = setup_vision_chain()
                    
                    # 4. 프롬프트 입력 포맷팅
                    prompt_input = {
                        'user_query': query_en,
                        'image_data_1': images[0],
                        'image_data_2': images[1]
                    }
                    
                    # 5. 스타일링 조언 생성
                    response_en = vision_chain.invoke(prompt_input)
                    
                    # 6. 응답 번역 (영어 -> 한글)
                    response_ko = translate(response_en, "Korean")
                    
                    # 결과 출력
                    st.header("🎯 FashionRAG의 스타일링 조언")
                    
                    # 검색된 이미지 표시
                    st.subheader("🖼️ 패션 이미지")
                    cols = st.columns(2)
                    for i, img_str in enumerate(images):
                        cols[i].image(
                            f"data:image/png;base64,{img_str}",
                            caption=f"패션 이미지 {i+1}",
                            width='stretch'
                        )
                    
                    # 스타일링 조언 표시
                    st.subheader("💡 패션 스타일링 조언")
                    st.markdown(response_ko)
                    
                    # 원본 영어 응답 (접기)
                    with st.expander("🔍 원본 영어 응답 보기", expanded=False):
                        st.markdown(response_en)
                    
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                    st.info("다시 시도해주세요.")
    
    # 정보 섹션
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 시스템 정보")
    st.sidebar.markdown(f"""
    - **데이터 소스**: HuggingFace Fashionpedia
    - **총 이미지**: 46,781개
    - **AI 모델**: GPT-4o
    - **이미지 선택**: 랜덤 샘플링
    - **배포**: Streamlit Cloud
    """)
    
    # 배포 정보
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 배포 정보")
    st.sidebar.markdown("**Streamlit Cloud에서 호스팅됨**")
    
    # 주의사항
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚠️ 주의사항")
    st.sidebar.markdown("""
    - 이미지는 랜덤하게 선택됩니다
    - 질문과 이미지가 직접적으로 연관되지 않을 수 있습니다
    - 더 정확한 결과를 원하면 질문을 구체적으로 작성해주세요
    """)

if __name__ == "__main__":
    main()
