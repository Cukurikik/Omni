defmodule OmniMoE.Registry do
  # OMNI MOTHER: Elixir Process Registry
  def start_link do
    Registry.start_link(keys: :unique, name: OmniMoERegistry)
  end
end
