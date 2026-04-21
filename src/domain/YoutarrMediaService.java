// ===========================================================================
// OMNI DOMAIN LAYER — YOUTARR MEDIA DOWNLOAD SERVICE
// ===========================================================================
// Source Paradigm : Youtarr media management / youtube-dl ecosystem
// Domain Layer   : Domain (Enterprise backend, media lifecycle)
// Language        : Java
// Function        : Media download service with playlist resolution, quality
//                   selection, metadata extraction, download queue management,
//                   and library organization with tag-based cataloging
// ===========================================================================

package domain;

import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

public class YoutarrMediaService {

    // ---- Enums ----------------------------------------------------------------

    public enum MediaType { VIDEO, AUDIO, PLAYLIST, CHANNEL }
    public enum Quality { BEST, HIGH_1080P, MEDIUM_720P, LOW_480P, AUDIO_ONLY }
    public enum DownloadState { QUEUED, DOWNLOADING, CONVERTING, COMPLETE, FAILED }

    // ---- Data Models ----------------------------------------------------------

    public static class MediaMetadata {
        public final String id;
        public final String title;
        public final String uploader;
        public final MediaType type;
        public final int durationSeconds;
        public final long viewCount;
        public final String thumbnailUrl;
        public final List<String> tags;
        public final Instant publishedAt;

        public MediaMetadata(String id, String title, String uploader,
                             MediaType type, int duration, long views,
                             String thumbnail, List<String> tags, Instant published) {
            this.id = id;
            this.title = title;
            this.uploader = uploader;
            this.type = type;
            this.durationSeconds = duration;
            this.viewCount = views;
            this.thumbnailUrl = thumbnail;
            this.tags = Collections.unmodifiableList(tags);
            this.publishedAt = published;
        }

        public String formattedDuration() {
            int h = durationSeconds / 3600;
            int m = (durationSeconds % 3600) / 60;
            int s = durationSeconds % 60;
            return h > 0 ? String.format("%d:%02d:%02d", h, m, s) : String.format("%d:%02d", m, s);
        }
    }

    public static class DownloadJob {
        public final String jobId;
        public final MediaMetadata metadata;
        public final Quality quality;
        public DownloadState state;
        public double progressPercent;
        public String outputPath;
        public String error;
        public int retryCount;
        public final Instant createdAt;
        public Instant completedAt;

        public DownloadJob(MediaMetadata metadata, Quality quality) {
            this.jobId = "job-" + UUID.randomUUID().toString().substring(0, 8);
            this.metadata = metadata;
            this.quality = quality;
            this.state = DownloadState.QUEUED;
            this.progressPercent = 0.0;
            this.retryCount = 0;
            this.createdAt = Instant.now();
        }
    }

    // ---- Library Catalog ------------------------------------------------------

    public static class MediaLibrary {
        private final Map<String, MediaMetadata> catalog = new LinkedHashMap<>();
        private final Map<String, Set<String>> tagIndex = new HashMap<>();

        public void addEntry(MediaMetadata meta) {
            catalog.put(meta.id, meta);
            for (String tag : meta.tags) {
                tagIndex.computeIfAbsent(tag.toLowerCase(), k -> new HashSet<>()).add(meta.id);
            }
            System.out.printf("[YOUTARR-OMNI-JAVA] Cataloged: %s (%s)%n", meta.title, meta.type);
        }

        public List<MediaMetadata> searchByTag(String tag) {
            Set<String> ids = tagIndex.getOrDefault(tag.toLowerCase(), Collections.emptySet());
            return ids.stream().map(catalog::get).collect(Collectors.toList());
        }

        public List<MediaMetadata> searchByTitle(String query) {
            String q = query.toLowerCase();
            return catalog.values().stream()
                    .filter(m -> m.title.toLowerCase().contains(q))
                    .collect(Collectors.toList());
        }

        public List<MediaMetadata> getByUploader(String uploader) {
            return catalog.values().stream()
                    .filter(m -> m.uploader.equalsIgnoreCase(uploader))
                    .collect(Collectors.toList());
        }

        public int size() { return catalog.size(); }
        public Set<String> allTags() { return tagIndex.keySet(); }
    }

    // ---- Download Queue Manager -----------------------------------------------

    private static final int MAX_RETRIES = 3;
    private final Queue<DownloadJob> queue = new LinkedList<>();
    private final List<DownloadJob> history = new ArrayList<>();
    private final MediaLibrary library = new MediaLibrary();

    public YoutarrMediaService() {
        System.out.println("[YOUTARR-OMNI-JAVA] Media service initialized.");
    }

    public DownloadJob enqueue(MediaMetadata metadata, Quality quality) {
        DownloadJob job = new DownloadJob(metadata, quality);
        queue.add(job);
        System.out.printf("[YOUTARR-OMNI-JAVA] Enqueued: %s (%s, %s)%n",
                metadata.title, quality, job.jobId);
        return job;
    }

    public List<DownloadJob> processQueue() {
        System.out.printf("[YOUTARR-OMNI-JAVA] Processing queue: %d job(s)%n", queue.size());
        List<DownloadJob> results = new ArrayList<>();

        while (!queue.isEmpty()) {
            DownloadJob job = queue.poll();
            processJob(job);
            results.add(job);
            history.add(job);

            if (job.state == DownloadState.COMPLETE) {
                library.addEntry(job.metadata);
            }
        }

        long completed = results.stream().filter(j -> j.state == DownloadState.COMPLETE).count();
        System.out.printf("[YOUTARR-OMNI-JAVA] Queue complete: %d/%d succeeded%n",
                completed, results.size());
        return results;
    }

    private void processJob(DownloadJob job) {
        System.out.printf("[YOUTARR-OMNI-JAVA]   Processing: %s%n", job.metadata.title);
        job.state = DownloadState.DOWNLOADING;

        // Production: spawn yt-dlp subprocess with quality args
        String qualityArg = switch (job.quality) {
            case BEST -> "bestvideo+bestaudio/best";
            case HIGH_1080P -> "bestvideo[height<=1080]+bestaudio/best[height<=1080]";
            case MEDIUM_720P -> "bestvideo[height<=720]+bestaudio/best[height<=720]";
            case LOW_480P -> "bestvideo[height<=480]+bestaudio/best[height<=480]";
            case AUDIO_ONLY -> "bestaudio";
        };

        job.progressPercent = 100.0;
        job.state = DownloadState.COMPLETE;
        job.outputPath = "/media/downloads/" + job.metadata.id + ".mp4";
        job.completedAt = Instant.now();

        System.out.printf("[YOUTARR-OMNI-JAVA]   ✓ Complete: %s → %s%n", job.jobId, job.outputPath);
    }

    public MediaLibrary getLibrary() { return library; }
}
