<div align="center">

<img src="https://img.shields.io/badge/LumiAssistant-a78bfa?style=for-the-badge&labelColor=0d0d1a" alt="LumiAssistant"/>

# ✦ LumiAssistant

**你的专属桌面 AI 伴侣：倾听你的每一天，并真正记住你。**

*记录 → 思考 → 记忆 → 智能问答 → 待办管理 —— 一气呵成。*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%2F%20Groq%20%2F%20OpenAI-a78bfa?style=flat-square)](https://ollama.com)
[![Groq](https://img.shields.io/badge/STT-Groq%20Whisper-34d399?style=flat-square)](https://console.groq.com)
[![SQLite](https://img.shields.io/badge/Storage-SQLite%20+%20FTS5-f59e0b?style=flat-square)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourname/lumiassistant?style=flat-square&color=fde68a)](https://github.com/yourname/lumiassistant/stargazers)

<br/>

> *"你的日记本应该懂你 —— 而不仅仅是存储你的文字。"*

</div>

---

LumiAssistant 是一款**悬浮桌面宠物 + AI 智能日记本**，它会安静地待在你的屏幕角落。对它说出你一天的境遇，它会同时为你做四件事：约 1 秒内完成语音转文字、给予你真诚的情感反馈、自动提取待办事项，并且——如果你在记录中提出了问题，**它会基于你过往的日记历史为你解答**。

```text
你：     "我最近好累。对了，我上周都干嘛了？"

Lumi：   [情绪共鸣]  你最近确实很拼 —— 这已经是你这三周以来第三次提到感到疲惫了。✦

         [记忆检索]  上周：周二你完成了设计文档，周三开了一整天的会，
                    周五下午休息了半天。不过到了周五晚上，你的心情似乎轻松了许多。
```

**所有数据与运算均可完全在本地运行，你的日记绝不泄露隐私。**

---

## 🌟 为什么选择 LumiAssistant？

| 功能 | LumiAssistant | Notion / 苹果备忘录 | Day One |
|---|---|---|--|
| **语音一秒转文字** | ✅ 极速精准 | ❌ | 💰 需付费 |
| **懂你的 AI 助理** | ✅ 深度阅读你的记忆 | ❌ | ❌ |
| **随时调用历史回忆** | ✅ 行云流水的无缝体验 | ❌ | ❌ |
| **智能待办管理** | ✅ 自然语言增/改/完成 | ❌ | ❌ |
| **支持上下文多轮对话** | ✅ 20轮超长记忆 | ❌ | ❌ |
| **大模型自由切换** | ✅ 本地、Groq 或 OpenAI | ❌ | ❌ |
| **100% 本地隐私安全** | ✅ (Ollama 模式下) | ❌ 云端存储 | ❌ 云端存储 |
| **超萌桌面悬浮宠物** | ✅ 灵动动画 ✦ | 😐 | 😐 |

---

## ✨ 核心特性

### 🐾 桌面悬浮宠物 —— 全息赛博伙伴
一个完全由几何图形绘制的灵动小宠，无需依赖任何图片文件。全新设计：拥有玻璃质感的透明身体、霓虹发光线条、悬浮的全息耳朵以及数据流效的尾巴。

```
发呆状态   →  呼吸级随动、随机眨眼
倾听状态   →  录音时头顶出现跳动的音频波纹（红色）
思考状态   →  等待大模型处理时，身边环绕旋转的星星
开心状态   →  闪烁星光、^‿^ 的笑脸、开心地跳跃
犯困状态   →  待机 10 分钟后冒出 Zzz 气泡，任意点击即可唤醒
```

### 🎙️ 语音优先，约 1 秒极速转写
点击录音，支持中文、英文、日文，甚至随意混录。[Groq Whisper](https://console.groq.com) 能够在 1 秒左右完成高精度转写 —— 默认支持语种自动检测，开箱即用。

### 🧠 全能意图识别 —— 七合一处理引擎

核心亮点：**仅需调用一次大模型**，就能准确理解你说的话，并在 8 种不同的意图中做出响应。短暂的闲聊片段不会被保存进日记数据库，保持日记本的纯洁性。

| 意图分类 | 用户输入示例 | LumiAssistant 会怎么做 | 是否保存到日记？ |
|--------|--------------------|-------------------|-----------------|
| `日记记录` | "昨天我在健身房练得很爽！" | 写下共鸣反馈并自动提取日期和内容 | ✅ 是 |
| `记忆查询` | "我上周因为什么事情感到焦虑？" | 检索过往日记并为你解答 | ✅ 是 |
| `复合处理` | "好累呀。我明天有什么安排？" | 情感反馈 + 待办事项查询 | ✅ 是 |
| `日常闲聊` | "早安呀 Lumi！" | 给予温暖、简短的问候 | ❌ 否 |
| `头脑风暴` | "马上要面试了很紧张，有什么建议吗？" | 化身 Copilot，提供详尽的指导与建议 | ❌ 否 |
| `应用指令` | "删掉昨天的日记" 或 "修改看牙医的时间" | 操作数据库执行你的指令（如修改/删除） | ❌ 否 |
| `人设更新` | "我要开始减肥了，以后每天监督我" | 更新长期 Agent 记忆，让它更懂你 | ❌ 否 |
| `待办管理` | "报告第三章写完了，接下来要写第四章" | 自动更新待办状态、添加新任务 | ❌ 否 |

所有结果会在日记书写界面的不同区域分类显示，无需来回切换标签页。更棒的是，它的长期记忆数据库会在潜移默化中不断加深对你的了解。

### 🔌 自由选择大语言模型 (LLM) — Ollama / Groq / OpenAI
根据你的需求随意搭配最适合的底座：
```env
LLM_PROVIDER=ollama   # 完全本地运行，隐私保护拉满 (默认推荐)
LLM_PROVIDER=groq     # 纯云端体验，响应速度极快，自带免费额度
LLM_PROVIDER=openai   # 调用 GPT-4o-mini 等最强模型
LLM_PROVIDER=custom   # 支持任何兼容 OpenAI API 格式的自定义端点
```

### ✅ 智能待办管理 —— 自然语言跟踪项目进度
用最自然的方式管理你的 To-Do，就像和同事汇报工作一样：
```
"我要完成报告的第三章"      → 📌 新增待办：完成报告第三章
"报告第三章写完了，接下来要写第四章"  → ✅ 完成“第三章” + 📌 新增“第四章”
```
待办列表有独立的 Tab 页，支持按项目分类、状态标签和一键完成。

### ⏰ 智能自动提取待办与提醒
用最自然的语言记录你的生活。内置 `dateparser`，**无延迟、零额外大模型调用成本**即可自动提取你的关键时间节点：
```
"明天上午 10 点有个会要开"    → ⏰ 2026-03-04 10:00
"下周一早上去看牙医"   → ⏰ 2026-03-09 09:00
```

### 💬 保持状态的无缝对话体验
自带最新的 20 轮对话历史记录，支持追问和复杂连带问题：
```
"我之前为了什么事感到有压力？"   → [回答具体事件]
"能跟我再详细说说那件事吗？"     → [结合上文继续给出解答]
```

---

## 🛠️ 技术栈揭秘

| 模块层级 | 使用技术 | 为什么这么选？ |
|-------|-----------|-----|
| 大模型 | Ollama / Groq / OpenAI / custom | 给你绝对的选择权 —— 要本地隐私，还是要云端高效 |
| 语音转文字 | [Groq Whisper](https://console.groq.com) | 速度是 OpenAI Whisper 的 10 倍，并且免费 |
| API SDK | `openai` Python 包 | 统一接口规范，一个包搞定所有大模型调用 |
| 数据库 | SQLite + FTS5 引擎 | 原生支持全文索引，无需繁琐配置，一个文件随插随走 |
| 时间解析 | `dateparser` | 自然语言提取时间，零延迟，无需损耗 LLM 性能 |
| 界面渲染 | `tkinter` + Canvas | Python 极简原生库，纯代码绘制灵动像素风悬浮宠物 |

---

## 🚀 极速部署指南

### 环境准备

- Python 3.11+ 运行环境
- 一个免费的 [Groq API 密钥](https://console.groq.com) (用于实现极致语音转录速度)
- **(可选)** 想要完全保护隐私？请安装并运行本地模型工具 [Ollama](https://ollama.com)

### 一键安装

```bash
git clone https://github.com/yourname/lumiassistant
cd lumiassistant
pip install -r requirements.txt
```

### 极其简单的配置

首先复制配置文件模板：
```bash
cp env.example .env
```

**选项 A: 极致隐私，纯本地运行 (Ollama)：**
```env
GROQ_API_KEY=你的_groq_api_key_填在这里
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
```

**选项 B: 极致速度，使用免费云端大模型 (Groq)：**
```env
GROQ_API_KEY=你的_groq_api_key_填在这里
LLM_PROVIDER=groq
LLM_API_KEY=你的_groq_api_key_也填在这一行
LLM_MODEL=llama-3.3-70b-versatile
```

### 启动项目

```bash
# 如果你使用 Ollama 模式，请先拉取模型并在后台运行
ollama pull llama3.2 && ollama serve

# 启动 AI 小宠物
python main.py
```

启动后，LumiAssistant 宠物将出现在屏幕的**右下角**。点击它即可打开炫酷的日记交互面板！

---

## 🎮 如何使用

| 操作 | 发生什么？ |
|--------|-------------|
| **左键点击** 宠物 | 呼出 / 收起 交互主面板 |
| **右键点击** 宠物 | 呼出快捷菜单：录音、设置心情、退出 |
| **拖拽** 宠物 | 它会乖乖跟着你的鼠标去屏幕的任意位置 |
| **🎙️ 录制语音** | [开始] → 宠物头顶出现音轨波纹 → [停止] → 1 秒转写 |
| **保存并反思** | 大模型一键帮你：情绪抚慰 + 回答疑惑 + 提取重点 |
| **切换 Chat 标签页** | 与 Lumi 进行最长 20 轮上下文的深度沉浸式对话 |

### 试着问它这些问题 (可以在输入框或 Chat 里直接问)

```text
"我上周都干了些啥？"
"我上一次提到去健身房是什么时候？"
"这个月我还有哪些待办事项？"
"棒我总结一下这个月的日记内容"
"最近有哪些事情让我感到特别兴奋？" 
```

### 待办管理示例

```text
"我要给项目A加个待办：完成设计文档"  → 新增待办
"项目A设计文档写完了"          → 标记完成
"项目B做到测试阶段了，下一步是部署"  → 更新进度 + 新增任务
"删掉那个设计文档的待办"         → 删除待办
```

---

## 📁 核心项目结构指引

```text
lumiassistant/
├── main.py                        主入口文件 —— 串联所有界面组件与回调
├── env.example                    包含所有配置项的环境变量参考样例
├── requirements.txt               核心依赖清单
└── modules/
    ├── llm_client.py              多模型底层调用：Ollama/Groq/OpenAI 兼容
    ├── ai_brain.py                「全能意图」判断引擎核心代码（8 种意图）
    ├── memory.py                  3 阶段管线核心：解析 → FTS5 查询 → 报告生成
    ├── database.py                本地 SQLite + 全文索引 (FTS5) + 待办管理
    ├── voice.py                   录音切片收音 + Groq 飞速转文本实现
    ├── reminder_scheduler.py      后台精灵线程：为你准点触发日程提醒
    └── pet_window.py              呈现赛博宠物动画 + 透明悬浮 5-tab 界面框架
```

---

## 🛡️ 关于隐私

- **Ollama 模式下：** 完全本地运行。除了使用 Groq 进行极速语音转写外（仅传输音频，不含最终的日记分析），所有数据绝对不会离开你的电脑。
- **Groq/OpenAI 模式下：** 日记文本数据会通过 API 发送给云端模型。你可以根据自己的需求自由选择。

---

## 🗺️ 未来蓝图 (Roadmap)

- [ ] 向量/语义记忆网络 (支持类似 "想不起名字但很让人头大的那个项目" 的模糊查询)
- [ ] VAD 语音自动停止 (智能断句检测机制 —— 再也不用手动点击停止录音)
- [ ] 长期情绪追踪引擎 + 周度图表展示面板
- [ ] AI 每周生活深度总结报告
- [ ] 支持日记精美导出为 Markdown / PDF 格式
- [ ] 通过 Supabase 增加云端同步功能 (用户自主选择是否开启)

---

<div align="center">
<sub>使用 Python 纯手工打造 · 支持纯本地运行 · 你的日记只属于你。</sub>
<br/>
<sub>✦ 如果 LumiAssistant 帮助到了你，请点亮 Star！ ✦</sub>
</div>
