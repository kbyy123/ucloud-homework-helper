# 本机作业助手

人工智能算法与工程已纳入每日12点流程，本人课程ID为 `2091774261898891268`，内容按数据结构处理。依据真实正文和全部附件作答，统一输出Typst PDF，内嵌C风格C++代码并归档独立 `.cpp`、测试用例与实际结果，采用 `ElemType`/`typedef`，不使用STL。代码起始模板在 `templates/ai-data-structures.cpp`。若明确要求视频或语音讲解，另附逐题可直接口述的 `讲解文稿.md`。具体执行要求在 `AGENTS.md`，复现入口为 `ai_algorithms.py`，材料按整份作业来源及附件指纹建立索引。

第三章和第五章两份作业已于11月11日完成，均10月29日布置、11月12日截止。第三章9页PDF包含五题答案、完整代码、测试结果及口述稿；第五章7页PDF包含六题答案、两种广义表结构图、完整代码及测试结果。PDF为 `output/10.29-人工智能算法与工程-第三章作业.pdf` 和 `output/10.29-人工智能算法与工程-第五章作业.pdf`。独立.cpp及原附件随作业归档，均由 `ai_algorithms.py` 按精确来源复现。

已跑通一份真实云邮作业：第三次作业——关系的表示及关系闭包。来源是学生端真实详情及课程活动关联，不通过标题猜测题目。

当前题库覆盖 Rosen《Discrete Mathematics and Its Applications》第 8 版的 9.3/14、9.3/32、9.4/26、9.4/28、9.4/29。第 32 题的三张依赖图、原书整页和全部运算过程已经保留。这里的“完成”表示本地学习材料生成成功，不改变云邮的提交状态。

“第四次作业：等价关系”已新增9.5/16、26、46、60的原题、中文解答与核对记录，目录为 `D:\BUPT\作业助手\离散数学\2113561808636010497`。第26题保留引用的第1题全部五个关系，第46题包含a–f，第60题包含a、b以及3.2节Θ定义的原书页。可复现生成器为 `rosen95.py`，索引为 `题库/rosen-8/9.5/index.json`，与早期章节采用独立材料指纹。

“第五次作业：偏序”（ID `2117142590505717762`）11月2日布置、11月6日截止。`rosen96.py` 和 `题库/rosen-8/9.6/index.json` 复现9.6/4、16、32、44完整四题及全部小问，保留书页662—664/PDF685—687和第32题原图；第16题另绘完整Hasse链。原生Typst集中输出 `11.02-离散数学-第五次作业.pdf`。程序独立核对图的闭包、覆盖边、极值与界，并检查逆序格运算；一般证明另有中文过程。9.6不改变旧章节材料指纹，新题/组合仍主动解答扩充。

数字逻辑现已新增“第二章第一次作业”的2、3、5、6、7、9、10七题，含原图、真值表、选择器连接和218个程序核验用例。`digital_ch2.py` 只复现这组已核验材料；第2、3题按用户确认保留原图疑点，第10题区分两套教材编码。

概率论与随机过程现已加入同一工作流：本人课程ID为 `2091774263564029955`，教材使用用户指定的 `D:\BUPT\26fa-概率论与随机过程\概率论与随机过程.pdf`，已确认是北邮出版社2021年1月第1版，ISBN 978-7-5635-6266-4。书页+11=PDF页。首次真实作业标题“第一次”，10月23日布置、10月29日截止，包含13项；对应 `probability_first.py`、`题库/probability-bupt-2021/index.json`，使用原生Typst写解答，保留指定小问、补充证明要求和全部原书页。

概率论页面索引已覆盖全书11章270题，保存在 `题库/页面索引/probability-bupt-2021`，按题号复用相关截图。边界题保守附相邻页；截图索引与已核验解答范围分开。新作业没有现成答案时，agent继续定位原题、解题和核验后扩充，不能止于报告旧答案未覆盖。概率课按书页解析题号及补充要求，不根据简短标题猜题。

概率第二次（ID `2116142042516131842`）10月30日布置、11月6日截止。独立题库 `题库/probability-bupt-2021/second` 和 `probability_second.py` 覆盖第1章21、23、26、一般加法公式归纳证明及第3章10、11、15、16、20、26，共10项；保留指定证明方法、跨页分布表和全部小问。原生Typst输出 `10.30-概率论与随机过程-第二次作业.pdf`。新旧题库独立路由与指纹，不改第一次归档。P18公式原排印遗漏P处有注记并保留原页。

## 查看样本

