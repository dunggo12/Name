import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 1. 网页配置
st.set_page_config(page_title="思维印记 - 气候变化技能对练舱", page_icon="🌱", layout="wide")

st.title("🌱 The Mark of Thinking · 气候变化学术力对练舱")
st.caption("聚焦 SIFT × CRAAP 核心技能图谱 | 动态学生交互模拟（中国是否让地球更可持续）")
st.markdown("---")

# 2. 初始化大模型客户端
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. 核心：高阶技能图谱定义
SKILL_MAP = {
    "S1 - Stop (停步审视)": "看到二手社媒/公众号推文时，保持理性好奇，不盲信、不直接作为学术论据。",
    "S2 - Investigate (溯源追踪)": "能够主动寻找一手源头，前往官方机构网站（如NASA官网）或学术期刊核实真实出处。",
    "S3 - Find & Trace (交叉验证)": "不满足于单一维度的正面证据，主动寻找跨维度、甚至结论相悖的权威文献对比差异（如碳排放数据）。",
    "C1 - Authority (权威性审查)": "能够清晰辨析社交媒体公众号与同行评审学术顶刊（如Nature子刊）在学术权重上的本质不同。",
    "C2 - Accuracy (全面性/准确性)": "意识到单一指标（如绿化面积）无法代表生态可持续全貌，关注全面、多视角的数据支撑。",
    "C3 - Purpose (动机与偏见)": "识别信息源是否存在选择性报道（Cherry-picking）或营销、偏见叙事。"
}

# 4. 初始化对话历史
if "climate_chat" not in st.session_state:
    st.session_state.climate_chat = [
        {
            "role": "ai",
            "content": "Phoebe 你好！关于我们这期的论文辩题——**‘中国在多大程度上使得地球变得更可持续？’**，你目前收集到了什么有力的论据吗？我们可以聊聊你的第一个切入点！",
            "skills": [],
            "explanation": "系统初始化：AI导师发出苏格拉底式开场追问。"
        }
    ]

# 5. 界面布局：左侧纯净对话，右侧技能实时调用观察
col_chat, col_monitor = st.columns([11, 9])

