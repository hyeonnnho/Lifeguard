import streamlit as st
import json

# 1. 외부 JSON 파일에서 문제 데이터 불러오기
@st.cache_data # 파일을 한 번만 읽어오도록 하여 속도를 높임
def load_data():
    with open("quiz_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

quiz_data = load_data()

# 2. 앱 진행 상태 초기화
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

def next_question():
    st.session_state.current_index += 1
    st.session_state.answered = False
    st.session_state.selected_option = None

# 3. 화면 UI 구성
st.title("🏊‍♂️ 수상구조사 필기시험 문제은행")

if st.session_state.current_index >= len(quiz_data):
    st.success("모든 문제를 다 풀었습니다! 🎉")
    if st.button("처음부터 다시 풀기"):
        st.session_state.current_index = 0
        st.session_state.answered = False
        st.rerun()
else:
    q_data = quiz_data[st.session_state.current_index]
    
    st.caption(f"문제 {st.session_state.current_index + 1} / {len(quiz_data)}")
    st.subheader(q_data["question"])
    
    # 보기 버튼 생성
    for i, option in enumerate(q_data["options"]):
        if st.button(f"{i + 1}. {option}", key=f"btn_{i}", disabled=st.session_state.answered):
            st.session_state.selected_option = i
            st.session_state.answered = True
            st.rerun()

    # 정답 선택 후 결과 및 해설 노출
    if st.session_state.answered:
        if st.session_state.selected_option == q_data["answerIndex"]:
            st.success("✅ 정답입니다!")
        else:
            st.error("❌ 오답입니다.")
            st.info(f"정답: {q_data['answerIndex'] + 1}번")
        
        st.warning(f"**해설:** {q_data['explanation']}")
        
        st.button("다음 문제 ➡️", on_click=next_question)