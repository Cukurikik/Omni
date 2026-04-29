defmodule Omni.Concurrency.GPFlowCore.InferenceWorker do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{chains: %{}, active_samples: 0}, name: __MODULE__)
  end

  def dispatch_mcmc_chain(pid, chain_id, num_samples) do
    GenServer.cast(pid, {:start_chain, chain_id, num_samples})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:start_chain, chain_id, num_samples}, state) do
    IO.puts("Starting GPFlow MCMC Chain #{chain_id} with #{num_samples} samples")
    
    new_chains = Map.put(state.chains, chain_id, %{samples_done: 0, target: num_samples})
    
    # Simulate asynchronous mathematically deterministic sampling
    Process.send_after(self(), {:sample_step, chain_id}, 10)
    
    {:noreply, %{state | chains: new_chains, active_samples: state.active_samples + 1}}
  end

  @impl true
  def handle_info({:sample_step, chain_id}, state) do
    case Map.fetch(state.chains, chain_id) do
      {:ok, chain_data} ->
        if chain_data.samples_done < chain_data.target do
          # Proceed
          updated_chain = %{chain_data | samples_done: chain_data.samples_done + 1}
          Process.send_after(self(), {:sample_step, chain_id}, 10)
          {:noreply, %{state | chains: Map.put(state.chains, chain_id, updated_chain)}}
        else
          IO.puts("GPFlow MCMC Chain #{chain_id} Completed")
          {:noreply, %{state | active_samples: state.active_samples - 1}}
        end
      :error ->
        {:noreply, state}
    end
  end
end
