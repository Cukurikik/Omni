# OMNI VLM Architecture Registry — Domain Layer
# Absorbing gokayfem/awesome-vlm-architectures: Famous VLM architecture catalog.
# Ruby domain engine for architecture comparison and feature mapping.

class OmniVlmArchRegistryEngine
  VLM_COMPONENTS = %w[vision_encoder text_decoder connector training_strategy].freeze

  attr_reader :lookups

  def initialize
    @architectures = {}
    @lookups = 0
  end

  def register_architecture(name, components = {})
    return { ok: false, error: "VlmArchError: Name required" } if name.nil? || name.empty?
    missing = VLM_COMPONENTS.select { |c| !components.key?(c.to_sym) && !components.key?(c) }
    return { ok: false, error: "VlmArchError: Missing components: #{missing.join(', ')}" } unless missing.empty?

    @architectures[name] = {
      name: name,
      components: components,
      registered_at: Time.now.to_i
    }
    { ok: true, registered: name }
  end

  def compare(arch_a, arch_b)
    return { ok: false, error: "VlmArchError: Architecture '#{arch_a}' not found" } unless @architectures.key?(arch_a)
    return { ok: false, error: "VlmArchError: Architecture '#{arch_b}' not found" } unless @architectures.key?(arch_b)

    @lookups += 1
    a = @architectures[arch_a][:components]
    b = @architectures[arch_b][:components]

    diff = {}
    VLM_COMPONENTS.each do |comp|
      key = comp.to_sym
      diff[comp] = { arch_a => a[key].to_s, arch_b => b[key].to_s, same: a[key].to_s == b[key].to_s }
    end

    { ok: true, comparison: diff }
  end

  def list_by_encoder(encoder_type)
    @lookups += 1
    matches = @architectures.select { |_, v| v[:components][:vision_encoder].to_s.downcase.include?(encoder_type.downcase) }
    { ok: true, results: matches.keys }
  end

  def diagnostics
    { engine: "OmniVlmArchRegistryEngine", architectures: @architectures.size,
      lookups: @lookups, status: "Operational" }
  end
end
