"""AI Developer Copilot - Streamlit原生组件版本"""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入模块
from modules.knowledge_base import KnowledgeBaseManager
from modules.code_analyzer import CodeAnalyzer
from modules.error_diagnosis import ErrorDiagnosis
from modules.note_generator import NoteGenerator
from modules.conversation_memory import ConversationMemory
from modules.agent_system import AgentSystem


# Session State初始化
if 'kb_manager' not in st.session_state:
    st.session_state.kb_manager = KnowledgeBaseManager()
if 'code_analyzer' not in st.session_state:
    st.session_state.code_analyzer = CodeAnalyzer()
if 'error_diagnosis' not in st.session_state:
    st.session_state.error_diagnosis = ErrorDiagnosis()
if 'note_generator' not in st.session_state:
    st.session_state.note_generator = NoteGenerator()
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory()
if 'agent_system' not in st.session_state:
    st.session_state.agent_system = AgentSystem()
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "chat"
if 'selected_kb' not in st.session_state:
    st.session_state.selected_kb = None


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## 🤖 AI Copilot")
    st.markdown("开发者智能助手")
    st.divider()

    # 功能导航
    st.markdown("### 功能")
    if st.button("💬 智能对话", use_container_width=True, type="secondary"):
        st.session_state.current_tab = "chat"
        st.rerun()

    if st.button("📚 知识库", use_container_width=True, type="secondary"):
        st.session_state.current_tab = "knowledge"
        st.rerun()

    if st.button("🔍 代码分析", use_container_width=True, type="secondary"):
        st.session_state.current_tab = "code"
        st.rerun()

    if st.button("🚨 报错诊断", use_container_width=True, type="secondary"):
        st.session_state.current_tab = "error"
        st.rerun()

    if st.button("📝 学习笔记", use_container_width=True, type="secondary"):
        st.session_state.current_tab = "notes"
        st.rerun()

    st.divider()

    # 新建对话
    if st.button("➕ 新建对话", use_container_width=True, type="primary"):
        st.session_state.conversation_memory.create_session()
        st.rerun()

    # 会话历史
    st.markdown("### 最近会话")
    sessions = st.session_state.conversation_memory.list_sessions()
    for s in sessions[:5]:
        is_active = s['session_id'] == st.session_state.conversation_memory._current_session_id
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"💬 {s['title'][:20]}", key=f"session_{s['session_id']}", use_container_width=True, type=btn_type):
            st.session_state.conversation_memory.select_session(s['session_id'])
            st.rerun()

    st.divider()
    st.markdown("### 用户")
    st.markdown("👤 开发者")


# ==================== 主内容区 ====================
st.title("AI Copilot")

# 标签页
tab_names = ["聊天", "知识库", "代码分析", "报错诊断", "学习笔记"]
tabs = st.tabs(tab_names)

# ==================== 聊天页面 ====================
with tabs[0]:
    st.markdown("### 💬 智能对话")

    # 显示聊天历史
    history = st.session_state.conversation_memory.get_conversation_history()

    if not history:
        st.info("👋 欢迎使用AI Copilot！开始对话吧。")
    else:
        for msg in history:
            role = msg["role"]
            avatar = "👤" if role == "user" else "🤖"
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg['content'])

    # 聊天输入
    if prompt := st.chat_input("输入你的问题..."):
        # 添加用户消息
        st.session_state.conversation_memory.add_user_message(prompt)

        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 调用AI - 流式输出
        with st.chat_message("assistant", avatar="🤖"):
            # 获取对话历史
            history = st.session_state.conversation_memory.get_conversation_history()
            # 使用流式生成器
            response_generator = st.session_state.agent_system.process_query_stream(prompt, history)
            # 流式显示回答
            response = st.write_stream(response_generator)

        # 保存AI回复
        st.session_state.conversation_memory.add_ai_message(response)


