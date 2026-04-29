defmodule Omni.Concurrency.PhySO.EvolutionPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, generation: 0, population: []}, name: __MODULE__)
  end

  def initialize_population(pid) do
    GenServer.call(pid, :init)
  end

  def evolve_generation(pid) do
    GenServer.cast(pid, :evolve)
  end

  def get_best_equation(pid) do
    GenServer.call(pid, :get_best)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call(:init, _from, state) do
    # Deterministic initialization of base population
    initial_pop = Enum.map(1..state.pool_size, fn id -> 
      %{id: id, string_repr: "x + #{id}", fitness: 0.0}
    end)
    
    {:reply, :ok, %{state | population: initial_pop, generation: 1}}
  end

  @impl true
  def handle_call(:get_best, _from, state) do
    best = if Enum.empty?(state.population) do
      nil
    else
      Enum.max_by(state.population, & &1.fitness)
    end
    {:reply, best, state}
  end

  @impl true
  def handle_cast(:evolve, state) do
    IO.puts("Evolving Generation #{state.generation} -> #{state.generation + 1}")
    
    # Deterministic simulation of crossover and mutation mathematically
    new_pop = Enum.map(state.population, fn eq ->
      # Simple deterministic evolution logic
      new_fitness = eq.fitness + 1.5
      new_repr = "sin(#{eq.string_repr}) * #{state.generation}"
      %{eq | string_repr: new_repr, fitness: new_fitness}
    end)

    {:noreply, %{state | population: new_pop, generation: state.generation + 1}}
  end
end
