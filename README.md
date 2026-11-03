# 🌐 다국어 번역기

입력한 글을 영어 / 일본어 / 베트남어로 번역하는 Streamlit 앱입니다. 번역은 OpenAI `GPT-6-Astra` 모델로 합니다.

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수 설정

`.env.example`을 복사해 `.env` 파일을 만들고 API 키를 입력합니다.

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-6-astra   # 생략하면 gpt-6-astra 사용
```

## 실행

```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 이 열립니다.
