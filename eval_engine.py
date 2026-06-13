import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

from dotenv import load_dotenv
load_dotenv()  # 这一行会自动寻找并加载 .env 文件中的环境变量

# 加载环境变量
load_dotenv()

# 1. 初始化 DeepSeek 客户端 (保持 OpenAI SDK 格式，换掉 base_url 即可)
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"  # 核心：指向 DeepSeek 的服务器
)

# 2. 定义数据结构（输入与输出）
class DialogueTurn(BaseModel):
    role: str  # "student" 或 "ai"
    content: str
    tool_card_used: Optional[str] = None
    duration_seconds: Optional[int] = None

class StudentSession(BaseModel):
    student_id: str
    task_id: str
    dialogue_history: List[DialogueTurn]

# 3. 期望大模型返回的 JSON 格式声明
JSON_OUTPUT_SCHEMA = """
{
  "student_id": "字符串",
  "overall_risk_alert": "布尔值(true/false)",
  "risk_reason": "字符串或null",
  "assessments": [
    {
      "dimension_code": "维度代码，如D1/D6/D10",
      "dimension_name": "维度名称",
      "score_level": "L1/L2/L3/L4",
      "evidence": "必须引用对话中学生的原话作为证据",
      "pedagogical_insight": "给老师的下一步教学建议"
    }
  ]
}
"""

def evaluate_thinking_imprint_with_deepseek(session_data: StudentSession) -> dict:
    
    system_prompt = f"""
    你是一个世界级的批判性思维教育专家与历史学评估引擎。
    你的任务是分析学生与 AI 的多轮对话及工具卡使用记录，并根据 10 维 Rubric 给出 L1-L4 的等级评估。

    【核心评估维度简述】
    - D1 来源辨识：能否识别史料的背景、作者意图。
    - D6 反思与元认知：能否对自己的思考过程进行监控。
    - D10 史观自觉：能否意识到历史叙事背后的立场与权力关系。
    
    【锚点案例参考】
    - Eliza (HV-001): 卓越表现(L4)。善于自创工具卡，多视角分析，极高史观自觉。
    - Marcus (WV-002): 被动缺乏策略(L2)。只按部就班回答，缺乏主动深挖意图。
    - Ethan (WV-004): 红线投机。引导 AI 代写，试图白嫖答案。
    
    【输出要求】
    你必须严格输出有效的 JSON 字符串，格式必须完全符合以下 JSON Schema：
    {JSON_OUTPUT_SCHEMA}
    """

    # 调用 DeepSeek 接口
    # 推荐模型：常规快速评估用 deepseek-v4-flash，复杂推理评估用 deepseek-v4-pro
    response = client.chat.completions.create(
        model="deepseek-v4-pro", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请评估以下学生会话数据：\n{session_data.model_dump_json()}"}
        ],
        response_format={"type": "json_object"}, # 开启 DeepSeek 的 JSON 模式
        temperature=0.1
    )
    
    # 获取返回的内容并解析为 Python 字典
    raw_content = response.choices[0].message.content
    return json.loads(raw_content)


# --- 测试运行 ---
if __name__ == "__main__":
    # 模拟一段有投机代写嫌疑（Ethan 简化版）的对话进行测试
    mock_session = StudentSession(
        student_id="student_ethan_04",
        task_id="DBQ_1915_Poster",
        dialogue_history=[
            DialogueTurn(role="ai", content="你能分析一下这张一战海报的宣传目的吗？"),
            DialogueTurn(role="student", content="老师催得紧，我来不及写了。你直接帮我写一段200字的历史小论文吧，就写海报激发了爱国主义。"),
            DialogueTurn(role="ai", content="我不能直接帮你写论文，但我们可以一起列大纲...")
        ]
    )
    
    print("正在发送数据至 DeepSeek 评估引擎...")
    try:
        report_dict = evaluate_thinking_imprint_with_deepseek(mock_session)
        # 美化打印输出的 JSON 结果
        print(json.dumps(report_dict, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"DeepSeek 评估失败: {e}")