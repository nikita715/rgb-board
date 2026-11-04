#pragma once

#include "shared/matrix/plugin/main.h"

#include <chrono>
#include <cstdint>
#include <mutex>
#include <vector>

using Plugins::BasicPlugin;
using Plugins::ImageProviderWrapper;
using Plugins::SceneWrapper;

namespace ExternalFrame {
    // UDP plugin id for frames from an outside renderer. Built-in plugins use 0x01..0x05.
    inline constexpr std::uint8_t UdpPluginId = 0x10;

    struct Frame {
        std::vector<std::uint8_t> rgb; // width * height * 3, row-major
        std::chrono::steady_clock::time_point received;
    };

    // The latest frame received over UDP, shared by the plugin and its scene.
    class Store {
    public:
        static Store &instance();
        void put(const std::uint8_t *data, std::size_t size);
        Frame latest() const;

    private:
        mutable std::mutex mutex_;
        Frame frame_;
    };
}

class ExternalFramePlugin : public BasicPlugin {
public:
    vector<std::unique_ptr<SceneWrapper>> create_scenes() override;
    vector<std::unique_ptr<ImageProviderWrapper>> create_image_providers() override;
    bool on_udp_packet(std::uint8_t plugin_id, const std::uint8_t *data, std::size_t size) override;
    std::string get_plugin_name() const override { return PLUGIN_NAME; }
};
