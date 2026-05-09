/// OMNI Swarm Physics Simulator
/// Fast 2D rigid body physics for multi-agent environments.

pub struct SwarmPhysicsSimulator {
    dt: f32,
    num_agents: usize,
    positions: Vec<[f32; 2]>,
    velocities: Vec<[f32; 2]>,
}

impl SwarmPhysicsSimulator {
    pub fn new(num_agents: usize, dt: f32) -> Self {
        Self {
            dt,
            num_agents,
            positions: vec![[0.0, 0.0]; num_agents],
            velocities: vec![[0.0, 0.0]; num_agents],
        }
    }

    pub fn set_positions(&mut self, positions: Vec<[f32; 2]>) {
        if positions.len() == self.num_agents {
            self.positions = positions;
        }
    }

    pub fn step(&mut self, actions: &[[f32; 2]]) -> Result<Vec<[f32; 2]>, &'static str> {
        if actions.len() != self.num_agents {
            return Err("Action array length mismatch");
        }

        for i in 0..self.num_agents {
            // Apply acceleration (action)
            self.velocities[i][0] += actions[i][0] * self.dt;
            self.velocities[i][1] += actions[i][1] * self.dt;

            // Apply velocity to position
            self.positions[i][0] += self.velocities[i][0] * self.dt;
            self.positions[i][1] += self.velocities[i][1] * self.dt;
            
            // Simple friction
            self.velocities[i][0] *= 0.95;
            self.velocities[i][1] *= 0.95;
        }

        Ok(self.positions.clone())
    }
}
