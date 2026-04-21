# ===========================================================================
# OMNI METAPROGRAMMING ENGINE (SEMESTER 3 — BATCH 38.10)
# ===========================================================================
# Absorbed From  : Ruby metaprogramming + ActiveSupport + dry-rb + rom-rb
# Logic Inherited: Ruby / Domain Layer (Dynamic Metaprogramming & DSL)
# ===========================================================================
#
# By studying Ruby metaprogramming, Mother learned:
#   1. define_method: create methods at runtime
#   2. method_missing: catch undefined method calls
#   3. class_eval/instance_eval: evaluate code in class/instance context
#   4. Open classes: reopen and extend any class
#   5. Mixins via include/extend/prepend for composition

module Omni
  module Domain
    module Ruby

      # ============================================================
      # PART 1: Attribute DSL (ActiveModel-inspired)
      # ============================================================

      module AttributeDSL
        def self.included(base)
          base.extend(ClassMethods)
          base.instance_variable_set(:@attributes, {})
          base.instance_variable_set(:@validations, [])
          base.instance_variable_set(:@callbacks, { before_save: [], after_save: [] })
        end

        module ClassMethods
          # Define a typed attribute with optional default.
          def attribute(name, type: :string, default: nil, required: false)
            @attributes[name] = {
              type: type, default: default, required: required
            }

            # Getter
            define_method(name) do
              value = instance_variable_get("@#{name}")
              value.nil? ? self.class.instance_variable_get(:@attributes)[name][:default] : value
            end

            # Setter with type coercion
            define_method("#{name}=") do |value|
              coerced = self.class.send(:coerce_value, value, type)
              instance_variable_set("@#{name}", coerced)
            end

            # Predicate (for boolean)
            if type == :boolean
              define_method("#{name}?") { !!send(name) }
            end
          end

          # Validation DSL
          def validates(name, **opts)
            @validations << { attribute: name, rules: opts }
          end

          # Callback DSL
          def before_save(&block)
            @callbacks[:before_save] << block
          end

          def after_save(&block)
            @callbacks[:after_save] << block
          end

          def attributes_config
            @attributes
          end

          def validations_config
            @validations
          end

          def callbacks_config
            @callbacks
          end

          private

          def coerce_value(value, type)
            return nil if value.nil?
            case type
            when :string  then value.to_s
            when :integer then value.to_i
            when :float   then value.to_f
            when :boolean then !!value
            when :symbol  then value.to_sym
            when :array   then Array(value)
            else value
            end
          end
        end

        # Instance methods
        def initialize(attrs = {})
          attrs.each do |key, value|
            send("#{key}=", value) if respond_to?("#{key}=")
          end
        end

        def valid?
          errors.empty?
        end

        def errors
          errs = []
          self.class.validations_config.each do |v|
            attr = v[:attribute]
            value = send(attr)
            rules = v[:rules]

            if rules[:presence] && (value.nil? || value.to_s.empty?)
              errs << "#{attr} can't be blank"
            end
            if rules[:min_length] && value.to_s.length < rules[:min_length]
              errs << "#{attr} is too short (min #{rules[:min_length]})"
            end
            if rules[:max_length] && value.to_s.length > rules[:max_length]
              errs << "#{attr} is too long (max #{rules[:max_length]})"
            end
            if rules[:format] && !value.to_s.match?(rules[:format])
              errs << "#{attr} format is invalid"
            end
            if rules[:inclusion] && !rules[:inclusion].include?(value)
              errs << "#{attr} is not included in #{rules[:inclusion]}"
            end
            if rules[:numericality]
              errs << "#{attr} is not a number" unless value.is_a?(Numeric)
            end
          end
          errs
        end

        def to_h
          self.class.attributes_config.keys.each_with_object({}) do |attr, hash|
            hash[attr] = send(attr)
          end
        end

        def to_json
          require 'json'
          to_h.to_json
        end

        def save
          return false unless valid?
          self.class.callbacks_config[:before_save].each { |cb| instance_exec(&cb) }
          # Persist logic would go here
          self.class.callbacks_config[:after_save].each { |cb| instance_exec(&cb) }
          true
        end
      end

      # ============================================================
      # PART 2: Dynamic Proxy (method_missing)
      # ============================================================

      class DynamicProxy
        def initialize(target)
          @target = target
          @call_log = []
          @intercepts = {}
        end

        def intercept(method_name, &block)
          @intercepts[method_name.to_sym] = block
        end

        def call_log
          @call_log.dup.freeze
        end

        def method_missing(name, *args, **kwargs, &block)
          @call_log << { method: name, args: args, kwargs: kwargs, at: Time.now }

          if @intercepts.key?(name)
            @intercepts[name].call(*args, **kwargs, &block)
          elsif @target.respond_to?(name)
            @target.send(name, *args, **kwargs, &block)
          else
            super
          end
        end

        def respond_to_missing?(name, include_private = false)
          @intercepts.key?(name) || @target.respond_to?(name, include_private) || super
        end
      end

      # ============================================================
      # PART 3: Concern Module (Rails-style)
      # ============================================================

      module Concern
        def self.extended(base)
          base.instance_variable_set(:@_class_methods, Module.new)
          base.instance_variable_set(:@_included_block, nil)
        end

        def class_methods(&block)
          @_class_methods.module_eval(&block)
        end

        def included_do(&block)
          @_included_block = block
        end

        def self.included(base)
          base.extend(self)
        end

        def append_features(base)
          super
          base.extend(@_class_methods) if @_class_methods
          base.class_eval(&@_included_block) if @_included_block
        end
      end

      # ============================================================
      # PART 4: Pipeline Operator (Method Chaining)
      # ============================================================

      module Pipeline
        def pipe(method_name = nil, &block)
          if block_given?
            block.call(self)
          elsif method_name
            send(method_name)
          else
            self
          end
        end

        def then_do(&block)
          block.call(self)
          self
        end
      end

      # ============================================================
      # Diagnostics
      # ============================================================

      def self.metaprogramming_diagnostics
        {
          engine: 'OmniMetaprogrammingEngine',
          layer:  'Ruby Domain',
          components: %w[
            AttributeDSL DynamicProxy Concern Pipeline
          ],
          features: [
            'define_method runtime method creation',
            'method_missing proxy delegation',
            'class_eval context evaluation',
            'attribute DSL with type coercion',
            'validation DSL with rules',
            'before/after save callbacks',
            'concern class_methods/included',
            'pipeline operator chaining'
          ],
          learned_logic: [
            'define-method-runtime-creation',
            'method-missing-proxy-delegation',
            'class-eval-context-evaluation',
            'attribute-dsl-type-coercion',
            'validation-dsl-rules-chain',
            'callback-before-after-hooks',
            'concern-mixin-composition',
            'open-class-extension-pattern'
          ]
        }
      end

    end
  end
end
