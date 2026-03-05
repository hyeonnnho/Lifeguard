import pdfplumber
import json
import re

def extract_quiz_data(pdf_path, output_json_path):
    questions_data = []
    
    print("PDF 텍스트 추출을 시작합니다... (약간의 시간이 소요될 수 있습니다)")
    
    # 1. PDF 열기 및 텍스트 추출
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
            
    # 2. 한 줄씩 순차적으로 읽으며 데이터 정제
    lines = full_text.split('\n')
    current_q = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # [수정] 1. '문제' 식별 (예: "1. 수상구조사의...")
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
            
        # [수정] 2. '정답' 식별을 보기보다 먼저! (예: "정 답 ④")
        ans_match = re.search(r'정\s*답\s*([①②③④])', line)
        if ans_match:
            ans_char = ans_match.group(1)
            mapping = {'①': 0, '②': 1, '③': 2, '④': 3}
            current_q["answerIndex"] = mapping.get(ans_char, -1)
            continue
            
        # [수정] 3. '해설' 식별도 보기보다 먼저!
        if line.startswith("해 설") or line.startswith("해설"):
            current_q["explanation"] = line
            continue
            
        # [수정] 4. 마지막으로 '보기' 식별
        if any(marker in line for marker in ['①', '②', '③', '④']):
            # 보기 앞의 번호 제거 후 추가
            clean_option = re.sub(r'^[①②③④]\s*', '', line)
            current_q["options"].append(clean_option)
            continue
            
        # 5. 정답이 이미 나왔다면, 이어진 해설 텍스트로 간주하여 붙임
        if current_q["answerIndex"] != -1: 
             current_q["explanation"] += " " + line

    # 마지막 문제 추가
    if current_q and current_q.get("answerIndex") != -1:
        questions_data.append(current_q)
        
    # 3. 완성된 데이터를 JSON 파일로 저장
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 데이터 정제 완료! 총 {len(questions_data)}문제가 {output_json_path}에 저장되었습니다.")

# 스크립트 실행
extract_quiz_data("수상구조사 필기시험 문제은행.pdf", "quiz_data.json")