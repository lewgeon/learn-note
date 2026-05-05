# single_quiz.py (修改版)
import tkinter as tk
import random
from mappings import NOTES, note_to_display, user_input_to_note

class SingleQuiz:
    def __init__(self, display_type: str, input_type: str, time_limit: float,
                 on_result_callback, on_new_question_callback):
        self.display_type = display_type
        self.input_type = input_type
        self.time_limit = time_limit
        self.on_result = on_result_callback
        self.on_new_question = on_new_question_callback

        self.current_note = None
        self.last_note = None
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

    def start(self):
        """开始新的练习（生成第一个题目）"""
        self.stop()  # 确保清理之前的计时
        self.start_new_question()

    def stop(self):
        """停止当前练习，取消计时器"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.waiting_input = False

    def start_new_question(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.waiting_input = True
        choices = [n for n in NOTES if n != self.last_note] if self.last_note else NOTES[:]
        self.current_note = random.choice(choices)
        self.last_note = self.current_note
        display_text = note_to_display(self.current_note, self.display_type)
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
        correct_display = note_to_display(self.current_note, self.input_type)
        self.on_result(False, f"超时！正确答案: {correct_display}")
        self.start_new_question()

    def submit_answer(self, user_input: str):
        if not self.waiting_input:
            return False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.waiting_input = False
        try:
            user_note = user_input_to_note(user_input, self.input_type)
            is_correct = (user_note == self.current_note)
            correct_display = note_to_display(self.current_note, self.input_type)
            if is_correct:
                self.on_result(True, "正确！")
            else:
                self.on_result(False, f"错误！正确答案: {correct_display}")
        except ValueError:
            correct_display = note_to_display(self.current_note, self.input_type)
            self.on_result(False, f"无效输入！正确答案: {correct_display}")
        self.start_new_question()
        return True