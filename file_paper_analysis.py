import os
import json
import pandas as pd  # 用于将结果保存到Excel
from zhipuai import ZhipuAI  # 假设你已经安装并配置好ZhipuAI

# 定义保存结果到Excel的函数
def append_to_excel(results, output_file, column_names):
    df = pd.DataFrame(results, columns=column_names)
    if os.path.exists(output_file):
        # 如果文件已存在，则追加数据
        existing_df = pd.read_excel(output_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel(output_file, index=False)
    print(f"结果已保存到 {output_file}")

def process_file(api_key, file_path, messages,question_types):
    # 初始化ZhipuAI客户端
    client = ZhipuAI(api_key=api_key)
    try:
        with open(file_path, 'rb') as uploaded_file:
            file_object = client.files.create(file=uploaded_file, purpose="file-extract")
            file_content = json.loads(client.files.content(file_id=file_object.id).content)["content"]
            client.files.delete(file_id=file_object.id)

            # 存储每个message的结果
            results = {}
            for i, message_template in enumerate(messages):
                message_content = message_template.format(file_content=file_content)
                response = client.chat.completions.create(
                    model="glm-4-long",
                    temperature=0.0,
                    messages=[{"role": "user", "content": message_content}],
                )
                answer = response.choices[0].message.content.strip()
                question = question_types[i+1] 
                results[question] = answer  # 将答案存储到results字典中
            return results  # 返回每个分析结果
    except Exception as e:
        print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        return {}

def main(api_key, file_path_or_folder, output_excel):
    print("===========================开始处理文件===========================")

   
    # 获取绝对路径
    file_path_or_folder = os.path.abspath(file_path_or_folder)
    output_excel = os.path.abspath(output_excel)

    # 定义每个问题的类型，作为Excel中的列标题
    question_types = [
        "文件名",
        "撰写摘要",
        "摘要",
        "作者",
        "会议/期刊",
        "主要解决的问题",
        "提出的方法",
        "所使用数据集",
        "评估方法的指标",
        "实验的表现",
        "论文所做的工作",
    ]
    
    # 对应的 message_content，分析每篇论文
    messages = [
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析，并撰写一份论文摘要。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,提取论文的摘要原文,摘要在Abstract之后,Introduction之前。",
        "请对\n{file_content}\n的内容进行分析,告诉我全部作者是谁，按以下格式列出：\n```\n作者1, 作者2, 作者3\n```。",
        "请对\n{file_content}\n的内容进行分析,告诉我这篇论文发表在哪个会议/期刊,不需要推理过程,直接回答。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,只告诉我主要解决的问题有哪些,其他内容不需要。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,只告诉我提出的方法有哪些,其他内容不需要。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,只告诉我所使用数据集有哪些,其他内容不需要。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,只告诉我评估方法的指标有哪些,其他内容不需要。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,只告诉我实验的表现,其他内容不需要。",
        "你是人工智能领域的专家，请对\n{file_content}\n的内容进行分析,总结论文所做的工作，包括动机、贡献点等,其他内容不需要。",
    ]

    # 检查或创建 Excel 文件
    if not os.path.exists(output_excel):
        # 如果文件不存在，则创建并写入标题行
        pd.DataFrame(columns=question_types).to_excel(output_excel, index=False)
    if os.path.isfile(file_path_or_folder):
        if file_path_or_folder.lower().endswith(".pdf"):  # 确保只处理PDF文件
            # 处理单个文件
            file_path = file_path_or_folder
            print(f"正在处理文件: {os.path.basename(file_path)}")
            try:
                analysis_results = process_file(api_key, file_path, messages,question_types)
                if analysis_results:
                    result = {"文件名": os.path.basename(file_path)}
                    result.update(analysis_results)  # 将每个问题的分析结果加入字典
                    append_to_excel([result], output_excel, question_types)
            except Exception as e:
                print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        else:
            print(f"文件 {os.path.basename(file_path_or_folder)} 不是PDF文件，跳过处理")
    elif os.path.isdir(file_path_or_folder):
        # 遍历源文件夹中的所有文件
        for root, dirs, files in os.walk(file_path_or_folder):
            for filename in files:
                if filename.lower().endswith(".pdf"):  # 确保只处理PDF文件
                    file_path = os.path.join(root, filename)
                    print(f"正在处理文件: {filename}")
                    try:
                        analysis_results = process_file(api_key, file_path, messages,question_types)
                        if analysis_results:
                            result = {"文件名": filename}
                            result.update(analysis_results)  # 将每个问题的分析结果加入字典
                            append_to_excel([result], output_excel, question_types)
                    except Exception as e:
                        print(f"处理文件 {filename} 时出错: {e}")
                else:
                    print(f"文件 {os.path.basename(file_path_or_folder)} 不是PDF文件，跳过处理")
    print("===========================处理完成===========================")

if __name__ == "__main__":
    # API Key, 待解析文件路径, 输出文件路径
    main("API Key", "待解析文件路径", "输出文件路径")
