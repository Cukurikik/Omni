# OMNI Optimization — Gurobi Cloud Cost Minimizer
# Mathematical optimization model for distributing workloads across clouds

import gurobipy as gp
from gurobipy import GRB

def optimize_cloud_deployment():
    try:
        # Create a new model
        m = gp.Model("omni_cloud_cost_minimization")
        m.Params.LogToConsole = 0

        # Clouds: 0=AWS, 1=GCP, 2=Azure
        num_clouds = 3
        # Workloads (e.g., Inference, Training, Storage)
        num_workloads = 3

        # Cost matrix: cost to run workload j on cloud i
        costs = [
            [10.0, 50.0, 2.0], # AWS costs
            [12.0, 45.0, 2.5], # GCP costs
            [11.0, 48.0, 1.8]  # Azure costs
        ]

        # Variables: x[i,j] is 1 if workload j is assigned to cloud i
        x = m.addVars(num_clouds, num_workloads, vtype=GRB.BINARY, name="x")

        # Objective: Minimize total cost
        m.setObjective(
            gp.quicksum(costs[i][j] * x[i, j] for i in range(num_clouds) for j in range(num_workloads)), 
            GRB.MINIMIZE
        )

        # Constraint: Each workload must be assigned to exactly one cloud
        for j in range(num_workloads):
            m.addConstr(gp.quicksum(x[i, j] for i in range(num_clouds)) == 1, name=f"assign_{j}")

        # Optimize
        m.optimize()

        if m.status == GRB.OPTIMAL:
            print(f"Optimal Total Cost: ${m.objVal}")
            for j in range(num_workloads):
                for i in range(num_clouds):
                    if x[i, j].x > 0.5:
                        print(f"Workload {j} assigned to Cloud {i}")

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")

if __name__ == "__main__":
    optimize_cloud_deployment()
