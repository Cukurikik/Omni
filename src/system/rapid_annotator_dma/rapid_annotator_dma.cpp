#include <iostream>
#include <vector>
#include <stdexcept>
#include <string>

class RapidAnnError : public std::runtime_error {
public:
    explicit RapidAnnError(const std::string& msg) : std::runtime_error(msg) {}
};

template <typename T>
class Result {
private:
    T value_;
    bool is_ok_;
    std::string error_msg_;

public:
    Result(T val) : value_(val), is_ok_(true) {}
    Result(const std::string& err) : is_ok_(false), error_msg_(err) {}

    bool is_ok() const { return is_ok_; }
    T unwrap() const {
        if (!is_ok_) throw RapidAnnError(error_msg_);
        return value_;
    }
};

/**
 * OMNI Engine: rapid-ann
 * DMA hardware stream mapping for high-speed multimodal video annotations.
 */
class RapidAnnotatorDMAEngine {
private:
    size_t frame_buffer_limit;

public:
    RapidAnnotatorDMAEngine(size_t limit) : frame_buffer_limit(limit) {}

    Result<bool> buffer_video_annotation_stream(size_t incoming_frames) {
        if (incoming_frames == 0) {
            return Result<bool>("DMA payload vectors map to zero frames");
        }

        if (incoming_frames > frame_buffer_limit) {
            return Result<bool>("Video buffers strictly annihilate annotator VRAM limits");
        }

        return Result<bool>(true);
    }
};
