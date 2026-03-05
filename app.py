import streamlit as st
import json
import random

@st.cache_data
def load_data():
    with open("quiz_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

all_data = load_data()

# --- 1. 사이드바 (좌측 메뉴) 구성 ---
st.sidebar.title("📚 학습 메뉴")
selected_part = st.sidebar.radio(
    "과목을 선택하세요",
    (
        "🎲 랜덤 1문제 풀기 (무한 반복)",   # 새로 추가된 랜덤 모드
        "전체 모의고사 (500문제)", 
        "PART 1. 수상구조사의 자세", 
        "PART 2. 조난사고의 이해", 
        "PART 3. 관련 법령", 
        "PART 4. 응급처치", 
        "PART 5. 구조기술", 
        "PART 6. 지도자의 자질", 
        "PART 7. 생존수영"
    )
)

# --- 2. 앱 상태 초기화 및 관리 ---
if 'previous_menu' not in st.session_state:
    st.session_state.previous_menu = selected_part
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'random_q' not in st.session_state:
    st.session_state.random_q = random.choice(all_data)

# 메뉴가 변경될 때마다 풀이 상태를 초기화
if st.session_state.previous_menu != selected_part:
    st.session_state.current_index = 0
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.previous_menu = selected_part
    # 랜덤 모드로 넘어왔을 때 새로운 문제 하나 뽑기
    if "랜덤" in selected_part:
        st.session_state.random_q = random.choice(all_data)

# '다음 문제' 버튼을 눌렀을 때 실행되는 함수
def next_question():
    if "랜덤" in selected_part:
        st.session_state.random_q = random.choice(all_data) # 랜덤 문제 새로 뽑기
    else:
        st.session_state.current_index += 1 # 순차적으로 다음 문제로 이동
        
    st.session_state.answered = False
    st.session_state.selected_option = None

# --- 3. 선택한 과목에 따라 데이터 설정 ---
is_random_mode = "랜덤" in selected_part

# ※ 순차 모드일 때만 데이터를 자릅니다. (인덱스는 실제 PDF에 맞게 수정 필요)
if not is_random_mode:
    if selected_part == "전체 모의고사 (500문제)":
        quiz_data = all_data
    elif "PART 1" in selected_part:
        quiz_data = all_data[0:30]
    elif "PART 2" in selected_part:
        quiz_data = all_data[30:80]
    elif "PART 3" in selected_part:
        quiz_data = all_data[80:130]
    elif "PART 4" in selected_part:
        quiz_data = all_data[130:200]
    elif "PART 5" in selected_part:
        quiz_data = all_data[200:300]
    elif "PART 6" in selected_part:
        quiz_data = all_data[300:400]
    elif "PART 7" in selected_part:
        quiz_data = all_data[400:500] 
else:
    quiz_data = [] # 랜덤 모드에서는 자른 데이터를 쓰지 않음

# --- 4. 메인 화면 UI ---
st.title("🏊‍♂️ 수상구조사 필기시험 문제은행")
st.write(f"**현재 모드:** {selected_part}")

# 순차 모드에서 모든 문제를 다 푼 경우
if not is_random_mode and st.session_state.current_index >= len(quiz_data):
    st.success("해당 파트의 모든 문제를 다 풀었습니다! 🎉")
    if st.button("처음부터 다시 풀기"):
        st.session_state.current_index = 0
        st.session_state.answered = False
        st.rerun()
else:
    # 어떤 데이터를 화면에 띄울지 결정
    if is_random_mode:
        q_data = st.session_state.random_q
        st.caption("전체 500문제 중 무작위 출제 중입니다.")
    else:
        q_data = quiz_data[st.session_state.current_index]
        st.caption(f"문제 {st.session_state.current_index + 1} / {len(quiz_data)}")
    
    st.subheader(q_data["question"])
    
    # 보기 버튼
    for i, option in enumerate(q_data["options"]):
        if st.button(f"{i + 1}. {option}", key=f"btn_{i}", disabled=st.session_state.answered):
            st.session_state.selected_option = i
            st.session_state.answered = True
            st.rerun()

    # 정답/오답 및 해설 출력
    if st.session_state.answered:
        if st.session_state.selected_option == q_data["answerIndex"]:
            st.success("✅ 정답입니다!")
        else:
            st.error("❌ 오답입니다.")
            st.info(f"정답: {q_data['answerIndex'] + 1}번")
        
        st.warning(f"**해설:** {q_data['explanation']}")
        
        st.button("다음 문제 ➡️", on_click=next_question)