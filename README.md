<div align="center">

<img src="https://img.shields.io/badge/LumiAssistant-a78bfa?style=for-the-badge&labelColor=0d0d1a" alt="LumiAssistant"/>

# ✦ LumiAssistant

**你的专属 AI 伴侣：倾听你的每一天，并真正记住你。**

*桌面宠物 · 手机秘书 · 双平台无缝体验*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Web](https://img.shields.io/badge/Web-PWA-34d399?style=flat-square&logo=googlechrome&logoColor=white)](LumiAssistantWeb/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%2F%20Groq%20%2F%20OpenAI-a78bfa?style=flat-square)](https://ollama.com)
[![Groq](https://img.shields.io/badge/STT-Groq%20Whisper-34d399?style=flat-square)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)](LICENSE)
[![Demo](https://img.shields.io/badge/Live%20Demo-lumilog.netlify.app-34d399?style=flat-square&logo=netlify&logoColor=white)](https://lumilog.netlify.app)
[![Stars](https://img.shields.io/github/stars/arronchen-520/LumiAssistant?style=flat-square&color=fde68a)](https://github.com/arronchen-520/LumiAssistant/stargazers)

<br/>

> *"你的日记本应该懂你 —— 而不仅仅是存储你的文字。"*

</div>

---

## 📱 双平台

| | 🖥️ 桌面版 | 🌐 Web 版 |
|---|---|---|
| **载体** | 桌面悬浮宠物 | 移动端网页 (PWA) |
| **AI** | Ollama / Groq / OpenAI | Groq API |
| **存储** | 本地 SQLite + FTS5 全文索引 | 浏览器 localStorage |
| **语音** | Groq Whisper | Groq Whisper |
| **待办** | ✅ 优先级 + 截止日 + 自然语言 | ✅ 子任务 + 快速添加 + 秒删 |
| **日记** | ✅ 全文检索 + 记忆问答 | ✅ AI 日记 + 情感反馈 |
| **人设** | ✅ 长期记忆 | ✅ 自动提取 + 长期记忆 |
| **隐私** | ✅ 纯本地（Ollama） | ✅ 数据不离你手机 |
| **部署** | `python main.py` | 拖到 Netlify / 双击打开 |

---

LumiAssistant 是一款**悬浮桌面宠物 + AI 智能日记本**，它会安静地待在你的屏幕角落。Web 版则化身为你手机上的**私人 AI 秘书**，用聊天的方式帮你管理一切。

对它说出你一天的境遇，它会同时为你做四件事：约 1 秒内完成语音转文字、给予你真诚的情感反馈、自动提取待办事项，并且——如果你在记录中提出了问题，**它会基于你过往的日记历史为你解答**。

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
| **手机 PWA 支持** | ✅ 随时随地 | ❌ | 💰 |

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

### 📱 Web 版 AI 秘书 —— 手机上的 Lumi
纯前端实现，一个 HTML 文件搞定一切：
- **聊天式交互** — 像发微信一样跟 Lumi 对话
- **动态 Lumi 头像** — 三种动画状态（呼吸、说话、思考）
- **快速待办** — 想到什么直接加，做完秒删
- **子任务** — 大任务自动拆解为可勾选的小步骤
- **Markdown 渲染** — AI 回复支持粗体、列表、代码块
- **自动人设** — 从聊天中自然提取你的爱好、习惯、目标

### 🧠 全能意图识别 —— 八合一处理引擎

**仅需调用一次大模型**，就能准确理解你说的话，并在 8 种不同的意图中做出响应。

| 意图分类 | 用户输入示例 | LumiAssistant 会怎么做 |
|--------|--------------------|--------------------|
| `日记` | "昨天我在健身房练得很爽！" | 写下共鸣反馈并自动归档 |
| `查询` | "我上周因为什么事情感到焦虑？" | 检索过往日记为你解答 |
| `复合` | "好累呀。我明天有什么安排？" | 情感反馈 + 待办查询 |
| `闲聊` | "早安呀 Lumi！" | 温暖问候（不存日记） |
| `脑暴` | "面试很紧张，有什么建议吗？" | 化身 Copilot 给出建议 |
| `指令` | "删掉昨天的日记" | 执行数据库操作 |
| `人设` | "我在准备 GRE" | 更新长期记忆 |
| `待办` | "报告写完了，下一步做 PPT" | ✅ 完成 + 📌 新增任务 |

### ✅ 智能待办管理

用最自然的方式管理你的 To-Do：
```
"帮我加个待办：完成设计文档"      → 📌 新增，自动判断优先级
"这个很紧急，周五前要交"          → 🔴 高优先级 + 📅 自动识别截止日
"设计文档写完了，接下来写测试"     → ✅ 完成 + 📌 新增下一步
```
支持优先级（高/中/低）、截止日期、过期提醒、子任务拆解。

### 🔌 自由选择大语言模型
```env
LLM_PROVIDER=ollama   # 完全本地运行，隐私保护拉满 (默认推荐)
LLM_PROVIDER=groq     # 纯云端体验，响应速度极快，自带免费额度
LLM_PROVIDER=openai   # 调用 GPT-4o-mini 等最强模型
LLM_PROVIDER=custom   # 支持任何兼容 OpenAI API 格式的自定义端点
```

---

## 🚀 极速部署指南

### 🖥️ 桌面版

```bash
# 克隆项目
git clone https://github.com/arronchen-520/LumiAssistant
cd LumiAssistant

# 安装依赖
pip install -r requirements.txt

# 配置
cp env.example .env
# 编辑 .env 填写 GROQ_API_KEY 和 LLM 配置

# 启动
python main.py
```

### 🌐 Web 版

**在线体验：** 👉 [lumilog.netlify.app](https://lumilog.netlify.app)

**方式一：直接打开**
```bash
# 双击 LumiAssistantWeb/index.html
```

**方式二：部署到 Netlify**
```bash
# 拖拽 LumiAssistantWeb/ 文件夹到 netlify.com/drop
# 或用 CLI
netlify deploy --dir ./LumiAssistantWeb
```

**方式三：手机 PWA**
1. 部署后用手机浏览器访问
2. 点击「添加到主屏幕」
3. 从桌面图标打开 = 全屏 App 体验

> Web 版只需要一个免费的 [Groq API Key](https://console.groq.com)，在 ⚙️ 设置 里填入即可。

---

## 📁 项目结构

```text
LumiAssistant/
├── main.py                        主入口 —— 桌面版启动文件
├── env.example                    环境变量参考样例
├── requirements.txt               桌面版依赖清单
├── modules/
│   ├── llm_client.py              多模型底层调用：Ollama/Groq/OpenAI
│   ├── ai_brain.py                8种意图判断引擎
│   ├── memory.py                  解析 → FTS5 查询 → 报告生成
│   ├── database.py                SQLite + FTS5 + 待办管理
│   ├── voice.py                   录音 + Groq Whisper 转写
│   ├── reminder_scheduler.py      后台精灵线程：准点提醒
│   └── pet_window.py              赛博宠物动画 + 5-tab 界面
│
└── LumiAssistantWeb/              📱 Web 版（可独立部署）
    ├── index.html                 全部代码（HTML + CSS + JS）
    ├── manifest.json              PWA 配置
    ├── icon.jpg                   应用图标
    └── README.md                  Web 版快速指南
```

---

## 🛡️ 关于隐私

- **桌面版 Ollama 模式：** 完全本地运行。所有数据绝对不会离开你的电脑。
- **Web 版：** 所有数据只存在于你浏览器的 localStorage 中。API Key 仅在请求 Groq 时使用。
- **零追踪、零 Cookie、零数据上传。** 源码完全透明，随时可审计。

---

## 🗺️ 未来蓝图

- [ ] 向量/语义记忆网络（模糊查询支持）
- [ ] VAD 语音自动停止（智能断句检测）
- [ ] 长期情绪追踪 + 周度图表
- [ ] AI 每周生活深度总结报告
- [ ] 日记导出 Markdown / PDF
- [ ] Web 版 Service Worker 离线支持
- [ ] Electron 打包一键安装

---

<div align="center">
<sub>使用 Python & JavaScript 纯手工打造 · 桌面 + 手机双平台 · 你的数据只属于你。</sub>
<br/>
<sub>✦ 如果 LumiAssistant 帮助到了你，请 <a href="https://github.com/arronchen-520/LumiAssistant">点亮 Star ⭐</a> ✦</sub>
</div>
