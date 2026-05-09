// omni_transcenter_tracker.cpp — Multiple Object Tracking
// Inspired by: TransCenter (Transformers with Dense Queries for MOT)
// Layer: System / C++
//
// Fast bounding box association and heatmap thresholding routines
// optimized for C++ tracking pipelines.

#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <tuple>

struct BoundingBox {
    float x_center;
    float y_center;
    float width;
    float height;
    float score;
    int track_id;
};

class OmniTransCenterTracker {
private:
    float iou_threshold;
    int next_track_id;
    std::vector<BoundingBox> active_tracks;

    float compute_iou(const BoundingBox& a, const BoundingBox& b) {
        float x1 = std::max(a.x_center - a.width / 2.0f, b.x_center - b.width / 2.0f);
        float y1 = std::max(a.y_center - a.height / 2.0f, b.y_center - b.height / 2.0f);
        float x2 = std::min(a.x_center + a.width / 2.0f, b.x_center + b.width / 2.0f);
        float y2 = std::min(a.y_center + a.height / 2.0f, b.y_center + b.height / 2.0f);

        if (x2 < x1 || y2 < y1) return 0.0f;

        float intersection = (x2 - x1) * (y2 - y1);
        float area_a = a.width * a.height;
        float area_b = b.width * b.height;

        return intersection / (area_a + area_b - intersection);
    }

public:
    OmniTransCenterTracker(float threshold = 0.4f) 
        : iou_threshold(threshold), next_track_id(1) {}

    // Processes dense queries from the transformer head into tracked objects
    std::vector<BoundingBox> update(const std::vector<BoundingBox>& detections) {
        if (active_tracks.empty()) {
            for (auto det : detections) {
                det.track_id = next_track_id++;
                active_tracks.push_back(det);
            }
            return active_tracks;
        }

        // Greedy matching based on center distance and IoU
        // In full TransCenter, this operates directly on heatmaps, 
        // but here we process the decoded dense bounding box queries.
        
        std::vector<bool> matched_detections(detections.size(), false);
        std::vector<bool> matched_tracks(active_tracks.size(), false);

        for (size_t t = 0; t < active_tracks.size(); ++t) {
            float best_iou = 0.0f;
            int best_det_idx = -1;

            for (size_t d = 0; d < detections.size(); ++d) {
                if (matched_detections[d]) continue;

                float iou = compute_iou(active_tracks[t], detections[d]);
                if (iou > best_iou && iou > iou_threshold) {
                    best_iou = iou;
                    best_det_idx = d;
                }
            }

            if (best_det_idx != -1) {
                // Update track
                active_tracks[t].x_center = detections[best_det_idx].x_center;
                active_tracks[t].y_center = detections[best_det_idx].y_center;
                active_tracks[t].width = detections[best_det_idx].width;
                active_tracks[t].height = detections[best_det_idx].height;
                active_tracks[t].score = detections[best_det_idx].score;
                
                matched_tracks[t] = true;
                matched_detections[best_det_idx] = true;
            }
        }

        // Remove unmatched tracks (simplified: immediate removal)
        std::vector<BoundingBox> new_tracks;
        for (size_t t = 0; t < active_tracks.size(); ++t) {
            if (matched_tracks[t]) {
                new_tracks.push_back(active_tracks[t]);
            }
        }

        // Add new tracks
        for (size_t d = 0; d < detections.size(); ++d) {
            if (!matched_detections[d]) {
                BoundingBox new_track = detections[d];
                new_track.track_id = next_track_id++;
                new_tracks.push_back(new_track);
            }
        }

        active_tracks = new_tracks;
        return active_tracks;
    }
};

// C-API Export for FFI to Python/Rust
extern "C" {
    OmniTransCenterTracker* tracker_create(float threshold) {
        return new OmniTransCenterTracker(threshold);
    }

    void tracker_destroy(OmniTransCenterTracker* tracker) {
        delete tracker;
    }

    int tracker_update(OmniTransCenterTracker* tracker, 
                       const BoundingBox* det_array, int num_det, 
                       BoundingBox* out_array, int max_out) {
        std::vector<BoundingBox> detections(det_array, det_array + num_det);
        auto tracks = tracker->update(detections);
        
        int count = std::min((int)tracks.size(), max_out);
        for (int i = 0; i < count; ++i) {
            out_array[i] = tracks[i];
        }
        return count;
    }
}
