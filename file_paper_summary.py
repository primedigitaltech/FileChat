import os
from zhipuai import ZhipuAI  # 假设你已经安装并配置好ZhipuAI
import argparse
# import dotenv

import file_paper_analysis_improve

# 使用ZhipuAI API生成综述
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

    
def main(api_key, file_path_or_folder,output_analysis_excel,output_analysis_question,output_summary_question,output_summary_result):
    print("===========================开始处理综述部分===========================")

    directory = os.path.dirname(output_summary_question)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"目录 {directory} 已创建")
        
    directory = os.path.dirname(output_summary_result)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"目录 {directory} 已创建")


    # 获取绝对路径
    file_path_or_folder = os.path.abspath(file_path_or_folder)
    output_summary_question = os.path.abspath(output_summary_question)
    output_summary_result = os.path.abspath(output_summary_result)

    summary_question = "你是人工智能领域的专家,以下是对多篇论文的信息提取与内容总结：\n\n" # 用于生成综述

    # 多篇文献的信息分析结果
    analysis_result = file_paper_analysis_improve.main(api_key, file_path_or_folder, output_analysis_excel, output_analysis_question)
    if analysis_result == "只有一个文件，无法进行比较":
        print("注意：只有一个文件，无法进行比较，你应该上次包含多篇论文的文件夹而不是文件")
        return
    summary_question += analysis_result
    
    summary_question+="请你根据以上不同论文及其内容，对这些论文生成一个综述，比较每篇论文提出方法的优劣，包括采用相同指标相同数据集所进行的实验结果的比较，讨论各方法的实际表现；最后，总结每篇论文的研究动机和贡献点，比较各论文在创新和实用性方面的不同之处，概括下这些研究在该领域中的地位和影响。"
    # 生成综述
    summary_result = generate_summary_from_files(api_key,summary_question)
     # 将问题保存到txt文件

    with open(output_summary_question, 'w', encoding='utf-8') as file:
        file.write(summary_question)
    print(f"生成综述的问题已保存到 {output_summary_question}")

     # 将结果保存到txt文件
    with open(output_summary_result, 'w', encoding='utf-8') as file:
        file.write(summary_result)
    print(f"生成的综述结果已保存到 {output_summary_result}")

    print("===========================综述部分处理完成===========================")

if __name__ == "__main__":
    
    # API Key, 待解析文件路径, 输出结果文件路径（excel）,输出问题路径（txt）,输出综述问题路径（txt）,输出综述结果路径（txt）
    main("f3489a829804ad775c645151fa17495a.AzE83g1jBq4PqSyY", "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文", 
        "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文/test.xlsx",
        "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文/test.txt",
        "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文/question-summary.txt",
        "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文/summary.txt")

