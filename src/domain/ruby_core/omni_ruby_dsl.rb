# OMNI Domain Layer: Ruby Business DSL
module Omni
  class BusinessDsl
    def define_rule(name, &block)
      yield if block_given?
    end
  end
end
