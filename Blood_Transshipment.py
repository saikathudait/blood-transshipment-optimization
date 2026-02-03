#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pulp
import math
import numpy as np
import networkx as nx
from pulp import *
import matplotlib.pyplot as plt


# In[2]:


model = LpProblem("Blood_Transshipment", LpMinimize)

model1 = LpProblem("Blood_Transshipment", LpMinimize)

# #### Define Nodes

# In[3]:


mobile_centers = [1, 2, 3, 4, 5, 6]
local_banks = [7, 8, 9, 10]
central_banks = [11, 12]
hospitals = [13, 14, 15, 16]
clinics = [17, 18, 19, 20, 21, 22]


# #### Supply at mobile centers

# In[4]:


supply = {1: 30, 2: 40, 3: 70, 4: 50, 5: 35, 6: 60}


# #### Local bank capacities

# In[5]:


local_bank_capacities = {7: 90, 8: 80, 9: 55, 10: 50}


# #### Central bank capacities

# In[6]:


central_bank_capacities = {11: 100, 12: 130}


# #### Hospital capacities

# In[7]:


hospital_capacities = {13: 60, 14: 60, 15: 45, 16: 35}


# #### Clinic demands

# In[8]:


clinic_demands = {17: 30, 18: 35, 19: 15, 20: 25, 21: 20, 22: 10}

beta_weeks = 2
t_max = beta_weeks * 7


# #### Define Valid Links

# In[9]:


arcs = []


# In[10]:


for i in mobile_centers:
    for j in local_banks:
        arcs.append((i, j))


# In[11]:


for i in local_banks:
    for j in central_banks:
        arcs.append((i, j))


# In[12]:


for i in central_banks:
    for j in list(hospitals):
        arcs.append((i, j))


# In[13]:


for i in hospitals:
    for j in list(clinics):
        arcs.append((i, j))



        
def transfer_time(i, j):
    return abs(i - j)

z = LpVariable.dicts("time_path", arcs, cat='Binary')

# #### Helper Functions

# In[14]:


def fixed_cost(i, j):
    return 10 * abs(i - j) + 5 * abs(math.cos(i * j))

def variable_cost(i, j):
    return 0.5 * abs(i - j) + 0.25 * abs(math.sin(i * j))

def deterioration_factor(i, j):
    return (10 * i + j) / (i * j * 40)

def max_transport(i, j):
    return 200 


# #### Decision Variables

# In[15]:


x = LpVariable.dicts("flow", arcs, lowBound=0)
y = LpVariable.dicts("use_arc", arcs, cat='Binary')


# #### Objective Function

# In[16]:


model += pulp.lpSum(fixed_cost(i, j) * y[i, j] + variable_cost(i, j) * x[i, j] for i, j in arcs)


### Bonus Section Starts ###
model1 += pulp.lpSum(fixed_cost(i, j) * y[i, j] + variable_cost(i, j) * x[i, j] for i, j in arcs)


for (i, j) in arcs:
    # Only consider flows to clinics
    if j in clinics:
        model1 += x[i, j] <= t_max * y[i, j] 
        
for (i, j) in arcs:
    # Only consider flows to clinics
    if j in clinics:
        model1 += x[i, j] <= t_max * y[i, j] 
        
### Bonus Section Ends ###

# #### Supply Constraints for Mobile Centers

# In[17]:


for i in mobile_centers:
    model += pulp.lpSum(x[i, j] for j in local_banks if (i, j) in x) <= supply[i]


# #### Local Bank Constraints

# In[18]:


for j in local_banks:
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in mobile_centers if (i, j) in x) <= local_bank_capacities[j]
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in mobile_centers if (i, j) in x) == \
            pulp.lpSum(x[j, k] for k in central_banks if (j, k) in x)


# #### Central Bank Constraints

# In[19]:


for j in central_banks:
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in local_banks if (i, j) in x) <= central_bank_capacities[j]
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in local_banks if (i, j) in x) == \
            pulp.lpSum(x[j, k] for k in hospitals if (j, k) in x)


# #### Hospital Constraints

# In[20]:


for j in hospitals:
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in central_banks if (i, j) in x) <= hospital_capacities[j]
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in central_banks if (i, j) in x) == \
            pulp.lpSum(x[j, k] for k in clinics if (j, k) in x)


# #### Clinic Demand Constraints

# In[21]:


for j in clinics:
    model += pulp.lpSum(x[i, j] * (1 - deterioration_factor(i, j))
                       for i in hospitals if (i, j) in x) == clinic_demands[j]


# #### Binary Constraints for Fixed Costs

# In[22]:


for i, j in arcs:
    model += x[i, j] <= max_transport(i, j) * y[i, j]


# In[23]:


model.solve()


# #### Output

# In[24]:


print(f"Status: {LpStatus[model.status]}")
print(f"Optimal Total Cost: ${value(model.objective):.2f}")

print("\nOptimal Flow Quantities:")
optimal_flows = []
for (i, j) in arcs:
    if value(x[i, j]) > 0.01:
        flow_value = value(x[i, j])
        print(f"From Node {i} to Node {j}: {flow_value:.2f} units")
        optimal_flows.append((i, j, flow_value))


# #### Network Graph

# In[26]:


mobile_center_color = "lightblue"
local_bank_color = "lightgreen"
central_bank_color = "pink"
hospital_color = "orange"
clinic_color = "yellow"

G = nx.DiGraph()
nodes = mobile_centers + local_banks + central_banks + hospitals + clinics
G.add_nodes_from(nodes)

for i, j, flow in optimal_flows:
    G.add_edge(i, j, weight=flow)

pos = {}
column_spacing = 8  
row_spacing = 4     

for idx, node in enumerate(mobile_centers):
    pos[node] = (0, -idx * row_spacing)

for idx, node in enumerate(local_banks):
    pos[node] = (column_spacing, -idx * row_spacing)

for idx, node in enumerate(central_banks):
    pos[node] = (2 * column_spacing, -idx * row_spacing)

for idx, node in enumerate(hospitals):
    pos[node] = (3 * column_spacing, -idx * row_spacing)

for idx, node in enumerate(clinics):
    pos[node] = (4 * column_spacing, -idx * row_spacing)

node_colors = []
for node in G.nodes():
    if node in mobile_centers:
        node_colors.append(mobile_center_color)
    elif node in local_banks:
        node_colors.append(local_bank_color)
    elif node in central_banks:
        node_colors.append(central_bank_color)
    elif node in hospitals:
        node_colors.append(hospital_color)
    elif node in clinics:
        node_colors.append(clinic_color)

plt.figure(figsize=(14, 8))
nx.draw_networkx_nodes(G, pos, node_size=500, node_color=node_colors)  
nx.draw_networkx_labels(G, pos, font_size=8)
nx.draw_networkx_edges(G, pos, edgelist=[(i, j) for i, j, _ in optimal_flows], edge_color="black", arrows=True)

edge_labels = {(i, j): f"{flow:.1f}" for i, j, flow in optimal_flows}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")

import matplotlib.pyplot as plt

plt.legend(
    handles=[
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=mobile_center_color, markersize=10, label="Mobile Center"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=local_bank_color, markersize=10, label="Local Bank"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=central_bank_color, markersize=10, label="Central Bank"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=hospital_color, markersize=10, label="Hospital"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=clinic_color, markersize=10, label="Clinic")
    ],
    loc="center left",
    bbox_to_anchor=(1.0, 0.9)  
)

plt.title("Blood Transshipment Network (Optimal Flow)")
plt.axis("off")
plt.show()


# In[ ]:




