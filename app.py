import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 🌟 检查这一行！必须确保把你在第一步写好的函数和结构导入进来
from eval_engine import evaluate_thinking_imprint_with_deepseek, StudentSession, DialogueTurn

load_dotenv()

st.set_page_config(page_title="思维印记 - 动态任务舱", page_icon="🧠", layout="wide")

st.title("🧠 The Mark of Thinking · 多任务动态对话舱")
st.markdown("---")

client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# ==================== 🛠️ 核心改造：定义任务数据库 ====================
# 未来你可以无限往这个字典里加新任务，红圈内容会自动更新！
TASK_DATABASE = {
    "一战经典征兵海报 (1915 Lumley)": {
        "greeting": "你好！我是你的历史研究助手。今天我们要一起分析 1915 年的 Lumley 征兵海报。看到这张海报上写着‘你的国家需要你’，以及士兵直视并指着前方的画面，你首先注意到了什么？或者你有什么疑问吗？",
        "system_prompt": "你是一个严谨的历史系导师，正在引导学生对 1915 年一战海报进行 OPCVL 史料分析。通过启发式追问引导学生自主思考，千万不要直接喂给学生标准答案。"
    },
    "后现代戏仿海报 (2018 Cullen)": {
        "greeting": "你好！今天我们的挑战是探究 2018 年 Cullen 创作的戏仿海报。这张海报对 1915 年的原作进行了大胆的视觉解构。仔细观察画面，你认为创作者最核心的批判点在哪里？",
        "system_prompt": "你是一个精通互文本性与后现代历史叙事的导师。引导学生分析 2018 年 Cullen 海报对原作的解构，看学生能否意识到历史记忆是如何被当下政治话语塑造的。"
    },
    "通用批判性思维训练 (CRAAP 练习)": {
        "greeting": "同学你好！欢迎来到批判性思维工坊。今天我们不限特定材料，请你任意输入一段你在网上看到的、让你怀疑其真实性的新闻或观点，我们一起用 CRAAP 卡片来拆解它的可靠性。你准备聊哪条新闻？",
        "system_prompt": "你是一个批判性思维教练，负责引导学生使用 CRAAP 原则（时效性、相关性、权威性、准确性、目的性）去评估日常信息。"
    }
}

# ==================== 界面布局 ====================
col_chat, col_dash = st.columns([1, 1])

with col_chat:
    st.subheader("💬 对话交互舱（学生端）")
    
    # 🌟 在左侧最顶部放一个任务选择下拉框
    selected_task_name = st.selectbox("🎯 请选择当前的教学任务/史料主题：", list(TASK_DATABASE.keys()))
    current_task = TASK_DATABASE[selected_task_name]

    # 🌟 如果用户切换了任务，自动清空并重新初始化对话
    if "current_task_name" not in st.session_state or st.session_state.current_task_name != selected_task_name:
        st.session_state.current_task_name = selected_task_name
        # 红圈内容在这里实现了动态注入！
        st.session_state.chat_history = [{"role": "ai", "content": current_task["greeting"]}]

    # 渲染历史对话
    chat_container = st.container(height=450)
    with chat_container:
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "student" else "🤖"
            with st.chat_message("user" if msg["role"] == "student" else "assistant", avatar=avatar):
                st.write(msg["content"])

    # 用户输入交互
    if user_input := st.chat_input("在这里输入你的回答..."):
        st.session_state.chat_history.append({"role": "student", "content": user_input})
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.write(user_input)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("导师正在组织语言..."):
                    # 动态注入当前任务专属的 System Prompt
                    tutor_messages = [{"role": "system", "content": current_task["system_prompt"]}]
                    for m in st.session_state.chat_history:
                        api_role = "user" if m["role"] == "student" else "assistant"
                        tutor_messages.append({"role": api_role, "content": m["content"]})
                    
                    tutor_response = client.chat.completions.create(
                        model="deepseek-chat", 
                        messages=tutor_messages,
                        temperature=0.7
                    )
                    ai_reply = tutor_response.choices[0].message.content
                    st.write(ai_reply)
        st.session_state.chat_history.append({"role": "ai", "content": ai_reply})
        st.rerun()

# ==================== 右侧：教师看板实时研判 ====================
with col_dash:
    st.subheader("📊 教师实时研判看板（教师端）")
    if len(st.session_state.chat_history) <= 1:
        st.warning("⏳ 暂无评估数据。请在左侧选择任务并输入对话。")
    else:
        with st.spinner("🧠 DeepSeek 正在全量解构当前思维路径..."):
            try:
                history_turns = [DialogueTurn(role=m["role"], content=m["content"]) for m in st.session_state.chat_history]
                session_data = StudentSession(
                    student_id="Live_User",
                    task_id=selected_task_name, # 动态传入当前任务 ID
                    dialogue_history=history_turns
                )
                report_dict = evaluate_thinking_imprint_with_deepseek(session_data)
                
                if report_dict.get('overall_risk_alert'):
                    st.error(f"🚨 **投机风险预警！**\n\n**原因：**{report_dict.get('risk_reason')}")
                else:
                    st.success("✅ **学术诚信状态安全**")
                st.markdown("---")
                
                for ass in report_dict.get('assessments', []):
                    level_color = "🟢" if ass['score_level'] in ["L4", "L3"] else "🟡"
                    st.markdown(f"### {level_color} {ass['dimension_code']} - {ass['dimension_name']} | 等级：**{ass['score_level']}**")
                    st.markdown(f"> {ass['evidence']}")
                    st.caption(ass['pedagogical_insight'])
                    st.markdown("---")
            except Exception as e:
                st.error(f"研判失败: {e}")