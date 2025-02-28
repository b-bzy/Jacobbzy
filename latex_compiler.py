import subprocess
import os
import json

def replace_placeholders(latex_content, replacements):
    for key, value in replacements.items():
        latex_content = latex_content.replace(f"{{{key}}}", str(value))
    return latex_content

def latex_to_pdf(latex_content, output_file):
    # 使用 UTF-8 编码写入临时文件
    with open('temp.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    # 使用 xelatex 替代 pdflatex，添加 -interaction=nonstopmode 参数
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'temp.tex'])
    
    if os.path.exists(output_file):
        os.remove(output_file)
    os.rename('temp.pdf', output_file)
    print(f"Successfully converted LaTeX to PDF: {output_file}")

def read_json_parameters(json_file_path, param_mapping):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    replacements = {}
    # 检查并获取第一个 API 结果中的 Result 数据
    first_api_result = next(iter(data.values()))
    if 'Result' in first_api_result:
        result_data = first_api_result['Result']
        for latex_param, json_key in param_mapping.items():
            if json_key in result_data:
                replacements[latex_param] = result_data[json_key]
    
    return replacements

def cleanup_temp_files():
    temp_files = ['temp.tex', 'temp.log', 'temp.aux']
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
    print("Temporary files cleaned up.")

if __name__ == '__main__':
    # 使用 UTF-8 编码读取 LaTeX 文件
    with open('table1.tex', 'r', encoding='utf-8') as f:
        latex_content = f.read()

    json_file_path = r'D:\桌面\deepseek赋能期货行业\task_1\result.json'
    
    param_mapping = {
        'param1': 'Name',
        'param2': 'RegistCapi',
        'param3': 'RegisteredCapitalCCY',
        'param4': 'EconKind',
        'param5': 'No'
    }

    replacements = read_json_parameters(json_file_path, param_mapping)    
    updated_content = replace_placeholders(latex_content, replacements)

    pdf_file = 'output.pdf'
    latex_to_pdf(updated_content, pdf_file)
    cleanup_temp_files()