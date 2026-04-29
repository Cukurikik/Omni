defmodule Omni.Concurrency.Graphics.CameraInterpolator do
  use GenServer
  require Logger

  defmodule Result do
    defsturct [:ok, :error]
    def ok(value), do: %Result{ok: value, error: nil}
    def error(reason), do: %Result{ok: nil, error: reason}
  end

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def generate_frames(keyframes, total_frames) when is_list(keyframes) do
    GenServer.call(__MODULE__, {:interpolate, keyframes, total_frames}, :infinity)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:interpolate, keyframes, total_frames}, _from, state) do
    if length(keyframes) < 2 do
      {:reply, Result.error("Requires at least 2 keyframes"), state}
    else
      # Parallelize segments between keyframes
      segments = Enum.chunk_every(keyframes, 2, 1, :discard)
      frames_per_segment = div(total_frames, length(segments))

      results = Task.async_stream(segments, fn [k1, k2] -> 
        lerp_segment(k1, k2, frames_per_segment)
      end, max_concurrency: System.schedulers_online())
      |> Enum.flat_map(fn {:ok, frames} -> frames end)

      {:reply, Result.ok(results), state}
    end
  end

  # Structural simulation of linear interpolation (in production: Catmull-Rom Spline or SLERP for quats)
  defp lerp_segment(k1, k2, steps) do
    Enum.map(0..(steps-1), fn step ->
      t = step / steps
      %{
        x: k1.x + (k2.x - k1.x) * t,
        y: k1.y + (k2.y - k1.y) * t,
        z: k1.z + (k2.z - k1.z) * t,
        timestamp: k1.timestamp + (k2.timestamp - k1.timestamp) * t
      }
    end)
  end
end
