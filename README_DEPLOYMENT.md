# 🚀 FashionRAG 웹 배포 가이드

FashionRAG 애플리케이션을 웹에서 접속할 수 있도록 배포하는 방법들을 안내합니다.

## 🌐 **배포 옵션들**

### 1. **Streamlit Cloud (추천 - 가장 쉬움)**

#### 📋 **준비사항**
1. GitHub 계정
2. OpenAI API 키
3. 프로젝트 코드

#### 🔧 **배포 단계**

**1단계: GitHub에 코드 업로드**
```bash
# GitHub에 새 저장소 생성 후
git init
git add .
git commit -m "Initial commit: FashionRAG app"
git branch -M main
git remote add origin https://github.com/yourusername/fashionrag.git
git push -u origin main
```

**2단계: Streamlit Cloud 배포**
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `yourusername/fashionrag`
5. Main file path: `streamlit_app.py`
6. "Deploy!" 클릭

**3단계: API 키 설정**
1. Streamlit Cloud 대시보드에서 앱 선택
2. "Settings" → "Secrets" 클릭
3. 다음 내용 추가:
```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

#### ✅ **장점**
- 무료 호스팅
- 자동 HTTPS
- 쉬운 설정
- 자동 배포 (GitHub 푸시시)

#### ❌ **단점**
- 제한된 리소스
- 일부 패키지 제한

---

### 2. **Heroku 배포**

#### 📋 **준비사항**
1. Heroku 계정
2. Heroku CLI 설치
3. Git 설치

#### 🔧 **배포 단계**

**1단계: Heroku 앱 생성**
```bash
heroku login
heroku create your-fashionrag-app
```

**2단계: 환경 변수 설정**
```bash
heroku config:set OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**3단계: 배포**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### ✅ **장점**
- 안정적인 호스팅
- 확장 가능
- 다양한 플랜

#### ❌ **단점**
- 유료 (무료 플랜 종료)
- 설정 복잡

---

### 3. **Railway 배포**

#### 📋 **준비사항**
1. Railway 계정
2. GitHub 계정

#### 🔧 **배포 단계**

**1단계: Railway 프로젝트 생성**
1. [railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. "New Project" → "Deploy from GitHub repo"
4. 저장소 선택

**2단계: 환경 변수 설정**
1. 프로젝트 대시보드에서 "Variables" 탭
2. `OPENAI_API_KEY` 추가

**3단계: 배포 설정**
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

#### ✅ **장점**
- 무료 크레딧 제공
- 빠른 배포
- 자동 HTTPS

#### ❌ **단점**
- 크레딧 소진시 유료

---

### 4. **VPS/클라우드 서버 배포**

#### 📋 **준비사항**
1. VPS (AWS EC2, DigitalOcean, Vultr 등)
2. 도메인 (선택사항)

#### 🔧 **배포 단계**

**1단계: 서버 설정**
```bash
# Ubuntu/Debian 기준
sudo apt update
sudo apt install python3 python3-pip nginx
```

**2단계: 애플리케이션 설치**
```bash
git clone https://github.com/yourusername/fashionrag.git
cd fashionrag
pip3 install -r requirements.txt
```

**3단계: 환경 변수 설정**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**4단계: Streamlit 실행**
```bash
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

**5단계: Nginx 설정 (선택사항)**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### ✅ **장점**
- 완전한 제어권
- 무제한 리소스
- 커스터마이징 가능

#### ❌ **단점**
- 설정 복잡
- 유지보수 필요
- 비용 발생

---

## 🔧 **배포 전 체크리스트**

### ✅ **코드 준비**
- [ ] `streamlit_app.py` 파일 생성
- [ ] `requirements.txt` 업데이트
- [ ] `.gitignore` 설정 (API 키 제외)
- [ ] README.md 작성

### ✅ **API 키 관리**
- [ ] OpenAI API 키 준비
- [ ] 환경 변수로 설정
- [ ] 코드에 하드코딩하지 않음

### ✅ **테스트**
- [ ] 로컬에서 정상 작동 확인
- [ ] 모든 의존성 설치 확인
- [ ] 메모리 사용량 확인

---

## 🌍 **도메인 및 SSL 설정**

### **커스텀 도메인 설정**
1. 도메인 구매 (Namecheap, GoDaddy 등)
2. DNS 설정에서 A 레코드 추가
3. SSL 인증서 설정 (Let's Encrypt)

### **HTTPS 설정**
```bash
# Let's Encrypt 설치 (Ubuntu)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📊 **모니터링 및 유지보수**

### **로그 확인**
```bash
# Streamlit 로그
streamlit run app.py --logger.level=debug

# 시스템 로그
journalctl -u streamlit.service -f
```

### **성능 모니터링**
- CPU 사용량
- 메모리 사용량
- 네트워크 트래픽
- 응답 시간

---

## 🚨 **보안 고려사항**

### **API 키 보안**
- 환경 변수 사용
- 코드에 직접 입력 금지
- 정기적인 키 교체

### **접근 제어**
- 방화벽 설정
- IP 화이트리스트
- 인증 시스템 추가

---

## 💡 **추천 배포 방법**

**초보자**: Streamlit Cloud
**중급자**: Railway
**고급자**: VPS/클라우드 서버

각 방법의 장단점을 고려하여 프로젝트 규모와 예산에 맞는 방법을 선택하세요!
