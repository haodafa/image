# 我现在用手机指挥三个 AI 写代码

上周四晚上，我窝在沙发上用手机给 Claude Code 发了句"把 auth 模块的测试补上"，扔下手机去洗了个澡。出来一看——测试写好了，CI 过了。

就这么个小事，让我意识到自己的工作方式已经变了。半年前我还在三个终端之间 alt-tab，现在我在手机上点两下就行了。

这篇聊聊让这件事变得可能的工具——Paseo。

---

## 先说问题出在哪

我不是只用一个 AI 编程工具的人。Claude Code 想得深但出活慢，适合做架构设计和复杂重构；Codex 手脚快，批量写实现和测试很顺手；OpenCode 我偶尔拿来做 code review。

每个都好用，但放在一起就不好用了。

三个工具三个终端窗口，各有各的权限弹窗，彼此不知道对方的存在。我在 A 窗口等 Claude 跑着，B 窗口的 Codex 可能已经卡在权限确认上了——但我压根没注意到。中午出去吃个饭，回来经常发现某个 Agent 空等了半小时。

这不是哪个工具做得不好，是"同时管多个 AI Agent"这件事本身缺一个管理层。

![没有 Paseo vs 用了 Paseo](https://raw.githubusercontent.com/haodafa/image/main/weEdit/card_before_after.png)

---

## Paseo 是什么

用它自己的话说：

> One interface for all your Claude Code, Codex and OpenCode agents.
> Run agents in parallel on your own machines. Ship from your phone or your desk.

翻译成人话：在你自己的电脑上跑一个后台服务，统一管理所有 AI 编程 Agent。手机、桌面、网页、命令行都能连上去操控。

不是云服务，不是套壳 ChatGPT，不采集数据，不需要注册账号。代码和对话内容始终在你自己的机器上。

![Paseo 核心能力](https://raw.githubusercontent.com/haodafa/image/main/weEdit/card_features.png)

---

## 它怎么做到的

核心是一个叫 Daemon 的常驻后台进程。所有 AI Agent 都由这个 Daemon 统一启动和管理。手机 App、桌面应用、网页、命令行，本质上都是连到这个 Daemon 的"遥控器"。

![Paseo 架构](https://raw.githubusercontent.com/haodafa/image/main/weEdit/card_architecture.png)

这个设计带来一个关键好处：**关掉任何客户端，Agent 还在跑。** 不像直接在终端跑 Claude Code，窗口一关全没了。

安装没什么门槛：

```bash
npm install -g @getpaseo/cli
paseo
```

它会自动检测你机器上装了哪些 Agent CLI（Claude Code、Codex、OpenCode），直接复用你已有的 API Key，不用再配一遍。

---

## 手机端能干活，不是只能看

很多工具的移动端就是个通知查看器，Paseo 的手机端是真的能操作——创建任务、审批权限、看实时输出、追加指令。连接方式也简单，桌面端扫个二维码就行。

Paseo 官方的手机端截图：

![Paseo 手机端](https://paseo.sh/mobile-mockup.png)

我现在的日常大概是这样：早上到工位，在桌面端把几个任务分给不同的 Agent。中午出去吃饭，手机上瞄一眼谁跑完了、谁卡住了，需要审批的顺手点一下。下午回来 review 结果。

不算什么颠覆，就是不用守着电脑等 Agent 了。

---

## 命令行是真正的灵魂

App 做得不错，但我觉得 Paseo 最值得说的是它的 CLI。整套命令跟 Docker 几乎一个味道——`run`、`ls`、`logs`、`wait`、`stop`——用过 Docker 的人闭着眼就能上手。

![Paseo CLI](https://raw.githubusercontent.com/haodafa/image/main/weEdit/card_cli.png)

这意味着你可以把 Agent 编排写进脚本。我现在有个 shell 脚本，提 PR 之前自动起三个 Agent：一个跑 lint，一个跑测试，一个做 code review，跑完汇总结果。以前这些事要开三个终端手动盯，现在一个脚本搞定。

Paseo 官方也举了类似的例子：

> ```bash
> paseo run --provider claude/opus-4.6 "implement user authentication"
> paseo run --provider codex/gpt-5.4 --worktree feature-x "implement feature X"
> paseo ls                           # list running agents
> paseo attach abc123                # stream live output
> paseo send abc123 "also add tests" # follow-up task
> ```

这种"把 AI Agent 当进程管理"的思路，在我用过的工具里，只有 Paseo 做到了比较完整的程度。

---

## 编排功能：有意思，但别抱太高期望

Paseo 有一个 Loop 模式，逻辑不复杂：让 Agent 写代码，跑测试，没过就重来，设个上限防止死循环。

![Loop 编排流程](https://raw.githubusercontent.com/haodafa/image/main/weEdit/card_loop.png)

我拿它修过几个不太复杂的 bug，体验还行——扔进去，设个上限 5 轮，去干别的事，回来一看修好了。

但得说实话，稍微复杂一点的问题，它会在几轮之间来回横跳——第二轮改的东西把第一轮修好的又搞坏了。这不完全是 Paseo 的问题，更多是当前 AI Agent 本身的能力天花板。不能指望"扔进去就不管了"。

Paseo 还有个更激进的 Orchestrator 模式，可以组建 Agent "团队"——Claude 做规划、Codex 做实现，通过 Chat Room 协调。官方把这叫 "Ralph loops"。概念很酷，但标记着 Unstable，我试了几次，Agent 之间偶尔会鸡同鸭讲。当作实验性功能玩玩就好。

---

## 几个值得一提的细节

**Worktree 隔离。** 一条 `--worktree feature-x` 参数，Agent 就在独立的 Git Worktree 里干活。两个 Agent 并行改同一个仓库的不同分支，不打架。

**Provider 模式映射。** Claude 的 Plan 模式自动对应 Codex 的 Read-only，Full Access 对 Full Access。在不同 Agent 之间切换不用去记各家的权限术语。

**数据全在本地。** `~/.paseo/` 下一堆 JSON 文件，人类可读，想看就看。没有遥测，没有强制登录。远程连接走端到端加密（ECDH + AES-256-GCM），中继服务器是零知识设计。

**项目还在早期。** v0.1.x 阶段，核心功能已经稳了，但编排类 API 还在快速迭代。心理预期要有。

---

## 谁该试试，谁可以不用

![适合你吗？](https://raw.githubusercontent.com/haodafa/image/main/weEdit/card_fit.png)

---

## 写在最后

我不想给 Paseo 贴什么"划时代"的标签。它做的事情很朴素——给多个 AI 编程 Agent 套了一层统一管理。

但就是这么个不起眼的东西，切切实实改变了我每天的工作节奏。以前同时开三个 Agent，心智负担不小，总怕漏看哪个的输出。现在任务往 Paseo 里一扔，该干嘛干嘛，有空了回来看结果。

工具好不好用有个简单的判断标准：你不会整天惦记它，但没了它你会很不习惯。Paseo 对我来说就是这样。

项目开源，AGPL-3.0 协议：**github.com/getpaseo/paseo**

快速上手只需要两步：

```bash
npm install -g @getpaseo/cli
paseo
```
