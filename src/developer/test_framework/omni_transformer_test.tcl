# @omni-layer Developer | @omni-lang Tcl | @omni-batch 18 | @omni-semester 16
# @omni-description Tcl transformer model testing framework: automated
# test harness for inference accuracy, latency, and regression detection.

package provide omni_transformer_test 1.0

namespace eval ::omni::test {
    variable test_results {}
    variable pass_count 0
    variable fail_count 0
    variable total_time 0

    proc run_suite {suite_name tests} {
        variable test_results
        variable pass_count
        variable fail_count

        puts "=== OMNI Transformer Test Suite: $suite_name ==="
        set suite_start [clock microseconds]

        foreach test $tests {
            set name [dict get $test name]
            set fn [dict get $test fn]
            set expected [dict get $test expected]

            set start [clock microseconds]
            set result [eval $fn]
            set elapsed [expr {([clock microseconds] - $start) / 1000.0}]

            if {[compare_result $result $expected]} {
                puts "  PASS: $name (${elapsed}ms)"
                incr pass_count
                lappend test_results [list $name pass $elapsed]
            } else {
                puts "  FAIL: $name - expected '$expected', got '$result'"
                incr fail_count
                lappend test_results [list $name fail $elapsed]
            }
        }

        set total [expr {([clock microseconds] - $suite_start) / 1000.0}]
        puts "=== Results: $pass_count passed, $fail_count failed (${total}ms) ==="
    }

    proc compare_result {actual expected} {
        if {$actual eq $expected} { return 1 }
        if {[string is double $actual] && [string is double $expected]} {
            return [expr {abs($actual - $expected) < 0.001}]
        }
        return 0
    }

    proc assert_latency {fn max_ms} {
        set start [clock microseconds]
        eval $fn
        set elapsed [expr {([clock microseconds] - $start) / 1000.0}]
        if {$elapsed > $max_ms} {
            return "FAIL: ${elapsed}ms > ${max_ms}ms"
        }
        return "PASS"
    }

    proc assert_output_shape {output expected_len} {
        set actual [llength $output]
        if {$actual != $expected_len} {
            return "FAIL: length $actual != $expected_len"
        }
        return "PASS"
    }

    proc assert_in_range {value min_val max_val} {
        if {$value < $min_val || $value > $max_val} {
            return "FAIL: $value not in \[$min_val, $max_val\]"
        }
        return "PASS"
    }

    proc generate_test_tokens {n vocab_size} {
        set tokens {}
        for {set i 0} {$i < $n} {incr i} {
            lappend tokens [expr {int(sin($i * 0.1) * $vocab_size / 2 + $vocab_size / 2) % $vocab_size}]
        }
        return $tokens
    }

    proc benchmark {name fn iterations} {
        set times {}
        for {set i 0} {$i < $iterations} {incr i} {
            set start [clock microseconds]
            eval $fn
            lappend times [expr {([clock microseconds] - $start) / 1000.0}]
        }
        set sorted [lsort -real $times]
        set n [llength $sorted]
        set avg [expr {[::tcl::mathop::+ {*}$sorted] / double($n)}]
        set p50 [lindex $sorted [expr {$n / 2}]]
        set p95 [lindex $sorted [expr {int($n * 0.95)}]]
        puts "Benchmark '$name': avg=${avg}ms p50=${p50}ms p95=${p95}ms ($iterations iters)"
        return [list avg $avg p50 $p50 p95 $p95]
    }

    proc summary {} {
        variable pass_count
        variable fail_count
        variable test_results
        set total [expr {$pass_count + $fail_count}]
        puts "\n=== OMNI Test Summary ==="
        puts "Total: $total | Pass: $pass_count | Fail: $fail_count"
        if {$fail_count > 0} {
            puts "FAILED tests:"
            foreach r $test_results {
                lassign $r name status elapsed
                if {$status eq "fail"} { puts "  - $name" }
            }
        }
        puts "========================"
        return [expr {$fail_count == 0}]
    }
}
