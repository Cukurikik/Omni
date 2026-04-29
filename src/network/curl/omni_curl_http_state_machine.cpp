// OMNI Curl HTTP State Machine Engine — Network Layer (C++)
// Absorbing curl/curl finite state machine mechanics
// Deterministic HTTP/1.1 lifecycle bound transitions

#include <vector>
#include <string>
#include <unordered_map>

template<typename T>
struct CurlResult {
    bool ok;
    T value;
    std::string error;
};

enum class CurlState {
    INIT,
    CONNECT,
    TLS_HANDSHAKE,
    SEND_REQUEST,
    READ_RESPONSE,
    DONE,
    ERROR_STATE
};

class OmniCurlHttpStateMachine {
private:
    uint64_t operations_run = 0;

public:
    OmniCurlHttpStateMachine() = default;

    /**
     * Executes the exact state transition matrix for core HTTP request flow.
     */
    CurlResult<CurlState> advance_state(CurlState current_state, bool io_success) {
        this->operations_run++;

        if (!io_success) {
            return {true, CurlState::ERROR_STATE, ""};
        }

        switch (current_state) {
            case CurlState::INIT:
                return {true, CurlState::CONNECT, ""};
            case CurlState::CONNECT:
                return {true, CurlState::TLS_HANDSHAKE, ""};
            case CurlState::TLS_HANDSHAKE:
                return {true, CurlState::SEND_REQUEST, ""};
            case CurlState::SEND_REQUEST:
                return {true, CurlState::READ_RESPONSE, ""};
            case CurlState::READ_RESPONSE:
                return {true, CurlState::DONE, ""};
            case CurlState::DONE:
                return {true, CurlState::DONE, ""};
            case CurlState::ERROR_STATE:
                return {true, CurlState::ERROR_STATE, ""};
            default:
                return {false, CurlState::ERROR_STATE, "CurlError: Unknown state bounds."};
        }
    }

    std::unordered_map<std::string, std::string> diagnostics() const {
        return {
            {"engine", "OmniCurlHttpStateMachine"},
            {"transitions_evaluated", std::to_string(operations_run)},
            {"status", "Operational"}
        };
    }
};
