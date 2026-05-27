import streamlit as st
from google import genai
from google.genai import types

# 페이지 설정
st.set_page_config(
    page_title="일정 정리 챗봇",
    page_icon="📅",
    layout="centered"
)

st.title("📅 일정 정리 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반 일정 관리 AI")

# API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ GEMINI_API_KEY가 secrets.toml에 설정되지 않았습니다.")
    st.stop()

# Gemini 클라이언트 생성
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Gemini 클라이언트 생성 실패: {e}")
    st.stop()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요 😊\n\n"
                "일정, 할 일, 공부 계획, 회의 내용을 입력하면\n"
                "깔끔하게 정리해드릴게요!"
            )
        }
    ]

# 채팅 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 입력창
prompt = st.chat_input("일정이나 할 일을 입력하세요...")

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 영역
    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        try:
            # 시스템 프롬프트
            system_prompt = """
            당신은 일정 정리 전문 AI 비서입니다.

            역할:
            - 사용자의 일정을 깔끔하게 정리
            - 우선순위 정리
            - 체크리스트 형태 제공
            - 시간 순서대로 정리
            - 중요한 일정 강조
            - 한국어로 자연스럽게 답변

            답변 스타일:
            - 보기 좋게 마크다운 사용
            - 필요 시 표 사용
            - 핵심 위주로 정리
            """

            # 이전 대화 기록 변환
            history = []

            for msg in st.session_state.messages:

                role = "user" if msg["role"] == "user" else "model"

                history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg["content"])]
                    )
                )

            # Gemini 호출
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.5,
                    max_output_tokens=1000,
                )
            )

            ai_response = response.text

            # 응답 출력
            message_placeholder.markdown(ai_response)

            # 채팅 기록 저장
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": ai_response
                }
            )

        except Exception as e:

            error_message = f"""
❌ 오류가 발생했습니다.

오류 내용:
{str(e)}
"""

            message_placeholder.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "죄송합니다 😢 오류가 발생했어요."
                }
            )

# 사이드바
with st.sidebar:

    st.header("⚙️ 기능")

    if st.button("채팅 기록 초기화"):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "안녕하세요 😊\n\n"
                    "일정을 입력하면 정리해드릴게요!"
                )
            }
        ]

        st.rerun()

    st.markdown("---")

    st.subheader("💡 예시 입력")

    st.markdown("""
    - 내일 해야 할 일 정리해줘  
    - 회의 내용 요약해줘  
    - 시험 공부 계획 짜줘  
    - 이번 주 일정 정리해줘  
    """)