群论已于2026年11月8日按用户要求恢复。新教材为Kolman / Busby / Ross《Discrete Mathematical Structures》第六版（高教社2010英文影印本，ISBN978-7-04-031045-0），`kolman-6`，书页+25=PDF页。同一离散课程的真实`Group Theory`章节使用新教材，Relations继续使用Rosen8；教材按活动详情章节选择。第9章半群与群9.1—9.6已建立206道节后习题、17道自测、7项实验的230个题号入口，46张截图含完整42个章节页。索引为`题库/页面索引/kolman-6/index.md`，查询`lookup-exercise.py --book kolman-6 --question 9.1/32`；第11章群与编码不混入该章。

第六次作业（ID `2118625671952728065`）采用正文第六版分支9.1/16、32、34，11月6日布置、11月13日截止。`kolman91.py`保留英文原题、例16依赖和四张源公式图片，原生Typst输出`11.06-离散数学-第六次作业.pdf`。新题或新组合按同一流程主动解答、核验并扩充；旧Rosen材料指纹与人工修改保留。

第七次“半群”作业（ID `2121152547941277697`）11月13日16:05布置、11月20日截止，采用第六版9.2/16、20、30。`kolman92.py` 与 `题库/kolman-6/9.2/index.json` 复现完整三题，原生Typst输出3页 `output/11.13-离散数学-第七次作业.pdf`，保留英文原题、六空原表和完整中文证明。第16题按正整数参数从1开始；第20题唯一补表由4096种候选穷举核对；第30题一般证明及19700个有限运算表交叉核验通过。新增解析在 `lib/group-semigroups.mjs`，测试在 `tests/semigroups.test.mjs`，既有9.1材料指纹保持稳定。

概率第三次（ID `2118854975265439746`）11月7日07:55布置、11月13日截止，包含3/21、28、29，4/2、5、6(2)、7(2)，1/40、42、47共10项。`probability_third.py` 与 `题库/probability-bupt-2021/third/index.json` 单独路由、保留前两次指纹。原生Typst输出 `11.07-概率论与随机过程-第三次作业.pdf`，全部题目、指定小问、分布表、参数边界和证明过程可追溯；射击题的通常独立模型及两命中率均为0的边界明确列出。

每份作业都使用Typst排版并编译PDF，最终PDF直接放在项目根目录的 `output` 文件夹。例如本次输出为 `D:\BUPT\作业助手\output\10.23-离散数学-第四次作业.pdf`。命名为 `MM.dd-课程名-第x次作业.pdf`；日期来自云邮真实详情 `assignmentBeginTime`（布置/开放时间，北京时间），不使用截止时间或抓取时间。

归档中保留 `解答.typ`、布局及图片依赖、`解答.pdf`、Markdown材料和核对记录。新题优先用原生Typst写解答；旧生成器可将已核验Markdown迁移为Typst后编译，保留原数学内容。所有页都应渲染检查，编译失败不得报完成。布置日期或作业序号缺失时回查来源，不能猜测命名。

样本目录：`D:\BUPT\作业助手\离散数学\2111013616410509314`。主要文件为 `题目.md`、`解答.md`、`核对记录.md`，图片在 `images`，机器验证结果在 `verification.json`。

老师要求的所有 $R^1$ 到 $R^5$ 和 $W_0$ 到 $W_5$ 都已逐步列出。9.4/29 按底集 $\{1,2,3,4\}$ 解答，底集假设在文档中明确说明。

## 按需运行

在 PowerShell 执行以下命令。该入口提示输入学号和不回显的密码，运行后清除临时环境变量。

```powershell
& 'D:\BUPT\作业助手\run.ps1' -Id '2111013616410509314'
```

读取当前 Windows 用户的凭据管理器，并扫描已配置课程的全部未完成、未过期待办：

```powershell
& 'D:\BUPT\作业助手\run-scheduled.ps1'
```

只采集来源、暂不生成：

```powershell
& 'D:\BUPT\作业助手\run-scheduled.ps1' -CaptureOnly
```

返回 JSON。退出码 `0` 表示扫描成功且没有待复核项，`2` 表示存在需 agent 复核或题库未覆盖的任务，`1` 表示运行失败。未配置课程只统计跳过，不猜测教材或作答。截止时间一律按北京时间解释；未知截止时间进入待确认，不自动作答。

## 凭据与每日运行

用户已明确允许将校园凭据加密保存在 Windows 凭据管理器，目标名为 `BUPT.HomeworkAssistant.Ucloud`，仅供当前 Windows 用户读取。脚本、题库、配置、产物中不包含校园密码或访问令牌。校园登录请求仍使用临时进程环境变量。

更换密码时运行：

```powershell
& 'D:\BUPT\作业助手\set-credential.ps1'
```

删除已存凭据时执行：

```powershell
. 'D:\BUPT\作业助手\credentials.ps1'
[BuptHomeworkVault]::Delete()
```

