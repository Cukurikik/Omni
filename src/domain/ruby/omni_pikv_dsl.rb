# OMNI MOTHER: Ruby DSL for PiKV configuration

module OmniPiKV
  class Config
    def self.setup(&block)
      config = new
      config.instance_eval(&block)
      config
    end

    def block_size(size)
      @block_size = size
    end

    def max_memory_gb(gb)
      @max_memory_gb = gb
    end
  end
end
