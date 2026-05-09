# omni_command_parser.rb — Omni CLI Command Parser
# Layer: Interface / Ruby
#
# A robust, dependency-free command-line argument parser for the Omni CLI.
# Supports subcommands, flags, typed arguments, and automatic help generation.
# Zero-mock implementation.

module Omni
  class CommandParser
    class ParseError < StandardError; end

    attr_reader :name, :description, :options, :subcommands

    def initialize(name, description)
      @name = name
      @description = description
      @options = []
      @subcommands = {}
    end

    # Registers a boolean or value-based flag
    def add_option(name, short:, description:, type: :boolean, required: false)
      @options << {
        name: name,
        short: short,
        description: description,
        type: type,
        required: required
      }
    end

    # Registers a nested subcommand
    def add_subcommand(parser)
      @subcommands[parser.name] = parser
    end

    # Parses ARGV into a structured hash
    def parse(argv)
      result = { command: @name, options: {}, arguments: [] }
      args = argv.dup

      if args.first && @subcommands.key?(args.first)
        subcommand_name = args.shift
        return @subcommands[subcommand_name].parse(args)
      end

      while args.any?
        arg = args.shift

        if arg.start_with?('--')
          process_long_option(arg, args, result[:options])
        elsif arg.start_with?('-')
          process_short_option(arg, args, result[:options])
        else
          result[:arguments] << arg
        end
      end

      validate_required_options!(result[:options])
      result
    end

    def generate_help
      output = "Usage: #{@name} [options] [arguments]\n"
      output += "#{@description}\n\n"
      
      if @subcommands.any?
        output += "Subcommands:\n"
        @subcommands.each do |sub_name, sub_parser|
          output += "  #{sub_name.ljust(15)} #{sub_parser.description}\n"
        end
        output += "\n"
      end

      if @options.any?
        output += "Options:\n"
        @options.each do |opt|
          req_str = opt[:required] ? "(required)" : ""
          output += "  -#{opt[:short]}, --#{opt[:name].ljust(10)} #{opt[:description]} #{req_str}\n"
        end
      end

      output
    end

    private

    def process_long_option(arg, args, parsed_options)
      opt_name = arg.sub('--', '')
      option = @options.find { |o| o[:name] == opt_name }
      raise ParseError, "Unknown option: #{arg}" unless option

      assign_option_value(option, args, parsed_options)
    end

    def process_short_option(arg, args, parsed_options)
      opt_short = arg.sub('-', '')
      option = @options.find { |o| o[:short] == opt_short }
      raise ParseError, "Unknown short option: #{arg}" unless option

      assign_option_value(option, args, parsed_options)
    end

    def assign_option_value(option, args, parsed_options)
      if option[:type] == :boolean
        parsed_options[option[:name].to_sym] = true
      elsif option[:type] == :string
        raise ParseError, "Missing value for option: #{option[:name]}" if args.empty? || args.first.start_with?('-')
        parsed_options[option[:name].to_sym] = args.shift
      end
    end

    def validate_required_options!(parsed_options)
      @options.each do |opt|
        if opt[:required] && !parsed_options.key?(opt[:name].to_sym)
          raise ParseError, "Missing required option: --#{opt[:name]}"
        end
      end
    end
  end
end
