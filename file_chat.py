import os
import json
import streamlit as st
from zhipuai import ZhipuAI


def main():
    st.set_page_config(page_title="文件对话demo", page_icon="📖", layout="wide")  # 页面设置
    st.header("📖文件对话demo")  # 标题
    
    with st.sidebar:  # 侧边栏
        st.markdown("调用智谱AI文件对话接口进行问答")
        api_key_input = st.text_input(
            "智谱API Key",
            type="password",
            value=os.environ.get("API_KEY", None)
            or st.session_state.get("API_KEY", ""),
            key="API_KEY",
        )

    api_key = st.session_state.get("API_KEY")
    if not api_key:
        st.warning(
            "请在侧边栏输入API_KEY。可从"
            " https://bigmodel.cn/usercenter/apikeys 获取"
        )
    client = ZhipuAI(api_key=api_key)
    uploaded_file = st.file_uploader(
        "上传文件",
        type=["pdf", "docx", "txt"],
        help="文件大小不超过50M，图片大小不超过5M",
        on_change=lambda: st.session_state.pop("messages", None),
    )

    if not uploaded_file:
        st.stop()
    else:
        if "messages" not in st.session_state:
            file_object = client.files.create(file=uploaded_file, purpose="file-extract")
            file_content = json.loads(client.files.content(file_id=file_object.id).content)["content"]
            client.files.delete(file_id=file_object.id)
            message_content = f"请对\n{file_content}\n的内容进行分析，并撰写一份论文摘要。"
            response = client.chat.completions.create(
                model="glm-4-long",
                messages=[
                    {"role": "user", "content": message_content}
                ],
            )
            msg = response.choices[0].message.content
            st.session_state["messages"] = [{"role": "assistant", "content": msg}]  # 每次提问时不带上全文信息
            # st.session_state["messages"] = [{"role": "user", "content": message_content}, {"role": "assistant", "content": msg}]  # 每次提问时带上全文信息

        for msg in st.session_state.get("messages", []):
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            response = client.chat.completions.create(model="glm-4-long", messages=st.session_state.messages)
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)


if __name__ == "__main__":
    main()
