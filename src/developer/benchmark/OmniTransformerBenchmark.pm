#!/usr/bin/perl
# OmniTransformerBenchmark.pm — Transformer Benchmarking Suite
# Inspired by: MLPerf benchmarking standards
# Layer: Developer Tools / Perl
#
# Benchmark harness for OMNI transformer inference latency,
# throughput, and memory profiling with statistical reporting.

package OmniTransformerBenchmark;

use strict;
use warnings;
use Time::HiRes qw(gettimeofday tv_interval);
use POSIX qw(floor ceil);
use Cwd qw(abs_path);

our $VERSION = '1.0.0';

sub new {
    my ($class, %opts) = @_;
    my $self = bless {
        name         => $opts{name} || 'omni-benchmark',
        warmup_iters => $opts{warmup_iters} || 10,
        bench_iters  => $opts{bench_iters}  || 100,
        batch_sizes  => $opts{batch_sizes}  || [1, 4, 8, 16, 32],
        seq_lengths  => $opts{seq_lengths}  || [128, 256, 512, 1024],
        results      => [],
        output_dir   => $opts{output_dir}   || './benchmark_results',
    }, $class;
    return $self;
}

sub run_benchmark {
    my ($self, $model_cmd, %opts) = @_;
    my $batch_sizes = $opts{batch_sizes} || $self->{batch_sizes};
    my $seq_lengths = $opts{seq_lengths} || $self->{seq_lengths};

    print "=" x 60, "\n";
    print "OMNI Transformer Benchmark: $self->{name}\n";
    print "=" x 60, "\n";
    print "Warmup iterations: $self->{warmup_iters}\n";
    print "Benchmark iterations: $self->{bench_iters}\n";
    print "-" x 60, "\n\n";

    for my $batch (@$batch_sizes) {
        for my $seq (@$seq_lengths) {
            my $result = $self->_run_single($model_cmd, $batch, $seq);
            push @{$self->{results}}, $result;
            $self->_print_result($result);
        }
    }

    $self->_print_summary();
    return $self->{results};
}

sub _run_single {
    my ($self, $cmd, $batch_size, $seq_len) = @_;

    # Warmup phase
    for (1..$self->{warmup_iters}) {
        my $full_cmd = "$cmd --batch-size=$batch_size --seq-len=$seq_len --quiet 2>/dev/null";
        system($full_cmd);
    }

    # Benchmark phase
    my @latencies;
    for (1..$self->{bench_iters}) {
        my $t0 = [gettimeofday()];
        my $full_cmd = "$cmd --batch-size=$batch_size --seq-len=$seq_len --quiet 2>/dev/null";
        system($full_cmd);
        my $elapsed = tv_interval($t0) * 1000; # ms
        push @latencies, $elapsed;
    }

    return $self->_compute_stats($batch_size, $seq_len, \@latencies);
}

sub _compute_stats {
    my ($self, $batch_size, $seq_len, $latencies) = @_;
    my @sorted = sort { $a <=> $b } @$latencies;
    my $n = scalar @sorted;

    my $sum = 0;
    $sum += $_ for @sorted;
    my $mean = $sum / $n;

    my $var_sum = 0;
    $var_sum += ($_ - $mean) ** 2 for @sorted;
    my $std = sqrt($var_sum / ($n - 1));

    my $p50 = $sorted[floor($n * 0.50)];
    my $p95 = $sorted[floor($n * 0.95)];
    my $p99 = $sorted[floor($n * 0.99)];
    my $min = $sorted[0];
    my $max = $sorted[-1];

    my $throughput = ($batch_size * 1000.0) / $mean; # samples/sec

    return {
        batch_size => $batch_size,
        seq_len    => $seq_len,
        iterations => $n,
        mean_ms    => sprintf("%.3f", $mean),
        std_ms     => sprintf("%.3f", $std),
        min_ms     => sprintf("%.3f", $min),
        max_ms     => sprintf("%.3f", $max),
        p50_ms     => sprintf("%.3f", $p50),
        p95_ms     => sprintf("%.3f", $p95),
        p99_ms     => sprintf("%.3f", $p99),
        throughput => sprintf("%.1f", $throughput),
    };
}

