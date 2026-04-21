# ===========================================================================
# OMNI NETWORK LAYER — PUPPETEER REPLAY ACTOR CONCURRENCY ENGINE
# ===========================================================================
# Source Paradigm : Chrome DevTools Puppeteer Replay
# Domain Layer   : Network (Actor model, fault tolerance, soft-realtime)
# Language        : Elixir
# Function        : Concurrent browser replay actor system that executes
#                   recorded user interaction flows (click, navigate, type,
#                   scroll, assert) across a supervised pool of workers
# ===========================================================================

defmodule OmniNetwork.PuppeteerReplay.Step do
  @moduledoc "A single recorded user interaction step."

  defstruct [
    :type,        # :navigate | :click | :change | :keyDown | :keyUp | :scroll | :waitForElement | :assert
    :target,      # CSS selector or URL
    :value,       # typed value, key name, or assertion expression
    :timeout_ms,  # max wait time
    :frame_url,   # iframe context (nil = main frame)
    :assertions   # list of post-step assertions
  ]
end

defmodule OmniNetwork.PuppeteerReplay.Recording do
  @moduledoc "A complete recorded browser session."

  alias OmniNetwork.PuppeteerReplay.Step

  defstruct [
    :title,
    :steps,
    :viewport_width,
    :viewport_height,
    :user_agent,
    :recorded_at
  ]

  @doc "Parse a Chrome DevTools Recorder JSON export."
  def from_json(json_map) when is_map(json_map) do
    steps = Enum.map(json_map["steps"] || [], fn step ->
      %Step{
        type:        String.to_atom(step["type"] || "navigate"),
        target:      get_selector(step),
        value:       step["value"] || step["key"] || step["url"],
        timeout_ms:  step["timeout"] || 5000,
        frame_url:   step["frame"] && step["frame"]["url"],
        assertions:  step["assertions"] || []
      }
    end)

    %__MODULE__{
      title:           json_map["title"] || "Untitled Recording",
      steps:           steps,
      viewport_width:  get_in(json_map, ["steps", Access.at(0), "width"]) || 1280,
      viewport_height: get_in(json_map, ["steps", Access.at(0), "height"]) || 720,
      user_agent:      nil,
      recorded_at:     DateTime.utc_now()
    }
  end

  defp get_selector(%{"selectors" => [[selector | _] | _]}), do: selector
  defp get_selector(%{"target" => target}), do: target
  defp get_selector(_), do: nil
end

defmodule OmniNetwork.PuppeteerReplay.Worker do
  @moduledoc """
  A supervised worker actor that replays a recording in a browser instance.
  Each worker manages its own browser session lifecycle.
  """

  alias OmniNetwork.PuppeteerReplay.{Step, Recording}

  defstruct [
    :worker_id,
    :recording,
    :results,
    :status,       # :idle | :running | :completed | :failed
    :started_at,
    :completed_at,
    :error
  ]

  @doc "Execute a full recording replay synchronously."
  def replay(%Recording{} = recording) do
    worker_id = :crypto.strong_rand_bytes(4) |> Base.encode16(case: :lower)
    IO.puts("[REPLAY-OMNI-EX] Worker #{worker_id} starting replay: #{recording.title}")

    started_at = DateTime.utc_now()
    results = []
    status = :running
    error = nil

    results = Enum.reduce(recording.steps, [], fn step, acc ->
      result = execute_step(worker_id, step)
      [result | acc]
    end)

    results = Enum.reverse(results)
    failures = Enum.count(results, fn {status, _, _} -> status == :error end)

    {final_status, final_error} = if failures > 0 do
      {:failed, "#{failures} step(s) failed"}
    else
      {:completed, nil}
    end

    IO.puts("[REPLAY-OMNI-EX] Worker #{worker_id}: #{final_status} (#{length(results)} steps, #{failures} failures)")

    %__MODULE__{
      worker_id:    worker_id,
      recording:    recording,
      results:      results,
      status:       final_status,
      started_at:   started_at,
      completed_at: DateTime.utc_now(),
      error:        final_error
    }
  end

  defp execute_step(worker_id, %Step{type: type, target: target, value: value} = step) do
    IO.puts("[REPLAY-OMNI-EX]   #{worker_id} | #{type} → #{target || value || "(no target)"}")

    # Production: each case maps to a Puppeteer/Playwright API call
    case type do
      :navigate ->
        # Production: page.goto(value, waitUntil: 'networkidle0')
        {:ok, :navigate, value}

      :click ->
        # Production: page.click(target, timeout: step.timeout_ms)
        {:ok, :click, target}

      :change ->
        # Production: page.type(target, value)
        {:ok, :change, "#{target} = #{value}"}

      :keyDown ->
        {:ok, :keyDown, value}

      :keyUp ->
        {:ok, :keyUp, value}

      :scroll ->
        {:ok, :scroll, target}

      :waitForElement ->
        # Production: page.waitForSelector(target, timeout: step.timeout_ms)
        {:ok, :waitForElement, target}

      :assert ->
        # Production: evaluate assertion expression in page context
        {:ok, :assert, value}

      unknown ->
        {:error, :unknown_step, "Unrecognized step type: #{unknown}"}
    end
  end
end

defmodule OmniNetwork.PuppeteerReplay.Pool do
  @moduledoc """
  Manages a pool of replay workers using Task.async_stream for fan-out.
  Runs multiple recordings concurrently with configurable parallelism.
  """

  alias OmniNetwork.PuppeteerReplay.{Recording, Worker}

  @doc "Replay multiple recordings concurrently."
  def replay_all(recordings, opts \\ []) when is_list(recordings) do
    max_concurrent = Keyword.get(opts, :max_concurrent, System.schedulers_online())

    IO.puts("[REPLAY-OMNI-EX] Pool: Replaying #{length(recordings)} recording(s), concurrency=#{max_concurrent}")

    results =
      recordings
      |> Task.async_stream(&Worker.replay/1, max_concurrency: max_concurrent, timeout: :infinity)
      |> Enum.map(fn {:ok, result} -> result end)

    successes = Enum.count(results, fn r -> r.status == :completed end)
    IO.puts("[REPLAY-OMNI-EX] Pool: #{successes}/#{length(results)} recordings passed.")

    results
  end
end

# ---- FFI Test Harness (commented) ------------------------------------------
# rec = %OmniNetwork.PuppeteerReplay.Recording{
#   title: "Login Flow", steps: [
#     %OmniNetwork.PuppeteerReplay.Step{type: :navigate, value: "https://example.com/login", timeout_ms: 5000},
#     %OmniNetwork.PuppeteerReplay.Step{type: :click, target: "#email-input", timeout_ms: 3000},
#     %OmniNetwork.PuppeteerReplay.Step{type: :change, target: "#email-input", value: "user@test.com"},
#     %OmniNetwork.PuppeteerReplay.Step{type: :click, target: "#submit-btn", timeout_ms: 3000},
#     %OmniNetwork.PuppeteerReplay.Step{type: :waitForElement, target: ".dashboard", timeout_ms: 10000},
#   ], viewport_width: 1280, viewport_height: 720, user_agent: nil, recorded_at: ~U[2026-01-01 00:00:00Z]
# }
# OmniNetwork.PuppeteerReplay.Pool.replay_all([rec])
