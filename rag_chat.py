import os
import time
import json
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from zhipuai import ZhipuAI
from zhipuai.types.knowledge import KnowledgeInfo


def init_client() -> ZhipuAI:
    api_key = st.session_state.get("API_KEY")
    if not api_key:
        st.warning(
            "请在侧边栏输入API_KEY。可从"
            " https://bigmodel.cn/usercenter/apikeys 获取"
        )
        st.stop()
    return ZhipuAI(api_key=api_key)


def config_sidebar() -> None:
    with st.sidebar:
        st.markdown("调用智谱AI知识库对话接口进行问答")
        st.text_input(
            "智谱API Key",
            type="password",
            value=os.environ.get("API_KEY", None)
            or st.session_state.get("API_KEY", ""),
            key="API_KEY",
        )
        st.button(
            "清空对话",
            use_container_width=True,
            on_click=lambda: st.session_state.pop("messages", None)
        )


def config_kb(client: ZhipuAI) -> KnowledgeInfo:
    kb_usage = client.knowledge.used()
    existing_kb = client.knowledge.query(page=1, size=10)
    st.code(f"现有{existing_kb.total}个知识库，已使用{kb_usage.used.word_num}字，共{kb_usage.total.word_num}字")  # 使用量
    
    selected_kb_index = st.session_state.get("selected_kb_index", 0)
    with st.expander("知识库信息", expanded=True):
        selected_kb = st.selectbox(
            "请选择或新建知识库",
            existing_kb.list+["新建知识库"],
            format_func=lambda x: x.name if not isinstance(x, str) else x,
            index=selected_kb_index
        )
        if selected_kb == "新建知识库":
            create_kb(client)
            st.stop()

        uploaded_files = st.file_uploader(
            f"上传文件至知识库{selected_kb.name}",
            accept_multiple_files=True,
            type=["pdf", "doc", "docx", "xlsx"],
            help="文件大小不超过50M",
        )

        kb_files = client.knowledge.document.list(purpose="retrieval", knowledge_id=selected_kb.id)
        st.write("知识库文件列表")
        st.write(pd.DataFrame([file.to_dict() for file in kb_files.list]), unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            upload_btn = st.button("上传文件", use_container_width=True)
        with cols[1]:
            delete_kb = st.button("删除知识库", use_container_width=True)

        if delete_kb:
            drop_kb(client, selected_kb)
        
        if upload_btn:
            if not uploaded_files:
                st.warning("请先上传文件")
                st.stop()
            else:
                for uploaded_file in uploaded_files:
                    client.files.create(file=uploaded_file, purpose="retrieval", knowledge_id=selected_kb.id)
                st.success(f"上传文件成功")
                st.rerun()
    return selected_kb


def chat_with_kb(client: ZhipuAI, kb: KnowledgeInfo) -> None:
    st.session_state["messages"] = st.session_state.get("messages", [])
    for msg in st.session_state.get("messages", []):
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        msg = {"role": "user", "content": prompt}
        st.session_state.messages.append(msg)
        st.chat_message("user").write(prompt)
        response = client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=[msg],
            tools=[{
                "type": "retrieval",
                "retrieval": {
                    "knowledge_id": kb.id,
                    "prompt_template": "从文档\n\"\"\"\n{{knowledge}}\n\"\"\"\n中找问题\n\"\"\"\n{{question}}\n\"\"\"\n的答案，找到答案就仅使用文档语句回答问题，找不到答案就用自身知识回答并且告诉用户该信息不是来自文档。\n不要复述问题，直接开始回答。"
                }
            }],
            stream=True,
        )
        reply = st.chat_message("assistant").write_stream(chunk.choices[0].delta.content for chunk in response)
        st.session_state.messages.append({"role": "assistant", "content": reply})


def create_kb(client: ZhipuAI) -> None:
    with st.form("新建知识库"):
        kb_name = st.text_input(
            "知识库名称",
            help="知识库名称，限制为20字以内。",
            placeholder="知识库名称，限制为20字以内。",
            key="kb_name",
        )
        kb_description = st.text_input(
            "知识库描述",
            help="知识库描述，限制为100字以内。",
            placeholder="知识库描述，限制为100字以内。",
            key="kb_info",
        )
        kb_embedding_id = st.selectbox(
            "向量化模型",
            options=["3"],
            help="知识库绑定的向量化模型，目前仅支持embedding-2。\n3:表示为embedding-2",
            key="kb_embedding",
        )
        submit = st.form_submit_button("新建")
        if submit:
            result = client.knowledge.create(
                embedding_id=kb_embedding_id,
                name=kb_name,
                description=kb_description,
            )
            st.success(f"新建知识库成功，知识库ID为{result.id}")
            time.sleep(0.5)
            st.rerun()


def drop_kb(client: ZhipuAI, kb: KnowledgeInfo) -> None:
    client.knowledge.delete(kb.id)
    st.success(f"删除知识库{kb.name}成功")
    time.sleep(0.5)
    st.rerun()


def main():
    st.set_page_config(page_title="知识库对话demo", page_icon="📖", layout="wide")  # 页面设置
    st.header("📖知识库对话demo")  # 标题
    config_sidebar()
    client = init_client()
    selected_kb = config_kb(client)
    chat_with_kb(client, selected_kb)


if __name__ == "__main__":
    main()
