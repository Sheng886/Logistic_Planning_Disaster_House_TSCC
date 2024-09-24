import pandas
import numpy as np
import math
import csv

scenarios = 5

k_neighbor = 4

mean_1 = 0.5037691
mean_2 = 0.5036693
min_1 = -0.3640831
st_1 = 0.01035242
st_2 = 0.008703158
min_2 = -0.4216035

lambda_1 = 0.71134
lambda_2 = 0.75294

sigma_1 = 0.20684
sigma_2 = 0.20695

fit_ian = pandas.read_csv('fit_ian.csv')
neighbors= pandas.read_csv('adjacent_county_ian.csv')

fit_1 = fit_ian["fit_trailer"].to_numpy()
fit_2 = fit_ian["fit_MHU"].to_numpy()

adjacent_matrix = np.zeros((67,67))
for i in range(0,67):
	adjacent_matrix[i][neighbors["n1"][i]-1] = 1/k_neighbor
	adjacent_matrix[i][neighbors["n2"][i]-1] = 1/k_neighbor
	adjacent_matrix[i][neighbors["n3"][i]-1] = 1/k_neighbor
	adjacent_matrix[i][neighbors["n4"][i]-1] = 1/k_neighbor


output_1_demand = np.zeros((scenarios,67))
output_2_demand = np.zeros((scenarios,67))

for k in range(0,scenarios):
	error_1 = np.random.normal(0, sigma_1, 67)
	error_2 = np.random.normal(0, sigma_2, 67)

	y_1 = fit_1 + np.matmul((np.identity(67) - lambda_1*adjacent_matrix),error_1)
	y_2 = fit_2 + np.matmul((np.identity(67) - lambda_2*adjacent_matrix),error_2)

	demand_1 = ((np.sign(y_1))*(np.abs(y_1))**(1/0.3030303) - 1e-9 + min_1)*st_1 + mean_1
	demand_2 = ((np.sign(y_2))*(np.abs(y_2))**(1/0.222222) - 1e-9 + min_2)*st_2 + mean_2

	demand_1 = np.log(demand_1) - np.log(1 - demand_1)
	demand_2 = np.log(demand_2) - np.log(1 - demand_2)

	for i in range(0,67):
		if(demand_1[i] <= 0):
			demand_1[i] = 0
		if(demand_2[i] <= 0):
			demand_2[i] = 0

	for j in range(0,67):
		output_1_demand[k][j] = demand_1[j]
		output_2_demand[k][j] = demand_2[j]

np.savetxt("trailer_demand.txt",np.transpose(output_1_demand))
np.savetxt("MHU_demand.txt",np.transpose(output_2_demand))







