"# OMNI Domain Layer - MedQA Medical Entities\
module Omni\
  module Domain\
    module MedQA\
      class EntityError < StandardError; end\
\
      class Result\
        attr_reader :value, :error\
        \
        def initialize(value: nil, error: nil)\
<truncated 462 bytes>