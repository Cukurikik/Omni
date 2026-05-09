#ifndef OMNI_WEATHER_PET_HARDWARE_H
#define OMNI_WEATHER_PET_HARDWARE_H

#include <cstdint>
#include <vector>

// OMNI MOTHER: Weather-Pet-Display Hardware Bridge Header (Production Grade)
// Defines the strict contract for interacting with the TFT display hardware.

namespace omni {
namespace weatherpet {

class HardwareDisplay {
public:
    HardwareDisplay(uint16_t width, uint16_t height);
    ~HardwareDisplay();

    // Prevent copying to avoid buffer duplication issues
    HardwareDisplay(const HardwareDisplay&) = delete;
    HardwareDisplay& operator=(const HardwareDisplay&) = delete;

    void init();
    void shutdown();

    void clear(uint16_t color = 0x0000);
    void draw_pixel(int x, int y, uint16_t color);
    void draw_sprite(int start_x, int start_y, int width, int height, const std::vector<uint16_t>& sprite_data);
    
    void swap_buffers();

    inline bool get_is_initialized() const { return is_initialized; }
    inline uint16_t get_width() const { return screen_width; }
    inline uint16_t get_height() const { return screen_height; }

private:
    uint16_t screen_width;
    uint16_t screen_height;
    bool is_initialized;

    // Double buffering strategy for smooth animations
    std::vector<uint16_t> front_buffer;
    std::vector<uint16_t> back_buffer;

    // Low level SPI hardware interaction routines
    void send_command(uint8_t cmd);
    void send_data(uint8_t data);
};

} // namespace weatherpet
} // namespace omni

#endif // OMNI_WEATHER_PET_HARDWARE_H
