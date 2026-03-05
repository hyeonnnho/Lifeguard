import pdfplumber
import json
import re

def extract_quiz_data(pdf_path, output_json_path):
    questions_data = []
    
    print("PDF 텍스트 추출을 시작합니다... (정밀 파싱 적용)")
    
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
            
        # 3. '해설' 식별
        if line.startswith("해 설") or line.startswith("해설"):
            current_q["explanation"] = line
            continue
            
        # 4. [수정됨] '보기' 식별 (한 줄에 여러 보기가 있는 경우 완벽 분리)
        markers = ['①', '②', '③', '④']
        if any(marker in line for marker in markers):
            # 만약 보기 기호보다 앞에 텍스트가 있다면, 그것은 '문제'의 일부가 줄바꿈된 것입니다.
            found_pos = [line.find(m) for m in markers if m in line]
            first_marker_pos = min(found_pos)
            
            if first_marker_pos > 0:
                before_text = line[:first_marker_pos].strip()
                if before_text:
                    current_q["question"] += " " + before_text
                    
            # 해당 줄에서 ①, ②, ③, ④ 단위로 쪼개서 보기 리스트에 추가
            # 정규식 해석: 보기 기호로 시작해서, 다음 보기 기호가 나오거나 줄이 끝날 때까지 추출
            options = re.findall(r'[①②③④]\s*(.*?)(?=[①②③④]|$)', line)
            for opt in options:
                clean_opt = opt.strip()
                if clean_opt:
                    current_q["options"].append(clean_opt)
            continue
            
        # 5. [추가됨] 어디에도 속하지 않는 텍스트 처리 (두 줄로 이어진 텍스트)
        if current_q["answerIndex"] != -1: 
            # 정답이 나온 후라면 해설이 길어서 줄바꿈된 것
            current_q["explanation"] += " " + line
        elif len(current_q["options"]) > 0:
            # 보기가 들어가는 중이었다면, 보기 내용이 길어서 줄바꿈된 것
            current_q["options"][-1] += " " + line
        else:
            # 보기가 시작되기도 전이라면, 문제 내용이 길어서 줄바꿈된 것
            current_q["question"] += " " + line

    # 마지막 문제 처리
    if current_q and current_q.get("answerIndex") != -1:
        questions_data.append(current_q)
        
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 정밀 데이터 정제 완료! 총 {len(questions_data)}문제가 저장되었습니다.")

# 스크립트 실행
extract_quiz_data("수상구조사 필기시험 문제은행.pdf", "quiz_data.json")