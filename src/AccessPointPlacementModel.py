
# coding: utf-8

# In[1]:

from gurobipy import *
import numpy as np
import csv


# In[14]:

model = Model("Coarse Model Linearized")

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
with open("../dat/source_demand.csv") as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        D_down.append(float(row[1]))
print(D_down)


#THIS CODE WILL NOT WORK UNTIL ALL INDECES MATCH
D_up = [50.0,50.0]
K = [30.0,30.0]

l = [[25.0,25.0],[25.0,25.0]]
L = [[25.0,25.0],[25.0,25.0]]
d = [[25.0,25.0],[25.0,25.0]]
lalpha = [[0.0,0.0],[0.0,0.0]]
Lalpha = [[0.0,0.0],[0.0,0.0]]
dalpha = [[0.0,0.0],[0.0,0.0]]

#Calculate d_ij^-alpha, l_ij^-alpha, L_ij^-alpha since Gurobi won't allow this directly
for i in range(2):
    for j in range(2):
        lalpha[i][j] = np.power(l[i][j],-alpha)
        Lalpha[i][j] = np.power(L[i][j],-alpha)
        if i == j:
            dalpha[i][j] = 0.0
        else:
            dalpha[i][j] = np.power(d[i][j],-alpha)

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
    model.addConstr(K[a]*z[a][a] >= D_down[a])
    model.addConstr(K[a]*v[a][a] >= D_up[a])
    #Equations 20,21
    model.addConstr(N*beta*y[a] + quicksum(lalpha[a][aprime]*beta*z[a][aprime] for aprime in range(0,a)) + 
                    quicksum(lalpha[a][aprime]*beta*z[a][aprime] for aprime in range(a+1,A)) <= dalpha[a][a])
    model.addConstr(N*beta*w[a] + quicksum(Lalpha[a][aprime]*beta*v[a][aprime] for aprime in range(0,a)) + 
                    quicksum(Lalpha[a][aprime]*beta*v[a][aprime] for aprime in range(a+1,A)) <= dalpha[a][a])
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


# In[15]:

model.optimize()


# In[ ]:



