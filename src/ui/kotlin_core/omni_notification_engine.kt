// ===========================================================================
// OMNI NOTIFICATION ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : Android NotificationCompat + Firebase Messaging concepts
// Logic Inherited: Kotlin / UI Layer (Channel-Based Notification Manager)
// Domain Layer   : UI Mobile (Kotlin Core)
// ===========================================================================
//
// By studying Android NotificationCompat and Firebase Cloud Messaging,
// Mother learned that production notification management requires:
//   1. Channel-based grouping (Android 8.0+ requirement)
//   2. Priority levels with do-not-disturb awareness
//   3. Notification deduplication by key
//   4. Action buttons with pending intent routing
//   5. Scheduled delivery with time-zone awareness
//
// Kotlin's sealed classes model notification variants at compile-time,
// while data classes provide immutable, copy-friendly payloads.

package dev.omni.engine.notification

import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.PriorityBlockingQueue
import java.util.concurrent.atomic.AtomicLong

// ---- Enums ----

enum class NotificationPriority(val androidImportance: Int) {
    URGENT(4),    // Heads-up notification, sound + vibration
    HIGH(3),      // Sound, shows in status bar
    DEFAULT(2),   // Sound, silently appears
    LOW(1),       // No sound, appears in shade
    MIN(0)        // No sound, no visual interruption
}

enum class NotificationStyle {
    STANDARD,     // Title + body
    BIG_TEXT,     // Expandable long text
    BIG_PICTURE,  // Large image
    INBOX,        // Multiple lines
    MESSAGING,    // Conversation history
    PROGRESS      // Progress bar
}

// ---- Sealed Class: Notification Content Variants ----

sealed class NotificationContent {
    data class Standard(
        val title: String,
        val body: String,
        val icon: String = "ic_default"
    ) : NotificationContent()

    data class BigText(
        val title: String,
        val summary: String,
        val expandedText: String,
        val icon: String = "ic_default"
    ) : NotificationContent()

    data class BigPicture(
        val title: String,
        val body: String,
        val imageUrl: String,
        val icon: String = "ic_default"
    ) : NotificationContent()

    data class Inbox(
        val title: String,
        val summary: String,
        val lines: List<String>,
        val icon: String = "ic_default"
    ) : NotificationContent()

    data class Progress(
        val title: String,
        val body: String,
        val progress: Int,       // 0-100
        val indeterminate: Boolean = false,
        val icon: String = "ic_progress"
    ) : NotificationContent()
}

// ---- Data Models ----

data class NotificationAction(
    val id: String,
    val label: String,
    val icon: String,
    val deepLink: String? = null,
    val destructive: Boolean = false
)

data class NotificationChannel(
    val id: String,
    val name: String,
    val description: String,
    val priority: NotificationPriority = NotificationPriority.DEFAULT,
    val vibrationPattern: LongArray? = null,
    val showBadge: Boolean = true,
    val soundUri: String? = null
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is NotificationChannel) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()
}

data class OmniNotification(
    val id: Long,
    val channelId: String,
    val content: NotificationContent,
    val priority: NotificationPriority = NotificationPriority.DEFAULT,
    val actions: List<NotificationAction> = emptyList(),
    val groupKey: String? = null,
    val deduplicationKey: String? = null,
    val scheduledAt: ZonedDateTime? = null,
    val autoCancel: Boolean = true,
    val tags: Set<String> = emptySet(),
    val createdAt: Instant = Instant.now(),
    val metadata: Map<String, String> = emptyMap()
) : Comparable<OmniNotification> {
    // Higher priority = earlier in queue
    override fun compareTo(other: OmniNotification): Int =
        other.priority.androidImportance.compareTo(this.priority.androidImportance)
}

data class DeliveryRecord(
    val notificationId: Long,
    val channelId: String,
    val priority: NotificationPriority,
    val deliveredAt: Instant,
    val contentType: String,
    val wasGrouped: Boolean
)

// ---- Listener Interface ----

interface NotificationListener {
    fun onNotificationPosted(notification: OmniNotification)
    fun onNotificationCancelled(notificationId: Long)
    fun onActionClicked(notificationId: Long, actionId: String)
}

// ---- Core Engine ----

class OmniNotificationEngine(
    private val defaultTimeZone: ZoneId = ZoneId.systemDefault()
) {
    private val idGenerator = AtomicLong(1000)
    private val channels = ConcurrentHashMap<String, NotificationChannel>()
    private val activeNotifications = ConcurrentHashMap<Long, OmniNotification>()
    private val deliveryHistory = CopyOnWriteArrayList<DeliveryRecord>()
    private val deduplicationCache = ConcurrentHashMap<String, Long>() // dedupKey → notifId
    private val scheduledQueue = PriorityBlockingQueue<OmniNotification>()
    private val listeners = CopyOnWriteArrayList<NotificationListener>()
    private val stats = NotificationStats()

    // ---- Channel Management ----

    /**
     * Register a notification channel. Required before posting notifications.
     */
    fun createChannel(channel: NotificationChannel) {
        channels[channel.id] = channel
    }

    fun deleteChannel(channelId: String) {
        channels.remove(channelId)
        // Cancel all notifications in this channel
        activeNotifications.values
            .filter { it.channelId == channelId }
            .forEach { cancel(it.id) }
    }

    fun getChannel(channelId: String): NotificationChannel? = channels[channelId]

    fun getAllChannels(): List<NotificationChannel> = channels.values.toList()

    // ---- Notification Posting ----

    /**
     * Post a notification immediately or schedule it for later delivery.
     */
    fun post(notification: OmniNotification): Long {
        val id = if (notification.id == 0L) idGenerator.incrementAndGet() else notification.id
        val notif = notification.copy(id = id)

        // Deduplication check
        notif.deduplicationKey?.let { key ->
            deduplicationCache[key]?.let { existingId ->
                // Cancel existing, replace with new
                cancel(existingId)
            }
            deduplicationCache[key] = id
        }

        // Validate channel exists
        val channel = channels[notif.channelId]
        if (channel == null) {
            stats.totalRejected.incrementAndGet()
            return -1
        }

        // Schedule or deliver immediately
        notif.scheduledAt?.let { scheduledTime ->
            if (scheduledTime.toInstant().isAfter(Instant.now())) {
                scheduledQueue.add(notif)
                stats.totalScheduled.incrementAndGet()
                return id
            }
        }

        return deliver(notif, channel)
    }

    /**
     * Build and post a notification using a builder-style API.
     */
    fun postSimple(
        channelId: String,
        title: String,
        body: String,
        priority: NotificationPriority = NotificationPriority.DEFAULT,
        groupKey: String? = null
    ): Long {
        val notif = OmniNotification(
            id = idGenerator.incrementAndGet(),
            channelId = channelId,
            content = NotificationContent.Standard(title, body),
            priority = priority,
            groupKey = groupKey
        )
        return post(notif)
    }

    /**
     * Post a progress notification (for downloads, uploads, etc.)
     */
    fun postProgress(
        channelId: String,
        title: String,
        body: String,
        progress: Int,
        notificationId: Long? = null
    ): Long {
        val id = notificationId ?: idGenerator.incrementAndGet()
        val notif = OmniNotification(
            id = id,
            channelId = channelId,
            content = NotificationContent.Progress(title, body, progress.coerceIn(0, 100)),
            priority = NotificationPriority.LOW,
            autoCancel = false
        )
        return post(notif)
    }

    // ---- Internal Delivery ----

    private fun deliver(notif: OmniNotification, channel: NotificationChannel): Long {
        activeNotifications[notif.id] = notif
        stats.totalDelivered.incrementAndGet()

        // Record delivery
        val contentType = when (notif.content) {
            is NotificationContent.Standard -> "standard"
            is NotificationContent.BigText -> "big_text"
            is NotificationContent.BigPicture -> "big_picture"
            is NotificationContent.Inbox -> "inbox"
            is NotificationContent.Progress -> "progress"
        }

        deliveryHistory.add(
            DeliveryRecord(
                notificationId = notif.id,
                channelId = notif.channelId,
                priority = notif.priority,
                deliveredAt = Instant.now(),
                contentType = contentType,
                wasGrouped = notif.groupKey != null
            )
        )

        // Notify listeners
        listeners.forEach { it.onNotificationPosted(notif) }

        return notif.id
    }

    // ---- Cancellation ----

    fun cancel(notificationId: Long) {
        activeNotifications.remove(notificationId)?.let {
            stats.totalCancelled.incrementAndGet()
            listeners.forEach { l -> l.onNotificationCancelled(notificationId) }
        }
    }

    fun cancelByGroup(groupKey: String) {
        activeNotifications.values
            .filter { it.groupKey == groupKey }
            .forEach { cancel(it.id) }
    }

    fun cancelByTag(tag: String) {
        activeNotifications.values
            .filter { tag in it.tags }
            .forEach { cancel(it.id) }
    }

    fun cancelAll() {
        val ids = activeNotifications.keys().toList()
        ids.forEach { cancel(it) }
    }

    // ---- Action Handling ----

    fun handleAction(notificationId: Long, actionId: String) {
        stats.totalActionsClicked.incrementAndGet()
        listeners.forEach { it.onActionClicked(notificationId, actionId) }

        // Auto-cancel if configured
        activeNotifications[notificationId]?.let {
            if (it.autoCancel) cancel(notificationId)
        }
    }

    // ---- Scheduled Notification Processing ----

    /**
     * Process scheduled notifications that are due.
     * Call this periodically (e.g., from AlarmManager or WorkManager).
     */
    fun processScheduledQueue(): Int {
        var delivered = 0
        val now = Instant.now()

        val iterator = scheduledQueue.iterator()
        while (iterator.hasNext()) {
            val notif = iterator.next()
            if (notif.scheduledAt != null && notif.scheduledAt.toInstant().isBefore(now)) {
                iterator.remove()
                val channel = channels[notif.channelId]
                if (channel != null) {
                    deliver(notif, channel)
                    delivered++
                }
            }
        }
        return delivered
    }

    // ---- Listener Management ----

    fun addListener(listener: NotificationListener) {
        listeners.add(listener)
    }

    fun removeListener(listener: NotificationListener) {
        listeners.remove(listener)
    }

    // ---- Query ----

    fun getActiveCount(): Int = activeNotifications.size
    fun getScheduledCount(): Int = scheduledQueue.size

    fun getActiveByChannel(channelId: String): List<OmniNotification> =
        activeNotifications.values.filter { it.channelId == channelId }

    fun getRecentHistory(limit: Int = 50): List<DeliveryRecord> =
        deliveryHistory.takeLast(limit)

    // ---- Diagnostics ----

    fun diagnostics(): Map<String, Any> = mapOf(
        "engine" to "OmniNotificationEngine",
        "layer" to "Kotlin UI Mobile",
        "channels_registered" to channels.size,
        "active_notifications" to activeNotifications.size,
        "scheduled_pending" to scheduledQueue.size,
        "dedup_cache_size" to deduplicationCache.size,
        "total_delivered" to stats.totalDelivered.get(),
        "total_cancelled" to stats.totalCancelled.get(),
        "total_scheduled" to stats.totalScheduled.get(),
        "total_rejected" to stats.totalRejected.get(),
        "total_actions_clicked" to stats.totalActionsClicked.get(),
        "delivery_history_size" to deliveryHistory.size,
        "listener_count" to listeners.size,
        "timezone" to defaultTimeZone.id,
        "learned_logic" to listOf(
            "sealed-class-content-variants",
            "notification-channel-android-8",
            "deduplication-key-replace",
            "priority-blocking-queue-scheduling",
            "copy-on-write-listener-safety",
            "concurrent-hashmap-active-tracking",
            "builder-style-posting-api"
        )
    )
}

// ---- Stats ----

internal class NotificationStats {
    val totalDelivered = AtomicLong(0)
    val totalCancelled = AtomicLong(0)
    val totalScheduled = AtomicLong(0)
    val totalRejected = AtomicLong(0)
    val totalActionsClicked = AtomicLong(0)
}
