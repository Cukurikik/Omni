# OMNI Ruby Business Layer: Grobid Document Domain
# Business rules for validating and structuring scientific documents parsed by Grobid.

module Omni
  module Business
    module Grobid
      
      class DocumentValidationError < StandardError; end

      class AcademicDocument
        attr_reader :title, :authors, :abstract, :sections

        def initialize(xml_content)
          @raw_xml = xml_content
          @authors = []
          @sections = []
          parse_document!
        end

        def validate!
          raise DocumentValidationError, "Missing title" if @title.nil? || @title.empty?
          raise DocumentValidationError, "Missing abstract" if @abstract.nil? || @abstract.empty?
          raise DocumentValidationError, "No authors identified" if @authors.empty?
          true
        end

        def summarize_structure
          {
            title: @title,
            author_count: @authors.length,
            section_count: @sections.length,
            is_valid: (validate! rescue false)
          }
        end

        private

        def parse_document!
          # Zero-mock regex parsing of TEI XML (Grobid output standard format)
          @title = extract_tag_content("title")
          @abstract = extract_tag_content("abstract")
          
          # Extracting authors from <author> blocks
          @raw_xml.scan(/<author>(.*?)<\/author>/m).each do |match|
            name_block = match.first
            first = name_block[/<forename.*?>(.*?)<\/forename>/, 1]
            last = name_block[/<surname.*?>(.*?)<\/surname>/, 1]
            @authors << "#{first} #{last}".strip if first || last
          end

          # Extracting sections
          @raw_xml.scan(/<head.*?>(.*?)<\/head>/).each do |match|
            @sections << match.first
          end
        end

        def extract_tag_content(tag)
          match = @raw_xml.match(/<#{tag}.*?>(.*?)<\/#{tag}>/m)
          match ? match[1].gsub(/<[^>]+>/, '').strip : nil
        end
      end

    end
  end
end
