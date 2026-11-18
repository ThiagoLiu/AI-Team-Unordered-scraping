# -*- coding: utf-8 -*-
r"""
第 2 步：Tool use —— 让模型调用你写的函数
目标：理解三件事
  1. 你怎样"告诉"模型有哪些工具可以用（名字 + 描述 + 参数格式）
  2. 模型自己决定要不要用工具；要用时，它不会自己执行，而是返回一个 tool_use 块"请求"你执行
  3. 你执行函数后，把结果用 tool_result 发回去，模型再据此给出最终回答

运行：
  .\.venv\Scripts\Activate.ps1
  $env:ANTHROPIC_API_KEY="你的key"
  python step2_tool_use.py
"""
import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

SYSTEM = """你在协助一个 3D 相机 + 机械臂的无序抓取项目。项目约定：
- 相机安装方式：眼在手外（eye-to-hand），固定在料箱正上方
- 长度单位一律用 mm
- 四元数顺序为 [w, x, y, z]
- T_base_cam 表示相机坐标系在机器人基座坐标系下的位姿"""


# ============================================================
# 第一部分：你自己写的普通 Python 函数（和 AI 无关）
# ============================================================

# 示例手眼标定结果：相机在基座上方 1200 mm 处，镜头朝下（绕 X 轴转了 180°）
T_BASE_CAM = [
    [1,  0,  0,  500],
    [0, -1,  0,    0],
    [0,  0, -1, 1200],
    [0,  0,  0,    1],
]


def camera_to_base(x_mm, y_mm, z_mm):
    """把相机坐标系下的点转换到基座坐标系：p_base = T_base_cam · p_cam"""
    p = [x_mm, y_mm, z_mm, 1]
    r = [sum(T_BASE_CAM[i][j] * p[j] for j in range(4)) for i in range(3)]
    return {"x_mm": r[0], "y_mm": r[1], "z_mm": r[2]}


# ============================================================
# 第二部分：把函数"介绍"给模型 —— 工具定义
# 模型看不到你的 Python 代码，它只能看到这份说明。
# description 写得好不好，直接决定模型会不会在正确的时候、用正确的参数调用它。
# ============================================================
TOOLS = [
    {
        "name": "camera_to_base",
        "description": "把相机坐标系下的一个点转换到机器人基座坐标系。"
                       "使用项目已标定好的手眼矩阵 T_base_cam。输入和输出的单位都是 mm。",
        "input_schema": {
            "type": "object",
            "properties": {
                "x_mm": {"type": "number", "description": "相机坐标系下的 X，单位 mm"},
                "y_mm": {"type": "number", "description": "相机坐标系下的 Y，单位 mm"},
                "z_mm": {"type": "number", "description": "相机坐标系下的 Z，单位 mm"},
            },
            "required": ["x_mm", "y_mm", "z_mm"],
        },
    }
]


def show(response):
    """把模型返回的每个内容块打印出来，方便观察"""
    print(f"  [停止原因: {response.stop_reason}]")
    for block in response.content:
        if block.type == "thinking":
            print(f"  [thinking 块] （思考了 {len(block.thinking)} 个字符，内容略）")
        elif block.type == "text":
            print(f"  [text 块] {block.text}")
        elif block.type == "tool_use":
            print(f"  [tool_use 块] 请求调用工具: {block.name}")
            print(f"               参数: {block.input}")
            print(f"               调用编号: {block.id}")


# ============================================================
# 实验一：一个不需要工具的问题
# ============================================================
print("=" * 20, "实验一：不需要工具的问题", "=" * 20)
q1 = "料箱无序抓取，相机为什么常用眼在手外？一句话回答。"
response = client.messages.create(
    model=MODEL, max_tokens=4000, system=SYSTEM, tools=TOOLS,
    messages=[{"role": "user", "content": q1}],
)
show(response)
# 观察：工具明明给了，但模型没有用 —— 它自己判断不需要


# ============================================================
# 实验二：一个需要工具的问题
# ============================================================
print("\n" + "=" * 20, "实验二：需要工具的问题", "=" * 20)
q2 = "相机检测到工件中心在相机坐标系下是 (0.1, 0.2, 0.5)，单位米。它在基座坐标系下的坐标是多少？"
response = client.messages.create(
    model=MODEL, max_tokens=4000, system=SYSTEM, tools=TOOLS,
    messages=[{"role": "user", "content": q2}],
)
show(response)
# 观察：
#   1. 停止原因变成了 tool_use —— 模型停下来，等你去执行工具
#   2. 看它传的参数：是 0.1 还是 100？它自己做了什么？
#   3. 到这里为止，camera_to_base 函数还一次都没有被执行过


# ============================================================
# 实验三：执行工具，把结果发回去，拿到最终回答
# ============================================================
print("\n" + "=" * 20, "实验三：执行工具并把结果发回", "=" * 20)

tool_call = next(b for b in response.content if b.type == "tool_use")

# 真正执行函数的是你的代码，不是模型
result = camera_to_base(**tool_call.input)
print(f"  [你的代码执行了 {tool_call.name}] 结果: {result}")

messages = [
    {"role": "user", "content": q2},                     # 原问题
    {"role": "assistant", "content": response.content},  # 模型上一轮的回复（含 tool_use 请求）
    {"role": "user", "content": [                         # 工具结果，用 tool_use_id 对上是哪一次请求
        {"type": "tool_result", "tool_use_id": tool_call.id, "content": json.dumps(result)}
    ]},
]
response = client.messages.create(
    model=MODEL, max_tokens=4000, system=SYSTEM, tools=TOOLS, messages=messages,
)
show(response)
# 观察：停止原因回到 end_turn，模型基于你函数算出的结果作答
