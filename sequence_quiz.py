# sequence_quiz.py
import tkinter as tk
import random
import re
from mappings import NOTES, note_to_display, user_input_to_note

class SequenceQuiz:
    def __init__(self, display_type: str, input_type: str, seq_length: int, time_limit: float,
                 on_result_callback, on_new_question_callback):
        self.display_type = display_type
        self.input_type = input_type
        self.seq_length = seq_length
        self.time_limit = time_limit
        self.on_result = on_result_callback
        self.on_new_question = on_new_question_callback

        self.current_sequence = None
        self.waiting_input = False
        self.timer_id = None
        self.time_left = time_limit
        self.root = None
        self.on_timer_update = None

    def set_root(self, root):
        self.root = root

    def set_on_timer_update(self, callback):
        self.on_timer_update = callback

    def update_time_limit(self, new_limit):
        self.time_limit = new_limit

    def update_seq_length(self, new_len):
        self.seq_length = new_len

    def start(self):
        self.stop()
        self.start_new_question()

    def stop(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.waiting_input = False

    def start_new_question(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.waiting_input = True
        self.current_sequence = [random.choice(NOTES) for _ in range(self.seq_length)]
        display_items = [note_to_display(n, self.display_type) for n in self.current_sequence]
        display_text = "  ".join(display_items)
        self.on_new_question(display_text)
        self.time_left = self.time_limit
        self._update_timer_display()
        self._start_timer()

    def _start_timer(self):
        if self.time_left <= 0:
            self._timeout()
            return
        self.timer_id = self.root.after(1000, self._countdown)

    def _countdown(self):
        if not self.waiting_input:
            return
        if self.time_left <= 0:
            self._timeout()
        else:
            self.time_left -= 1
            self._update_timer_display()
            self.timer_id = self.root.after(1000, self._countdown)

    def _update_timer_display(self):
        if self.on_timer_update:
            self.on_timer_update(self.time_left)

    def _timeout(self):
        if not self.waiting_input:
            return
        self.waiting_input = False
        correct_answers = [note_to_display(n, self.input_type) for n in self.current_sequence]
        correct_str = " ".join(correct_answers)
        self.on_result(False, f"超时！正确答案: {correct_str}")
        self.start_new_question()

    def submit_answer(self, user_input: str):
        if not self.waiting_input:
            return False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.waiting_input = False

        parts = re.split(r'\s+', user_input.strip())
        if len(parts) != self.seq_length:
            correct_answers = [note_to_display(n, self.input_type) for n in self.current_sequence]
            correct_str = " ".join(correct_answers)
            self.on_result(False, f"长度错误！需要 {self.seq_length} 个，你输入了 {len(parts)} 个。正确答案: {correct_str}")
            self.start_new_question()
            return True

        user_notes = []
        valid = True
        for i, token in enumerate(parts):
            try:
                note = user_input_to_note(token, self.input_type)
                user_notes.append(note)
            except ValueError:
                self.on_result(False, f"第{i+1}项 '{token}' 无效")
                valid = False
                break
        if not valid:
            self.start_new_question()
            return True

        if user_notes == self.current_sequence:
            self.on_result(True, "完全正确！")
        else:
            correct_answers = [note_to_display(n, self.input_type) for n in self.current_sequence]
            correct_str = " ".join(correct_answers)
            self.on_result(False, f"错误！正确答案: {correct_str}")
        self.start_new_question()
        return True