sub _print_result {
    my ($self, $r) = @_;
    printf "BS=%-4d SEQ=%-6d | mean=%-8s p50=%-8s p95=%-8s p99=%-8s | %.1f samples/s\n",
        $r->{batch_size}, $r->{seq_len},
        $r->{mean_ms}, $r->{p50_ms}, $r->{p95_ms}, $r->{p99_ms},
        $r->{throughput};
}

sub _print_summary {
    my ($self) = @_;
    print "\n", "=" x 60, "\n";
    print "BENCHMARK SUMMARY\n";
    print "=" x 60, "\n";

    printf "%-6s %-8s %-10s %-10s %-10s %-12s\n",
        "Batch", "SeqLen", "Mean(ms)", "P95(ms)", "P99(ms)", "Throughput";
    print "-" x 60, "\n";

    for my $r (@{$self->{results}}) {
        printf "%-6d %-8d %-10s %-10s %-10s %-12s\n",
            $r->{batch_size}, $r->{seq_len},
            $r->{mean_ms}, $r->{p95_ms}, $r->{p99_ms},
            "$r->{throughput} s/s";
    }

    # Find best configuration
    my $best = (sort { $b->{throughput} <=> $a->{throughput} } @{$self->{results}})[0];
    if ($best) {
        print "\nBest throughput: BS=$best->{batch_size} SEQ=$best->{seq_len} ",
              "-> $best->{throughput} samples/s (p99=$best->{p99_ms}ms)\n";
    }
}

sub export_csv {
    my ($self, $filename) = @_;
    $filename ||= "$self->{output_dir}/benchmark_results.csv";

    # Ensure directory exists
    my $dir = $filename;
    $dir =~ s|/[^/]*$||;
    mkdir $dir unless -d $dir;

    open my $fh, '>', $filename or die "Cannot write $filename: $!";
    print $fh "batch_size,seq_len,iterations,mean_ms,std_ms,min_ms,max_ms,p50_ms,p95_ms,p99_ms,throughput\n";

    for my $r (@{$self->{results}}) {
        print $fh join(',',
            $r->{batch_size}, $r->{seq_len}, $r->{iterations},
            $r->{mean_ms}, $r->{std_ms}, $r->{min_ms}, $r->{max_ms},
            $r->{p50_ms}, $r->{p95_ms}, $r->{p99_ms}, $r->{throughput}
        ), "\n";
    }

    close $fh;
    print "Results exported to: $filename\n";
}

sub export_json {
    my ($self, $filename) = @_;
    $filename ||= "$self->{output_dir}/benchmark_results.json";

    my $dir = $filename;
    $dir =~ s|/[^/]*$||;
    mkdir $dir unless -d $dir;

    open my $fh, '>', $filename or die "Cannot write $filename: $!";
    print $fh "[\n";

    for my $i (0..$#{$self->{results}}) {
        my $r = $self->{results}[$i];
        print $fh "  {\n";
        for my $key (sort keys %$r) {
            my $val = $r->{$key};
            if ($val =~ /^\d+\.?\d*$/) {
                print $fh "    \"$key\": $val";
            } else {
                print $fh "    \"$key\": \"$val\"";
            }
            print $fh "," unless $key eq (sort keys %$r)[-1];
            print $fh "\n";
        }
        print $fh "  }";
        print $fh "," unless $i == $#{$self->{results}};
        print $fh "\n";
    }

    print $fh "]\n";
    close $fh;
    print "Results exported to: $filename\n";
}

1;

__END__

=head1 NAME

OmniTransformerBenchmark - Benchmarking suite for OMNI transformer models

=head1 SYNOPSIS

    use OmniTransformerBenchmark;

    my $bench = OmniTransformerBenchmark->new(
        name         => 'soundstorm-conformer',
        warmup_iters => 10,
        bench_iters  => 100,
    );

    $bench->run_benchmark('python inference.py');
    $bench->export_csv();
    $bench->export_json();

=cut
