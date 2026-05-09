#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <mutex>
#include <atomic>
#include <random>
#include <algorithm>

// OMNI MOTHER: Weather Pet Core Logic (Production Grade)
// Multi-threaded pet logic simulator that reacts to weather API data.

namespace omni {
namespace weatherpet {

enum class PetState {
    SLEEPING,
    AWAKE,
    PLAYING,
    EATING,
    SAD,
    EXCITED
};

enum class WeatherCond {
    SUNNY,
    RAINY,
    CLOUDY,
    SNOWY,
    THUNDERSTORM
};

class WeatherPetCore {
private:
    std::string pet_name;
    std::atomic<PetState> current_state;
    std::atomic<WeatherCond> current_weather;
    
    int hunger_level;
    int happiness_level;
    int energy_level;
    
    std::atomic<bool> is_running;
    std::thread logic_thread;
    std::mutex data_mutex;

public:
    WeatherPetCore(const std::string& name) 
        : pet_name(name), 
          current_state(PetState::AWAKE), 
          current_weather(WeatherCond::SUNNY),
          hunger_level(50), 
          happiness_level(80), 
          energy_level(100),
          is_running(false) {
    }

    ~WeatherPetCore() {
        stop();
    }

    void start() {
        if (is_running) return;
        is_running = true;
        logic_thread = std::thread(&WeatherPetCore::logic_loop, this);
        std::cout << "[OMNI PET] " << pet_name << " has spawned!" << std::endl;
    }

    void stop() {
        if (is_running) {
            is_running = false;
            if (logic_thread.joinable()) {
                logic_thread.join();
            }
            std::cout << "[OMNI PET] " << pet_name << " was despawned." << std::endl;
        }
    }

    void update_weather(WeatherCond weather) {
        current_weather = weather;
        reevaluate_state();
    }

    void feed() {
        std::lock_guard<std::mutex> lock(data_mutex);
        hunger_level = std::min(100, hunger_level + 30);
        happiness_level = std::min(100, happiness_level + 10);
        current_state = PetState::EATING;
        std::cout << "[OMNI PET] You fed " << pet_name << "!" << std::endl;
    }

    PetState get_state() const { return current_state; }
    
    // For the renderer to consume
    void get_stats(int& hunger, int& happy, int& energy) {
        std::lock_guard<std::mutex> lock(data_mutex);
        hunger = hunger_level;
        happy = happiness_level;
        energy = energy_level;
    }

private:
    void logic_loop() {
        std::mt19937 rng(std::random_device{}());
        std::uniform_int_distribution<int> decay(1, 5);

        while (is_running) {
            std::this_thread::sleep_for(std::chrono::seconds(2));
            
            {
                std::lock_guard<std::mutex> lock(data_mutex);
                
                // Decay stats over time
                if (current_state != PetState::SLEEPING) {
                    hunger_level = std::max(0, hunger_level - decay(rng));
                    energy_level = std::max(0, energy_level - decay(rng));
                }
                
                if (current_state == PetState::SLEEPING) {
                    energy_level = std::min(100, energy_level + 10);
                }

                // Happiness drops if hungry
                if (hunger_level < 20) {
                    happiness_level = std::max(0, happiness_level - decay(rng));
                }
            }
            
            reevaluate_state();
        }
    }

    void reevaluate_state() {
        std::lock_guard<std::mutex> lock(data_mutex);
        
        if (energy_level < 15) {
            current_state = PetState::SLEEPING;
            return;
        }

        if (happiness_level < 30 || hunger_level < 20) {
            current_state = PetState::SAD;
            return;
        }

        if (current_weather == WeatherCond::THUNDERSTORM) {
            current_state = PetState::SAD; // Scared
            return;
        }

        if (current_weather == WeatherCond::SUNNY && energy_level > 60) {
            current_state = PetState::EXCITED;
            return;
        }

        if (current_state != PetState::EATING) {
            current_state = PetState::AWAKE;
        }
    }
};

} // namespace weatherpet
} // namespace omni
