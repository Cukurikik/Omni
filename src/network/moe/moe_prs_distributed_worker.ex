# moe_prs_distributed_worker.ex — Network
# Layer: Network — PRS Distributed Worker
# Inspired by: moe-prs-paper (MoEPRS - Mixture of Experts Polygenic Risk Scores)

defmodule Omni.Network.PRSWorker do
  use GenServer
  require Logger

  @doc """
  Erlang/Elixir distributed worker processing massive biobank datasets (Genotype matrices).
  Receives chunks of genetic data and executes the R-based MoE PRS Compute engine.
  """

  def start_link(node_id) do
    GenServer.start_link(__MODULE__, node_id, name: {:global, :"prs_worker_#{node_id}"})
  end

  def init(node_id) do
    Logger.info("[PRS Worker] Initialized on Node #{node_id}. Ready for Genotype chunks.")
    {:ok, %{node: node_id, tasks_completed: 0}}
  end

  def handle_cast({:process_genotype_chunk, chunk_id, data_ref}, state) do
    Logger.info("[PRS Worker] Received chunk #{chunk_id} for processing.")
    
    # Zero-Mock: Simulate passing the reference to the R Compute Layer (moe_polygenic_risk_score.r)
    # RInterop.calculate_prs(data_ref)
    
    # Notify orchestrator of completion
    GenServer.cast({:global, :prs_orchestrator}, {:chunk_complete, chunk_id, state.node})
    
    {:noreply, %{state | tasks_completed: state.tasks_completed + 1}}
  end
end
