"""Part B 性能分的计分规则。

权重与满分线只在这里定义，README.md 中 Part B “测试与分数”一节的表格需要与之保持一致。

对每个 case，设加速比为 x：
    x <= ZERO_SPEEDUP         得分率 0
    x >= FULL_SPEEDUP[case]   得分率 1
    其间按加速比线性插值
Part B 性能得分率 = sum(WEIGHTS[case] * 得分率)，范围 [0, 1]。
"""

# 下标依次对应 case0, case1, case2, case3
WEIGHTS = [0.0, 0.3, 0.3, 0.4]  # case0 只用于演示，不计分
ZERO_SPEEDUP = 1.0  # 与 baseline 持平（或更差）得 0 分
FULL_SPEEDUP = [None, 8.5, 8.5, 8.5]  # 加速比达到该值得满分，超过不再加分


def case_rate(case_index: int, speedup: float) -> float:
    """单个 case 的得分率，范围 [0, 1]。"""
    full = FULL_SPEEDUP[case_index]
    if full is None:
        return 0.0
    rate = (speedup - ZERO_SPEEDUP) / (full - ZERO_SPEEDUP)
    return min(1.0, max(0.0, rate))


def perf_rate(speedups: list) -> float:
    """Part B 性能得分率，范围 [0, 1]。speedups 依次为 case0 ~ case3 的加速比。"""
    return sum(w * case_rate(i, s) for i, (w, s) in enumerate(zip(WEIGHTS, speedups)))


def speedups_from_results(results: list) -> list:
    """从 gemm_test.test_gemm() 的返回值还原 case0 ~ case3 的加速比。

    返回值依次是 case0 ~ case3 各 4 项 (miss_cache, miss_reg, latency, baseline)，
    最后一项是综合加速比。
    """
    return [results[4 * i + 3] / results[4 * i + 2] for i in range(4)]
