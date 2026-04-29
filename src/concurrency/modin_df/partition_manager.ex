defmodule Omni.Concurrency.ModinDF.PartitionManager do
  use GenServer

  def start_link(num_partitions) do
    GenServer.start_link(__MODULE__, %{total: num_partitions, computed: 0, results: []}, name: __MODULE__)
  end

  def submit_partition_result(pid, partition_id, value) do
    GenServer.cast(pid, {:result, partition_id, value})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:result, partition_id, value}, state) do
    new_results = state.results ++ [{partition_id, value}]
    new_computed = state.computed + 1

    IO.puts("Modin: Partition #{partition_id} computed => #{value}")

    if new_computed == state.total do
      # All partitions complete, reduce (simulate MapReduce barrier)
      total_sum = Enum.reduce(new_results, 0.0, fn {_, v}, acc -> acc + v end)
      final_mean = total_sum / state.total
      IO.puts("Modin: MapReduce Complete. Final Aggregated Mean: #{final_mean}")
    end

    {:noreply, %{state | computed: new_computed, results: new_results}}
  end
end
