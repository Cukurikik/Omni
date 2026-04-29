module Omni
  module NLP
    class Result
      attr_reader :data, :error

      def initialize(data: nil, error: nil)
        @data = data
        @error = error
      end

      def ok?
        @error.nil?
      end

      def unwrap
        raise "Unwrap failed: #{@error}" unless ok?
        @data
      end
    end

    class CitationMatcher
      def initialize(citation_database)
        # Citation database represents e.g., DBLP or ACL anthology entries
        # Array of hashes: [{id: "conf/acl/Vaswani17", title: "Attention is all you need", authors: ["Vaswani", ...]}, ...]
        @db = citation_database
      end

      def match_entities_to_citations(extracted_entities, raw_text_tokens)
        begin
          if extracted_entities.length != raw_text_tokens.length
            return Result.new(error: "Tokens and entities length mismatch")
          end

          # Assemble entities
          assembled_authors = []
          current_author = []

          extracted_entities.each_with_index do |tag, idx|
            if tag == "B-PER"
              assembled_authors << current_author.join(" ") unless current_author.empty?
              current_author = [raw_text_tokens[idx]]
            elsif tag == "I-PER" && !current_author.empty?
              current_author << raw_text_tokens[idx]
            else
              assembled_authors << current_author.join(" ") unless current_author.empty?
              current_author = []
            end
          end
          assembled_authors << current_author.join(" ") unless current_author.empty?
          assembled_authors.uniq!

          # Search DB based on author match
          # In production, this uses the Levenshtein FFI for fuzzy matching
          matches = @db.select do |entry|
            entry[:authors].any? { |db_author| 
              assembled_authors.any? { |ext_author| 
                db_author.downcase.include?(ext_author.downcase) || ext_author.downcase.include?(db_author.downcase)
              }
            }
          end

          Result.new(data: {
            extracted_authors: assembled_authors,
            matched_citations: matches.map { |m| m[:id] }
          })
        rescue StandardError => e
          Result.new(error: "Citation matching failed: #{e.message}")
        end
      end
    end
  end
end