# ==================== 知识库页面 ====================
with tabs[1]:
    st.markdown("### 📚 知识库管理")

    # 统计
    kb_stats = st.session_state.kb_manager.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("知识库数量", kb_stats.get('total_kbs', 0))
    with col2:
        st.metric("总文档数", kb_stats.get('total_docs', 0))
    with col3:
        st.metric("向量数量", kb_stats.get('total_chunks', 0))
    with col4:
        st.success("● 运行中")

    st.divider()

    # 知识库列表和操作
    col_list, col_detail = st.columns([1, 2])

    with col_list:
        st.markdown("#### 知识库列表")

        # 新建知识库
        new_kb_name = st.text_input("新建知识库", placeholder="输入名称...")
        if st.button("➕ 创建", use_container_width=True) and new_kb_name:
            st.session_state.kb_manager.create_kb(new_kb_name)
            st.session_state.selected_kb = new_kb_name
            st.success(f"已创建: {new_kb_name}")
            st.rerun()

        st.markdown("---")

        # 知识库列表
        kbs = st.session_state.kb_manager.list_kbs()
        for kb in kbs:
            is_active = kb['name'] == st.session_state.selected_kb
            btn_type = "primary" if is_active else "secondary"
            
            col_kb_btn, col_kb_del = st.columns([3, 1])
            with col_kb_btn:
                if st.button(f"📁 {kb['name']}", key=f"kb_{kb['name']}", use_container_width=True, type=btn_type):
                    st.session_state.selected_kb = kb['name']
                    st.rerun()
            with col_kb_del:
                if st.button("🗑️", key=f"del_kb_{kb['name']}", use_container_width=True):
                    if st.session_state.kb_manager.delete_kb(kb['name']):
                        if st.session_state.selected_kb == kb['name']:
                            st.session_state.selected_kb = None
                        st.success(f"已删除知识库: {kb['name']}")
                    else:
                        st.error(f"删除知识库失败: {kb['name']}")
                    st.rerun()

    with col_detail:
        if st.session_state.selected_kb:
            kb_name = st.session_state.selected_kb
            st.markdown(f"#### 📄 {kb_name}")

            # 上传文件
            st.markdown("**上传文档**")
            uploaded_file = st.file_uploader("拖拽文件或点击上传", type=["pdf", "docx", "md", "txt"])
            if uploaded_file and st.button("📤 上传", use_container_width=True):
                with st.spinner("上传中..."):
                    import tempfile
                    import os
                    suffix = Path(uploaded_file.name).suffix
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    try:
                        # 传递原始文件名，支持中文文件名
                        result = st.session_state.kb_manager.add_document(kb_name, tmp_path, original_name=uploaded_file.name)
                        if result:
                            st.session_state.kb_manager.rebuild_index(kb_name)
                            st.success("上传成功!")
                        else:
                            st.error("上传失败")
                    finally:
                        os.unlink(tmp_path)
                    st.rerun()

            st.markdown("---")

            # 文档列表
            st.markdown("**文档列表**")
            docs = st.session_state.kb_manager.list_documents(kb_name)
            if docs:
                for doc in docs:
                    col_doc_name, col_doc_del = st.columns([4, 1])
                    with col_doc_name:
                        st.markdown(f"- 📄 {doc}")
                    with col_doc_del:
                        if st.button("🗑️", key=f"del_doc_{kb_name}_{doc}", use_container_width=True):
                            if st.session_state.kb_manager.delete_document(kb_name, doc):
                                st.session_state.kb_manager.rebuild_index(kb_name)
                                st.success(f"已删除文件: {doc}")
                            else:
                                st.error(f"删除文件失败: {doc}")
                            st.rerun()
            else:
                st.info("暂无文档")

            st.markdown("---")

            # 知识库问答
            st.markdown("**🔍 知识库问答**")
            query = st.text_input("输入问题搜索知识库...", placeholder="请输入问题...")
            if query and st.button("搜索", use_container_width=True):
                with st.spinner("查询中..."):
                    answer = st.session_state.kb_manager.generate_answer(kb_name, query)
                    st.markdown("**回答:**")
                    st.info(answer)
        else:
            st.info("👈 从左侧选择一个知识库或创建新知识库")


