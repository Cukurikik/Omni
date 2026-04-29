# Omni OpenGPT Model Registry (Ruby)
# Ref: SunLemuria/OpenGPTAndBeyond
module Omni
  module OpenGPTRegistry
    MODEL_CATALOG = {
      'gpt2' => { params: '124M', arch: 'transformer', license: 'MIT' },
      'llama' => { params: '7B', arch: 'transformer', license: 'Meta' },
      'alpaca' => { params: '7B', arch: 'transformer', license: 'Apache-2.0' },
      'chatglm' => { params: '6B', arch: 'glm', license: 'Apache-2.0' },
    }.freeze
    def self.lookup(name)
      MODEL_CATALOG[name.downcase] || { error: "Model '#{name}' not found" }
    end
    def self.list_all
      MODEL_CATALOG.keys
    end
  end
end
