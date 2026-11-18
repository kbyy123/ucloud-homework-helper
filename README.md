# UCloud 作业助手（北邮云邮只读作业工作流）

一个面向北邮云邮（UCloud）的本地只读作业助手工作流：自动抓取未完成作业与附件、结合本地电子书建立**按题号裁剪的页面索引**、由 AI Agent 核对原题与教材截图后生成 **Typst 排版解答**，并按课程归档输出为规范化的 PDF。

> **安全与只读原则**：
> - 校园接口通过 `lib/ucloud.mjs` 白名单客户端运行，**仅读取数据**，严禁任何提交、上传、删除或业务 POST 操作。
> - 账号密码保存在 **Windows 凭据管理器**（目标名 `BUPT.HomeworkAssistant.Ucloud`），不写入代码、配置或日志。

---

## 环境准备

- **Node.js** `>= 20`
- **Python 3**（用于题库索引裁剪、PDF 检查与题目生成器，如依赖 `pymupdf` / `fitz` 等）
- **Typst**（用于将 `解答.typ` 编译为 `解答.pdf`）
- **Windows PowerShell**（用于读取/写入 Windows 凭据管理器）

---

## 使用流程

### 1. 克隆仓库并准备本地配置

建议拉取 `template` 分支作为工作流起点：

```powershell
git clone -b template https://github.com/kbyy123/ucloud-homework-helper.git
cd ucloud-homework-helper
```

复制示例配置文件为本地配置（真实配置已被 `.gitignore` 忽略，不会提交到远端）：

```powershell
Copy-Item config.example.json config.json
Copy-Item runtime.example.json runtime.json
```

编辑 `runtime.json`，填入本机的 `python`、`typst`、`pandoc` 可执行文件路径（若已在系统 `PATH` 中可直接保留命令名）。

---

### 2. 自行确定需要跟踪的课程并配置 `config.json`

在云邮中确认你需要做作业的课程，获取对应的 `siteId` 与 `siteName`，并写入 `config.json` 的 `courses` 数组中：

- `key`：课程简称（用于 `output/<课程名>/` 目录命名，如 `离散数学`、`概率论与随机过程`）
- `siteId` / `siteName`：云邮课程 ID 与完整课程名称（运行时会做严格校验，防止绑定错课程）
- `bookId`：教材标识（如 `rosen-8`、`digital-logic-7`、`kolman-6`、`probability-bupt-2021`）
- `textbook`：本地电子书 PDF 的路径
- `imageCatalogue`：教材页面索引 JSON 路径（如 `题库/页面索引/rosen-8/index.json`）
- `chapterBindings`（可选）：同一门课不同章节使用不同教材时，可按活动章节名精确绑定教材（例如离散数学的图论/关系用 `rosen-8`，群论用 `kolman-6`）

> 未写入 `config.json` 的课程在抓取时会自动跳过，不会误判或猜测教材。

---

### 3. 提供电子书并由脚本/Agent 裁剪建立题号索引

为了让 Agent 准确读取原题（保留图表、上下标、公式与原题语言）而不必每次把整本几百页的 PDF 塞进上下文，需要先把电子书按页/按题号裁剪成图片索引：

1. **放置电子书**：将各门课的教材 PDF 放到本地目录（如 `./textbooks/`），并在 `config.json` 中填写对应路径。
2. **生成页面索引与裁剪截图**：使用 `scripts/` 下的索引脚本对电子书进行页面渲染与题号区域定位（可根据新教材参照现有脚本扩展）：
   - `scripts/build-page-index.py` / `scripts/build-probability-index.py` / `scripts/index-computer-pages.py` / `scripts/index-kolman-group-pages.py`
   - `scripts/verify-page-index.py`：校验索引完整性与页码映射（书页与 PDF 页码偏移）
3. **Agent 按题号精准查图**：抓取到作业题号后，Agent 通过 `scripts/lookup-exercise.py` 只读取对应题号的裁剪图片（必要时用 `--context` 补充同节上下文）：
   ```powershell
   python scripts/lookup-exercise.py --book rosen-8 --question 9.4/28
   ```

---

### 4. 配置凭据并抓取最新作业

将校园账号密码安全存入当前用户的 Windows 凭据管理器（只需执行一次，重启电脑后依然有效）：

```powershell
powershell -ExecutionPolicy Bypass -File .\set-credential.ps1
```

随后运行只抓取模式，从云邮拉取未完成、未过期的待办详情与附件到 `.inbox/`（不自动作答）：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-scheduled.ps1 -CaptureOnly
```

> 退出码说明：`0` 表示无待处理新项；`2` 表示有需要核对或作答的新作业（在 `needsReview` 中列出）；`1` 表示运行或登录异常。

---

### 5. Agent 核对、作答、编译与规范化输出

1. **核对来源**：Agent 读取 `.inbox/<作业ID>/<sourceHash>/source.json` 与附件，结合 `lookup-exercise.py` 返回的教材裁剪图核实完整题干、小问与教师附加要求。
2. **编写与验证**：编写原生 Typst 解答（`解答.typ`，模板在 `templates/homework.typ`），如有编程题或数值题则独立运行验证。
3. **编译与视觉检查**：通过 `lib/pdf-delivery.mjs` 调用 Typst 编译为 `解答.pdf`，并使用 `scripts/check-pdf.py` 渲染全部页面进行视觉核对（检查公式、中文、图表、分页与完整性）。
4. **归档与集中输出**：核验通过后归档，并统一发布到按课程分目录的 `output/`：
   ```text
   output/
   ├── 离散数学/
   │   ├── 10.23-第四次作业.pdf
   │   └── 11.02-第五次作业.pdf
   ├── 概率论与随机过程/
   │   └── 10.23-第一次作业.pdf
   └── 人工智能算法与工程/
       └── 10.29-第三章作业.pdf
   ```
   日期取云邮真实的布置时间 `assignmentBeginTime`（北京时间），不使用截止时间或抓取时间。
5. **增量知识点总结**：每次作业归档完成后，Agent 会自动读取该课程已有的 `knowledge/<课程名>/知识点总结.typ` 与本次作业的 `题目.md`、`解答.typ`，按 `templates/knowledge.typ` 模板增量补充本次涉及的核心概念、公式、解题套路与易错点（通过 `meta.json` 去重），编译检查后同步输出到 `knowledge/<课程名>/知识点总结.pdf` 与 `output/<课程名>/知识点总结.pdf`。

---

## 项目结构与分支约定

```text
.
├── run.mjs                 # 核心工作流入口
├── run.ps1 / run-scheduled.ps1 / set-credential.ps1 / credentials.ps1
├── lib/                    # 云邮客户端、题目解析、归档与 Typst/PDF 交付引擎
├── generators/             # 已核验作业的可复现 Python 生成器
├── scripts/                # 电子书裁剪建索、按题查图与 PDF 渲染检查脚本
├── templates/              # Typst 作业模板与 C 风格数据结构模板
├── tests/                  # Node.js 单元测试（npm test）
├── config.example.json     # 课程与教材配置示例
└── runtime.example.json    # 本地工具路径配置示例
```

- **`template` 分支（推送到 GitHub）**：仅保留工作流代码、模板、脚本、测试与示例配置，不包含个人课程 ID、电子书、题库截图与作业产物。
- **`main` 分支（仅本地使用，不 push 到 remote）**：在 `template` 基础上保存个人的 `config.json`、`题库/`、`output/`、各课程归档与核对记录。

## 运行测试

```powershell
npm test
```
