# Blood Transshipment Optimization Model

This repository contains a Python-based optimization model for managing blood transshipment across a healthcare supply chain. The model minimizes transportation and fixed costs while ensuring demand satisfaction and capacity constraints across multiple network levels.

## Problem Overview
The network consists of:
- Mobile blood collection centers
- Local blood banks
- Central blood banks
- Hospitals
- Clinics

Blood units are transported through this network while accounting for:
- Capacity limits
- Clinic demand requirements
- Deterioration of blood during transport
- Fixed and variable transportation costs

## Methodology
- Linear Programming (LP)
- Binary decision variables for route activation
- Continuous variables for flow quantities
- Network flow visualization using NetworkX

## Technologies Used
- Python
- PuLP (Linear Programming)
- NumPy
- NetworkX
- Matplotlib

