# AI Team Unordered Picking —— 借无序抓取项目学习 AI

以 3D 相机（眼在手外）+ 机械臂的料箱无序抓取为场景，一步步学习大模型 API、tool use、agent、skill 等概念。

## 文件说明

- `CLAUDE.md`：给 Claude Code 的项目说明（教学方式、项目约定、安全红线），每次打开项目自动加载
- `docs/learning_log.md`：完整学习记录、每一步进度和下一步计划

## 学习路线

| 步骤 | 文件 | 内容 | 状态 |
|---|---|---|---|
| 第 1 步 | `step1_hello_api.py` | 调用大模型 API；模型没有记忆；内容块；`max_tokens` 与 `stop_reason`；system 提示 | 已完成 |
| 第 2 步 | `step2_tool_use.py` | Tool use：定义工具、模型请求调用、执行并返回结果 | 已运行，巩固中 |
| 第 3 步 | — | Agent 循环：模型自己决定调用哪些工具、调用几次 | 待开始 |
| 第 4 步 | — | 在手写 agent 里实现最简单的 skill 机制 | 待开始 |

## 环境配置（Windows PowerShell）

```powershell
py -m venv .venv                   # 新 Windows 上 python 可能是应用商店占位程序，用 py 启动器建环境
.\.venv\Scripts\Activate.ps1       # 激活后 python 就指向 .venv 里的解释器
python -m pip install -r requirements.txt
$env:ANTHROPIC_API_KEY="你的key"   # 只对当前窗口有效，不要写进代码或提交到 git
```

## 项目约定

- 相机安装方式：眼在手外（eye-to-hand），固定在料箱正上方
- 长度单位一律用 mm
- 四元数顺序为 [w, x, y, z]
- `T_base_cam` 表示相机坐标系在机器人基座坐标系下的位姿
