#!/usr/bin/awk -f
# OMNI Fast Log Aggregation and Parsing Tool

BEGIN {
    FS = " "
    print "OMNI Log Analyzer Starting..."
    total_errors = 0
    total_requests = 0
}

{
    total_requests++
    # Assuming standard Apache/Nginx format: $9 is status code
    if ($9 >= 400 && $9 < 500) {
        client_errors[$1]++
    } else if ($9 >= 500) {
        total_errors++
        server_errors[$1]++
    }
}

END {
    print "====================="
    print "Total Requests: " total_requests
    print "Total Server Errors: " total_errors
    print "--- Top 5 IPs causing Client Errors ---"
    for (ip in client_errors) {
        print ip, "->", client_errors[ip] | "sort -k3 -nr | head -n 5"
    }
}
