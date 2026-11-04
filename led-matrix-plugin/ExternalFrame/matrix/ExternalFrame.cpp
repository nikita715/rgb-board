#include "ExternalFrame.h"

#include "scenes/ExternalFrameScene.h"

REGISTER_PLUGIN(ExternalFrame, ExternalFramePlugin)

namespace ExternalFrame {
    Store &Store::instance() {
        static Store store;
        return store;
    }

    void Store::put(const std::uint8_t *data, std::size_t size) {
        std::lock_guard lock(mutex_);
        frame_.rgb.assign(data, data + size);
        frame_.received = std::chrono::steady_clock::now();
    }

    Frame Store::latest() const {
        std::lock_guard lock(mutex_);
        return frame_;
    }
}

vector<std::unique_ptr<SceneWrapper>> ExternalFramePlugin::create_scenes() {
    vector<std::unique_ptr<SceneWrapper>> scenes;
    scenes.push_back(std::make_unique<Scenes::ExternalFrameSceneWrapper>());
    return scenes;
}

vector<std::unique_ptr<ImageProviderWrapper>> ExternalFramePlugin::create_image_providers() {
    return {};
}

bool ExternalFramePlugin::on_udp_packet(std::uint8_t plugin_id, const std::uint8_t *data, std::size_t size) {
    if (plugin_id != ExternalFrame::UdpPluginId)
        return false;
    // The scene checks the size against the panel; any other size shows black.
    ExternalFrame::Store::instance().put(data, size);
    return true;
}
