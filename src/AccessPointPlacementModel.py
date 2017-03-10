from gurobipy import *
import numpy as np
import csv

A = 2
N = 12.0
Q = 1
alpha = 2.0
beta = 5.0
x = {}
y = {}
w = {}
v = {}
z = {}
D_down = []
D_up = []
min_dist = []
max_dist = []
avg_dist = []
lalpha = [[0 for i in range(A)] for j in range(A)]
Lalpha = [[0 for i in range(A)] for j in range(A)]
dalpha = [[0 for i in range(A)] for j in range(A)]
K = [30.0,30.0]

with open("../dat/source_demand.csv") as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        D_down.append((row[0],float(row[1])))
print(D_down)
with open("../dat/access_data.csv") as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        D_up.append((row[0],row[1],float(row[2])))
with open("../dat/distances.csv") as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        min_dist.append((row[0],row[1],float(row[3])))
        max_dist.append((row[0],row[1],float(row[4])))
        med_dist.append((row[0],row[1],float(row[2])))
with open("../dat/clients.csv") as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        avg_dist.append((row[0],float(row[1])))

#THIS CODE DOES NOT YET PROVIDE A CORRECT SOLUTION TO ANYTHING, IT ONLY WORKS

#Calculate d_ij^-alpha, l_ij^-alpha, L_ij^-alpha since Gurobi won't allow this directly
for i in range(len(min_dist)):
    for j in range(len(min_dist)):
        if max_dist[i][0] == max_dist[i][1] or min_dist[i][0] == min_dist[i][1] or med_dist[i][0] == med_dist[i][1] or avg_dist[i][0] == avg_dist[i][1]:
            dpalpha[i][j] = (max_dist[i][0],max_dist[i][1],0.0)
            lalpha[i][j] = (min_dist[i][0],min_dist[i][1],0.0)
            Lalpha[i][j] = (med_dist[i][0],med_dist[i][1],0.0)
        else:
            dpalpha[i][j] = (max_dist[i][0],max_dist[i][1],np.power(max_dist[i][2],-alpha))
            lalpha[i][j] = (min_dist[i][0],min_dist[i][1],np.power(min_dist[i][2],-alpha))
            Lalpha[i][j] = (med_dist[i][0],med_dist[i][1],np.power(med_dist[i][2],-alpha))
for i in range(avg_dist):
    dalpha[i] = (avg_dist[i][0],np.power(avg_dist[i][1],-alpha))

model = Model("Coarse Model Linearized")

#Create the variables
for a in range(A):
    x[a] = model.addVar(vtype=GRB.INTEGER, lb = 1, name="x"+str(a))
    y[a] = model.addVar(vtype=GRB.BINARY, name="y"+str(a))
    w[a] = model.addVar(vtype=GRB.BINARY, name="w"+str(a))
    v[a] = {}
    z[a] = {}
    for aprime in range(A):
        v[a][aprime] = model.addVar(vtype=GRB.INTEGER, lb = 0, name="v"+str(a)+str(aprime))
        z[a][aprime] = model.addVar(vtype=GRB.INTEGER, lb = 0, name="z"+str(a)+str(aprime))
model.update()

#Define the objective function
model.setObjective(quicksum(x[a] for a in range(A)), GRB.MINIMIZE)
model.update()

#Set the constraints
for a in range(A):
    #Equations 18,19
    model.addConstr(K[a]*z[a][a] >= D_down[a][1])
    model.addConstr(K[a]*v[a][a] >= D_up[a][2])
    #Equations 20,21
    model.addConstr(N*beta*y[a] + quicksum(lalpha[a][aprime][2]*beta*z[a][aprime] for aprime in range(0,a)) +
                    quicksum(lalpha[a][aprime][2]*beta*z[a][aprime] for aprime in range(a+1,A)) <= dalpha[a][1])
    model.addConstr(N*beta*w[a] + quicksum(Lalpha[a][aprime][2]*beta*v[a][aprime] for aprime in range(0,a)) +
                    quicksum(Lalpha[a][aprime][2]*beta*v[a][aprime] for aprime in range(a+1,A)) <= dalpha[a][1])
    #Equations 22-29; Equations 25 and 29 are handled by the lower bound of the variables
    for aprime in range(A):
        if aprime != a:
            model.addConstr(z[a][aprime] <= x[aprime])
            model.addConstr(z[a][aprime] <= y[a])
            model.addConstr(z[a][aprime] >= x[aprime] - (1.0 - y[a])*Q)
            model.addConstr(v[a][aprime] <= x[aprime])
            model.addConstr(v[a][aprime] <= y[a])
            model.addConstr(v[a][aprime] >= x[aprime] - (1.0 - w[a])*Q)
model.update()
model.optimize()


# In[ ]:



