"""Run both parts locally and report the automatically measured subtotal."""

import argparse
from pathlib import Path
import sys

from csim_test import test_csim
from gemm_test import test_gemm
from grading import perf_rate, speedups_from_results
from utils import EvaluationError


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    results_file = Path(".overall_results")
    results_file.unlink(missing_ok=True)
    try:
        results_csim = test_csim()
        results_gemm = test_gemm()
    except EvaluationError as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1

    results_file.write_text(
        " ".join(map(str, results_csim)) + "\n"
        + " ".join(map(str, results_gemm)) + "\n"
    )
    part_a = 40 * results_csim[1] / 100
    part_b = 40 * perf_rate(speedups_from_results(results_gemm))
    print(f"Part A: {part_a:.2f} / 40")
    print(f"Part B performance: {part_b:.2f} / 40")
    print(f"Automatic subtotal: {part_a + part_b:.2f} / 80")
    print("Report/style points and any Part B report credit are assessed by the TAs.")
    print(f"Raw results saved to {results_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
