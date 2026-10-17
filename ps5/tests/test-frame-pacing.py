#!/usr/bin/env python3
"""Run the real frame-pacing functions against a deterministic render clock."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / 'runtime/src/interp.cpp').read_text()
start = source.index('using pace_clock = std::chrono::steady_clock;')
end = source.index('}  // namespace interp', start)
functions = source[start:end].replace(
    'using pace_clock = std::chrono::steady_clock;', 'using pace_clock = TestClock;')
preamble = r'''
#include <atomic>
#include "ps5_pacing_backoff.h"
using interp::Ps5PacingBackoff;
#include <chrono>
#include <cstdio>
#include <cstdlib>
struct TestClock {
    using duration = std::chrono::steady_clock::duration;
    using time_point = std::chrono::time_point<TestClock, duration>;
    static inline time_point current{duration(1)};
    static time_point now() { return current; }
};
namespace threads {
void park_sleep_until(TestClock::time_point deadline) { TestClock::current = deadline; }
}
#define LOG(...) ((void)0)
int selectedMode = 1;
bool keepSpeed = true;
bool enabled() { return selectedMode != 0; }
bool interp_on() { return selectedMode == 1; }
bool paced() { return keepSpeed; }
bool g_exact_step = false, g_hold_next = false;
std::atomic<float> g_paced_share{-1};
'''
tests = r'''
double run(int mode, bool keep, double costMs) {
    selectedMode = mode; keepSpeed = keep;
    TestClock::current = TestClock::time_point(TestClock::duration(1));
    g_last_logic = {}; g_last_entry = {}; g_slept = {};
    g_pass_avg = std::chrono::milliseconds(16);
    g_hold_next = g_wait_step = false;
    int steps = 0;
    auto start = TestClock::now();
    const auto cost = std::chrono::duration_cast<TestClock::duration>(
        std::chrono::duration<double, std::milli>(costMs));
    while (TestClock::now() - start < std::chrono::seconds(20)) {
        paced_pass_start();
        bool preview = g_hold_next;
        if (!preview) ++steps;
        TestClock::current += cost;
        if (preview) g_hold_next = false;
        else paced_after_logic();
    }
    return steps / std::chrono::duration<double>(TestClock::now() - start).count();
}
int main() {
    for (int mode : {1, 2}) {
        for (double ms : {16.7, 20.0, 30.0}) {
            double rate = run(mode, true, ms);
            std::printf("mode %d, render %.1f ms: %.3f logic steps/s\n", mode, ms, rate);
            if (rate < 29.7 || rate > 30.3) return 1;
        }
    }
    // Control: without pacing, two 30 ms passes advance only one logic step.
    if (run(2, false, 30.0) > 17.0) return 2;
    // Switching modes must not keep an old wait or stale duration estimate.
    selectedMode = 0;
    g_wait_step = true;
    g_pass_avg = std::chrono::seconds(1);
    paced_pass_start();
    if (g_wait_step || g_last_entry != TestClock::time_point{} ||
        g_pass_avg != std::chrono::milliseconds(16)) return 3;
}
'''
with tempfile.TemporaryDirectory(prefix='wwhd-pacing-') as work:
    work = Path(work)
    cpp = work / 'pacing.cpp'
    cpp.write_text(preamble + functions + tests)
    for mode, flags in [('host', []), ('ps5-policy', ['-D__PROSPERO__'])]:
        exe = work / ('pacing-' + mode)
        subprocess.run(['c++', '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined',
                        '-I' + str(root / 'runtime/src'), *flags,
                        str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
