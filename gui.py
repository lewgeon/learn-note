# gui.py
import tkinter as tk
from tkinter import ttk
from config import TYPES, MODES, DEFAULT_TIME_LIMIT, DEFAULT_SEQ_LENGTH
from logic import QuestionGenerator

class MusicTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音名唱名数字转换训练器")
        self.root.geometry("580x450") 
        
        self.logic = QuestionGenerator()
        
        # 状态变量
        self.current_question = None
        self.time_left = 0
        self.timer_id = None
        self.feedback_id = 0
        self.is_paused = False  
        
        # 统计变量
        self.correct_count = 0
        self.wrong_count = 0
        
        # Tkinter 变量声明
        self.mode_var = tk.StringVar(value=MODES[0])
        self.type_var = tk.StringVar(value=TYPES[0])
        self.time_var = tk.IntVar(value=DEFAULT_TIME_LIMIT)
        self.seq_var = tk.IntVar(value=DEFAULT_SEQ_LENGTH)
        
        self.setup_ui()
        
        self.mode_var.trace_add("write", self.on_mode_change)
        self.mode_var.trace_add("write", self.interrupt_game)
        self.type_var.trace_add("write", self.interrupt_game)
        self.time_var.trace_add("write", self.interrupt_game)
        self.seq_var.trace_add("write", self.interrupt_game)
        
        self.on_mode_change()
        
    def setup_ui(self):
        # --- 设置区域 (顶部) ---
        frame_settings = tk.LabelFrame(self.root, text="游戏设置", padx=10, pady=10)
        frame_settings.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_settings, text="主模式:").grid(row=0, column=0, sticky="e")
        self.combo_mode = ttk.Combobox(frame_settings, textvariable=self.mode_var, values=MODES, state="readonly", width=12)
        self.combo_mode.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_settings, text="出题类型:").grid(row=0, column=2, sticky="e")
        ttk.Combobox(frame_settings, textvariable=self.type_var, values=TYPES, state="readonly", width=8).grid(row=0, column=3, padx=5)
        
        tk.Label(frame_settings, text="时间限制(秒):").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Spinbox(frame_settings, from_=1, to=60, textvariable=self.time_var, width=5).grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(frame_settings, text="序列长度:").grid(row=1, column=2, sticky="e", pady=5)
        self.spin_seq = ttk.Spinbox(frame_settings, from_=2, to=10, textvariable=self.seq_var, width=5)
        self.spin_seq.grid(row=1, column=3, sticky="w", padx=5)
        
        # 按钮区
        tk.Button(frame_settings, text="开始训练", command=self.start_game, bg="lightblue").grid(row=0, column=4, rowspan=2, padx=(10, 5), sticky="nsew")
        self.btn_pause = tk.Button(frame_settings, text="暂停", command=self.toggle_pause, state="disabled")
        self.btn_pause.grid(row=0, column=5, rowspan=2, padx=(0, 5), sticky="nsew")

        # --- 统计区域 ---
        frame_stats = tk.Frame(self.root)
        frame_stats.pack(fill="x", padx=20, pady=5)
        self.lbl_stats = tk.Label(frame_stats, text="正确: 0   |   错误: 0", font=("Arial", 12, "bold"), fg="purple")
        self.lbl_stats.pack(side="right")

        # --- 游戏区域 (中部) ---
        frame_game = tk.Frame(self.root, padx=10, pady=10)
        frame_game.pack(fill="both", expand=True)
        
        self.lbl_timer = tk.Label(frame_game, text="准备就绪", font=("Arial", 12), fg="blue")
        self.lbl_timer.pack()
        
        self.lbl_question = tk.Label(frame_game, text="---", font=("Arial", 36, "bold"))
        self.lbl_question.pack(pady=20)
        
        frame_input = tk.Frame(frame_game)
        frame_input.pack()
        
        self.entry_answer = tk.Entry(frame_input, font=("Arial", 16), width=15)
        self.entry_answer.pack(side="left", padx=10)
        self.entry_answer.bind("<Return>", self.check_answer)
        self.entry_answer.config(state="disabled")
        
        self.lbl_feedback = tk.Label(frame_input, text="", font=("Arial", 14, "bold"), width=10)
        self.lbl_feedback.pack(side="left")

        # 修改了这里的提示文本
        self.lbl_hint = tk.Label(frame_game, text="输入另外两种类型之一。(序列模式可连续输入，无需空格)", fg="gray")
        self.lbl_hint.pack(pady=10)

    def on_mode_change(self, *args):
        if self.mode_var.get() == "单符号模式":
            self.spin_seq.config(state="disabled")
        else:
            self.spin_seq.config(state="normal")

    def interrupt_game(self, *args):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        self.current_question = None
        self.lbl_question.config(text="---")
        self.entry_answer.delete(0, tk.END)
        self.entry_answer.config(state="disabled")
        
        self.is_paused = False
        self.btn_pause.config(text="暂停", state="disabled")
        
        self.correct_count = 0
        self.wrong_count = 0
        self.update_stats_display()
        
        self.lbl_timer.config(text="设置已更改，请点击「开始训练」", fg="orange")
        self.lbl_feedback.config(text="")

    def update_stats_display(self):
        self.lbl_stats.config(text=f"正确: {self.correct_count}   |   错误: {self.wrong_count}")

    def toggle_pause(self):
        if not self.current_question:
            return
            
        if self.is_paused:
            self.is_paused = False
            self.btn_pause.config(text="暂停")
            self.entry_answer.config(state="normal")
            self.entry_answer.focus()
            self.update_timer()
        else:
            self.is_paused = True
            self.btn_pause.config(text="继续")
            self.entry_answer.config(state="disabled")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.lbl_timer.config(text=f"已暂停 (剩余时间: {self.time_left} 秒)", fg="orange")

    def start_game(self):
        self.correct_count = 0
        self.wrong_count = 0
        self.update_stats_display()
        
        self.is_paused = False
        self.btn_pause.config(text="暂停", state="normal")
        self.entry_answer.config(state="normal")
        self.entry_answer.focus()
        self.next_question()

    def next_question(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            
        mode = self.mode_var.get()
        q_type = self.type_var.get()
        
        try:
            seq_length = self.seq_var.get()
            time_limit = self.time_var.get()
        except tk.TclError:
            self.lbl_timer.config(text="配置格式错误!", fg="red")
            return
            
        if mode == "单符号模式":
            self.current_question = self.logic.generate_single(q_type)
            self.lbl_question.config(text=self.current_question)
        else:
            self.current_question = self.logic.generate_sequence(q_type, seq_length)
            self.lbl_question.config(text=" ".join(self.current_question))
            
        self.entry_answer.delete(0, tk.END)
        self.time_left = time_limit
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.lbl_timer.config(text=f"剩余时间: {self.time_left} 秒", fg="blue")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.wrong_count += 1
            self.update_stats_display()
            self.show_feedback("超时错误!", "red")
            self.next_question()

    def check_answer(self, event=None):
        if not self.current_question or self.is_paused: return
        
        answer = self.entry_answer.get()
        mode = self.mode_var.get()
        q_type = self.type_var.get()
        
        is_correct = False
        if mode == "单符号模式":
            is_correct = self.logic.validate_single(self.current_question, q_type, answer)
        else:
            is_correct = self.logic.validate_sequence(self.current_question, q_type, answer)
            
        if is_correct:
            self.correct_count += 1
            self.show_feedback("正确 ✔", "green")
        else:
            self.wrong_count += 1
            self.show_feedback("错误 ✘", "red")
            
        self.update_stats_display()
        self.next_question()

    def show_feedback(self, text, color):
        self.feedback_id += 1
        current_id = self.feedback_id
        
        self.lbl_feedback.config(text=text, fg=color)
        
        def clear_if_current():
            if self.feedback_id == current_id:
                self.lbl_feedback.config(text="")
                
        self.root.after(1500, clear_if_current)