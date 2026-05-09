# omni_logger_terminal.rb — Formatted CLI Logger
# Layer: Interface / Ruby
#
# A structured, colorized terminal logger for Ruby CLI applications.
# Supports multiple log levels, timestamp formatting, and ANSI escape codes.

module Omni
  class TerminalLogger
    LEVELS = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
      fatal: 4
    }.freeze

    COLORS = {
      reset: "\e[0m",
      gray: "\e[90m",
      cyan: "\e[36m",
      green: "\e[32m",
      yellow: "\e[33m",
      red: "\e[31m",
      magenta: "\e[35m",
      bold: "\e[1m"
    }.freeze

    attr_accessor :min_level

    def initialize(min_level: :info)
      @min_level = LEVELS[min_level] || 1
      @mutex = Mutex.new
    end

    def debug(msg)
      log(:debug, msg, COLORS[:gray])
    end

    def info(msg)
      log(:info, msg, COLORS[:cyan])
    end

    def success(msg)
      log(:info, msg, COLORS[:green], prefix: "SUCCESS")
    end

    def warn(msg)
      log(:warn, msg, COLORS[:yellow])
    end

    def error(msg)
      log(:error, msg, COLORS[:red])
    end

    def fatal(msg)
      log(:fatal, msg, COLORS[:magenta])
      exit(1)
    end

    private

    def log(level, message, color, prefix: nil)
      level_val = LEVELS[level]
      return if level_val < @min_level

      timestamp = Time.now.strftime("%H:%M:%S.%L")
      level_str = prefix || level.to_s.upcase.ljust(5)
      
      @mutex.synchronize do
        puts "#{COLORS[:gray]}[#{timestamp}]#{COLORS[:reset]} #{color}#{COLORS[:bold]}#{level_str}#{COLORS[:reset]} #{message}"
      end
    end
  end
end
