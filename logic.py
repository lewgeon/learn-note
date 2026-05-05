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
        # 移除可能存在的空格
        cleaned_answer = re.sub(r'\s+', '', answer_seq_str.strip().lower())
        
        pattern_parts = []
        for q in question_seq:
            idx = NOTES_MAP[q_type].index(q)
            valid_answers = []
            for t in TYPES:
                if t != q_type:
                    valid_answers.append(NOTES_MAP[t][idx].lower())
            pattern_parts.append(f"({'|'.join(valid_answers)})")
            
        pattern = "^" + "".join(pattern_parts) + "$"
        return bool(re.match(pattern, cleaned_answer))