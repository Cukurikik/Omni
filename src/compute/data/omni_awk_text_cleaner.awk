#!/usr/bin/awk -f

# OMNI Data & Pipeline Layer
# High-speed text cleaner for the dataloader ingestion pipeline.
# AWK is chosen for its C-like performance on massive text streams before passing 
# to the Omni C++ tokenizer.

BEGIN {
    # Set field separator to tab (assuming TSV inputs like CommonCrawl dumps)
    FS = "\t"
    OFS = "\t"
    print "OMNI Dataloader: Initializing AWK text cleaning pipeline..." > "/dev/stderr"
    valid_records = 0
    dropped_records = 0
}

{
    # We assume field 3 contains the raw text content
    text = $3
    
    # 1. Remove HTML tags
    gsub(/<[^>]+>/, "", text)
    
    # 2. Strip excessive whitespace and newlines
    gsub(/[ \t\r\n]+/, " ", text)
    
    # 3. Strip non-printable ASCII characters
    gsub(/[^[:print:]]/, "", text)
    
    # 4. Filter out sequences that are too short (less than 10 words)
    words = split(text, word_array, " ")
    
    if (words > 10) {
        # Valid output: ID, Date, Cleaned Text
        print $1, $2, text
        valid_records++
    } else {
        dropped_records++
    }
}

END {
    print "OMNI Dataloader: Processing Complete." > "/dev/stderr"
    print "Valid Records:   " valid_records > "/dev/stderr"
    print "Dropped Records: " dropped_records > "/dev/stderr"
}
