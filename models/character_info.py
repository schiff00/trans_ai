import pandas as pd

class CharacterInfo:
    def __init__(self, logger):
        self.logger = logger
        self.data = None

    def load_from_file(self, file_path):
        try:
            self.data = pd.read_excel(file_path)
            self.logger.info(f"캐릭터 정보 파일이 로드되었습니다: {file_path}")
            self.logger.info(f"캐릭터 정보 열: {self.data.columns}")
            self.logger.info(f"캐릭터 정보 샘플:\n{self.data.head()}")
        except Exception as e:
            self.logger.error(f"캐릭터 정보 파일 로드 중 오류 발생: {str(e)}")
            raise

    def get_info(self, speaker, target_lang):
        if self.data is None or pd.isna(speaker) or speaker == "":
            self.logger.warning(f"캐릭터 정보가 로드되지 않았거나 화자 정보가 없습니다. 화자: {speaker}")
            return None

        possible_column_names = ['스크립트에출력될캐릭터이름', 'm_CharStr', 'm_CharStr_KOREA', '캐릭터명']
        character_name_column = next((col for col in possible_column_names if col in self.data.columns), None)

        if character_name_column is None:
            self.logger.warning("캐릭터 이름을 포함하는 열을 찾을 수 없습니다.")
            return None

        character_info = self.data[self.data[character_name_column] == speaker]
        if character_info.empty:
            self.logger.warning(f"화자 '{speaker}'의 정보가 없습니다.")
            return None

        info = {'name': speaker}
        for column, key in [('age', 'age'), ('Gender', 'gender'), ('Personality', 'personality'), ('Speech', 'speech')]:
            if column in character_info.columns and pd.notna(character_info[column].iloc[0]):
                info[key] = character_info[column].iloc[0]

        self.logger.info(f"화자 '{speaker}'의 정보: {info}")
        return info