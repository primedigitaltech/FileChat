# 文件对话demo

调用智谱AI文件对话接口进行问答

## 代码结构
```
.
├── LICENSE (Git仓库的开源许可证)
├── README.md (本文档)
├── environment.yml (Conda使用的环境需求文件)
├── file_chat.py (文件对话Streamlit页面)
└── requirements.txt (Pip使用的环境需求文件)
```

## 环境配置-Conda版本

* 安装Conda：建议使用命令行安装 [Miniconda](https://docs.anaconda.com/miniconda/#quick-command-line-install)

* 创建虚拟环境
    ```
    conda env create -f environment.yml --name <虚拟环境名称>
    ```

## 环境配置-Venv版本

* 安装Python：版本>=3.10, 参考各操作系统对应网上教程

* 创建虚拟环境
    ```
    python3 -m venv venv
    ```

## 启动

* 激活虚拟环境
    * Conda
        ```
        conda activate <虚拟环境名称>
        ```
    * Venv
        ```
        source venv/bin/activate
        ```

* 启动文件对话用户界面
    ```
    streamlit run file_chat.py
    ```

## 一些相关开发技术文档链接

* Streamlit： https://docs.streamlit.io/
* 智谱文件问答API：https://bigmodel.cn/dev/howuse/fileqa
* 智谱RAG问答API：https://bigmodel.cn/dev/howuse/retrieval