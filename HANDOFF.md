# HANDOFF：CacheLab 2026 改版交接

写给接手本仓库的助教。读完这份文档（约 5 分钟），你应该知道：2026 版相对 2025 版改了什么、为什么这样改、怎么验证、还剩什么没做。

最后更新：2026-11-06。待办事项的实时状态以 [issue #3](https://github.com/JackXing875/Cachelab-2026/issues/3) 为准。

## 1. 一句话概述

2026 版在 2025 版的基础上只做了两件事：

1. Part B 的 **case3 换成 27×41×27**（原来是 29×35×29）；
2. Part B **取消根据排行榜名次计分**，改为按**综合加速比**线性计分，综合加速比达到 **8** 得满分。

Part A、框架（`common.h`、`matrix.*`、`simulator.cpp`）、各个 case 的 baseline 实现、`Makefile`、报告模板都没有改。

## 2. 改动清单

| 文件 | 改动 |
| ---- | ---- |
| [`simulator.h`](./simulator.h) | `case3_m/n/p`：29/35/29 → 27/41/27 |
| [`README.md`](./README.md) | case3 形状；重写 Part B 计分规则；实验须知、实现注意事项、测试与分数、总分构成里去掉与排行榜名次有关的表述 |
| [`test/grading.py`](./test/grading.py)（新增） | 权重、零分线、满分线和得分率的计算，是计分规则的**唯一来源** |
| [`test/gemm_test.py`](./test/gemm_test.py) | 报告末尾新增 `Part B performance score`；`test_gemm()` 的返回值布局不变 |
| [`test/gemm_test2.py`](./test/gemm_test2.py) | `.autograder_result` 改为 Part B 性能得分（0–100）；原来是 `(综合加速比 - 1) * 100`，没有上限 |

对应的 PR 和 issue：[#4](https://github.com/JackXing875/Cachelab-2026/pull/4)（case3 形状，关闭 #1）、[#5](https://github.com/JackXing875/Cachelab-2026/pull/5)（计分规则，关闭 #2）。两个 PR 都是 squash 合并，主线上是 `8af64b5` 和 `a35f5bc`；PR 页面里保留了讨论过程中被替换掉的中间方案。

在线评测网站（`submit_gemm.sh` 上传到的 `cachelab.rucics.tech`）**保留**，仅用于提交和展示分数，不再参与排名计分。

## 3. 计分规则

综合加速比 $W = 0.3 x_1 + 0.3 x_2 + 0.4 x_3$（$x_i$ 是 case$i$ 的加速比，case0 只用于演示，不计分）。

```
得分率 s = clip((W - 1) / (8 - 1), 0, 1)
Part B 性能分 = 40 × s
```

- W = 1（与 baseline 持平或更差）得 0 分，W = 8 得满分，其间线性插值，超过 8 不再加分；
- **不对单个 case 设满分线**，各个 case 之间可以互相弥补（例如 case1 优化到极致、case3 一般，也可以拿满分）；
- 报告里的技术性深度思考可以在性能分不足时酌情补分，Part B 总分不超过 40；
- 结果不正确的 case，README 写的是“加速比按 0 计”。

数字写在三个地方，**改的时候要同步**：

| 位置 | 内容 |
| ---- | ---- |
| `test/grading.py` | `WEIGHTS`、`ZERO_SPEEDUP`、`FULL_SPEEDUP` |
| `README.md`，Part B “测试与分数” | 权重表；公式里的 $W_{\mathrm{full}} = 8$；“达到 8 得满分”；示例“综合加速比为 4.5，得分率为 50%”（这个例子依赖满分线，改满分线时要重算） |
| `README.md`，总分构成 | 一般不用改，除非改变 Part B 的 40 分的构成 |

## 4. 为什么这样定

**case3 = 27×41×27**
- 要求（来自负责人）：沿用往年奇数、a×b×a 的形式，三个维度都与 2024（31×37×31）、2025（29×35×29）不同，并且便于优化。曾考虑过偶数形状（34×36×24），因为优化起来过于容易而放弃。
- 乘加次数 29,889，与 2025 年（29,435）几乎相同，评测耗时不变。
- 奇数形状之间的差别很大。**加速比是相对 baseline 的**，而 baseline 的 cache 表现随形状剧烈变化（每次乘加 11.7 到 20.7 个单位时间），优化后的绝对开销却相差不大。所以挑形状时要看 baseline：27×41×27 的 baseline 约 20 个单位时间 / 乘加，与 case1（19.6）、case2（18.5）同量级，三个 case 的加速比处在同一量级，综合加速比里 30/30/40 的权重才名副其实。
- 排除了“陷阱”形状（如 27×43×27：朴素实现和最优实现差距悬殊，不适合作为题目）。27×41×27 邻近的取值表现平滑。

**按综合加速比，而不是逐 case 设满分线**
- 来自负责人的决定：如果某位同学在 case1 上做到了最强，case3 做得一般，也应该可以拿满分。

**满分线 W = 8**
- 内部参考解（均在 36 个寄存器限制内，已在真实框架里验证）的最强综合加速比约 8.85，8 约是其 90%，沿用 CMU / PKU 的思路：满分线略宽松于标准解，而不是卡在极限上；
- 一个优化到位的标准实现（约 8.2）可以拿满分，三个 case 统一使用教科书式实现约得 93 分。

## 5. 参考数据

**baseline**（`make caseN_baseline` 的结果，`latency = 15 × miss_cache + miss_reg`）

| case | 形状 | miss_cache | miss_reg | latency |
| ---- | ---- | ---------- | -------- | ------- |
| case0 | 2×2×2 | 3 | 20 | 65 |
| case1 | 16×16×16 | 4792 | 8448 | 80328 |
| case2 | 32×32×32 | 36032 | 66560 | 607040 |
| case3 | 27×41×27 | 36869 | 60507 | 613542 |

**不同水平的解法对应的得分**（用 `test/gemm_test.py` 实测，case3 为 27×41×27）

| 解法水平 | case1 / case2 / case3 加速比 | 综合加速比 W | Part B 性能分（满分 100） |
| -------- | ---------------------------- | ------------ | ------------------------- |
| 最简单的优化 | 3.1 / 3.3 / 2.5 | 2.9 | 27 |
| 稍好的优化 | 3.9 / 4.5 / 4.2 | 4.2 | 46 |
| 教科书式的实现，三个 case 统一 | 8.2 / 9.3 / 5.7 | 7.5 | 93.5 |
| 优化到位的标准实现 | 8.6 / 9.3 / 7.1 | 8.2 | 100 |
| 内部找到的最强解 | 10.2 / 9.4 / 7.4 | 8.85 | 100 |
| case1 做到极致，case2、case3 用教科书式 | 10.2 / 9.3 / 5.7 | 8.1 | 100 |

这些是内部能找到的上限，不是理论最优。如果去年榜单上的最高分明显高于这些数（尤其 case1、case2），说明满分线可能偏低，需要重新评估。

## 6. 怎么验证

```bash
make -j
python3 test/gemm_test.py --ignore_submit   # 本地报告，不上传
python3 test/gemm_test2.py && cat .autograder_result   # autograding 入口，输出 0–100
bash test/test.sh                           # gemm.cpp 合法性检查的自测，退出码 0 为通过
make clean
```

对仓库里未优化的 `gemm.cpp`，预期是：各个 case 加速比为 1.0，`Part B performance score: 0.00 / 100`，baseline 数值与上表一致。需要仓库里的 `csim-ref`（已提交的二进制）。

## 7. 常见修改怎么做

**换 case3 的形状**
1. 改 `simulator.h` 的三个 `#define`，以及 `README.md` 题目描述里的一行；
2. 跑 `make case3_baseline` 取新 baseline，同步给评测网站；
3. **重新评估满分线**。形状变了，case3 能达到的加速比就变了，W = 8 不一定还合适。做法是写几份不同水平的参考解，用 `gemm_test.py` 算出 W，对照第 5 节的标准（满分线约为最强解的 90%）。

**调满分线或权重**：改 `test/grading.py`，再按第 3 节同步 `README.md`。

**不要改的东西**：`gemm_test.py` 中 `test_gemm()` 的返回值布局（每个 case 依次是 `miss_cache, miss_reg, latency, baseline`，最后是综合加速比）。`overall_test.py` 把它写入 `.overall_results`，外部工具可能在读；`test/grading.py` 的 `speedups_from_results()` 也依赖这个布局。

## 8. 待办与待决

以下对应 [issue #3](https://github.com/JackXing875/Cachelab-2026/issues/3)，请以 issue 里的勾选状态为准。

**需要确认的决策**
- 满分线 8 和权重 30/30/40 是否合适；
- 成绩以“网站上的最优提交”还是“最终 commit”为准（现在沿用旧规则：报告里的版本必须与网站上的最优提交一致，README 只是把“排行榜”改成了“网站”）；
- Part B 的 40 分是否要给报告单独划分（现在没有，报告只能补分）。

**需要同步的事项**
- **在线评测网站**（代码不在本仓库）：使用新的 case3 形状；新 baseline 见上表；展示的分数与 `test/grading.py` 的规则一致，或明确只展示加速比；
- README 中**与年份相关、本次未改**的内容：模板仓库和 ISSUE 的链接仍指向 `RUCICS/Cachelab-2025Fall`；“主要负责助教”仍是 2025 年的两位同学；obe 上“获取排行榜密钥”条目的名称（README 原样引用）是否更名；
- 在 Github Classroom 上重新创建作业，确认 autograding 的两个 test 正常运行；
- 把另一位助教加为协作者，建议给 `main` 开启“合并前需要 review”；
- 可选：`report/report.md` 的表格增加“Part B 性能得分”一列；
- **发布前决定是否保留本文件**：Github Classroom 会把模板仓库复制进每位学生的仓库，本文件也会一起被复制。

## 9. 注意事项

- Github Actions 里 `Autograding Reporter` 显示**失败是正常的**：模板里 `csim.c` 是桩代码、`gemm.cpp` 是朴素实现，得分为 0，初始提交的 `main` 上也是这样。关键是 csim test 和 gemm test 两步本身都能跑通。
- 某个 case 抛出错误（结果不对、寄存器超限等）时，`gemm_test.py` 会整体失败，autograding 得分为 0。这是原有行为，README 里“按 0 计”只是人工评分时的口径。
- [`test/gemm_test2.py`](./test/gemm_test2.py) 里被注释掉的几行 `assert` 下标整体错位了一个 case（`result[0:4]` 其实是 case0，case1 从 `result[4]` 开始），如果要启用需要先修正。
- `gemm_test.py --public` 会给 `submit_gemm.sh` 传一个 `public` 参数，但脚本并不读取参数，这个选项目前没有实际作用。
- 评测网站的地址写在 [`submit_gemm.sh`](./submit_gemm.sh) 里，用的是 http。

## 10. 不在本仓库里的东西

- **评测网站的代码**：不在本仓库，需要向网站的维护者确认。
- **参考解和用来评估形状、阈值的工具**：不在本仓库，也没有保留。本仓库是公开的，并且会被复制进学生的仓库，放进来会泄露解法。第 5 节的数字是用它们得到的，需要复现时得重新写。所用模型与 `csim-ref` 完全一致（直接映射，32 组，每块 16 字节，A、B、C、buffer 在内存中依次紧密排列，`latency = 15 × miss_cache + miss_reg`），已用 baseline 和多个解法核对过。
