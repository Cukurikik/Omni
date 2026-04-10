// ==========================================
// 🌍 OMNI-JS STDLIB: API Users Route
// ==========================================
// URL: /api/users
// Mendemonstrasikan RESTful handler dengan semua HTTP methods.
// ==========================================

function OmniHandler(req) {
    const users = [
        { id: 1, name: "Komandan", role: "CTO" },
        { id: 2, name: "Anita", role: "Principal Architect" },
        { id: 3, name: "OMNI-CORE", role: "Rust V8 Engine" },
    ];

    switch (req.method) {
        case "GET":
            return JSON.stringify({
                status: "success",
                method: "GET",
                data: users,
                total: users.length,
            });

        case "POST":
            const newUser = JSON.parse(req.body || "{}");
            return JSON.stringify({
                status: "created",
                method: "POST",
                data: { id: users.length + 1, ...newUser },
                message: "User berhasil dibuat di dalam V8 Sandbox!",
            });

        case "PUT":
            return JSON.stringify({
                status: "updated",
                method: "PUT",
                message: "Full update dilakukan oleh Rust-V8 Engine",
            });

        case "DELETE":
            return JSON.stringify({
                status: "deleted",
                method: "DELETE",
                message: "Data dihapus — tetapi hanya di dalam Sandbox isolasi!",
            });

        default:
            return JSON.stringify({
                error: "Method not supported",
                method: req.method,
            });
    }
}
