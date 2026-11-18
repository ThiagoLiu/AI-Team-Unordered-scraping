# -*- coding: utf-8 -*-
"""
第 1 步：认识大模型 API
目标：理解两件事
  1. 调用大模型 = 调用一个函数：发一段文字过去，拿一段文字回来
  2. 模型本身没有记忆：它"记得"什么，完全取决于你这次发了什么

运行前准备（Windows PowerShell）：
  pip install anthropic
  $env:ANTHROPIC_API_KEY="你的key"     # 只对当前窗口有效，不要把 key 写进代码
  python step1_hello_api.py
"""
import anthropic

client = anthropic.Anthropic()  # 自动读取环境变量 ANTHROPIC_API_KEY
MODEL = "claude-sonnet-5-5"     # 学习阶段用 Sonnet，便宜够用


def get_text(response):
    """模型的回答是一个"内容块"列表，可能包含思考块(thinking)、文字块(text)、
    工具调用块(tool_use)等。这里只把文字块拼起来。"""
    for block in response.content:
        print(f"  [内容块类型: {block.type}]")
    # stop_reason 说明模型为什么停下：end_turn=正常说完，max_tokens=额度用完被截断
    print(f"  [停止原因: {response.stop_reason}]")
    return "".join(block.text for block in response.content if block.type == "text")


# ---------- 实验一：最简单的一次调用 ----------
print("=" * 20, "实验一：一问一答", "=" * 20)

response = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    messages=[
        {"role": "user", "content": "手眼标定里 eye-in-hand 和 eye-to-hand 有什么区别？用三句话说明。"}
    ],
)
print(get_text(response))
print(f"[消耗] 输入 {response.usage.input_tokens} token，输出 {response.usage.output_tokens} token")


# ---------- 实验二：模型没有记忆 ----------
print("\n" + "=" * 20, "实验二：不带历史再问一次", "=" * 20)

response = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    messages=[
        {"role": "user", "content": "我刚才问你的是什么问题？"}
    ],
)
print(get_text(response))  # 观察：它答不出来


# ---------- 实验三：把历史一起发过去，它就"记得"了 ----------
print("\n" + "=" * 20, "实验三：带上历史再问", "=" * 20)

history = [
    {"role": "user", "content": "手眼标定里 eye-in-hand 和 eye-to-hand 有什么区别？用三句话说明。"},
    {"role": "assistant", "content": "（这里是上一轮模型的回答，略）"},
    {"role": "user", "content": "我刚才问你的是什么问题？"},
]
response = client.messages.create(model=MODEL, max_tokens=2000, messages=history)
print(get_text(response))  # 观察：这次能答出来


# ---------- 实验四 / 五：system 提示 = 最原始的 CLAUDE.md ----------
PROJECT_RULES = """你在协助一个 3D 相机 + 机械臂的无序抓取项目。项目约定：
- 长度单位一律用 mm
- 四元数顺序为 [w, x, y, z]
- 手眼标定矩阵 T_base_cam 表示相机坐标系在机器人基座坐标系下的位姿"""

QUESTION = "相机检测到工件在相机坐标系下的位置是 (0.1, 0.2, 0.5)，单位米。这个坐标应该怎么转换到基座坐标系？只写公式和单位处理，不用算数值，200 字以内。"

print("\n" + "=" * 20, "实验四：带项目约定（有 system）", "=" * 20)
response = client.messages.create(
    model=MODEL,
    max_tokens=4000,   # 思考也要消耗这个额度，原来的 300 不够用
    system=PROJECT_RULES,
    messages=[{"role": "user", "content": QUESTION}],
)
print(get_text(response))

print("\n" + "=" * 20, "实验五：同样的问题，不带项目约定（无 system）", "=" * 20)
response = client.messages.create(
    model=MODEL,
    max_tokens=4000,
    messages=[{"role": "user", "content": QUESTION}],
)
print(get_text(response))
# 对比实验四和实验五：结果用的单位是什么？变换矩阵叫什么、方向是怎么理解的？
