# streamlit_app.py
# Streamlit Cloud 배포용 FashionRAG 애플리케이션

import os
import streamlit as st
from dotenv import load_dotenv
import chromadb
import base64
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from datasets import load_dataset
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path

# OpenAI API 키 설정
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다. Streamlit Cloud의 Secrets에서 설정해주세요.")
    st.stop()
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 스크립트 파일의 디렉터리 경로 가져오기
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def setup_dataset():
    """
    Fashionpedia 데이터셋을 설정합니다.
    """
    try:
        with st.spinner("데이터셋을 로드하는 중..."):
            dataset = load_dataset("detection-datasets/fashionpedia")
        
        dataset_folder = os.path.join(SCRIPT_DIR, 'fashion_dataset')
        os.makedirs(dataset_folder, exist_ok=True)
        
        st.success(f"✅ 데이터셋 로드 완료: {len(dataset['train'])} 훈련 이미지, {len(dataset['val'])} 검증 이미지")
        return dataset, dataset_folder
    except Exception as e:
        st.error(f"❌ 데이터셋 로드 실패: {str(e)}")
        return None, None

def save_images(dataset, dataset_folder, num_images=100):
    """
    데이터셋 이미지를 로컬 폴더에 저장합니다.
    """
    with st.spinner(f"{num_images}개 이미지를 저장하는 중..."):
        for i in range(min(num_images, len(dataset['train']))):
            image = dataset['train'][i]['image']
            image.save(os.path.join(dataset_folder, f'image_{i+1}.png'))
    st.success(f"✅ {min(num_images, len(dataset['train']))}개 이미지를 {dataset_folder}에 저장했습니다.")

@st.cache_resource
def setup_chroma_db():
    """
    ChromaDB 벡터 데이터베이스를 설정합니다.
    """
    vdb_path = os.path.join(SCRIPT_DIR, 'img_vdb')
    chroma_client = chromadb.PersistentClient(path=vdb_path)
    image_loader = ImageLoader()
    clip_embedder = OpenCLIPEmbeddingFunction()
    image_vdb = chroma_client.get_or_create_collection(
        name="image_vdb",
        embedding_function=clip_embedder,
        data_loader=image_loader
    )
    return image_vdb

def add_images_to_db(image_vdb, dataset_folder):
    """
    이미지를 벡터 데이터베이스에 추가합니다.
    """
    ids = []
    uris = []
    for i, filename in enumerate(sorted(os.listdir(dataset_folder))):
        if filename.endswith('.png'):
            file_path = os.path.join(dataset_folder, filename)
            ids.append(str(i+1))
            uris.append(file_path)

    if ids:
        with st.spinner(f"{len(ids)}개 이미지를 벡터 데이터베이스에 추가하는 중..."):
            image_vdb.add(ids=ids, uris=uris)
        st.success(f"✅ {len(ids)}개 이미지가 벡터 데이터베이스에 추가되었습니다.")
    else:
        st.warning("⚠️ 추가할 이미지가 없습니다.")

def query_db(image_vdb, query, results=2):
    """
    벡터 데이터베이스에서 이미지를 검색합니다.
    """
    return image_vdb.query(
        query_texts=[query],
        n_results=results,
        include=['uris', 'distances']
    )

@st.cache_data
def translate(text, target_lang):
    """
    텍스트를 번역합니다.
    """
    translation_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
    translation_prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a translator. Translate the following text to {target_lang}."),
        ("user", "{text}")
    ])
    translation_chain = translation_prompt | translation_model | StrOutputParser()
    return translation_chain.invoke({"text": text})

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
            {"type": "image_url", "image_url": "data:image/jpeg;base64,{image_data_1}"},
            {"type": "image_url", "image_url": "data:image/jpeg;base64,{image_data_2}"},
        ])
    ])
    return image_prompt | gpt4 | parser

def format_prompt_inputs(data, user_query):
    """
    프롬프트 입력을 포맷팅합니다.
    """
    inputs = {'user_query': user_query}
    
    # 첫 번째 이미지 인코딩
    with open(data['uris'][0][0], 'rb') as f:
        inputs['image_data_1'] = base64.b64encode(f.read()).decode('utf-8')
    
    # 두 번째 이미지 인코딩
    with open(data['uris'][0][1], 'rb') as f:
        inputs['image_data_2'] = base64.b64encode(f.read()).decode('utf-8')
    
    return inputs

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
    
    # 데이터셋 및 벡터DB 초기화
    if 'data_initialized' not in st.session_state:
        with st.spinner("데이터셋과 데이터베이스를 초기화하는 중입니다..."):
            # 1. 데이터셋 설정
            dataset, dataset_folder = setup_dataset()
            if not dataset:
                st.error("❌ 데이터셋 설정에 실패했습니다.")
                st.stop()
            
            # 2. 이미지 저장 (처음 실행시에만)
            if not os.path.exists(dataset_folder) or not any(fname.endswith('.png') for fname in os.listdir(dataset_folder)):
                save_images(dataset, dataset_folder, num_images=100)
            
            # 3. 벡터 데이터베이스 설정
            vdb_path = os.path.join(SCRIPT_DIR, 'img_vdb')
            if not os.path.exists(vdb_path):
                st.session_state.image_vdb = setup_chroma_db()
                add_images_to_db(st.session_state.image_vdb, dataset_folder)
            else:
                st.session_state.image_vdb = setup_chroma_db()
                st.success("✅ 기존 벡터 데이터베이스를 로드했습니다.")
            
            # 4. 비전 체인 설정
            st.session_state.vision_chain = setup_vision_chain()
            
        st.session_state.data_initialized = True
        st.success("🎉 FashionRAG 초기화 완료!")
    
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
                    
                    # 2. 이미지 검색
                    results = query_db(st.session_state.image_vdb, query_en, results=2)
                    
                    # 3. 프롬프트 입력 포맷팅
                    prompt_input = format_prompt_inputs(results, query_en)
                    
                    # 4. 스타일링 조언 생성
                    response_en = st.session_state.vision_chain.invoke(prompt_input)
                    
                    # 5. 응답 번역 (영어 -> 한글)
                    response_ko = translate(response_en, "Korean")
                    
                    # 결과 출력
                    st.header("🎯 FashionRAG의 스타일링 조언")
                    
                    # 검색된 이미지 표시
                    st.subheader("🖼️ 검색된 패션 이미지")
                    cols = st.columns(2)
                    for i, uri in enumerate(results['uris'][0]):
                        with open(uri, "rb") as f:
                            img_bytes = f.read()
                            encoded_img = base64.b64encode(img_bytes).decode()
                            cols[i].image(
                                f"data:image/png;base64,{encoded_img}",
                                caption=f"이미지 ID: {results['ids'][0][i]} (유사도: {results['distances'][0][i]:.3f})",
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
    - **벡터 DB**: ChromaDB
    - **이미지 임베딩**: OpenCLIP
    """)
    
    # 배포 정보
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 배포 정보")
    st.sidebar.markdown("**Streamlit Cloud에서 호스팅됨**")

if __name__ == "__main__":
    main()
