import tkinter as tk
from tkinter import messagebox
import requests
import time
import hashlib
import json

class CompanyInfoConfig:
    DEFAULT_APP_KEY = "8da7ffbb70cb4cc79c3a8a6a3f130677"
    DEFAULT_SECRET_KEY = "68B4DFFE02DA2125A1CD5E57C754621C"
    DEFAULT_COMPANY_NAME = "东海资本管理有限公司"

class CompanyInfoAPI:
    def __init__(self):
        self.encode = 'utf-8'
        self.api_configs = {
            '410': {
                'base_url': 'https://api.qichacha.com/ECIV4/GetBasicDetailsByName',
                'param_format': lambda k: f'keyword={k}',
                'headers': lambda t, ts: {'Token': t, 'Timespan': ts}
            }
        }

    def _generate_token(self, app_key, secret_key):
        timespan = str(int(time.time()))
        token = app_key + timespan + secret_key
        hl = hashlib.md5()
        hl.update(token.encode(encoding=self.encode))
        return hl.hexdigest().upper(), timespan

    def fetch_company_info(self, keyword, app_key, secret_key):
        token, timespan = self._generate_token(app_key, secret_key)
        combined_result = {}
        
        for api_name, api_config in self.api_configs.items():
            try:
                paramStr = api_config['param_format'](keyword)
                url = f"{api_config['base_url']}?key={app_key}&{paramStr}"
                headers = api_config['headers'](token, timespan)
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                content = response.content.decode(self.encode)
                if not content.strip():
                    raise ValueError("Empty response received")
                    
                result = json.loads(content)
                result['ApiSource'] = api_name
                combined_result[api_name] = result
                
            except requests.exceptions.RequestException as e:
                combined_result[api_name] = {"Status": "Error", "Message": f"请求错误: {str(e)}"}
            except json.JSONDecodeError as e:
                combined_result[api_name] = {"Status": "Error", "Message": f"JSON解析错误: {str(e)}\n响应内容: {content}"}
            except Exception as e:
                combined_result[api_name] = {"Status": "Error", "Message": f"其他错误: {str(e)}"}
        
        return combined_result

class CompanyInfoGUI:
    def __init__(self):
        self.api = CompanyInfoAPI()
        self.setup_gui()

    def save_to_json(self, data, filename="result.json"):
        formatted_data = {}
        for api_name, api_result in data.items():
            if isinstance(api_result, dict) and "Message" in api_result and "JSON解析错误" in api_result["Message"]:
                content_start = api_result["Message"].find('响应内容: ') + 6
                if content_start > 6:
                    try:
                        raw_content = api_result["Message"][content_start:]
                        parsed_content = json.loads(raw_content)
                        formatted_data[api_name] = parsed_content
                    except json.JSONDecodeError:
                        formatted_data[api_name] = api_result
            else:
                formatted_data[api_name] = api_result

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)

    def search_company(self):
        company_name = self.company_entry.get()
        credit_code = self.credit_code_entry.get()
        app_key = self.app_key_entry.get()
        secret_key = self.secret_key_entry.get()
        
        if not company_name and not credit_code:
            messagebox.showerror("错误", "请输入企业名称或统一社会信用代码")
            return
        
        try:
            keyword = company_name or credit_code
            results = self.api.fetch_company_info(keyword, app_key, secret_key)
            
            if results:
                self.result_text.delete(1.0, tk.END)
                for api_name, result in results.items():
                    self.result_text.insert(tk.END, f"\n=== {api_name} API 结果 ===\n")
                    self.result_text.insert(tk.END, json.dumps(result, ensure_ascii=False, indent=2))
                    self.result_text.insert(tk.END, "\n")
                
                self.save_to_json(results)
                messagebox.showinfo("提示", "查询结果已保存到result.json文件")
            else:
                messagebox.showinfo("提示", "未获取到查询结果")
        except Exception as e:
            messagebox.showerror("错误", f"查询过程中出现错误：{str(e)}")

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("企业信息查询")

        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 输入区域
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="请输入企业名称:").pack(pady=5)
        self.company_entry = tk.Entry(input_frame, width=50)
        self.company_entry.insert(0, CompanyInfoConfig.DEFAULT_COMPANY_NAME)
        self.company_entry.pack(pady=5)

        tk.Label(input_frame, text="请输入统一社会信用代码:").pack(pady=5)
        self.credit_code_entry = tk.Entry(input_frame, width=50)
        self.credit_code_entry.pack(pady=5)

        tk.Label(input_frame, text="请输入AppKey:").pack(pady=5)
        self.app_key_entry = tk.Entry(input_frame, width=50)
        self.app_key_entry.insert(0, CompanyInfoConfig.DEFAULT_APP_KEY)
        self.app_key_entry.pack(pady=5)

        tk.Label(input_frame, text="请输入SecretKey:").pack(pady=5)
        self.secret_key_entry = tk.Entry(input_frame, width=50)
        self.secret_key_entry.insert(0, CompanyInfoConfig.DEFAULT_SECRET_KEY)
        self.secret_key_entry.pack(pady=5)

        # 按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="查询", command=self.search_company).pack(side=tk.LEFT, padx=5)

        # 结果显示区域
        result_frame = tk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, height=20, width=80)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CompanyInfoGUI()
    app.run()