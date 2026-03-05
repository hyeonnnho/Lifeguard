import pdfplumber
import json
import re

def extract_quiz_data(pdf_path, output_json_path):
    questions_data = []
    
    print("PDF 텍스트 추출을 시작합니다... (보기/해설 완벽 분리 적용)")
    
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
            
    lines = full_text.split('\n')
    current_q = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # --- [노이즈 데이터 자동 필터링 로직] ---
        # 1. 책 제목 및 헤더 무시
        if line == "수상구조사 필기시험 문제은행" or line == "CONTENTS":
            continue
        # 2. 페이지 번호 (숫자만 있는 줄) 무시
        if re.match(r'^\d+$', line):
            continue
        # 3. 파트 제목 무시 (예: "PART 01 수상구조사의 자세", "PART 01" 등)
        if line.startswith("PART"):
            continue
        # ----------------------------------------
        
        # 1. '문제' 식별
        if re.match(r'^(\d+)\.\s*(.*)', line):
            if current_q and current_q.get("answerIndex") != -1:
                questions_data.append(current_q)
            
            current_q = {
                "question": line,
                "options": [],
                "answerIndex": -1,
                "explanation": ""
            }
            continue
            
        if not current_q:
            continue
            
        # 2. '정답' 식별
        ans_match = re.search(r'정\s*답\s*([①②③④])', line)
        if ans_match:
            ans_char = ans_match.group(1)
            mapping = {'①': 0, '②': 1, '③': 2, '④': 3}
            current_q["answerIndex"] = mapping.get(ans_char, -1)
            continue
            
        # 3. '해설' 식별 (명시적 시작 단어)
        if line.startswith("해 설") or line.startswith("해설"):
            current_q["explanation"] += " " + line
            continue
            
        # 4. [핵심 수정] 정답이 이미 나왔다면, 이후의 모든 텍스트는 해설에 이어붙입니다! (보기 기호 무시)
        if current_q["answerIndex"] != -1:
            current_q["explanation"] += " " + line
            continue
            
        # 5. '보기' 식별 (정답이 나오기 전까지만 작동)
        markers = ['①', '②', '③', '④']
        if any(marker in line for marker in markers):
            found_pos = [line.find(m) for m in markers if m in line]
            first_marker_pos = min(found_pos)
            
            # 보기 기호 앞의 텍스트는 문제의 일부
            if first_marker_pos > 0:
                before_text = line[:first_marker_pos].strip()
                if before_text:
                    current_q["question"] += " " + before_text
                    
            options = re.findall(r'[①②③④]\s*(.*?)(?=[①②③④]|$)', line)
            for opt in options:
                clean_opt = opt.strip()
                if clean_opt:
                    current_q["options"].append(clean_opt)
            continue
            
        # 6. 어디에도 속하지 않는 텍스트 (정답 이전)
        if len(current_q["options"]) > 0:
            # 보기가 있는 상태라면 마지막 보기에 이어 붙임
            current_q["options"][-1] += " " + line
        else:
            # 보기가 아직 없다면 문제에 이어 붙임
            current_q["question"] += " " + line

    # 마지막 문제 처리
    if current_q and current_q.get("answerIndex") != -1:
        questions_data.append(current_q)
        
    # 콘솔에서 디버깅: 보기가 4개가 아닌 문항이 있는지 검사
    abnormal_count = 0
    for q in questions_data:
        if len(q["options"]) != 4:
            print(f"⚠️ 확인 필요: 문제 '{q['question'][:25]}...' 의 보기 개수가 {len(q['options'])}개입니다.")
            abnormal_count += 1

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ 정제 완료! 총 {len(questions_data)}문제 저장됨.")
    if abnormal_count == 0:
        print("🎉 모든 문제의 보기가 완벽하게 4개씩 분리되었습니다!")

# 스크립트 실행
extract_quiz_data("수상구조사 필기시험 문제은행.pdf", "quiz_data.json")