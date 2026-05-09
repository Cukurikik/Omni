defmodule Omni.TransframerJobWorker do
  use GenServer

  def start_link(job_id) do
    GenServer.start_link(__MODULE__, job_id)
  end

  @impl true
  def init(job_id) do
    {:ok, %{id: job_id, status: :pending}}
  end
end
