from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# 업로드 폴더 설정
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 초기 가짜 데이터 (서버 실행 시 엑셀 없이도 화면이 깨지지 않게 함)
DEFAULT_DATA = [
    {'location': 'A101', 'type': 'WUR', 'qty': 1600},
    {'location': 'A102', 'type': 'WCRS', 'qty': 1701},
    {'location': 'A103', 'type': 'WASW', 'qty': 604},
    {'location': 'A104', 'type': 'WASWP', 'qty': 1403},
    {'location': 'A201', 'type': 'WUSH', 'qty': 27},
    {'location': 'B101', 'type': 'BU', 'qty': 2213},
    {'location': 'B102', 'type': 'BU', 'qty': 2233},
]

@app.route('/', methods=['GET', 'POST'])
def index():
    data = DEFAULT_DATA
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                try:
                    # 엑셀 파일 읽기 (헤더가 첫 줄에 있다고 가정)
                    df = pd.read_excel(filepath)
                    data = []
                    # 데이터프레임 순회 (이미지 기준: 0번=위치, 1번=종류, 3번=재고)
                    for _, row in df.iterrows():
                        # 값이 비어있는 행 제외
                        if pd.isna(row.iloc[0]): continue
                        
                        loc = str(row.iloc[0])
                        qty_val = row.iloc[3]
                        
                        # 재고량이 숫자가 아닐 경우 처리
                        try:
                            qty = int(float(qty_val))
                        except:
                            qty = 0

                        data.append({
                            'location': loc,
                            'type': str(row.iloc[1]),
                            'qty': qty
                        })
                except Exception as e:
                    print(f"에러 발생: {e}")

    # 요약표 데이터 계산 (종류별로 A구역, B구역 합계 계산)
    summary_dict = {}
    
    for item in data:
        t = item['type']
        qty = item['qty']
        loc = item['location']
        
        if t not in summary_dict:
            summary_dict[t] = {'A': 0, 'B': 0, 'Total': 0}
            
        # 위치 첫 글자로 구역 판단 (A..., B...)
        zone = loc[0].upper()
        if zone == 'A':
            summary_dict[t]['A'] += qty
        elif zone == 'B':
            summary_dict[t]['B'] += qty
            
        summary_dict[t]['Total'] += qty

    return render_template('index.html', inventory=data, summary=summary_dict)

if __name__ == '__main__':
    app.run(debug=True, port=5000)