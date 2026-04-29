defmodule Omni.Compute.ElixirCore.RateLimiter do
  @moduledoc """
  OMNI MOTHER — SEMESTER 14 BATCH 36
  Elixir — Concurrency & Networking Layer (OMNI Zero-Mock Implementation)
  Implements production-grade Token Bucket Rate Limiter.
  Absorbs patterns from: github.com/ExHammer/hammer, Plug.Throttle

  ## Algorithm: Token Bucket

  Each client gets a bucket with `max_tokens` capacity.
  Tokens replenish at `refill_rate` per `refill_interval_ms`.
  A request consumes 1 token. If the bucket is empty, the request is denied.

  ## Math

  tokens_to_add = floor((now - last_refill) / refill_interval_ms) * refill_rate
  current_tokens = min(max_tokens, stored_tokens + tokens_to_add)
  """

  defstruct [
    :client_id,
    :max_tokens,
    :current_tokens,
    :refill_rate,
    :refill_interval_ms,
    :last_refill_time
  ]

  @type t :: %__MODULE__{
    client_id: String.t(),
    max_tokens: pos_integer(),
    current_tokens: non_neg_integer(),
    refill_rate: pos_integer(),
    refill_interval_ms: pos_integer(),
    last_refill_time: integer()
  }

  @type result :: {:ok, t()} | {:error, String.t()}

  @doc """
  Creates a new rate limiter bucket for a client.

  ## Parameters
    - client_id: Unique identifier for the client
    - max_tokens: Maximum bucket capacity
    - refill_rate: Tokens added per refill interval
    - refill_interval_ms: Milliseconds between refill events
  """
  @spec new(String.t(), pos_integer(), pos_integer(), pos_integer()) :: result()
  def new(client_id, max_tokens, refill_rate, refill_interval_ms)
      when is_binary(client_id) and
           is_integer(max_tokens) and max_tokens > 0 and
           is_integer(refill_rate) and refill_rate > 0 and
           is_integer(refill_interval_ms) and refill_interval_ms > 0 do
    {:ok, %__MODULE__{
      client_id: client_id,
      max_tokens: max_tokens,
      current_tokens: max_tokens,
      refill_rate: refill_rate,
      refill_interval_ms: refill_interval_ms,
      last_refill_time: System.monotonic_time(:millisecond)
    }}
  end

  def new(_, _, _, _), do: {:error, "All rate limiter parameters must be positive integers"}

  @doc """
  Attempts to consume a token from the bucket.
  Returns {:ok, updated_limiter} if allowed, {:error, reason} if denied.
  """
  @spec try_acquire(t()) :: result()
  def try_acquire(%__MODULE__{} = limiter) do
    refilled = refill_tokens(limiter)

    if refilled.current_tokens > 0 do
      {:ok, %{refilled | current_tokens: refilled.current_tokens - 1}}
    else
      {:error, "Rate limit exceeded for client '#{refilled.client_id}'"}
    end
  end

  @doc """
  Attempts to consume N tokens from the bucket.
  """
  @spec try_acquire(t(), pos_integer()) :: result()
  def try_acquire(%__MODULE__{} = limiter, cost) when is_integer(cost) and cost > 0 do
    refilled = refill_tokens(limiter)

    if refilled.current_tokens >= cost do
      {:ok, %{refilled | current_tokens: refilled.current_tokens - cost}}
    else
      {:error, "Insufficient tokens: need #{cost}, have #{refilled.current_tokens}"}
    end
  end

  @doc """
  Returns the number of tokens currently available.
  """
  @spec available_tokens(t()) :: non_neg_integer()
  def available_tokens(%__MODULE__{} = limiter) do
    refilled = refill_tokens(limiter)
    refilled.current_tokens
  end

  @doc """
  Returns diagnostics about the rate limiter.
  """
  @spec diagnostics(t()) :: map()
  def diagnostics(%__MODULE__{} = limiter) do
    refilled = refill_tokens(limiter)
    %{
      engine: "OmniElixirRateLimiter",
      layer: "concurrency/elixir",
      client_id: refilled.client_id,
      current_tokens: refilled.current_tokens,
      max_tokens: refilled.max_tokens,
      refill_rate: refilled.refill_rate,
      refill_interval_ms: refilled.refill_interval_ms,
      utilization_pct: round((1 - refilled.current_tokens / refilled.max_tokens) * 100),
      status: "operational"
    }
  end

  # -- Private Helpers --

  defp refill_tokens(%__MODULE__{} = limiter) do
    now = System.monotonic_time(:millisecond)
    elapsed = now - limiter.last_refill_time

    if elapsed >= limiter.refill_interval_ms do
      intervals = div(elapsed, limiter.refill_interval_ms)
      tokens_to_add = intervals * limiter.refill_rate
      new_tokens = min(limiter.max_tokens, limiter.current_tokens + tokens_to_add)
      new_refill_time = limiter.last_refill_time + intervals * limiter.refill_interval_ms

      %{limiter | current_tokens: new_tokens, last_refill_time: new_refill_time}
    else
      limiter
    end
  end
end
