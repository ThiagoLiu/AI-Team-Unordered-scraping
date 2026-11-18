# CLAUDE.md

## 这个项目是什么

这是一个**学习项目**，不是交付项目。用户借 3D 相机 + 机械臂的料箱无序抓取场景，系统学习大模型 API、tool use、agent、skill、MCP、hooks、subagent 等 AI 概念，最终目标是自己能熟练用起来，并能把"换工件快速部署"的流程封装成 skill。

**开始工作前，先读 `docs/learning_log.md`**，里面有完整的学习路线、每一步的进度、用户的回答和下一步计划。

## 用户情况

- 机器人/视觉方向工程师，主要用 Python（之前做过人脸识别项目），C++ 只用于必须的实时控制部分
- Windows + PowerShell；项目用 `.venv` 虚拟环境；代码托管在 https://github.com/ThiagoLiu/AI-Team-Unordered-scraping
- 用中文交流

## 教学方式（必须遵守）

1. **一次只推进一小步**：每步一个可运行的小实验文件 `stepN_xxx.py`，跑完当场能看到结果
2. **每步都要讲解**：讲清"这一步的核心概念"，并联系无序抓取的实际场景举例
3. **每步结束出 2～3 个检验问题**，等用户回答后再进入下一步；用户答得不完整时，具体指出缺了什么，不要只说"对"
4. 用户运行报错时，把报错当作教学机会：先解释为什么错，再修复
5. 适时把当前步骤和 Claude Code 的真实功能对应起来（例如"你手写的这个机制，就是 Claude Code 里 skill 的原理"）
6. 每完成一步：更新 `README.md` 的进度表和 `docs/learning_log.md`，并提醒用户 `git commit` / `git push`

## 项目约定（坐标系和单位）

- 相机安装方式：眼在手外（eye-to-hand），固定在料箱正上方
- 长度单位一律用 mm
- 四元数顺序为 [w, x, y, z]
- `T_base_cam` 表示相机坐标系在机器人基座坐标系下的位姿，`p_base = T_base_cam · p_cam`

## 代码规范

- Python，注释和打印信息用中文
- API key 只从环境变量 `ANTHROPIC_API_KEY` 读取，**绝不写进代码或提交到 git**
- 学习阶段默认模型 `claude-sonnet-5-5`
- 处理模型回复时遍历 `response.content` 并按 `block.type` 区分，不要假设 `content[0]` 是文字
- 检查 `stop_reason`；`max_tokens` 要留够（思考也消耗额度，至少 2000）
- 新依赖加到 `requirements.txt`

## 安全红线

- 任何代码都**不得向真实机器人或控制器发送运动指令**；涉及机器人的部分一律用模拟/示例数据
- 后续学 hooks 时，要把这条规则落实成拦截 hook
