import subprocess
import os
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import queue
import sys

class ExecutionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("企业信息查询与报告生成系统")
        self.output_queue = queue.Queue()
        self.setup_gui()
        self.check_output_queue()

    def setup_gui(self):
        self.root.geometry("800x600")
        
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # 上半部分：标题和按钮
        upper_frame = tk.Frame(main_frame)
        upper_frame.pack(fill='x', pady=(0, 10))

        tk.Label(upper_frame, text="企业信息查询与报告生成系统", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(upper_frame, text="点击下方按钮开始执行流程：", 
                font=('Arial', 10)).pack(pady=5)
        
        tk.Button(upper_frame, text="开始执行", command=self.run_process,
                 font=('Arial', 12), width=20, height=2).pack(pady=10)
        
        self.status_label = tk.Label(upper_frame, text="等待执行...", 
                                   font=('Arial', 10))
        self.status_label.pack(pady=5)

        # 下半部分：终端输出
        terminal_frame = tk.Frame(main_frame)
        terminal_frame.pack(fill='both', expand=True)

        tk.Label(terminal_frame, text="执行日志：", 
                font=('Arial', 10, 'bold')).pack(anchor='w')

        self.terminal = scrolledtext.ScrolledText(terminal_frame, height=15,
                                                bg='black', fg='white',
                                                font=('Consolas', 10))
        self.terminal.pack(fill='both', expand=True)

    def run_process(self):
        self.terminal.delete(1.0, tk.END)
        threading.Thread(target=self._run_process_thread, daemon=True).start()

    def _run_process_thread(self):
        try:
            self.status_label.config(text="正在执行企业信息查询...")
            self.update_terminal("开始执行企业信息查询...\n")

            # 执行第一个脚本
            process = subprocess.Popen(
                ['python', 'd:/桌面/deepseek赋能期货行业/task_1/api_download.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 指定编码为 UTF-8
                errors='replace'    # 处理无法解码的字符
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.output_queue.put(output.strip())

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args)

            self.output_queue.put("\n等待文件保存...\n")
            time.sleep(2)
            
            self.status_label.config(text="正在生成报告...")
            self.output_queue.put("开始生成报告...\n")

           
            # 执行第二个脚本
            process = subprocess.Popen(
                ['python', 'd:/桌面/deepseek赋能期货行业/task_1/latex_compiler.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 指定编码为 UTF-8
                errors='replace'    # 处理无法解码的字符
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.output_queue.put(output.strip())

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args)
            
            self.status_label.config(text="执行完成！")
            self.output_queue.put("\n执行完成！\n")
            messagebox.showinfo("成功", "流程执行完成！\n1. 企业信息已保存到 result.json\n2. 报告已生成为 output.pdf 和 output.docx")

        except subprocess.CalledProcessError as e:
            self.status_label.config(text="执行出错！")
            self.output_queue.put(f"\n执行错误：{str(e)}\n")
            messagebox.showerror("错误", f"执行过程中出现错误：\n{str(e)}")
        except Exception as e:
            self.status_label.config(text="执行出错！")
            self.output_queue.put(f"\n未知错误：{str(e)}\n")
            messagebox.showerror("错误", f"发生未知错误：\n{str(e)}")

    def update_terminal(self, text):
        self.terminal.insert(tk.END, text + '\n')
        self.terminal.see(tk.END)

    def check_output_queue(self):
        while True:
            try:
                output = self.output_queue.get_nowait()
                self.update_terminal(output)
            except queue.Empty:
                break
        self.root.after(100, self.check_output_queue)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExecutionGUI()
    app.run()