# ==================== 代码分析页面 ====================
with tabs[2]:
    st.markdown("### 🔍 代码仓库分析")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📦 项目上传")
        st.markdown("支持上传 ZIP 压缩包或拖拽整个文件夹")
        uploaded_files = st.file_uploader(
            "上传项目", 
            type=None, 
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        project_name = st.text_input("项目名称", placeholder="输入项目名称", key="zip_project_name")
        
        if st.button("开始分析", use_container_width=True, type="primary") and uploaded_files:
            with st.spinner("分析中..."):
                import tempfile
                import os
                import zipfile
                
                # 创建临时ZIP文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    tmp_path = tmp_file.name
                
                try:
                    # 将上传的文件打包成ZIP
                    with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for uploaded_file in uploaded_files:
                            # 获取文件内容
                            file_content = uploaded_file.getvalue()
                            # 使用原始文件名保存到ZIP中
                            zipf.writestr(uploaded_file.name, file_content)
                    
                    result = st.session_state.code_analyzer.analyze_project(tmp_path, "zip", project_name)
                    st.success("分析完成!")
                    st.json(result)
                finally:
                    os.unlink(tmp_path)

    with col2:
        st.markdown("#### 🐙 GitHub仓库")
        github_url = st.text_input("仓库URL", placeholder="https://github.com/username/repo", key="github_url")
        repo_name = st.text_input("项目名称", placeholder="输入项目名称", key="github_repo_name")
        if st.button("克隆并分析", use_container_width=True, type="primary") and github_url:
            with st.spinner("克隆和分析中..."):
                result = st.session_state.code_analyzer.analyze_project(github_url, "github", repo_name)
                st.success("分析完成!")
                st.json(result)


# ==================== 报错诊断页面 ====================
with tabs[3]:
    st.markdown("### 🚨 报错诊断助手")

    st.markdown("#### 提交报错信息")
    error_input = st.text_area("粘贴报错信息", placeholder="请粘贴完整的报错信息...", height=150)
    code_input = st.text_area("相关代码（可选）", placeholder="粘贴相关代码片段...", height=120)

    if st.button("开始诊断", use_container_width=True, type="primary") and error_input:
        with st.spinner("诊断中..."):
            result = st.session_state.error_diagnosis.diagnose_error(error_input, code_input)
            st.success("诊断完成!")
            st.json(result)


# ==================== 学习笔记页面 ====================
with tabs[4]:
    st.markdown("### 📝 学习笔记生成")

    st.markdown("#### 上传教程文档")
    uploaded_note = st.file_uploader("上传教程文档", type=["pdf", "md", "txt"])

    if uploaded_note and st.button("生成学习笔记", use_container_width=True, type="primary"):
        import tempfile
        import os
        suffix = Path(uploaded_note.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_note.getvalue())
            tmp_path = tmp_file.name
        try:
            notes_result = st.session_state.note_generator.generate_notes_stream(tmp_path)
            
            st.markdown("### 📚 学习笔记")
            st.write_stream(notes_result.get("study_notes"))
            
            st.markdown("### ❓ 面试题")
            st.write_stream(notes_result.get("interview_questions"))
            
            st.markdown("### 📖 知识总结")
            st.write_stream(notes_result.get("knowledge_summary"))
            
            st.markdown("### 🛤️ 学习路线")
            st.write_stream(notes_result.get("learning_roadmap"))
            
            st.success("生成完成!")
        finally:
            os.unlink(tmp_path)

    st.markdown("---")
    st.markdown("#### 已有笔记")
    st.info("暂无笔记，上传文档后会自动生成")
