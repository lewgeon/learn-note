# logic.py
import random
import re
from config import NOTES_MAP, TYPES

class QuestionGenerator:
    def __init__(self):
        self.last_single = None

    def _get_random_item(self, q_type):
        return random.choice(NOTES_MAP[q_type])

    def generate_single(self, q_type):
        item = self._get_random_item(q_type)
        while item == self.last_single:
            item = self._get_random_item(q_type)
        self.last_single = item
        return item

    def generate_sequence(self, q_type, length):
        return [self._get_random_item(q_type) for _ in range(length)]

    def validate_single(self, question, q_type, answer):
        idx = NOTES_MAP[q_type].index(question)
        
        valid_answers = []
        for t in TYPES:
            if t != q_type:
                valid_answers.append(NOTES_MAP[t][idx].lower())
        
        return answer.strip().lower() in valid_answers

    def validate_sequence(self, question_seq, q_type, answer_seq_str):
        # 移除用户输入中的所有空格和逗号，统一转为小写
        cleaned_answer = re.sub(r'[\s,]+', '', answer_seq_str.strip().lower())
        
        # 动态构造正则表达式匹配模式
        pattern_parts = []
        for q in question_seq:
            idx = NOTES_MAP[q_type].index(q)
            valid_answers = []
            for t in TYPES:
                if t != q_type:
                    valid_answers.append(NOTES_MAP[t][idx].lower())
            
            # 将当前音符对应的所有合法答案用 "|" 拼接，并加上括号作为正则的一个分组
            # 例如对于音符 'C'，合法答案是 '1' 或 'do'，生成正则部件: (1|do)
            pattern_parts.append(f"({'|'.join(valid_answers)})")
            
        # 拼装成完整从头到尾的精确匹配正则
        # 如果序列是 ["C", "D"]，正则就是 ^(1|do)(2|re)$
        pattern = "^" + "".join(pattern_parts) + "$"
        
        # 进行正则匹配
        return bool(re.match(pattern, cleaned_answer))