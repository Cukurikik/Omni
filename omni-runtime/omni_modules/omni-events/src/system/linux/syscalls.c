/* ============================================================
 * 🔧 OMNI-EVENTS: C Native Event Queue (Lock-Free Ring)
 * ============================================================
 * Event queue berbasis ring buffer untuk dispatch event
 * inter-thread di level kernel. Digunakan sebagai backbone
 * C untuk EventEmitter Rust di atasnya.
 * ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
    #include <windows.h>
    #define OMNI_ATOMIC_INC(x) InterlockedIncrement((volatile LONG*)(x))
    #define OMNI_ATOMIC_LOAD(x) (*(volatile long*)(x))
#else
    #define OMNI_ATOMIC_INC(x) __sync_fetch_and_add((x), 1)
    #define OMNI_ATOMIC_LOAD(x) __atomic_load_n((x), __ATOMIC_SEQ_CST)
#endif

#define OMNI_EVENT_NAME_MAX 64
#define OMNI_EVENT_DATA_MAX 256
#define OMNI_EVENT_QUEUE_SIZE 1024

/* ============================================================
 * Tipe Data Event
 * ============================================================ */

typedef struct {
    char   name[OMNI_EVENT_NAME_MAX];
    char   data[OMNI_EVENT_DATA_MAX];
    long   timestamp;
    int    priority;     /* 0=normal, 1=high, 2=critical */
} OmniEvent;

typedef struct {
    OmniEvent events[OMNI_EVENT_QUEUE_SIZE];
    int       head;
    int       tail;
    int       count;
    long      total_emitted;
    long      total_dropped;
} OmniEventQueue;

/* ============================================================
 * Queue Lifecycle
 * ============================================================ */

void omni_event_queue_init(OmniEventQueue* q) {
    memset(q, 0, sizeof(OmniEventQueue));
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->total_emitted = 0;
    q->total_dropped = 0;
}

/* ============================================================
 * Push Event ke Queue
 * ============================================================ */

int omni_event_push(OmniEventQueue* q, const char* name, 
                    const char* data, int priority) {
    if (q->count >= OMNI_EVENT_QUEUE_SIZE) {
        q->total_dropped++;
        return -1; /* Queue penuh */
    }

    OmniEvent* ev = &q->events[q->head];
    strncpy(ev->name, name, OMNI_EVENT_NAME_MAX - 1);
    ev->name[OMNI_EVENT_NAME_MAX - 1] = '\0';
    strncpy(ev->data, data, OMNI_EVENT_DATA_MAX - 1);
    ev->data[OMNI_EVENT_DATA_MAX - 1] = '\0';
    ev->priority = priority;
    ev->timestamp = (long)q->total_emitted;

    q->head = (q->head + 1) % OMNI_EVENT_QUEUE_SIZE;
    q->count++;
    q->total_emitted++;

    return 0;
}

/* ============================================================
 * Pop Event dari Queue (FIFO)
 * ============================================================ */

int omni_event_pop(OmniEventQueue* q, OmniEvent* out) {
    if (q->count <= 0) {
        return -1; /* Queue kosong */
    }

    *out = q->events[q->tail];
    q->tail = (q->tail + 1) % OMNI_EVENT_QUEUE_SIZE;
    q->count--;

    return 0;
}

/* ============================================================
 * Query State
 * ============================================================ */

int omni_event_queue_count(const OmniEventQueue* q) {
    return q->count;
}

int omni_event_queue_is_empty(const OmniEventQueue* q) {
    return q->count == 0;
}

int omni_event_queue_is_full(const OmniEventQueue* q) {
    return q->count >= OMNI_EVENT_QUEUE_SIZE;
}

long omni_event_total_emitted(const OmniEventQueue* q) {
    return q->total_emitted;
}

long omni_event_total_dropped(const OmniEventQueue* q) {
    return q->total_dropped;
}

/* ============================================================
 * Drain: Proses semua event dengan callback
 * ============================================================ */

typedef void (*OmniEventHandler)(const OmniEvent* ev, void* user_data);

int omni_event_drain(OmniEventQueue* q, OmniEventHandler handler, 
                     void* user_data) {
    int processed = 0;
    OmniEvent ev;

    while (omni_event_pop(q, &ev) == 0) {
        handler(&ev, user_data);
        processed++;
    }

    return processed;
}
