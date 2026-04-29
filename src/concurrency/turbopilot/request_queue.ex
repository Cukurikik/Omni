# OMNI TURBOPILOT: Request Queue
# Elixir OTP GenServer managing the queue of incoming code completion requests.
# Drops stale requests if the user types faster than the local CPU can generate.
# Source: ravenscroftj/turbopilot

defmodule Omni.Turbopilot.RequestQueue do
  use GenServer
  require Logger

  @max_queue_size 5

  # Client API
  def start_link(_) do
    GenServer.start_link(__MODULE__, %{queue: :queue.new(), active: 0}, name: __MODULE__)
  end

  def submit_request(prompt, req_id) do
    GenServer.call(__MODULE__, {:submit, prompt, req_id})
  end

  # Server Callbacks
  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:submit, prompt, req_id}, _from, state) do
    q_len = :queue.len(state.queue)

    if q_len >= @max_queue_size do
      # Drop the oldest request (user has moved on)
      {{:value, dropped_req}, new_queue} = :queue.out(state.queue)
      Logger.warn("Queue full. Dropping stale request: #{inspect(dropped_req)}")
      
      new_queue2 = :queue.in({prompt, req_id}, new_queue)
      {:reply, :enqueued, %{state | queue: new_queue2}}
    else
      new_queue = :queue.in({prompt, req_id}, state.queue)
      
      # Trigger processing if idle
      if state.active == 0 do
        send(self(), :process_next)
      end
      
      {:reply, :enqueued, %{state | queue: new_queue}}
    end
  end

  @impl true
  def handle_info(:process_next, state) do
    case :queue.out(state.queue) do
      {{:value, {prompt, req_id}}, new_queue} ->
        # Asynchronously send to the C/GGML NIF layer for generation
        Task.start(fn -> 
          Logger.info("Processing request: #{req_id}")
          # Simulate execution: Omni.GGML.generate(prompt)
          :timer.sleep(1000) 
          GenServer.cast(__MODULE__, :finished_task)
        end)
        
        {:noreply, %{state | queue: new_queue, active: 1}}
        
      {:empty, _} ->
        {:noreply, %{state | active: 0}}
    end
  end

  @impl true
  def handle_cast(:finished_task, state) do
    # Trigger next when current finishes
    send(self(), :process_next)
    {:noreply, %{state | active: 0}}
  end
end
