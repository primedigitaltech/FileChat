import os
import json
import re
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

# 使用ZhipuAI API生成需要的信息
def process_file(api_key, file_path, message, question_types):
    # 初始化ZhipuAI客户端
    client = ZhipuAI(api_key=api_key)
    try:
        with open(file_path, 'rb') as uploaded_file:
            file_object = client.files.create(file=uploaded_file, purpose="file-extract")
            file_content = json.loads(client.files.content(file_id=file_object.id).content)["content"]
            client.files.delete(file_id=file_object.id)
            # 存储每个message的结果
            results = {}
            # 使用统一的message模板
            message_content = message.format(file_content=file_content)
            response = client.chat.completions.create(
                model="glm-4-long",
                temperature=0.0,
                messages=[{"role": "user", "content": message_content}],
                max_tokens=4095  # 限制最大生成长度
            )

            # 获取的初始回答
            answer = response.choices[0].message.content.strip()

            answer_sections = answer.split("\n\n")  # 以双换行分段

            # 将每个问题的答案对应存储到results字典中
            for i, question in enumerate(question_types[1:]):  # 跳过"文件名"这一列
                if i < len(answer_sections):

                    # 去掉所有*号，清理标记
                    cleaned_answer = answer_sections[i].replace("*", "")
                    # 去掉类似 "第x个问题:" 或 "第x个问题：" 的标记，x是中文数字
                    cleaned_answer = re.sub(r"\s*第\s*(?:[一二三四五六七八九]+(?:十[一二三四五六七八九]*)?|[二三四五六七八九十百]+)\s*个\s*问题\s*[:：]", "", cleaned_answer)
                    # 去掉类似 **动机**：的**标记
                    cleaned_answer = re.sub(r"\*\*[^*]+\*\*：", "", cleaned_answer)  
                    # 去除每一行最前面的空格
                    cleaned_answer = "\n".join(line.lstrip() for line in cleaned_answer.splitlines())

                    results[question] = cleaned_answer.strip()  # 提取每个问题的答案
                    
                else:
                    results[question] = "未找到对应答案"  # 如果没有足够的段落，填充默认值

            return results
    except Exception as e:
        print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        return {}


def main(api_key, file_path_or_folder, output_excel,output_question):
    print("===========================开始处理文件===========================")

    directory = os.path.dirname(output_question)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"目录 {directory} 已创建")

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

    # 检查或创建 Excel 文件
    if not os.path.exists(output_excel):
        # 如果文件不存在，则创建并写入标题行
        pd.DataFrame(columns=question_types).to_excel(output_excel, index=False)

    # 获取绝对路径
    file_path_or_folder = os.path.abspath(file_path_or_folder)
    output_question = os.path.abspath(output_question)

    message = """
        你是人工智能领域的专家，以下内容是一篇论文：\n\n{file_content}\n\n请以这篇论文的内容为依据和回答的背景知识，逐条回复以下问题。请确保每个问题的回答独立分段，每个问题之间不留空行，并按顺序提供。
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
    
    # 用于生成综述所需的论文信息
    summary_question=""

    # 处理单个文件
    if os.path.isfile(file_path_or_folder):
        if file_path_or_folder.lower().endswith(".pdf"):  # 确保只处理PDF文件
            
            file_path = file_path_or_folder
            print(f"正在处理文件: {os.path.basename(file_path)}")
            try:
                analysis_results = process_file(api_key, file_path, message,question_types)
                if analysis_results:
                    result = {"文件名": os.path.basename(file_path)}
                    result.update(analysis_results)  # 将每个问题的分析结果加入字典
                    append_to_excel([result], output_excel, question_types)
            except Exception as e:
                print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        else:
            print(f"文件 {os.path.basename(file_path_or_folder)} 不是PDF文件，跳过处理")
        summary_question = "只有一个文件，无法进行比较"  # 用于生成综述
        # 将结果保存到txt文件
        with open(output_question, 'w', encoding='utf-8') as file:
            file.write(message)
        print(f"结果已保存到 {output_question}")
        return summary_question

    # 处理文件夹
    elif os.path.isdir(file_path_or_folder):
        # 遍历源文件夹中的所有文件
        for root, dirs, files in os.walk(file_path_or_folder):
            for i, filename in enumerate(files):
                if filename.lower().endswith(".pdf"):  # 确保只处理PDF文件
                    file_path = os.path.join(root, filename)
                    print(f"正在处理文件: {filename}")
                    try:
                        analysis_results = process_file(api_key, file_path, message,question_types)
                        if analysis_results:
                            summary_question+=f"第{i+1}篇论文：{analysis_results}\n\n" # 用于生成综述
                            result = {"文件名": filename}
                            result.update(analysis_results)  # 将每个问题的分析结果加入字典
                            append_to_excel([result], output_excel, question_types)
                    except Exception as e:
                        print(f"处理文件 {filename} 时出错: {e}")
                else:
                    print(f"文件 {os.path.basename(file_path_or_folder)} 不是PDF文件，跳过处理")
        # 将结果保存到txt文件
        with open(output_question, 'w', encoding='utf-8') as file:
            file.write(message)
        print(f"结果已保存到 {output_question}")

    print("===========================处理完成===========================")
    return summary_question
    
if __name__ == "__main__":
    
    # API Key, 待解析文件路径, 输出结果文件路径（excel）,输出问题路径（txt）
    main("replace your own api key", 
         "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文", 
         "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文/test.xlsx",
         "/Users/lee/Desktop/documents/华师/teaching/人工智能通识课-大模型/论文/test.txt")
