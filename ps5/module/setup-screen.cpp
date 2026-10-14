#include "gfx/renderer.h"
#include "gfx/vulkan/backend.h"
#include "../native/platform.h"
#include <SDL3/SDL.h>
#include <chrono>
#include <thread>
namespace overlay { void set_setup_message(const std::string&); }
namespace gfxvk {
int game_setup_screen(const std::string& message) {
    render::init();
    overlay::set_setup_message(message);
    R.tv.scan = std::make_unique<Surface>();
    auto& scan = *R.tv.scan;
    scan.width = 16; scan.height = 16; scan.format = 0x1a;
    scan.fmt = format_info(scan.format, false);
    create_surface_image(&scan, false);
    transition_image(&scan, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_ACCESS_TRANSFER_WRITE_BIT);
    VkClearColorValue color{{0.035f, 0.055f, 0.075f, 1.0f}};
    VkImageSubresourceRange range{VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1};
    vkCmdClearColorImage(command_buffer(), scan.image, scan.layout, &color, 1, &range);
    mark_gpu_written(&scan);
    pad_open();
    struct pad pad{};
    for (;;) {
        SDL_PumpEvents();
        render::swap();
        pad_poll(&pad);
        if (!(pad.held & PAD_INTERCEPTED) && (pad.pressed & PAD_CROSS)) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(16));
    }
    return 0;
}
}
