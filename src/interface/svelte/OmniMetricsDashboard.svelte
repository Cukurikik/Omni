<script>
    import { onMount } from 'svelte';

    let activeConnections = 0;
    let systemHealth = "Nominal";

    onMount(() => {
        const interval = setInterval(() => {
            activeConnections = Math.floor(Math.random() * 1000) + 5000;
        }, 2000);
        return () => clearInterval(interval);
    });

    function restartSubsystem() {
        systemHealth = "Restarting...";
        setTimeout(() => systemHealth = "Nominal", 3000);
    }
</script>

<main class="dashboard">
    <h1>OMNI Svelte Dashboard</h1>
    <div class="card">
        <p>Active Connections: <strong>{activeConnections}</strong></p>
        <p>System Health: <strong>{systemHealth}</strong></p>
        <button on:click={restartSubsystem}>Restart Subsystem</button>
    </div>
</main>

<style>
    .dashboard { font-family: sans-serif; background: #000; color: #0f0; padding: 2rem; height: 100vh; }
    .card { border: 1px solid #0f0; padding: 1rem; border-radius: 8px; }
    button { background: #0f0; color: #000; border: none; padding: 0.5rem 1rem; cursor: pointer; }
</style>
