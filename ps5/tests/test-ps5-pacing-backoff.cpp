#include "ps5_pacing_backoff.h"
#include <cassert>
#include <chrono>
using namespace std::chrono;
using interp::Ps5PacingBackoff;

int main() {
    Ps5PacingBackoff backoff;
    const auto step = duration_cast<Ps5PacingBackoff::Duration>(nanoseconds(33'333'333));
    const auto cheap = duration_cast<Ps5PacingBackoff::Duration>(milliseconds(10));
    auto t = duration_cast<Ps5PacingBackoff::Duration>(seconds(5));
    assert(backoff.allow_hold(t, cheap, step, true));
    assert(!backoff.allow_hold(t, cheap, step, false));
    // Three late holds out of four enter backoff.
    backoff.observe_hold(t, true);
    backoff.observe_hold(t, false);
    backoff.observe_hold(t, true);
    backoff.observe_hold(t, true);
    assert(!backoff.allow_hold(t + milliseconds(500), cheap, step, true));
    // One trial after the deadline, even if the old estimate is stale.
    t += milliseconds(1100);
    assert(!backoff.allow_hold(t, step, step, false));
    assert(backoff.allow_hold(t, cheap, step, false));
    backoff.observe_hold(t + milliseconds(45), true);
    assert(!backoff.allow_hold(t + milliseconds(100), cheap, step, true));
    // An on-time probe restores normal estimate-based pacing.
    t += milliseconds(2200);
    assert(backoff.allow_hold(t, cheap, step, false));
    backoff.observe_hold(t + milliseconds(20), false);
    assert(!backoff.allow_hold(t + milliseconds(25), cheap, step, false));
    assert(backoff.allow_hold(t + milliseconds(25), cheap, step, true));
    backoff.reset();
    assert(backoff.allow_hold(t, cheap, step, true));
}
