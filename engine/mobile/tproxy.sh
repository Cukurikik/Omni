#!/system/bin/sh
# ==========================================
# 📱 OMNI MOBILE: Box for Magisk Tproxy Route (Phase 82)
# ==========================================
# Terinjeksi di root /data/adb/modules/omni_box/
# Skrip ini memodifikasi iptables kernel Android untuk
# rute internet sistem ke OMNI Kube Networks.

echo "📱 [OMNI-MAGISK] Memulai Pemasangan Iptables TPROXY di Android Kernel..."

# Menghapus tabel lama yang tertinggal
iptables -t mangle -F OMNI_PROXY 2>/dev/null
iptables -t mangle -X OMNI_PROXY 2>/dev/null

echo "🔗 Membuat Chain khusus OMNI_PROXY..."
iptables -t mangle -N OMNI_PROXY

# Hindari loop trafik lokal
iptables -t mangle -A OMNI_PROXY -d 127.0.0.0/8 -j RETURN
iptables -t mangle -A OMNI_PROXY -d 192.168.0.0/16 -j RETURN

# Arahkan semua soket TCP ke Port 4002 (Engine OMNI C++ HFT)
iptables -t mangle -A OMNI_PROXY -p tcp -j TPROXY --on-port 4002 --tproxy-mark 1

# Pasang ke PREROUTING Kernel Device
iptables -t mangle -A PREROUTING -j OMNI_PROXY

echo "✅ [SUCCESS] HP Android kini bernapas melalui Paru-Paru OMNI Framework!"
exit 0
