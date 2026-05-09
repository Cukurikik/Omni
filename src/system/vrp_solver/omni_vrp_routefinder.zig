// omni_vrp_routefinder.zig — Foundation Model Routing System
// Inspired by: RouteFinder for Vehicle Routing Problems
// Layer: System / Zig
//
// High-performance heuristics and meta-heuristics solver for
// Capacitated Vehicle Routing Problems (CVRP) to complement ML models.

const std = @import("std");
const math = std.math;
const Allocator = std.mem.Allocator;

pub const Node = struct {
    id: usize,
    x: f32,
    y: f32,
    demand: f32,
};

pub const Route = struct {
    nodes: []usize,
    load: f32,
    distance: f32,
};

pub const VRPProblem = struct {
    depot: Node,
    customers: []Node,
    capacity: f32,
    
    pub fn distance(self: *const VRPProblem, n1: usize, n2: usize) f32 {
        const node1 = if (n1 == 0) self.depot else self.customers[n1 - 1];
        const node2 = if (n2 == 0) self.depot else self.customers[n2 - 1];
        
        const dx = node1.x - node2.x;
        const dy = node1.y - node2.y;
        return @sqrt(dx * dx + dy * dy);
    }
};

pub const VRPSolution = struct {
    routes: []Route,
    total_distance: f32,
    
    pub fn destroy(self: *VRPSolution, alloc: Allocator) void {
        for (self.routes) |route| {
            alloc.free(route.nodes);
        }
        alloc.free(self.routes);
    }
};

pub const OmniVRPSolver = struct {
    alloc: Allocator,
    
    pub fn init(alloc: Allocator) OmniVRPSolver {
        return .{ .alloc = alloc };
    }
    
    /// Clarke-Wright Savings Algorithm
    pub fn solveSavings(self: *OmniVRPSolver, problem: *const VRPProblem) !VRPSolution {
        const n = problem.customers.len;
        if (n == 0) return VRPSolution{ .routes = &[_]Route{}, .total_distance = 0 };
        
        // 1. Initial solution: one route per customer
        var routes = std.ArrayList(Route).init(self.alloc);
        var in_route = try self.alloc.alloc(usize, n + 1);
        defer self.alloc.free(in_route);
        
        var total_dist: f32 = 0;
        
        for (0..n) |i| {
            const c_id = i + 1;
            var path = try self.alloc.alloc(usize, 3);
            path[0] = 0;
            path[1] = c_id;
            path[2] = 0;
            
            const dist = problem.distance(0, c_id) * 2.0;
            try routes.append(Route{
                .nodes = path,
                .load = problem.customers[i].demand,
                .distance = dist,
            });
            in_route[c_id] = i; // Map customer to route index
            total_dist += dist;
        }
        
        // 2. Compute savings
        const Saving = struct { i: usize, j: usize, s: f32 };
        var savings = std.ArrayList(Saving).init(self.alloc);
        defer savings.deinit();
        
        for (1..n + 1) |i| {
            for (i + 1..n + 1) |j| {
                const s = problem.distance(i, 0) + problem.distance(0, j) - problem.distance(i, j);
                if (s > 0) {
                    try savings.append(.{ .i = i, .j = j, .s = s });
                }
            }
        }
        
        // Sort savings descending
        std.sort.pdq(Saving, savings.items, {}, struct {
            fn lessThan(_: void, a: Saving, b: Saving) bool {
                return a.s > b.s;
            }
        }.lessThan);
        
        // 3. Merge routes
        for (savings.items) |saving| {
            const r_i_idx = in_route[saving.i];
            const r_j_idx = in_route[saving.j];
            
            if (r_i_idx == r_j_idx) continue;
            
            const r_i = routes.items[r_i_idx];
            const r_j = routes.items[r_j_idx];
            
            // Check capacity
            if (r_i.load + r_j.load > problem.capacity) continue;
            
            // Ensure i and j are adjacent to depot
            const i_at_end = r_i.nodes[r_i.nodes.len - 2] == saving.i;
            const j_at_start = r_j.nodes[1] == saving.j;
            
            if (i_at_end and j_at_start) {
                // Merge r_j into r_i
                var new_nodes = try self.alloc.alloc(usize, r_i.nodes.len + r_j.nodes.len - 2);
                @memcpy(new_nodes[0..r_i.nodes.len - 1], r_i.nodes[0..r_i.nodes.len - 1]);
                @memcpy(new_nodes[r_i.nodes.len - 1..], r_j.nodes[1..]);
                
                const new_dist = r_i.distance + r_j.distance - saving.s;
                
                // Update r_i
                self.alloc.free(r_i.nodes);
                routes.items[r_i_idx].nodes = new_nodes;
                routes.items[r_i_idx].load += r_j.load;
                routes.items[r_i_idx].distance = new_dist;
                
                // Update map
                for (1..r_j.nodes.len - 1) |k| {
                    in_route[r_j.nodes[k]] = r_i_idx;
                }
                
                // Invalidate r_j
                self.alloc.free(r_j.nodes);
                routes.items[r_j_idx].nodes = &[_]usize{};
                total_dist -= saving.s;
            }
        }
        
        // 4. Clean up empty routes
        var final_routes = std.ArrayList(Route).init(self.alloc);
        for (routes.items) |r| {
            if (r.nodes.len > 0) {
                try final_routes.append(r);
            }
        }
        routes.deinit();
        
        return VRPSolution{
            .routes = try final_routes.toOwnedSlice(),
            .total_distance = total_dist,
        };
    }
};

test "Clarke-Wright VRP basic" {
    const alloc = std.testing.allocator;
    var solver = OmniVRPSolver.init(alloc);
    
    var customers = [_]Node{
        .{ .id = 1, .x = 0, .y = 10, .demand = 10 },
        .{ .id = 2, .x = 10, .y = 10, .demand = 10 },
        .{ .id = 3, .x = 10, .y = 0, .demand = 10 },
    };
    
    const problem = VRPProblem{
        .depot = .{ .id = 0, .x = 0, .y = 0, .demand = 0 },
        .customers = &customers,
        .capacity = 25,
    };
    
    var solution = try solver.solveSavings(&problem);
    defer solution.destroy(alloc);
    
    // Expect 2 routes because total demand (30) > capacity (25)
    try std.testing.expectEqual(@as(usize, 2), solution.routes.len);
}