每日调度由桌面端定时任务返回本聊天执行，计划为北京时间每天 12:00。`config.json` 的 `schedule` 是本项目的状态记录，本身不启动定时器；实际调度以桌面端任务为准。到点需要电脑和应用保持运行、该目录可访问，详见[官方定时任务说明](https://learn.chatgpt.com/docs/automations?surface=app)。休眠或关机时的补跑不作保证，可启动应用后按需执行。

定时工作流读取 `AGENTS.md`：先调用凭据管理器入口，再核对新要求。对已有准确教材、原题可读的新作业，即使没有现成答案或生成器，agent 也应继续整理原题、解答、独立验证并接入归档；不因解答题库尚未覆盖而止于通知。只有确实缺少教材、题号或图形有歧义、附件异常等无法可靠解题的情况才保留待确认。没有变化时保持安静。只有新答案、真实阻塞、运行失败或需要用户确认时通知，使用 `notification-log.json` 避免每天重复通知同一事项。

## 归档与重跑规则

- 来源包括课程 ID、作业 ID、正文、截止时间、附件摘要；题库内容、题图和生成器也有独立指纹。
- 相同来源与材料直接跳过；检测到人工修改时保留，并在返回值的 `preservedEdits` 列出。缺失文件也不会被静默覆盖。
- 新来源先进入 `.inbox`，不能仅因题号相同就复用旧答案。agent 看过具体要求、教材与核验结果后，才记录对应的 `sourceHash` 和 `materialHash`。
- 要求或已核对材料变化时，另存 `revisions/<指纹>`；原产物继续保留。读取本次返回的 `directory` 可定位新版本。
- 先在 `.staging` 生成，必需文件与验证结果齐全后再原子归档。失败不记完成，允许重跑。
- 已启用 `config.json.delivery.format=typst`：数学材料核验后，统一入口调用 `lib/pdf-delivery.mjs` 编译、检查PDF，再归档并发布到 `output`；PDF输出路径会出现在JSON的 `pdf` 字段。模板、编译逻辑和Typst程序的指纹也纳入材料指纹，格式升级另存revisions，原产物不覆盖。
- `pdf-output.json` 记录集中输出的文件哈希。相同内容重跑跳过；检测到人工修改或其他作业的同名PDF时停止覆盖并报告。受管理的旧版可在原归档或revisions中追溯。输出复制失败可重跑恢复，不需要重新解题。
- 正常命令使用 `.run.lock` 防止重叠运行。进程被强制终止后，如遗留运行锁，先确认没有其他运行进程，再手动移除该锁；不要自动删除未知运行锁。

## 扩充题库

教材与课程绑定在 `config.json`，题库按“教材版本/章节/题号”组织。`题库/rosen-8/index.json` 记录已核验五题的教材 SHA-256、原书页码、题图依赖和核对状态。

另建了[教材页面索引](题库/页面索引/README.md)：Rosen 第8版的关系、图论、树，以及《数字逻辑》第七版全书习题；Kolman第六版第9章半群与群也已加入。整页 PNG 保留原书图形、公式和所有小问；JSON/Markdown 支持“题号→图片”，并关联跨页题和课文配图。日常 agent 按题号查询所需图片，避免反复扫描整本书。

页面已索引不表示答案已验证；这要求agent完成新题的整理、作答和核验，并不要求先向用户请求允许。离散数学与数字逻辑均按此流程扩充，不能套用不相符的旧解答。`imageBookId`/`imageCatalogue` 是截图入口，与现有解答生成器的 `bookId` 分开记录。

当前 `pilot.py` 是已核对五题的可复现生成器，不是通用 OCR 或模型服务。它可按明确题号组合其中的题目；新的教材习题需要 agent 识别原题、保留图形、解答并增加验证后，再接入生成器和索引。整个流程由定时唤醒的 agent 完成核对，不需要另配模型 API 密钥。

数字逻辑解答题库为 `题库/digital-logic-7/index.json`，与全书截图索引分开。课程已改用该教材ID。`scripts/archive-digital.mjs` 可对已采集并核对的本次作业离线原子归档，不发校园请求；相同来源与材料仍会跳过，人工修改保留。

计算机组成原理与体系结构已接入同一流程，监控本人两门同名课程的活动ID。教材为戴志涛、白中英《计算机组成原理》第七版（科学出版社2024年6月，ISBN 978-7-03-078281-6）。`computer-organization-7` 的页面索引覆盖第1—10章168道章末题，31张整页图片包含题目页及本次必要定义/版本页；书页+11=PDF页。第11、12章为课程设计，不计入章末题。查询 `scripts/lookup-exercise.py --book computer-organization-7 --question 4/8`。

本次第二次作业为第四章2、7、8、9、11、12、17，无附件；10月22日布置、10月31日截止。`computer_ch4.py` 复现已核验完整七题，原生Typst解答包含全部原题及小问；第9题明确区分32位有效地址、编址单位和18位位移窗口。新题或新组合继续转录、作答和核验后扩充，不受旧生成器题号限制。输出文件名为 `10.22-计算机组成原理与体系结构-第二次作业.pdf`。

第三次作业为第5章第3、6、8、16题，无附件。11月9日布置，11月22日截止。`computer_ch5.py` 复现四题，题库索引包含书页201–202、图5.1及相关定义。PDF包含取数指令流程图、控存容量推导、8位字段及逐条译码、三组指令的读写集分析。当前教材文件位置见 `config.json`。

附件读取仅通过已从前端核实的资源接口；附件下载不发送校园令牌，下载主机限制为学校文件域。当前样本没有附件，尚未用真实附件验证文件下载字段；新附件结构、未知主机或无法直读的附件会停止本轮并交给 agent 处理，不猜测下载链接。

## 验证

```powershell
node --test 'D:\BUPT\作业助手\tests\workflow.test.mjs'
node --test 'D:\BUPT\作业助手\tests\pdf-delivery.test.mjs'
node --test 'D:\BUPT\作业助手\tests\probability.test.mjs'
node --test 'D:\BUPT\作业助手\tests\probability-second.test.mjs'
node --test 'D:\BUPT\作业助手\tests\computer.test.mjs'
node --test 'D:\BUPT\作业助手\tests\rosen96.test.mjs'
node --test 'D:\BUPT\作业助手\tests\probability-third.test.mjs'
node --test 'D:\BUPT\作业助手\tests\group-theory.test.mjs'
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\kolman91.py' --verify
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\scripts\index-kolman-group-pages.py'
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\probability_third.py' --verify
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\rosen96.py' --verify
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\computer_ch4.py' --verify
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\pilot.py' --verify
& 'C:\Users\Lin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\BUPT\作业助手\probability_second.py' --verify
```

测试覆盖截止边界、严格题号解析、只读白名单、登录失败不重试、附件主机与文件名、重复运行、人工修改保留、变更版本、失败后恢复及待核对流程。

数学验证覆盖布尔幂、每一步 Warshall、独立图搜索、完整路径枚举、图关系性质，以及 9.4/29 全部 4096 个超关系的性质与最小性。

`rosen95.py --verify` 补充等价关系的有限穷举、有理数精确计算与区间边界检查；无限集合和Θ增长阶的一般结论另有完整证明，有限程序样例不作为无限结论的证明。流程测试还检查9.5章节路由、教材及依赖变化阻止复用、原章节指纹保持稳定。

PDF测试覆盖真实布置日期与作业序号命名、日期缺失拒绝猜测、集中输出去重、同名及人工修改保护、缺少编译产物不记完成。可用 `scripts/check-pdf.py 路径\解答.pdf --previews 临时目录` 渲染全部PDF页面做视觉检查。

概率作业通过 `probability_first.py --verify` 核对：35个无放回抽样组合、分布函数全部跳跃和严格端点、分段密度的有理数精确积分、二维矩形和三角形积分、CDF边界与混合差分、独立事件条件。公理证明和对称密度的一般证明另做推理复核，不以有限样例代替证明。`scripts/build-probability-index.py` 可校验或重建概率教材截图索引，不同内容或人工修改会触发保护。

计组作业通过 `computer_ch4.py --verify` 检查全部有效OP和寄存器的位字段往返、16/19/20位补码全域、寻址子格式互斥、基址覆盖构造与全部65536个扩展操作码机器字。`scripts/index-computer-pages.py` 校验或重建全书章末题截图索引；不同内容不覆盖。流程测试覆盖正文附加要求保留、整组复用限制、教材/解答变化拦截、重复运行与人工修改保护。

依赖：Node.js 20+、本机 PowerShell，以及 `runtime.json` 指定的 Python。首次构建题库图片还需要 Poppler、Pillow、pypdf；日常运行复用已生成图片。运行时路径变化后可更新 `runtime.json`，或临时设置 `HOMEWORK_PYTHON`。

PDF依赖使用本地Typst 0.15.1便携版（`tools/typst-0.15.1`，从官方发行页下载并校验SHA-256）、已安装的Pandoc及Python的pypdf/pypdfium2；不上传内容到在线排版服务。中文使用本机宋体，数学使用Typst内置字体。排版模板不依赖在线包。

2026年11月13日新增概率第四次作业的来源路由 `lib/probability-fourth.mjs` 和复现入口 `probability_fourth.py`：完整8道教材题及二维正态相关系数证明，教材原题、版本页和定义依赖位于 `题库/probability-bupt-2021/fourth`。`probability_fourth.py --verify` 交叉核对积分、随机配对、正态概率和协方差；`tests/probability-fourth.test.mjs` 核对附加要求、小问、来源版本及重复运行。正式5页PDF为 `output/11.12-概率论与随机过程-第四次作业.pdf`，日期取真实布置时间。原生Typst、Markdown、原书截图、程序核验和核对记录随活动ID `2120815538116870145` 归档。
