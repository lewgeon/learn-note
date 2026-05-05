# config.py

# 音名、唱名与数字的对应关系字典
NOTES_MAP = {
    "数字": ["1", "2", "3", "4", "5", "6", "7"],
    "唱名": ["do", "re", "mi", "fa", "sol", "la", "si"],
    "音名": ["C", "D", "E", "F", "G", "A", "B"]
}

TYPES = ["数字", "唱名", "音名"]
MODES = ["单符号模式", "符号序列模式"]

# 默认设置
DEFAULT_TIME_LIMIT = 5
DEFAULT_SEQ_LENGTH = 4