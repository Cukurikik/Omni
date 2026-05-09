# omni_lb_consistent_hash.ex — Consistent Hashing Load Balancer
# Layer: Network / Elixir
#
# OTP module that hashes requests (e.g. by Tenant ID) to map them consistently
# to the same worker nodes. Essential for maximizing KV Cache hit rates in LLMs.

defmodule Omni.Network.ConsistentHashRing do
  @moduledoc """
  A Consistent Hashing ring using cryptographic hashes to assign keys
  to specific backend inference nodes.
  """

  # State is an ordered list of {hash_val, node_name}
  
  def new(nodes, virtual_nodes \\ 100) do
    ring =
      Enum.flat_map(nodes, fn node ->
        Enum.map(1..virtual_nodes, fn i ->
          {hash_key("#{node}_vnode_#{i}"), node}
        end)
      end)
      |> Enum.sort_by(fn {hash, _} -> hash end)
      
    ring
  end

  def add_node(ring, node, virtual_nodes \\ 100) do
    new_vnodes =
      Enum.map(1..virtual_nodes, fn i ->
        {hash_key("#{node}_vnode_#{i}"), node}
      end)
      
    (ring ++ new_vnodes)
    |> Enum.sort_by(fn {hash, _} -> hash end)
  end

  def remove_node(ring, node) do
    Enum.reject(ring, fn {_hash, n} -> n == node end)
  end

  @doc """
  Finds the appropriate node for a given key (e.g., Tenant ID).
  """
  def get_node([], _key), do: nil
  def get_node(ring, key) do
    key_hash = hash_key(key)
    
    # Find the first vnode on the ring with a hash >= key_hash
    found = Enum.find(ring, fn {h, _node} -> h >= key_hash end)
    
    case found do
      {_h, node} -> node
      # If we wrap around, take the first node
      nil -> 
        {_h, node} = hd(ring)
        node
    end
  end

  defp hash_key(key) do
    :crypto.hash(:md5, key) |> :binary.decode_unsigned()
  end
end
