import google.generativeai as genai
from config import API_KEY

class Translator:
    def __init__(self, logger):
        self.logger = logger
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def translate_item(self, cut_scen_key, korean_text, df, target_lang, character_info):
        try:
            self.logger.info(f"번역 시작: cut_scen_key={cut_scen_key}, korean_text={korean_text}")
            
            if self.is_symbol_only(korean_text):
                self.logger.info("텍스트가 기호만으로 구성되어 있어 번역을 생략합니다.")
                return korean_text

            if not target_lang:
                raise ValueError("번역할 언어를 선택해주세요.")

            lang_column = f"m_Talk_{self.get_lang_code(target_lang)}"
            row_index = df.index[df['m_CutScenKey'] == cut_scen_key].tolist()[0]
            
            speaker = df.at[row_index, "m_CharStr"]
            speaker_info = character_info.get_info(speaker, target_lang)
            
            previous_dialogues = self.get_previous_dialogues(df, row_index, 3)
            
            english_text = df.at[row_index, "m_Talk_ENG"] if "m_Talk_ENG" in df.columns else None
            japanese_text = df.at[row_index, "m_Talk_JAPAN"] if "m_Talk_JAPAN" in df.columns else None
            
            prompt = self.create_translation_prompt(target_lang, korean_text, speaker_info, previous_dialogues, english_text, japanese_text)

            response = self.model.generate_content(prompt)

            if not response.parts:
                raise ValueError("번역 결과가 반환되지 않았습니다. API 응답을 확인하세요.")

            translated_text = response.text.strip()

            self.logger.info(f"번역이 완료되었습니다: {translated_text}")

            return translated_text
        except Exception as e:
            self.logger.error(f"번역 중 오류 발생: {str(e)}")
            return f"번역 오류: {str(e)}"

    def is_symbol_only(self, text):
        return text.strip().translate(str.maketrans("", "", "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/")) == ""

    def get_previous_dialogues(self, df, current_index, count):
        previous_dialogues = []
        for i in range(current_index - 1, max(0, current_index - count - 1), -1):
            speaker = df.at[i, "m_CharStr"]
            text = df.at[i, "m_Talk_KOREA"]
            if pd.notna(speaker) and pd.notna(text):
                previous_dialogues.append((speaker, text))
        return list(reversed(previous_dialogues))

    def create_translation_prompt(self, target_lang, korean_text, speaker_info, previous_dialogues, english_text=None, japanese_text=None):
        prompt = f"다음 한국어 텍스트를 {target_lang}으로 번역하세요. 일본 애니메이션에 등장하는 인물의 대사입니다.\n\n"
        
        if previous_dialogues:
            prompt += "이전 대화 내용:\n"
            for speaker, text in previous_dialogues:
                prompt += f"{speaker}: {text}\n"
            prompt += "\n"
        
        prompt += f"지금 번역해야할 한국어 대사: {korean_text}\n"
        
        if english_text:
            prompt += f"참고용 영어 번역: {english_text}\n"
        if japanese_text:
            prompt += f"참고용 일본어 번역: {japanese_text}\n"

        prompt += "\n"
        
        if speaker_info:
            prompt += f"현재 화자는 {speaker_info['name']}입니다. "
            if 'age' in speaker_info:
                prompt += f"나이는 {speaker_info['age']}세, 나이에 맞는 어투로 말해주세요. "
            if 'gender' in speaker_info:
                if speaker_info['gender'] == 'F':
                    prompt += "여성입니다. "
                elif speaker_info['gender'] == 'M':
                    prompt += "남성입니다. "
                else:
                    prompt += f"성별은 {speaker_info['gender']}입니다. "
            if 'personality' in speaker_info:
                prompt += f"성격은 {speaker_info['personality']}이고, "
            if 'speech' in speaker_info:
                prompt += f"'{speaker_info['speech']}' 같은 말투를 사용합니다. "
        else:
            prompt += "이 대사는 나레이션입니다. "
        
        prompt += f"\n\n이러한 특성과 이전 대화의 맥락, 그리고 제공된 영어와 일본어 번역(있는 경우)을 참고하여 {target_lang}으로 번역해주세요. 단어의 뉘앙스와 맥락을 잘 살려주세요."
        
        self.logger.info(f"생성된 번역 프롬프트: {prompt}")
        return prompt

    def get_lang_code(self, target_lang):
        lang_codes = {
            "일본어": "JAPAN",
            "영어": "ENG",
            "대만어": "TWN",
            "태국어": "THA",
            "베트남어": "VTN",
            "중국어": "SCN",
            "독일어": "DEU",
            "프랑스어": "FRA"
        }
        return lang_codes.get(target_lang, "")