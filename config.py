import os

API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")