#pragma once

#include <chrono>
#include <cstdint>

namespace interp {

// Back off optional 60 Hz in-between passes when they repeatedly delay the
// 30 Hz logic clock. Periodic probes detect when a scene becomes cheaper.
class Ps5PacingBackoff {
public:
    using Duration = std::chrono::steady_clock::duration;

    bool allow_hold(Duration now, Duration logic_cost, Duration step, bool estimated_fit) {
        if (next_probe_ == Duration::zero()) return estimated_fit;
        if (now < next_probe_) return false;
        // Do not probe if logic alone has already used the frame budget.
        if (logic_cost >= step) return false;
        probe_pending_ = true;
        return true;
    }

    void observe_hold(Duration now, bool step_late) {
        if (probe_pending_) {
            probe_pending_ = false;
            if (step_late) next_probe_ = now + std::chrono::seconds(1);
            else reset();
            return;
        }
        late_bits_ = static_cast<std::uint8_t>(((late_bits_ << 1) | (step_late ? 1 : 0)) & 15);
        if (samples_ < 4) ++samples_;
        if (samples_ == 4 && late_count() >= 3)
            next_probe_ = now + std::chrono::seconds(1);
    }

    void reset() {
        late_bits_ = 0;
        samples_ = 0;
        probe_pending_ = false;
        next_probe_ = Duration::zero();
    }

private:
    int late_count() const {
        auto bits = late_bits_;
        int count = 0;
        while (bits) { count += bits & 1; bits >>= 1; }
        return count;
    }

    std::uint8_t late_bits_ = 0;
    std::uint8_t samples_ = 0;
    bool probe_pending_ = false;
    Duration next_probe_ = Duration::zero();
};

} // namespace interp
