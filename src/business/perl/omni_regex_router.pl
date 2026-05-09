#!/usr/bin/perl
use strict;
use warnings;

# OMNI Legacy Perl API Router
# Uses ultra-fast PCRE to route incoming payload strings

my $request_uri = $ARGV[0] || "/api/v1/status";

print "OMNI Perl Router parsing: $request_uri\n";

if ($request_uri =~ m{^/api/v1/infer/([a-zA-Z0-9_-]+)$}) {
    my $model_id = $1;
    print "Matched Inference Route. Model ID: $model_id\n";
    # Dispatch to C++ backend
} elsif ($request_uri =~ m{^/api/v1/train/([a-zA-Z0-9_-]+)$}) {
    my $job_id = $1;
    print "Matched Training Route. Job ID: $job_id\n";
    # Dispatch to Python Airflow DAG
} elsif ($request_uri =~ m{^/api/v1/status$}) {
    print "Matched Status Route.\n";
} else {
    print "404 Route Not Found.\n";
}
