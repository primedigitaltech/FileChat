# 文件对话demo

调用智谱AI文件对话接口进行问答

## 代码结构
```
.
├── LICENSE
├── README.md
├── environment.yml
└── file_chat.py
```

## 环境配置

* Python虚拟环境，建议使用命令行安装[Miniconda](https://docs.anaconda.com/miniconda/#quick-command-line-install)

* 创建虚拟环境
    ```
    conda env create -f environment.yml --name <虚拟环境名称>
    ```

## 启动

* 激活虚拟环境
    ```
    conda activate <虚拟环境名称>
    ```

* 启动文件对话用户界面
    ```
    streamlit run file_chat.py
    ```