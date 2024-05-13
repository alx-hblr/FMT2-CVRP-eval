from z3 import *
from problem import *

depot = data["depot"]
num_vehicles = data["num_vehicles"]
vehicle_capacity = data["vehicle_capacity"][0]
demands = data["demand"]
num_customers = len(demands) -1 
distances = data["distance_matrix"]

solver = Optimize()
print("generating a list of Variables...")

# Generate list of Variables
x = {}
u = {}
for i in range(num_customers + 1):
    for j in range(num_customers + 1):
        # skip travel to itsself
        if i != j:
            for k in range(num_vehicles):
                x[i, j, k] = Bool(f"x_{i}_{j}_{k}")
    if i != depot:  
        # Auxiliary variables for MTZ constraints, not defined for the depot
        u[i] = Int(f"u_{i}")

print(f"number of customers: {len(u)}")
print(f"number of derived variables: {len(x)}")
print("minimizing total distance")

# Objective: minimize total distance
solver.minimize(
    Sum([x[i, j, k] * distances[i][j] 
         for i in range(num_customers + 1) 
         for j in range(num_customers + 1) if i != j 
         for k in range(num_vehicles)]))

print("adding constraints")

# Constraints
# Each customer is visited exactly once by exactly one vehicel
for j in range(1, num_customers + 1):
    solver.add(
        Sum([x[i, j, k]
            for i in range(num_customers + 1) if i != j
            for k in range(num_vehicles)]) == 1
        )

for i in range(1, num_customers + 1):
    for j in range(1, num_customers + 1):
        if i != j:
            for k in range(num_vehicles):
                solver.add(Implies(x[i, j, k], u[i] + 1 == u[j]))

# Demand and vehicle capacity constraints
for k in range(num_vehicles):
    solver.add(Sum([demands[j] * x[i, j, k] 
        for i in range(num_customers + 1)
        for j in range(1, num_customers + 1) if i != j]) <= vehicle_capacity)

print("solving CVRP...")

# Solve the problem
if solver.check() == sat:
    model = solver.model()
    for k in range(num_vehicles):
        for i in range(num_customers + 1):
            for j in range(num_customers + 1):
                if i != j and model.evaluate(x[i, j, k]):
                    print(f"Vehicle {k} travels from {i} to {j}")
else:
    print("No solution found")
