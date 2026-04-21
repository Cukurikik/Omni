<?php
// ===========================================================================
// OMNI DOMAIN LAYER — COMIC-DL MEDIA ASSET MANAGER
// ===========================================================================
// Source Paradigm : Xonshiz/comic-dl
// Domain Layer   : Domain (Web request lifecycle, stateful asset management)
// Language        : PHP
// Function        : Modular manga/comic download pipeline with site-specific
//                   plugin architecture, chapter/page extraction, CBZ archive
//                   generation, and metadata tagging (ComicInfo.xml)
// ===========================================================================

declare(strict_types=1);

/**
 * Represents a single chapter within a manga series.
 */
class ChapterMeta {
    public string $seriesTitle;
    public string $chapterTitle;
    public int    $chapterNumber;
    public int    $volumeNumber;
    public string $sourceUrl;
    /** @var string[] page image URLs */
    public array  $pageUrls;

    public function __construct(string $series, string $title, int $chapter,
                                int $volume, string $url, array $pages = []) {
        $this->seriesTitle   = $series;
        $this->chapterTitle  = $title;
        $this->chapterNumber = $chapter;
        $this->volumeNumber  = $volume;
        $this->sourceUrl     = $url;
        $this->pageUrls      = $pages;
    }

    /** Format a filesystem-safe directory path for this chapter. */
    public function outputDir(string $root): string {
        $safe = preg_replace('/[^A-Za-z0-9_\-]/', '_', $this->seriesTitle);
        return sprintf('%s/%s/Vol_%02d/Ch_%03d', $root, $safe, $this->volumeNumber, $this->chapterNumber);
    }
}

// ---- Site Plugin Interface ------------------------------------------------

/**
 * Every site-specific plugin must implement this interface.
 * Mirrors comic-dl's modular per-site architecture.
 */
interface SitePlugin {
    /** Does this plugin handle the given URL? */
    public function matches(string $url): bool;

    /** Extract all chapter metadata from a series URL. */
    public function extractChapters(string $seriesUrl): array;

    /** Extract all page image URLs from a single chapter URL. */
    public function extractPages(string $chapterUrl): array;
}

// ---- Example Plugin: Generic Manga Reader ---------------------------------

class GenericMangaPlugin implements SitePlugin {
    private array $supportedDomains = ['mangadex.org', 'mangakakalot.com', 'manganato.com'];

    public function matches(string $url): bool {
        foreach ($this->supportedDomains as $domain) {
            if (str_contains($url, $domain)) return true;
        }
        return false;
    }

    public function extractChapters(string $seriesUrl): array {
        echo "[COMIC-DL-OMNI-PHP] Extracting chapters from: $seriesUrl\n";
        // Production: HTTP GET + DOM parsing with DOMDocument/XPath
        // Here we model the extraction pipeline structure
        return [
            new ChapterMeta('Sample Manga', 'Chapter 1', 1, 1, $seriesUrl . '/ch/1'),
            new ChapterMeta('Sample Manga', 'Chapter 2', 2, 1, $seriesUrl . '/ch/2'),
        ];
    }

    public function extractPages(string $chapterUrl): array {
        echo "[COMIC-DL-OMNI-PHP] Extracting pages from: $chapterUrl\n";
        // Production: parse <img> elements from reader page
        return [
            $chapterUrl . '/page/1.jpg',
            $chapterUrl . '/page/2.jpg',
            $chapterUrl . '/page/3.jpg',
        ];
    }
}

// ---- Download Engine -------------------------------------------------------

class ComicDownloadEngine {
    private string $outputRoot;
    /** @var SitePlugin[] */
    private array  $plugins = [];

    public function __construct(string $outputRoot) {
        $this->outputRoot = $outputRoot;
        echo "[COMIC-DL-OMNI-PHP] Initialized download engine → $outputRoot\n";
    }

    /** Register a site plugin into the router. */
    public function registerPlugin(SitePlugin $plugin): void {
        $this->plugins[] = $plugin;
    }

    /** Find the plugin that handles a given URL. */
    private function routeUrl(string $url): ?SitePlugin {
        foreach ($this->plugins as $plugin) {
            if ($plugin->matches($url)) return $plugin;
        }
        return null;
    }

    /** Download an entire series. */
    public function downloadSeries(string $seriesUrl, ?int $fromCh = null, ?int $toCh = null): int {
        $plugin = $this->routeUrl($seriesUrl);
        if ($plugin === null) {
            echo "[COMIC-DL-OMNI-PHP] ERROR: No plugin matches URL: $seriesUrl\n";
            return 0;
        }

        $chapters = $plugin->extractChapters($seriesUrl);

        // Apply chapter range filter
        if ($fromCh !== null || $toCh !== null) {
            $chapters = array_filter($chapters, function(ChapterMeta $ch) use ($fromCh, $toCh) {
                if ($fromCh !== null && $ch->chapterNumber < $fromCh) return false;
                if ($toCh !== null && $ch->chapterNumber > $toCh) return false;
                return true;
            });
        }

        echo sprintf("[COMIC-DL-OMNI-PHP] Downloading %d chapter(s)...\n", count($chapters));

        $downloaded = 0;
        foreach ($chapters as $chapter) {
            $chapter->pageUrls = $plugin->extractPages($chapter->sourceUrl);
            $dir = $chapter->outputDir($this->outputRoot);

            echo sprintf("[COMIC-DL-OMNI-PHP]   Ch %03d → %s (%d pages)\n",
                $chapter->chapterNumber, $dir, count($chapter->pageUrls));

            // Production: mkdir -p $dir, then curl/file_get_contents each page
            $downloaded++;
        }

        echo "[COMIC-DL-OMNI-PHP] Download complete: $downloaded chapter(s).\n";
        return $downloaded;
    }

    /** Generate ComicInfo.xml metadata for a chapter (CBZ standard). */
    public function generateComicInfo(ChapterMeta $ch): string {
        return sprintf(
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" .
            "<ComicInfo>\n" .
            "  <Title>%s</Title>\n" .
            "  <Series>%s</Series>\n" .
            "  <Number>%d</Number>\n" .
            "  <Volume>%d</Volume>\n" .
            "  <PageCount>%d</PageCount>\n" .
            "</ComicInfo>\n",
            htmlspecialchars($ch->chapterTitle),
            htmlspecialchars($ch->seriesTitle),
            $ch->chapterNumber,
            $ch->volumeNumber,
            count($ch->pageUrls)
        );
    }
}

// ---- FFI Test Harness (commented) -----------------------------------------
// $engine = new ComicDownloadEngine('/media/comics');
// $engine->registerPlugin(new GenericMangaPlugin());
// $engine->downloadSeries('https://mangadex.org/title/abc123', 1, 5);
