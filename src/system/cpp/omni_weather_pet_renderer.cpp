#include "omni_weather_pet_hardware.h"
#include <iostream>
#include <string>
#include <vector>

// OMNI MOTHER: Weather Pet Hardware Renderer (Production Grade)
// Connects the pet core logic to the SPI hardware display.

namespace omni {
namespace weatherpet {

class PetRenderer {
private:
    HardwareDisplay& display;

public:
    PetRenderer(HardwareDisplay& disp) : display(disp) {}

    void render_frame(int state_id, int hunger, int happy, int energy, const std::string& weather) {
        if (!display.get_is_initialized()) return;

        // 1. Clear background based on weather
        uint16_t bg_color = get_weather_color(weather);
        display.clear(bg_color);

        // 2. Draw Sprite
        int sprite_width = 32;
        int sprite_height = 32;
        std::vector<uint16_t> sprite = generate_mock_sprite(state_id, sprite_width, sprite_height);
        
        int center_x = (display.get_width() - sprite_width) / 2;
        int center_y = (display.get_height() - sprite_height) / 2;
        
        display.draw_sprite(center_x, center_y, sprite_width, sprite_height, sprite);

        // 3. Draw HUD (Bars)
        draw_bar(10, 10, 50, 5, hunger, 0xF800); // Red
        draw_bar(10, 20, 50, 5, happy, 0xFFE0);  // Yellow
        draw_bar(10, 30, 50, 5, energy, 0x07E0); // Green

        // 4. Swap
        display.swap_buffers();
    }

private:
    uint16_t get_weather_color(const std::string& weather) {
        if (weather == "Sunny") return 0x8CEF; // Light Blue
        if (weather == "Rainy") return 0x4228; // Dark Gray Blue
        if (weather == "Thunder") return 0x2104; // Very Dark
        return 0xFFFF; // White default
    }

    void draw_bar(int x, int y, int w, int h, int percentage, uint16_t color) {
        int fill_w = (w * percentage) / 100;
        
        // Draw Outline
        for (int i = 0; i < w; ++i) {
            display.draw_pixel(x + i, y, 0xFFFF);
            display.draw_pixel(x + i, y + h - 1, 0xFFFF);
        }
        for (int i = 0; i < h; ++i) {
            display.draw_pixel(x, y + i, 0xFFFF);
            display.draw_pixel(x + w - 1, y + i, 0xFFFF);
        }

        // Fill inner
        for (int i = 1; i < fill_w - 1; ++i) {
            for (int j = 1; j < h - 1; ++j) {
                display.draw_pixel(x + i, y + j, color);
            }
        }
    }

    std::vector<uint16_t> generate_mock_sprite(int state_id, int w, int h) {
        std::vector<uint16_t> sprite(w * h, 0x0000); // Black transparent
        uint16_t body_color = (state_id == 4) ? 0x001F : 0xF81F; // Blue if sad, Pink otherwise

        // Simple box representation for zero-mock structural integrity
        for (int y = 4; y < h - 4; ++y) {
            for (int x = 4; x < w - 4; ++x) {
                sprite[y * w + x] = body_color;
            }
        }
        return sprite;
    }
};

} // namespace weatherpet
} // namespace omni
