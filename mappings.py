# mappings.py
# 基础映射：音名 -> (数字, 唱名列表)
NOTE_MAP = {
    'C': {'num': '1', 'solfege': ['do']},
    'D': {'num': '2', 'solfege': ['re']},
    'E': {'num': '3', 'solfege': ['mi']},
    'F': {'num': '4', 'solfege': ['fa']},
    'G': {'num': '5', 'solfege': ['sol', 'so']},
    'A': {'num': '6', 'solfege': ['la']},
    'B': {'num': '7', 'solfege': ['si', 'ti']}
}
NOTES = list(NOTE_MAP.keys())  # ['C','D','E','F','G','A','B']

# 辅助映射：唱名 -> 音名
SOLFEGE_TO_NOTE = {s: note for note, data in NOTE_MAP.items() for s in data['solfege']}
# 辅助映射：数字 -> 音名
NUM_TO_NOTE = {data['num']: note for note, data in NOTE_MAP.items()}

def note_to_display(note: str, display_type: str) -> str:
    """将音名根据显示类型转换为对应的字符串"""
    if display_type == 'note':
        return note
    elif display_type == 'num':
        return NOTE_MAP[note]['num']
    elif display_type == 'solfege':
        return NOTE_MAP[note]['solfege'][0]  # 取第一个唱名
    else:
        raise ValueError(f"Unknown display type: {display_type}")

def user_input_to_note(user_str: str, input_type: str) -> str:
    """将用户输入的字符串（根据输入类型）转换为标准音名"""
    s = user_str.strip().lower()
    if input_type == 'note':
        upper = s.upper()
        if upper in NOTES:
            return upper
    elif input_type == 'num':
        if s in NUM_TO_NOTE:
            return NUM_TO_NOTE[s]
    elif input_type == 'solfege':
        if s in SOLFEGE_TO_NOTE:
            return SOLFEGE_TO_NOTE[s]
    raise ValueError(f"Invalid {input_type} input: {user_str}")

def is_valid_input(user_str: str, input_type: str) -> bool:
    """检查用户输入是否合法（用于实时验证，可选）"""
    try:
        user_input_to_note(user_str, input_type)
        return True
    except ValueError:
        return False