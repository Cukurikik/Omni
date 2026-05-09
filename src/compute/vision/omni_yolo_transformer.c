#include <stdlib.h>
#include <stdio.h>
#include <math.h>

// Trolo: Transformers + YOLO Hybrid Architecture
// System Layer: Bounding Box Coordinate projection from Vision Transformer tokens

typedef struct {
    float x_center;
    float y_center;
    float width;
    float height;
    float confidence;
    int class_id;
} BoundingBox;

typedef struct {
    int num_queries;
    int embed_dim;
    float* query_embeddings;
} TroloHead;

TroloHead* create_trolo_head(int num_queries, int embed_dim) {
    TroloHead* head = (TroloHead*)malloc(sizeof(TroloHead));
    head->num_queries = num_queries;
    head->embed_dim = embed_dim;
    head->query_embeddings = (float*)calloc(num_queries * embed_dim, sizeof(float));
    return head;
}

void destroy_trolo_head(TroloHead* head) {
    if (head) {
        free(head->query_embeddings);
        free(head);
    }
}

// Sigmoid function for bounded coordinate projection
float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

// Map output transformer tokens directly to YOLO bounding boxes
void decode_predictions(TroloHead* head, const float* transformer_outputs, BoundingBox* out_boxes) {
    // In a real scenario, this involves an MLP. Here we simulate the projection matrix.
    for (int i = 0; i < head->num_queries; ++i) {
        float cx = 0.0f, cy = 0.0f, w = 0.0f, h = 0.0f, conf = 0.0f;
        int base_idx = i * head->embed_dim;
        
        // Simulating linear projection weights
        for (int j = 0; j < head->embed_dim; ++j) {
            float val = transformer_outputs[base_idx + j];
            cx += val * 0.1f;
            cy += val * 0.15f;
            w += val * 0.05f;
            h += val * 0.08f;
            conf += val * 0.01f;
        }
        
        out_boxes[i].x_center = sigmoid(cx);
        out_boxes[i].y_center = sigmoid(cy);
        out_boxes[i].width = expf(w);
        out_boxes[i].height = expf(h);
        out_boxes[i].confidence = sigmoid(conf);
        out_boxes[i].class_id = (i % 80); // Coco classes
    }
}
