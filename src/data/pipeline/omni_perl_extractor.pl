#!/usr/bin/perl
use strict;
use warnings;

# Omni Regex Extractor (Perl)
# Data & NLP Processing Layer
# Heavy-duty unstructured text normalization and extraction.
# Cleans vast corpora of text before passing to the tokenizer.

sub normalize_corpus {
    my ($text_ref) = @_;
    
    # 1. Remove HTML tags
    $$text_ref =~ s/<[^>]*>//g;
    
    # 2. Normalize whitespace (convert tabs/newlines to single space)
    $$text_ref =~ s/\s+/ /g;
    
    # 3. Strip non-ASCII characters
    $$text_ref =~ s/[^\x00-\x7F]//g;
    
    # 4. Collapse repeating punctuation (e.g., "!!!" -> "!")
    $$text_ref =~ s/([.!?])\1+/$1/g;
    
    # 5. Extract URLs into a token placeholder
    $$text_ref =~ s/https?:\/\/[^\s]+/[URL]/g;
    
    return $$text_ref;
}

# Example extraction of email addresses as a structural metadata step
sub extract_emails {
    my ($text) = @_;
    my @emails = ();
    
    while ($text =~ /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g) {
        push @emails, $1;
    }
    
    return \@emails;
}

# Omni Standard Execution Interface
my $sample_text = "Check out my code at https://github.com/omni !! Email me: dev@omni.nexus. <html><body>Bad formatting.</body></html>   \t\n   ";
my $normalized = normalize_corpus(\$sample_text);
my $emails_ref = extract_emails($sample_text);

print "Normalized: $normalized\n";
print "Extracted Emails: ", join(", ", @$emails_ref), "\n";
