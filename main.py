# main.py
import tkinter as tk
from gui import MusicTrainerApp

def main():
    # 创建主窗口
    root = tk.Tk()
    
    # 实例化应用
    app = MusicTrainerApp(root)
    
    # 开启事件循环
    root.mainloop()

if __name__ == "__main__":
    main()