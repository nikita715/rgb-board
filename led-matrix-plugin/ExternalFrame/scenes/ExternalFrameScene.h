#pragma once

#include "shared/matrix/Scene.h"
#include "shared/matrix/wrappers.h"

namespace Scenes {
    // Shows the latest frame sent by an outside renderer (rgbboard) over UDP.
    // Not meant for presets or Automatic Mode: rgbboard puts it on screen through Scene Lab.
    class ExternalFrameScene : public Scene {
    public:
        bool render(rgb_matrix::FrameCanvas *canvas) override;
        string get_name() const override { return "external_frame"; }
        std::string get_category() const override { return "External"; }
        void register_properties() override {}
        tmillis_t get_default_duration() override { return 60000; }
        int get_default_weight() override { return 1; }
        SceneDescriptor get_descriptor() const override;
    };

    class ExternalFrameSceneWrapper : public Plugins::SceneWrapper {
    public:
        std::unique_ptr<Scene> create() override { return std::make_unique<ExternalFrameScene>(); }
    };
}