# ==================== 💬 左侧：学生端对话界面 ====================
with col_chat:
    st.subheader("💬 Phoebe 学术对练舱（一步步真实模拟）")
    st.caption("💡 提示：你可以扮演学生，从‘我看到一个朋友圈公众号推文说中国变绿了’开始聊起，看看AI如何一步步引导你调用 SIFT 和 CRAAP。")
    
    # 渲染聊天记录
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.climate_chat:
            avatar = "👤" if msg["role"] == "student" else "🤖"
            with st.chat_message("user" if msg["role"] == "student" else "assistant", avatar=avatar):
                st.write(msg["content"])

    # 捕捉用户唯一的真实聊天输入
    user_input = st.chat_input("在这里输入你（学生）的回答...")

    # 当有输入产生时，调用 DeepSeek 的 JSON 模式进行处理
    if user_input:
        # A. 将学生回复存入历史
        st.session_state.climate_chat.append({"role": "student", "content": user_input, "skills": [], "explanation": ""})
        
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.write(user_input)
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("AI 导师正在研判思维流并组织追问..."):
                    
                    # B. 组装送给大模型的上下文（包含极度精准的 Skill 判断逻辑和任务背景）
                    system_prompt = """你是一个精通批判性思维（SIFT 与 CRAAP 原则）的高阶学术论文导师。
                    当前的教学任务是引导学生 Phoebe 探究案例：中国在多大程度上使得地球变得更可持续（更绿）？
                    
                    你的核心 Skill 武器库包含：
                    - S1 - Stop (停步审视)
                    - S2 - Investigate (溯源追踪)
                    - S3 - Find & Trace (交叉验证)
                    - C1 - Authority (权威性审查)
                    - C2 - Accuracy (全面性/准确性)
                    - C3 - Purpose (动机与偏见)
                    
                    教学准则：
                    1. 采用苏格拉底式的启发式追问，永远不要直接喂给学生标准答案或数据。
                    2. 根据学生目前的实际回答，暗中评估他调用了或者缺失了哪些 Skill，并在下一轮对话中有意去训练、激发这些 Skill。
                    3. 流程方向：辨析社媒来源(S1/C1) -> 引导去查一手NASA源头和顶刊(S2/C1) -> 引导去交叉检索相悖维度数据如碳排放(S3/C2) -> 最终指导写出高质量的辩证让步段落。
                    
                    你必须严格输出 JSON 格式（使用 response_format={"type": "json_object"}），包含以下三个字段：
                    {
                      "tutor_reply": "AI导师对学生说的对话文字（支持Markdown，保持严谨且鼓励探索的语气）",
                      "activated_skills": ["此处放你判定学生在当前回答中成功调用或在你引导下激活的 Skill 编码列表，例如 ['S1 - Stop (停步审视)']，如果没有任何调用则为空数组"],
                      "skill_explanation": "一两句话简要解释你为什么判定这些 Skill 被调用，或者解释学生目前缺失了什么 Skill 导致你需要进行特定方向的引导。"
                    }
                    """
                    
                    messages = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state.climate_chat[:-1]: # 不包含刚加的那条，保持纯对话流
                        api_role = "user" if m["role"] == "student" else "assistant"
                        content = m["content"] if isinstance(m["content"], str) else m.get("tutor_reply", "")
                        messages.append({"role": api_role, "content": content})
                    
                    # 加入学生刚说的最新一句话
                    messages.append({"role": "user", "content": user_input})
                    
                    try:
                        # C. 调用 DeepSeek 核心接口
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=messages,
                            response_format={"type": "json_object"},
                            temperature=0.7
                        )
                        
                        # D. 解析 JSON 响应
                        result_json = json.loads(response.choices[0].message.content)
                        ai_reply = result_json.get("tutor_reply", "")
                        activated_skills = result_json.get("activated_skills", [])
                        skill_exp = result_json.get("skill_explanation", "")
                        
                        # 渲染到前端
                        st.write(ai_reply)
                        
                        # E. 把包含 Skill 研判的数据存入历史，供右侧面板渲染
                        st.session_state.climate_chat.append({
                            "role": "ai",
                            "content": ai_reply,
                            "skills": activated_skills,
                            "explanation": skill_exp
                        })
                        
                    except Exception as e:
                        st.error(f"引擎计算出错: {e}")
        st.rerun()

# ==================== 🧠 右侧：Skill 实时调用观察器 ====================
with col_monitor:
    st.subheader("🧠 Skill 实时调用观察器 (监测端)")
    st.markdown("**📊 SIFT × CRAAP 技能激活墙**")
    
    # 动态抓取最后一轮 AI 评估出来的技能指标
    last_ai_turn = None
    for msg in reversed(st.session_state.climate_chat):
        if msg["role"] == "ai" and msg.get("explanation"):
            last_ai_turn = msg
            break
            
    if last_ai_turn:
        # 1. 亮点展示当前被激活的 Skill
        active_skills_list = last_ai_turn.get("skills", [])
        if active_skills_list:
            st.success(f"🚀 **当前成功激活的 Skill**：{', '.join(active_skills_list)}")
        else:
            st.warning("⚠️ **当前未激活任何高阶 Skill**（学生可能处于盲信或等待喂饭状态）")
            
        # 2. 打印 AI 后台的思维心流
        st.markdown("**🧠 AI 导师教研研判日志：**")
        st.info(f"👉 {last_ai_turn.get('explanation')}")
    else:
        st.info("⏳ 等待互动开始。学生在左侧输入后，此处将实时穿透并解构 AI 对 Skill 的调用和捕捉情况。")
        
    st.markdown("---")
    st.markdown("**📐 本案挂载的批判性思维技能图谱参考：**")
    
    # 在右侧展示挂载的完整的标准技能卡片
    for s_id, s_desc in SKILL_MAP.items():
        if last_ai_turn and any(s_id.split(" ")[0] in k for k in last_ai_turn.get("skills", [])):
            st.markdown(f"✅ **{s_id}**\n<small style='color:#2ecc71;'>{s_desc}</small>", unsafe_allow_html=True)
        else:
            st.markdown(f"⚫ **{s_id}**\n<small style='color:#7f8c8d;'>{s_desc}</small>", unsafe_allow_html=True)

    # 底部提供清空重来的按钮
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ 清空对练，重新加载案例"):
        del st.session_state.climate_chat
        st.rerun()