# ===========================================================================
# OMNI DOMAIN LAYER — AUTO ANIME MEDIA ORGANIZER
# ===========================================================================
# Source Paradigm : AutoAnimeMV-Teams/AutoAnimeMv
# Domain Layer   : Domain (Convention-over-configuration, declarative DSL)
# Language        : Ruby
# Function        : Automatic anime episode recognition, renaming, and
#                   season/episode directory structuring for media servers
# ===========================================================================

module OmniDomain
  # Represents a single media file pending classification.
  MediaFile = Struct.new(:path, :original_name, :extension, :size_kb)

  # Result of the recognition pipeline.
  RecognitionResult = Struct.new(:series_title, :season, :episode, :subtitle_lang, :new_path)

  class AutoAnimeOrganizer
    # Regex bank for episode extraction (covers [sub-group], SxxExx, - 01, etc.)
    PATTERNS = [
      /S(\d{1,2})E(\d{1,3})/i,              # S01E05
      /\[(\d{1,2})\]/,                        # [05]
      /\s-\s(\d{2,3})(?:\s|\[|\.)/,           # - 05
      /Episode\s*(\d{1,3})/i,                 # Episode 5
    ].freeze

    SUBTITLE_EXTS = %w[.srt .ass .ssa .sub .vtt].freeze
    VIDEO_EXTS    = %w[.mp4 .mkv .avi .flv .webm].freeze

    def initialize(output_root:)
      @output_root = output_root
      puts "[AUTOANIME-OMNI-RB] Initializing media organizer → #{@output_root}"
    end

    # Classify a single file and return a RecognitionResult.
    def classify(file)
      puts "[AUTOANIME-OMNI-RB] Classifying: #{file.original_name}"

      episode = extract_episode(file.original_name)
      season  = extract_season(file.original_name) || 1
      title   = extract_title(file.original_name)
      sub     = SUBTITLE_EXTS.include?(file.extension) ? detect_sub_lang(file.original_name) : nil

      new_name = sub ? "E#{'%02d' % episode}.#{sub}#{file.extension}" : "E#{'%02d' % episode}#{file.extension}"
      new_path = File.join(@output_root, title, "Season#{'%02d' % season}", new_name)

      puts "[AUTOANIME-OMNI-RB]   → #{title} / Season#{season} / #{new_name}"

      RecognitionResult.new(title, season, episode, sub, new_path)
    end

    # Batch-process an array of MediaFile structs.
    def organize(files)
      puts "[AUTOANIME-OMNI-RB] Batch organizing #{files.length} file(s)..."
      files.map { |f| classify(f) }
    end

    private

    def extract_episode(name)
      PATTERNS.each do |pat|
        if (m = name.match(pat))
          return m.captures.last.to_i
        end
      end
      0
    end

    def extract_season(name)
      m = name.match(/S(\d{1,2})/i)
      m ? m[1].to_i : nil
    end

    def extract_title(name)
      # Strip common noise: [SubGroup], resolution, codec tags
      clean = name
        .gsub(/\[.*?\]/, '')
        .gsub(/\(.*?\)/, '')
        .gsub(/\d{3,4}[xX×]\d{3,4}/, '')
        .gsub(/HEVC|AVC|x264|x265|AAC|FLAC|10bit/i, '')
        .strip
      # Take everything before the first episode marker
      clean.split(/\s-\s|\sS\d/i).first&.strip || 'Unknown'
    end

    def detect_sub_lang(name)
      return 'chs' if name =~ /\.(chs|sc|chi)/i
      return 'cht' if name =~ /\.(cht|tc)/i
      return 'eng' if name =~ /\.(eng|en)/i
      'und'
    end
  end
end

# ── FFI Test Harness (commented) ──────────────────────────────────────
# org = OmniDomain::AutoAnimeOrganizer.new(output_root: '/media/anime')
# files = [
#   OmniDomain::MediaFile.new('/dl/[SubGrp] Bofuri S02 - 05 (1080p).mkv',
#                              '[SubGrp] Bofuri S02 - 05 (1080p).mkv', '.mkv', 350_000),
#   OmniDomain::MediaFile.new('/dl/[SubGrp] Bofuri S02 - 05.chs.ass',
#                              '[SubGrp] Bofuri S02 - 05.chs.ass', '.ass', 45),
# ]
# org.organize(files).each { |r| puts r.inspect }
