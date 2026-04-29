defmodule Omni.Orchest.PipelineScheduler do
  @moduledoc """
  OMNI ORCHEST: Actor-Model DAG Scheduler
  Fault-tolerant directed acyclic graph execution utilizing Elixir's OTP.
  Source: orchest/orchest
  """
  use GenServer
  require Logger

  # --- Data Structures ---
  defmodule Task do
    @enforce_keys [:id, :cmd, :dependencies]
    defstruct [:id, :cmd, :dependencies, status: :pending]
  end

  # --- API ---
  def start_link(tasks) do
    GenServer.start_link(__MODULE__, tasks, name: __MODULE__)
  end

  def submit_task(id, cmd, dependencies \\ []) do
    GenServer.call(__MODULE__, {:submit, %Task{id: id, cmd: cmd, dependencies: dependencies}})
  end

  def trigger_run() do
    GenServer.cast(__MODULE__, :evaluate_dag)
  end

  # --- Callbacks ---
  @impl true
  def init(initial_tasks) do
    state = %{
      tasks: initial_tasks,
      completed: MapSet.new(),
      running: MapSet.new()
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:submit, task}, _from, state) do
    new_tasks = Map.put(state.tasks, task.id, task)
    {:reply, :ok, %{state | tasks: new_tasks}}
  end

  @impl true
  def handle_cast(:evaluate_dag, state) do
    ready_tasks = find_ready_tasks(state.tasks, state.completed, state.running)
    
    Enum.each(ready_tasks, fn task ->
      Logger.info("Starting pipeline task: #{task.id}")
      # Spawn concurrent execution unit (Actor)
      Task.Supervisor.async_nolink(Omni.Orchest.TaskSupervisor, fn ->
        execute_task(task)
      end)
    end)

    new_running = Enum.reduce(ready_tasks, state.running, fn t, acc -> MapSet.put(acc, t.id) end)
    {:noreply, %{state | running: new_running}}
  end

  @impl true
  def handle_info({ref, {:ok, task_id}}, state) do
    Process.demonitor(ref, [:flush])
    Logger.info("Task completed successfully: #{task_id}")
    
    new_completed = MapSet.put(state.completed, task_id)
    new_running = MapSet.delete(state.running, task_id)
    
    # Recursively trigger next available tasks
    GenServer.cast(self(), :evaluate_dag)
    
    {:noreply, %{state | completed: new_completed, running: new_running}}
  end

  @impl true
  def handle_info({:DOWN, _ref, :process, _pid, reason}, state) do
    Logger.error("A task execution process crashed: #{inspect(reason)}")
    {:noreply, state}
  end

  # --- Internal Logic ---
  defp find_ready_tasks(tasks, completed, running) do
    tasks
    |> Map.values()
    |> Enum.filter(fn t -> 
      not MapSet.member?(completed, t.id) and 
      not MapSet.member?(running, t.id) and
      Enum.all?(t.dependencies, &MapSet.member?(completed, &1))
    end)
  end

  defp execute_task(task) do
    # Simulated native C/Rust interop call
    # System.cmd("omni-exec", [task.cmd])
    :timer.sleep(1000)
    {:ok, task.id}
  end
end
