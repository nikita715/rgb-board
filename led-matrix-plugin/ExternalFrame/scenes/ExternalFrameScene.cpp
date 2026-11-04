#include "ExternalFrameScene.h"

#include "matrix/ExternalFrame.h"

using namespace Scenes;

// rgbboard resends its frame every second; if frames stop, the sender is gone.
static constexpr auto StaleAfter = std::chrono::seconds(5);

bool ExternalFrameScene::render(rgb_matrix::FrameCanvas *canvas) {
    const auto frame = ExternalFrame::Store::instance().latest();
    const auto expected = static_cast<std::size_t>(matrix_width) * matrix_height * 3;
    const bool fresh = std::chrono::steady_clock::now() - frame.received < StaleAfter;
    if (!fresh || frame.rgb.size() != expected) {
        canvas->Clear();
        return true;
    }
    const auto *p = frame.rgb.data();
    for (int y = 0; y < matrix_height; y++)
        for (int x = 0; x < matrix_width; x++, p += 3)
            canvas->SetPixel(x, y, p[0], p[1], p[2]);
    return true;
}

SceneDescriptor ExternalFrameScene::get_descriptor() const {
    auto descriptor = Scene::get_descriptor();
    descriptor.family = "external";
    descriptor.automatic_eligible = false;
    descriptor.automatic_default = false;
    return descriptor;
}
