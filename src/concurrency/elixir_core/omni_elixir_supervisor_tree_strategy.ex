// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Elixir — Concurrency & Networking Layer (OMNI Zero-Mock Implementation)
// Implements deterministic Supervisor tree restart strategy evaluation.
// Absorbs patterns from: github.com/elixir-lang/elixir, OTP supervisor

defmodule Omni.Concurrency.SupervisorStrategy do
  @moduledoc """
  Production-grade Supervisor restart strategy engine.
  Implements :one_for_one, :one_for_all, :rest_for_one with exact OTP semantics.
  Includes max_restarts / max_seconds intensity checking.
  """

  @type strategy :: :one_for_one | :one_for_all | :rest_for_one
  @type child_id :: integer()

  @type restart_result ::
    {:restart, [child_id()]}
    | {:shutdown, String.t()}
    | {:error, String.t()}

  @doc """
  Evaluates which children to restart based on supervisor strategy.

  ## Parameters
  - `strategy` - The supervisor restart strategy
  - `failed_child_index` - Index of the child that crashed (0-based)
  - `total_children` - Total number of children under supervision
  - `restart_count` - Number of restarts in current window
  - `max_restarts` - Maximum restarts allowed in time window
  - `max_seconds` - Time window for restart counting (seconds)
  - `elapsed_seconds` - Time elapsed since first restart in window

  ## Returns
  - `{:restart, child_ids}` - List of child indices to restart
  - `{:shutdown, reason}` - Supervisor should shut down (intensity exceeded)
  - `{:error, reason}` - Invalid parameters
  """
  @spec evaluate_restart(strategy(), child_id(), pos_integer(), non_neg_integer(), pos_integer(), pos_integer(), non_neg_integer()) :: restart_result()
  def evaluate_restart(strategy, failed_child_index, total_children, restart_count, max_restarts, max_seconds, elapsed_seconds) do
    # Validate inputs
    cond do
      total_children <= 0 ->
        {:error, "Supervisor must have at least one child."}

      failed_child_index < 0 or failed_child_index >= total_children ->
        {:error, "Failed child index #{failed_child_index} out of range [0, #{total_children - 1}]."}

      max_restarts <= 0 ->
        {:error, "max_restarts must be > 0."}

      true ->
        # Check restart intensity
        if restart_count >= max_restarts and elapsed_seconds <= max_seconds do
          {:shutdown, "Supervisor intensity exceeded: #{restart_count} restarts in #{elapsed_seconds}s (max: #{max_restarts} in #{max_seconds}s)."}
        else
          compute_restart_targets(strategy, failed_child_index, total_children)
        end
    end
  end

  defp compute_restart_targets(:one_for_one, failed_child_index, _total) do
    # Only restart the failed child
    {:restart, [failed_child_index]}
  end

  defp compute_restart_targets(:one_for_all, _failed_child_index, total_children) do
    # Restart ALL children
    {:restart, Enum.to_list(0..(total_children - 1))}
  end

  defp compute_restart_targets(:rest_for_one, failed_child_index, total_children) do
    # Restart the failed child and all children started AFTER it
    {:restart, Enum.to_list(failed_child_index..(total_children - 1))}
  end

  defp compute_restart_targets(unknown_strategy, _, _) do
    {:error, "Unknown supervisor strategy: #{inspect(unknown_strategy)}"}
  end

  @doc """
  Returns diagnostics for the supervisor strategy.
  """
  @spec diagnostics(strategy()) :: map()
  def diagnostics(strategy) do
    %{
      strategy: strategy,
      description: case strategy do
        :one_for_one -> "Restart only the crashed child process."
        :one_for_all -> "Restart all children when any child crashes."
        :rest_for_one -> "Restart crashed child and all children started after it."
        _ -> "Unknown strategy."
      end
    }
  end
end
