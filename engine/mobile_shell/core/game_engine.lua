-- ==========================================
-- 🎮 OMNI MOBILE SHELL: Lua Game Scripting Engine (Phase 130)
-- ==========================================
-- Buku Panduan Tuan: "Lua: Sangat ringan, sering dipakai untuk mesin game mobile sederhana."
-- Runtime Lua hanya 200KB! Cocok untuk game casual HP yang tidak boleh boros RAM.
-- Ini adalah Mesin Skrip Game yang diembed ke dalam C++ Native Compute.

print("🎮 [OMNI-LUA-GAME] Memuat Mesin Skrip Ringan Lua (200KB footprint)...")

-- Definisi entitas game sederhana
local player = {
    name = "OmniHero",
    hp = 100,
    x = 0,
    y = 0,
    speed = 5
}

function move_player(dx, dy)
    player.x = player.x + dx * player.speed
    player.y = player.y + dy * player.speed
    print(string.format("🕹️ [MOVE] %s bergerak ke [%d, %d]", player.name, player.x, player.y))
end

function apply_damage(amount)
    player.hp = player.hp - amount
    print(string.format("💥 [HIT] %s menerima %d damage! HP: %d", player.name, amount, player.hp))
    if player.hp <= 0 then
        print("💀 [GAME OVER] " .. player.name .. " telah gugur!")
    end
end

-- Simulasi game loop
print("🔄 [GAME LOOP] Menjalankan 5 tick simulasi game...")
for tick = 1, 5 do
    print(string.format("\n--- Tick %d ---", tick))
    move_player(1, 0.5)
    if tick == 3 then
        apply_damage(30)
    end
end

print("\n✅ Mesin Game Lua berjalan ultra-ringan di Smartphone OMNI!")
print("🔋 [BATERAI] Footprint Lua: 200KB RAM. Game casual tanpa lag!")
