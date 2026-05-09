#!/usr/bin/awk -f

# Omni Log Parser (Awk)
# Operations Layer
# Extremely fast text-processing script for aggregating latency metrics 
# from raw Omni Nginx/gRPC logs on the fly, without heavy dependencies.
# Usage: cat omni_grpc.log | ./omni_awk_log_parser.awk

BEGIN {
    FS = " "
    total_requests = 0
    total_latency = 0
    max_latency = 0
    print "Omni Log Parser: Initiating fast metric extraction..."
}

{
    # Assuming log format: IP - [Time] "Request" STATUS BYTES LATENCY
    # Example: 10.0.0.1 - [10/Oct/2026:13:55:36] "POST /generate" 200 1024 45.2
    
    latency = $9  # 9th field is latency in ms
    status = $6   # 6th field is HTTP/gRPC status
    
    if (status == "200") {
        total_requests++
        total_latency += latency
        
        if (latency > max_latency) {
            max_latency = latency
        }
    } else {
        error_count++
    }
}

END {
    if (total_requests > 0) {
        avg_latency = total_latency / total_requests
        print "--------------------------------------"
        print "Total Successful Requests: " total_requests
        print "Total Errors: " error_count
        printf "Average Latency: %.2f ms\n", avg_latency
        printf "Max Latency Spike: %.2f ms\n", max_latency
        print "--------------------------------------"
    } else {
        print "No valid requests found in log."
    }
}
