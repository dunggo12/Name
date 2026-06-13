import os
import json
from openai import OpenAI
from dotenv import load_dotenv
# 复用我们之前定义的数据结构
from eval_engine import StudentSession, DialogueTurn, evaluate_thinking_imprint_with_deepseek

load_dotenv()

# 1. 模拟 Eliza 在 18 轮对话中的高光片段
eliza_session = StudentSession(
    student_id="student_eliza_wang_G11",
    task_id="IB_History_DBQ_1915_vs_2018",
    dialogue_history=[
        DialogueTurn(
            role="ai", 
            content="很好，你已经分析了1915年Lumley海报的宣传目的。那对于2018年Cullen这张戏仿（Parody）海报，你觉得它的核心批判点在哪里？"
        ),
        DialogueTurn(
            role="student", 
            content="我刚去查了 V&A 博物馆的馆藏记录，并且读了 Hiley (1997) 关于一战政治宣传的论文。我发现不能把2018年的海报当成普通史料。它其实是对1915年原作进行解构的‘二阶史料’（Second-order Source）。Cullen 不是在批判战争本身，他是在批判后人如何利用1915年的海报来将当年强迫军人牺牲的行为‘浪漫化’。AI，你刚才的提示忽略了这种戏仿背后的互文本性（Intertextuality）。",
            tool_card_used="史观自觉卡（Eliza自创扩展版）",
            duration_seconds=420  # 停留了7分钟，说明进行了深度的查阅和思考
        ),
        DialogueTurn(
            role="ai", 
            content="非常震撼的洞察！你提到了‘二阶史料’和‘互文本性’，并且主动引入了外部学术文献。那你认为这种解构对于我们今天理解历史有什么反思？"
        ),
        DialogueTurn(
            role="student", 
            content="这让我意识到历史叙事从来都不是客观的。2018年的海报暴露出，历史记忆是如何被当下的政治话语重新塑造的。我们在评价史料时，不仅要看创作者在想什么，还要看我们这些后来的观察者处于什么‘反身性位置’（Reflexive Position）。我自己前几轮也陷入了盲区，直到我意识到我必须跳出海报画面本身。",
            tool_card_used="兔子洞日志卡"
        )
    ]
)

if __name__ == "__main__":
    print("🚀 正在向 DeepSeek 发送 Eliza 高阶案例进行压力测试...")
    try:
        # 调用我们在 eval_engine.py 里写好的 DeepSeek 评测函数
        report = evaluate_thinking_imprint_with_deepseek(eliza_session)
        
        print("\n=== 🧠 DeepSeek 评估报告 ===")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"测试失败: {e}")