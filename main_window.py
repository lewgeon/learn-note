# main_window.py
import tkinter as tk
from tkinter import ttk
from single_quiz import SingleQuiz
from sequence_quiz import SequenceQuiz

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("音名练习器 - 多模式")
        self.root.geometry("720x580")
        self.root.resizable(False, False)

        # 控制变量
        self.mode_var = tk.StringVar(value="single")
        self.display_type = tk.StringVar(value="note")
        self.input_type = tk.StringVar(value="num")
        self.seq_length = tk.IntVar(value=3)
        self.time_limit = tk.DoubleVar(value=5.0)

        self.quiz = None          # 当前quiz实例
        self.is_started = False   # 是否已点击开始

        self._create_widgets()
        self._update_info()
        # 初始状态：未开始，禁用输入框，显示开始按钮可用
        self._set_started_state(False)

    def _create_widgets(self):
        # 顶部控制面板
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5, fill=tk.X)

        # 模式选择
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(mode_frame, text="模式:").pack(side=tk.LEFT)
        modes = [("单题", "single"), ("序列", "sequence")]
        for text, val in modes:
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val,
                                command=self._on_setting_changed)
            rb.pack(side=tk.LEFT, padx=5)

        # 显示类型
        disp_frame = tk.Frame(control_frame)
        disp_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(disp_frame, text="显示为:").pack(side=tk.LEFT)
        disp_opts = [("音名", "note"), ("数字", "num"), ("唱名", "solfege")]
        for text, val in disp_opts:
            rb = tk.Radiobutton(disp_frame, text=text, variable=self.display_type, value=val,
                                command=self._on_setting_changed)
            rb.pack(side=tk.LEFT, padx=5)

        # 输入类型
        input_frame = tk.Frame(control_frame)
        input_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(input_frame, text="输入为:").pack(side=tk.LEFT)
        input_opts = [("音名", "note"), ("数字", "num"), ("唱名", "solfege")]
        for text, val in input_opts:
            rb = tk.Radiobutton(input_frame, text=text, variable=self.input_type, value=val,
                                command=self._on_setting_changed)
            rb.pack(side=tk.LEFT, padx=5)

        # 序列长度（仅序列模式显示）
        self.len_frame = tk.Frame(control_frame)
        tk.Label(self.len_frame, text="序列长度:").pack(side=tk.LEFT)
        self.len_spin = tk.Spinbox(self.len_frame, from_=2, to=6, width=3,
                                   textvariable=self.seq_length, command=self._on_seq_len_changed)
        self.len_spin.pack(side=tk.LEFT, padx=5)

        # 时间限制滑动条（共用）
        time_frame = tk.Frame(control_frame)
        time_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(time_frame, text="限时(秒):").pack(side=tk.LEFT)
        self.time_slider = tk.Scale(time_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                    resolution=0.5, length=120, variable=self.time_limit,
                                    command=self._on_time_changed)
        self.time_slider.pack(side=tk.LEFT)

        # 开始按钮
        self.start_btn = tk.Button(control_frame, text="开始练习", command=self._start_practice,
                                   bg="lightgreen")
        self.start_btn.pack(side=tk.LEFT, padx=10)

        # 重置统计按钮
        reset_btn = tk.Button(control_frame, text="重置统计", command=self._reset_stats)
        reset_btn.pack(side=tk.RIGHT, padx=10)

        # 题目显示区域
        self.question_label = tk.Label(self.root, text="", font=("Arial", 48, "bold"), fg="blue")
        self.question_label.pack(pady=30)

        # 倒计时显示
        self.timer_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.timer_label.pack(pady=5)

        # 输入区域
        input_area = tk.Frame(self.root)
        input_area.pack(pady=20)
        tk.Label(input_area, text="你的答案:").pack(side=tk.LEFT)
        self.entry = tk.Entry(input_area, font=("Arial", 14), width=30)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", self._on_submit)
        submit_btn = tk.Button(input_area, text="提交", command=self._on_submit)
        submit_btn.pack(side=tk.LEFT)

        # 反馈标签
        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), fg="red")
        self.feedback_label.pack(pady=10)

        # 统计标签
        self.stats_label = tk.Label(self.root, text="正确: 0   错误: 0", font=("Arial", 11))
        self.stats_label.pack(pady=5)

        # 说明信息
        self.info_label = tk.Label(self.root, text="", font=("Arial", 9), fg="gray", wraplength=680)
        self.info_label.pack(side=tk.BOTTOM, pady=10)

        # 统计计数
        self.correct_count = 0
        self.wrong_count = 0

        # 初始化序列长度frame可见性
        self._update_len_frame_visibility()

    def _update_len_frame_visibility(self):
        if self.mode_var.get() == "single":
            self.len_frame.pack_forget()
        else:
            # pack在控制栏的合适位置，这里简单重新pack
            self.len_frame.pack(side=tk.LEFT, padx=10, before=self.time_slider.master)
            # 上面的 before 需要小心，简单处理：先取消隐藏再重新
            # 不用太精确，只要在界面上即可
            try:
                self.len_frame.pack(side=tk.LEFT, padx=10)
            except:
                pass

    def _on_setting_changed(self):
        """任何设置改变（模式、显示、输入、序列长度滑块）时，如果已开始，则停止并重置为未开始状态"""
        if self.is_started:
            self._stop_practice()
            self._set_started_state(False)
            self.feedback_label.config(text="设置已更改，请重新点击“开始练习”", fg="orange")
            self.root.after(2000, lambda: self.feedback_label.config(text=""))
        # 更新界面
        self._update_len_frame_visibility()
        self._update_info()

    def _on_seq_len_changed(self):
        self._on_setting_changed()

    def _on_time_changed(self, val):
        # 时间改变时如果已经开始，需要更新当前quiz的time_limit
        if self.is_started and self.quiz:
            self.quiz.update_time_limit(self.time_limit.get())
        # 同时更新信息
        self._update_info()

    def _start_practice(self):
        if self.is_started:
            return
        # 根据当前设置创建quiz对象
        if self.quiz:
            self.quiz.stop()
            self.quiz = None
        mode = self.mode_var.get()
        disp = self.display_type.get()
        inp = self.input_type.get()
        time_lim = self.time_limit.get()
        if mode == "single":
            self.quiz = SingleQuiz(disp, inp, time_lim,
                                   self._on_result, self._on_new_question)
        else:
            length = self.seq_length.get()
            self.quiz = SequenceQuiz(disp, inp, length, time_lim,
                                     self._on_result, self._on_new_question)
        self.quiz.set_root(self.root)
        self.quiz.set_on_timer_update(self._on_timer_update)
        # 开始
        self.quiz.start()
        self.is_started = True
        self._set_started_state(True)
        self.feedback_label.config(text="练习已开始！", fg="blue")
        self.root.after(1500, lambda: self.feedback_label.config(text=""))

    def _stop_practice(self):
        """停止当前练习（清空计时器）"""
        if self.quiz:
            self.quiz.stop()
            self.quiz = None
        self.is_started = False

    def _set_started_state(self, started):
        """根据是否开始，启用/禁用控件"""
        state_normal = tk.NORMAL if started else tk.DISABLED
        self.entry.config(state=state_normal)
        # 开始按钮文字变更
        if started:
            self.start_btn.config(text="练习中...", state=tk.DISABLED)
        else:
            self.start_btn.config(text="开始练习", state=tk.NORMAL)
        # 如果未开始，清空题目显示和计时
        if not started:
            self.question_label.config(text="")
            self.timer_label.config(text="")
            self.entry.delete(0, tk.END)

    def _on_result(self, is_correct, message):
        if is_correct:
            self.correct_count += 1
            color = "green"
        else:
            self.wrong_count += 1
            color = "red"
        self._update_stats()
        self.feedback_label.config(text=message, fg=color)
        self.root.after(2000, lambda: self.feedback_label.config(text=""))

    def _on_new_question(self, display_text):
        self.question_label.config(text=display_text)
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

    def _on_timer_update(self, time_left):
        self.timer_label.config(text=f"剩余时间: {time_left:.1f} 秒")

    def _on_submit(self, event=None):
        if not self.is_started or self.quiz is None:
            self.feedback_label.config(text="请先点击“开始练习”", fg="orange")
            self.root.after(1500, lambda: self.feedback_label.config(text=""))
            return
        user_input = self.entry.get().strip()
        if not user_input:
            self.feedback_label.config(text="请输入答案", fg="orange")
            self.root.after(1000, lambda: self.feedback_label.config(text=""))
            return
        self.quiz.submit_answer(user_input)

    def _update_stats(self):
        self.stats_label.config(text=f"正确: {self.correct_count}   错误: {self.wrong_count}")

    def _reset_stats(self):
        self.correct_count = 0
        self.wrong_count = 0
        self._update_stats()
        self.feedback_label.config(text="统计已重置", fg="blue")
        self.root.after(1500, lambda: self.feedback_label.config(text=""))

    def _update_info(self):
        mode = self.mode_var.get()
        disp = self.display_type.get()
        inp = self.input_type.get()
        if mode == "single":
            info = f"单题模式：显示为 {disp}，你需要输入 {inp}。每个题目限时 {self.time_limit.get()} 秒。"
        else:
            info = f"序列模式：显示 {self.seq_length.get()} 个 {disp}，你需要输入对应的 {inp}，空格分隔。每个序列限时 {self.time_limit.get()} 秒。"
        self.info_label.config(text=info)