import os

import openai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="다국어 번역기", page_icon="🌐")

DEFAULT_MODEL = "gpt-6-astra"
MAX_CHARS = 5000

LANGUAGES = {
    "🇺🇸 영어": "English",
    "🇯🇵 일본어": "Japanese",
    "🇻🇳 베트남어": "Vietnamese",
}

SYSTEM_PROMPT = (
    "You are a professional translator.\n"
    "Translate the user's text into {target_language}.\n"
    "Preserve the original meaning, tone, line breaks, and formatting.\n"
    "Output only the translated text without any explanation."
)


# ---------- 번역 로직 ----------

def get_model() -> str:
    return os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_MODEL


@st.cache_resource
def get_client(api_key: str) -> openai.OpenAI:
    return openai.OpenAI(api_key=api_key)


def translate(text: str, target_language: str) -> str:
    """OpenAI 모델로 text를 target_language로 번역해 반환한다."""
    client = get_client(os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(target_language=target_language)},
            {"role": "user", "content": text},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def validate(text: str) -> str | None:
    """입력에 문제가 있으면 경고 메시지를, 없으면 None을 반환한다."""
    if not text.strip():
        return "번역할 내용을 입력해주세요."
    if len(text) > MAX_CHARS:
        return f"최대 {MAX_CHARS:,}자까지 번역할 수 있습니다. (현재 {len(text):,}자)"
    return None


def run_translation(text: str, label: str, language: str) -> None:
    """번역을 실행하고 결과 또는 오류를 session_state에 저장한다."""
    st.session_state.error = None
    try:
        with st.spinner("번역 중..."):
            result = translate(text, language)
    except openai.AuthenticationError:
        st.session_state.error = "API 키가 올바르지 않습니다."
    except openai.RateLimitError:
        st.session_state.error = "요청이 많습니다. 잠시 후 다시 시도해주세요."
    except openai.APIConnectionError:
        st.session_state.error = "OpenAI 서버에 연결할 수 없습니다. 네트워크를 확인해주세요."
    except openai.NotFoundError:
        st.session_state.error = f"모델 '{get_model()}'을(를) 찾을 수 없습니다. .env의 OPENAI_MODEL 값을 확인해주세요."
    except openai.APIError as e:
        st.session_state.error = f"번역 중 오류가 발생했습니다: {e}"
    except Exception as e:  # 예상하지 못한 오류에도 앱이 멈추지 않도록
        st.session_state.error = f"알 수 없는 오류가 발생했습니다: {e}"
    else:
        st.session_state.result = result
        st.session_state.result_label = label


# ---------- UI ----------

CSS = """
<style>
/* 언어 버튼: 둥근 모서리 + hover 효과 */
div[data-testid="stButton"] > button {
    border-radius: 999px;
    font-weight: 600;
    transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
div[data-testid="stButton"] > button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(127, 127, 127, .25);
}
/* 글자 수 카운터 */
.char-counter { text-align: right; font-size: .85rem; opacity: .7; margin-top: .35rem; }
.char-counter.over { color: #e5484d; opacity: 1; font-weight: 600; }
/* 결과 코드 블록: 긴 줄 줄바꿈, 일반 글꼴 */
div[data-testid="stCode"] pre, div[data-testid="stCode"] code {
    white-space: pre-wrap !important;
    word-break: break-word;
    font-family: inherit !important;
    font-size: 1rem !important;
    line-height: 1.6;
}
</style>
"""


def clear_all() -> None:
    st.session_state.source_text = ""
    st.session_state.result = None
    st.session_state.result_label = None
    st.session_state.error = None


st.session_state.setdefault("result", None)
st.session_state.setdefault("result_label", None)
st.session_state.setdefault("error", None)

st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown(f"**사용 모델**  \n`{get_model()}`")
    st.markdown(
        "**사용 방법**\n"
        "1. 번역할 글을 입력합니다.\n"
        "2. 영어 / 일본어 / 베트남어 버튼을 누릅니다.\n"
        "3. 결과 오른쪽 위 아이콘으로 복사합니다."
    )
    st.caption(f"최대 {MAX_CHARS:,}자까지 번역할 수 있습니다.")

st.title("🌐 다국어 번역기")
st.caption("입력한 글을 영어 / 일본어 / 베트남어로 번역합니다.")

api_key_missing = not os.getenv("OPENAI_API_KEY", "").strip()
if api_key_missing:
    st.error(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "프로젝트 폴더의 .env 파일에 `OPENAI_API_KEY=sk-...` 형식으로 키를 입력한 뒤 앱을 다시 실행해주세요."
    )

text = st.text_area(
    "번역할 내용",
    key="source_text",
    placeholder="번역할 내용을 입력하세요.",
    height=200,
)

clear_col, counter_col = st.columns([1, 3], vertical_alignment="center")
clear_col.button("🧹 지우기", on_click=clear_all, type="tertiary")
over = len(text) > MAX_CHARS
counter_col.markdown(
    f'<div class="char-counter{" over" if over else ""}">{len(text):,} / {MAX_CHARS:,}자</div>',
    unsafe_allow_html=True,
)

cols = st.columns(len(LANGUAGES))
for col, (label, language) in zip(cols, LANGUAGES.items()):
    if col.button(label, disabled=api_key_missing, width="stretch"):
        warning = validate(text)
        if warning:
            st.session_state.error = None
            st.warning(warning)
        else:
            run_translation(text, label, language)

if st.session_state.error:
    st.error(st.session_state.error)

st.divider()

if st.session_state.result is not None:
    language_name = st.session_state.result_label.split(" ", 1)[1]
    with st.container(border=True):
        st.markdown(f"#### 번역 결과 ({language_name})")
        st.code(st.session_state.result, language=None, wrap_lines=True)
else:
    st.info("언어 버튼을 눌러 번역을 시작하세요.", icon="👆")
