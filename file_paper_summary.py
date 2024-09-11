import os
import json
import time
import pandas as pd  # 用于将结果保存到Excel
from zhipuai import ZhipuAI  # 假设你已经安装并配置好ZhipuAI

def process_file(api_key, file_path, messages):
    # 初始化ZhipuAI客户端
    client = ZhipuAI(api_key=api_key)
   
    try:
        with open(file_path, 'rb') as uploaded_file:
            file_object = client.files.create(file=uploaded_file, purpose="file-extract")
            file_content = json.loads(client.files.content(file_id=file_object.id).content)["content"]
            client.files.delete(file_id=file_object.id)
            for i, message_template in enumerate(messages):
                message_content = message_template.format(file_content=file_content)
                response = client.chat.completions.create(
                    model="glm-4-long",
                    temperature=0.0,
                    messages=[{"role": "user", "content": message_content}],
                    max_tokens=4095 # 限制最大生成长度
                )
                answer = response.choices[0].message.content
            # print(answer)
            return answer  # 返回每个分析结果
    except Exception as e:
        print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        return {}

def generate_summary_from_files(api_key, file_content):
    client = ZhipuAI(api_key=api_key)
    try:
        message_content = file_content
        response = client.chat.completions.create(
            model="glm-4-long",
            temperature=0.0,
            messages=[{"role": "user", "content": message_content}],
            max_tokens=4095
        )
        summary = response.choices[0].message.content
        return summary  # 返回综述结果
    except Exception as e:
        print(f"文件比较出错时出错: {e}")
        return {}
def main(api_key, file_path_or_folder):
    print("===========================开始处理文件===========================")

    # 获取绝对路径
    file_path_or_folder = os.path.abspath(file_path_or_folder)

    # 对应的 message_content，分析每篇论文
    messages = [
        """
        你是人工智能领域的专家，以下内容是一篇论文：\n\n{file_content}\n\n请以这篇论文的内容为依据和回答的背景知识，逐条回复以下问题。请确保每个问题的回答独立分段，并按顺序提供。
        **第一个问题**：请对论文的内容进行摘要总结，包含研究背景与问题、研究目的、方法、主要结果和结论，字数要求在150-300字之间，使用论文中的术语和概念。
        **第二个问题**：请提取论文的摘要原文，摘要一般在Abstract之后，Introduction之前。
        **第三个问题**：请列出论文的全部作者，按照以下格式：\n```\n作者1, 作者2, 作者3\n```。
        **第四个问题**：请直接告诉我这篇论文发表在哪个会议或期刊，请不要推理或提供额外信息。
        **第五个问题**：请详细描述这篇论文主要解决的核心问题，并用简洁的语言概述。
        **第六个问题**：请告诉我这篇论文提出了哪些方法，请用最简洁的方式概括每个方法的核心思路。
        **第七个问题**：请告诉我这篇论文所使用的数据集，包括数据集的名称和来源。
        **第八个问题**：请列举这篇论文评估方法的所有指标，并简要说明这些指标的作用。
        **第九个问题**：请总结这篇论文实验的表现，包含具体的数值表现和实验结论。
        **第十个问题**：请清晰地描述论文所作的工作，分别列举出动机和贡献点以及主要创新之处。
        """
    ]

    summary_question = "你是人工智能领域的专家,以下是对多篇论文的信息提取与内容总结：" # 用于生成综述
    # 遍历源文件夹中的所有文件
    for root, dirs, files in os.walk(file_path_or_folder):
        for i, filename in enumerate(files):
            if filename.lower().endswith(".pdf"):  # 确保只处理PDF文件
                file_path = os.path.join(root, filename)
                print(f"正在处理文件: {filename}")
                try:
                    analysis_results = process_file(api_key, file_path, messages)
                    if analysis_results:
                        summary_question+=f"第{i+1}篇论文：{analysis_results}\n\n"
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {e}")
            else:
                print(f"文件 {os.path.basename(file_path_or_folder)} 不是PDF文件，跳过处理")

        summary_question+="请你根据以上不同论文及其内容，对这些论文生成一个综述，比较每篇论文提出方法的优劣，包括采用相同指标相同数据集所进行的实验结果的比较，讨论各方法的实际表现；最后，总结每篇论文的研究动机和贡献点，比较各论文在创新和实用性方面的不同之处，概括下这些研究在该领域中的地位和影响。"
        # 生成综述
        summary_result = generate_summary_from_files(api_key,summary_question)
        # print(summary_result)
    print("===========================处理完成===========================")

if __name__ == "__main__":
    main("API Key", "待解析文件路径")
