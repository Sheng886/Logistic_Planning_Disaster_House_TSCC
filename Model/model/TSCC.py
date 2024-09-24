from model import func
from arguments import Arguments
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

class two_stage_chance():
    def __init__(self, args):

        self.args = args
        # import pdb;pdb.set_trace()

        ### ------------------ Transportation price ------------------ ### 
        self.trans_price = args.trans_cost

        ### ------------------ House Information ------------------ ###

        df = pd.read_excel(args.House_Info_path)

        self.house_name = list(df.columns)
        self.house_name = self.house_name[1:]

        self.house_price = np.zeros(args.P)
        self.house_volumn_factor = np.zeros(args.P)
        self.house_install_time = np.zeros(args.P)
        

        for i in range(0,args.P):
        	self.house_price[i] = df[self.house_name[i]][1]
        	self.house_volumn_factor[i] = df[self.house_name[i]][2]
        	self.house_install_time[i] = df[self.house_name[i]][3]

        df = pd.read_excel(args.House_Match)

        self.house_0_match = np.zeros(args.P)

        for i in range(1,args.P):
            self.house_0_match[i] = df[self.house_name[i]][0]


        ### ------------------ Deprivation Cost Function ------------------ ###

        df = pd.read_excel(args.Deprivation_Penalty_path)
        self.deprivation_a0 = df["a_0"]
        self.deprivation_a1 = df["a_1"]

        ### ------------------ Mismatch Penalty ------------------ ###

        df = pd.read_excel(args.Mismatch_Penalty_path)
        self.group_name = list(df.columns)
        self.group_name = self.group_name[1:]
        self.mismatch = np.zeros((args.P-1,args.G))
        for i in range (0,args.P-1):
        	for j in range(0,args.G):
        		self.mismatch[i][j] = df[self.group_name[j]][i]

        ### ------------------ Unmet Penalty ------------------ ###

        df = pd.read_excel(args.Unmet_Penalty_path)
        unmet_column = list(df.columns)
        self.unmet = np.zeros(args.G)
        for g in range(0,args.G):
        	self.unmet[g] = df[unmet_column[g]][0]

        ### ------------------ Unused Inventory Penalty ------------------ ###

        df = pd.read_excel(args.Unused_Inventory_Penalty_path)
        unused_column = list(df.columns)
        self.unused = np.zeros(args.P)
        for p in range(0,args.P):
        	self.unused[p] = df[unused_column[p]][0]

        ### ------------------ Staging Area ------------------ ###
        
        df = pd.read_excel(args.Staging_Area_path)
        staging_area_column = list(df.columns)
        staging_area_location = df[['latitude','longitude']]
        self.staging_area_capacity = np.zeros(args.W)
        self.high_staging_area_flow = np.zeros(args.W)
        self.mid_staging_area_flow = np.zeros(args.W)
        self.low_staging_area_flow = np.zeros(args.W)
        for i in range(0,args.W):
            self.staging_area_capacity[i] = df[staging_area_column[2]][i]
            self.high_staging_area_flow[i] = df[staging_area_column[3]][i]
            self.mid_staging_area_flow[i] = df[staging_area_column[4]][i]
            self.low_staging_area_flow[i] = df[staging_area_column[5]][i]

        ### ------------------ Scenario Generation ------------------ ###
        # func.scenario_generation(args, args.K)


        ### ------------------ Study Region ------------------ ###

        df = pd.read_excel(args.Study_Region_path)
        study_region_column = list(df.columns)
        study_region_location = df[['latitude','longitude']]
        self.homeowner_occupied = np.zeros(args.J)
        self.demand_per_trailer = np.loadtxt(args.Demand_Trailer_path)
        self.demand_per_MHU = np.loadtxt(args.Demand_MHU_path)
        for j in range(0,args.J):
            self.homeowner_occupied[j] = df[study_region_column[5]][j]
            for k in range(0,args.K):
                self.demand_per_trailer[k][j] = self.homeowner_occupied[j]*self.demand_per_trailer[k][j]
                self.demand_per_MHU[k][j] = self.homeowner_occupied[j]*self.demand_per_MHU[k][j]
        
        # np.savetxt("trailer_50.txt",self.demand_per_trailer)
        # np.savetxt("MHU_50.txt",self.demand_per_MHU)

        self.demand_per_trailer = np.loadtxt("test_data/trailer_50.txt")
        self.demand_per_MHU = np.loadtxt("test_data/MHU_50.txt")

        # self.demand_per_trailer = np.loadtxt("sc_50_type1.txt").transpose()
        # self.demand_per_MHU = np.loadtxt("sc_50_type2.txt").transpose()

        # import pdb;pdb.set_trace()

        self. demand = np.stack((self.demand_per_trailer,self.demand_per_MHU),axis=1)


        ### ------------------ Supply ------------------ ###

        df = pd.read_excel(args.Supplier_path)
        supplier_column = list(df.columns)
        supplier_location = df[['latitude','longitude']]
        self.supplier_price = np.zeros((args.I,args.P))
        self.high_supplier_inventory = np.zeros((args.I,args.P))
        self.mid_supplier_inventory = np.zeros((args.I,args.P))
        self.low_supplier_inventory = np.zeros((args.I,args.P))
        self.high_supplier_prod_time = np.zeros((args.I,args.P))
        self.mid_supplier_prod_time = np.zeros((args.I,args.P))
        self.low_supplier_prod_time = np.zeros((args.I,args.P))
        self.num_production_line = np.zeros(args.I)
        self.extra_production_line = np.zeros(args.I)
        self.high_supplier_flow = np.zeros(args.I)
        self.mid_supplier_flow = np.zeros(args.I)
        self.low_supplier_flow = np.zeros(args.I)
        for i in range(0,args.I):
            self.num_production_line[i] = df[supplier_column[24]][i]
            self.extra_production_line[i] = df[supplier_column[25]][i]
            self.high_supplier_flow[i] = df[supplier_column[26]][i]
            self.mid_supplier_flow[i] = df[supplier_column[27]][i]
            self.low_supplier_flow[i] = df[supplier_column[28]][i]
            for p in range(0, args.P):
            	self.supplier_price[i][p] = df[supplier_column[3+p]][i]
            	self.mid_supplier_inventory[i][p] = df[supplier_column[6+p]][i]
            	self.high_supplier_inventory[i][p] = df[supplier_column[12+p]][i]
            	self.low_supplier_inventory[i][p] = df[supplier_column[9+p]][i]
            	self.high_supplier_prod_time[i][p] = df[supplier_column[15+p]][i]
            	self.mid_supplier_prod_time[i][p] = df[supplier_column[18+p]][i]
            	self.low_supplier_prod_time[i][p] = df[supplier_column[21+p]][i]

        ### ------------------ time point ------------------ ###

        df = pd.read_excel(args.Timepoint_path)
        self.first_end_time_point = df["First_End"][0]
        self.deprivation_time_point = df["Deprivation_Start"][0]
        self.second_end_time_point = df["Second_End"][0]

        
        ### ------------------ distance matrix ------------------ ###

        self.supplier_area_distance = func.distance_matrix(supplier_location,staging_area_location)
        self.area_region_distance = func.distance_matrix(staging_area_location,study_region_location)
        self.supplier_region_distance = func.distance_matrix(supplier_location,study_region_location)

        ### ------------------ Model ------------------ ###

        # self.demand[0][0][0] = 100000

        self.model = gp.Model("TSCC_model")

        # First-stage
        self.x = self.model.addVars(args.I, args.W, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Xiwpt')
        self.s = self.model.addVars(args.I, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Sipt')
        self.m = self.model.addVars(args.W, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Mwpt')
        self.v = self.model.addVars(args.I, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Vipt')
        self.a = self.model.addVars(args.I, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Awpt')
        self.z = self.model.addVars(args.K, vtype=GRB.BINARY, name='Zk')

        # Second-stage
        self.vk = self.model.addVars(args.K, args.I, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Vk_ipt')
        self.nuk = self.model.addVars(args.K, args.I, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Nuk_ipt')
        self.fk_ij = self.model.addVars(args.K, args.I, args.J, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Fk_ijpt')
        self.fk_wj = self.model.addVars(args.K, args.W, args.J, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Fk_wjpt')
        self.fk0_j = self.model.addVars(args.K, args.J, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Fk0_jpt')
        self.yk = self.model.addVars(args.K, args.J, args.P, args.G, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='yk_jpgt')
        self.mk = self.model.addVars(args.K, args.W, args.P, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='Mk_wpt')
        self.bk = self.model.addVars(args.K, args.I, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='bk_it')
        self.dk = self.model.addVars(args.K, args.J, args.G, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='dk_jgt')
        self.qk = self.model.addVars(args.K, args.J, args.G, args.T, lb=0.0, vtype=GRB.CONTINUOUS, name='qk_jgt')


        # Objective
        self.model.setObjective(sum((self.supplier_price[i][p] + self.supplier_area_distance[i][w]*self.house_volumn_factor[p]*self.trans_price)*self.x[i,w,p,t] for i in range(args.I) for w in range(args.W) for p in range(args.P) for t in range(args.T))
                              + (1/args.K)*(sum(self.area_region_distance[w][j]*self.house_volumn_factor[p]*self.trans_price*self.fk_wj[k,w,j,p,t] for k in range(args.K) for w in range(args.W) for j in range(args.J) for p in range(args.P) for t in range(self.first_end_time_point,args.T))
                                + sum(self.unmet[g]*self.house_price[g+1]*(self.qk[k,j,g,args.T-1]) for k in range(args.K) for j in range(args.J) for g in range(args.G))
                                + sum((self.mismatch[p-1][g])*self.house_price[p]*self.yk[k,j,p,g,t] for k in range(args.K) for j in range(args.J) for p in range(1,args.P) for g in range(args.G) for t in range(self.first_end_time_point,args.T))
                                + sum(self.unused[p]*self.house_price[p]*self.mk[k,w,p,args.T-1] for k in range(args.K) for w in range(args.W) for p in range(args.P))
                                + sum((self.deprivation_a0[0] + self.deprivation_a1[0]*(args.T-t))*self.house_price[g+1]*(self.qk[k,j,g,t]) for k in range(args.K) for j in range(args.J) for t in range(self.deprivation_time_point,args.T) for g in range(args.G))
                                + sum((args.emergency_price_factor*self.house_price[p] + self.supplier_region_distance[i][j]*self.house_volumn_factor[p]*self.trans_price)*self.fk_ij[k,i,j,p,t] for k in range(args.K) for i in range(args.I) for j in range(args.J) for t in range(self.first_end_time_point,args.T) for p in range(args.P))
                                 ),GRB.MINIMIZE);

        # self.model.setObjective(1 ,GRB.MINIMIZE);


        # no second-stage decision will be made before T^H
        for k in range(args.K):
            for i in range(args.I):
                for p in range(args.P):
                    for t in range(0,self.first_end_time_point):
                        self.model.addConstr(self.vk[k,i,p,t] == 0)
                        self.model.addConstr(self.nuk[k,i,p,t] == 0)

        for k in range(args.K):
            for w in range(args.W):
                for j in range(args.J):
                    for p in range(args.P):
                        for t in range(0,self.first_end_time_point):
                            self.model.addConstr(self.fk_wj[k,w,j,p,t] == 0)

        for k in range(args.K):
            for j in range(args.J):
                for p in range(args.P):
                    for t in range(0,self.first_end_time_point):
                        self.model.addConstr(self.fk0_j[k,j,p,t] == 0)

        for i in range(args.I):
            for k in range(args.K):
                for j in range(args.J):
                    for p in range(args.P):
                        for t in range(0,self.first_end_time_point):
                            self.model.addConstr(self.fk_ij[k,i,j,p,t] == 0)

        for k in range(args.K):
            for j in range(args.J):
                for p in range(args.P):
                    for g in range(args.G):
                        self.model.addConstr(self.yk[k,j,p,g,args.T-1] == 0)
                        for t in range(0,self.first_end_time_point):
                            self.model.addConstr(self.yk[k,j,p,g,t] == 0)

        for k in range(args.K):
            for w in range(args.W):
                for p in range(args.P):
                    for t in range(0,self.first_end_time_point):
                        self.model.addConstr(self.mk[k,w,p,t] == 0)

        for k in range(args.K):
            for i in range(args.I):
                for t in range(0,self.first_end_time_point):
                    self.model.addConstr(self.bk[k,i,t] == 0)

        for k in range(args.K):
            for j in range(args.J):
                for g in range(args.G):
                    for t in range(0,self.first_end_time_point):
                        self.model.addConstr(self.dk[k,j,g,t] == 0)
                        self.model.addConstr(self.qk[k,j,g,t] == 0)

        for w in range(args.W):
            for p in range(args.P):
                self.model.addConstr(self.m[w,p,0] == 0)

        # Recovery plan constraint
        self.model.addConstr(sum(self.z[k] for k in range(args.K)) <= args.error)

            
        # Initial Machine Capacity && Machine used flow && Every time unit Machine Capacity
        for i in range(args.I):
            self.model.addConstr(self.a[i,0] == 0)
            for t in range(args.T-1):
                self.model.addConstr(self.a[i,t+1] + sum(self.s[i,p,t-self.mid_supplier_prod_time[i][p]] for p in range(args.P) if t-self.mid_supplier_prod_time[i][p] >= 0) ==  sum(self.s[i,p,t] for p in range(args.P)) + self.a[i,t])
                self.model.addConstr(self.a[i,t] <= self.num_production_line[i])

        # Initial Inventory && Inventory flow
        for i in range(args.I):
            for p in range(args.P):
                self.model.addConstr(self.v[i,p,0] == self.mid_supplier_inventory[i][p])
                for t in range(args.T-1):
                    if(t-self.mid_supplier_prod_time[i][p] >= 0):
                        self.model.addConstr(self.v[i,p,t+1] + sum(self.x[i,w,p,t] for w in range(args.W)) ==  self.v[i,p,t] + self.s[i,p,t-self.mid_supplier_prod_time[i][p]])
                    else:
                        self.model.addConstr(self.v[i,p,t+1] + sum(self.x[i,w,p,t] for w in range(args.W)) ==  self.v[i,p,t] )

        # Second-stage Supplier initial Inventory
        for k in range(args.K):
            for i in range(args.I):
                for p in range(args.P):
                    self.model.addConstr(self.vk[k,i,p,self.first_end_time_point] == self.v[i,p,self.first_end_time_point])

        # Second-stage Supplier Inventory flow
        for k in range(args.K):
            for i in range(args.I):
                for p in range(args.P):
                    for t in range(self.first_end_time_point,args.T-1):
                        self.model.addConstr(self.vk[k,i,p,t+1] + sum(self.x[i,w,p,t] for w in range(args.W)) + sum(self.fk_ij[k,i,j,p,t] for j in range(args.J)) == self.vk[k,i,p,t] + self.nuk[k,i,p,t-self.low_supplier_prod_time[i][p]] + self.s[i,p,t-self.mid_supplier_prod_time[i][p]])
                        
                    
        # Supply sending flow
        for t in range(args.T):
            for i in range(args.I):
                self.model.addConstr(sum(self.house_volumn_factor[p]*self.x[i,w,p,t] for w in range(args.W) for p in range(args.P)) <= self.mid_supplier_flow[i])

        # First-stage Staging area inventory flow limitation
        for w in range(args.W): 
            for t in range(0,self.first_end_time_point):
                for p in range(args.P):
                    self.model.addConstr(self.m[w,p,t+1] == sum(self.x[i,w,p,t] for i in range(args.I)) + self.m[w,p,t])

        # Second-stage staging area initail inventory
        for w in range(args.W):
            for k in range(args.K):
                for p in range(args.P):
                    self.model.addConstr(self.mk[k,w,p,self.first_end_time_point] == self.m[w,p,self.first_end_time_point])

        #Second-stage stating area inventory flow
        for w in range(args.W):
            for p in range(args.P):
                for t in range(self.first_end_time_point,args.T-1):
                    for k in range(args.K):
                        self.model.addConstr(self.mk[k,w,p,t+1] + sum(self.fk_wj[k,w,j,p,t] for j in range(args.J)) == sum(self.x[i,w,p,t] for i in range(args.I)) + self.mk[k,w,p,t])

        # Statgin area Capacity
        for w in range(args.W):
            for t in range(0,self.first_end_time_point):
                self.model.addConstr(sum(self.house_volumn_factor[p]*self.m[w,p,t] for p in range(args.P)) <= self.staging_area_capacity[w])

        # Statgin area Capacity (second-stage)
        for w in range(args.W):
            for t in range(self.first_end_time_point,args.T):
                for k in range(args.K):
                    self.model.addConstr(sum(self.house_volumn_factor[p]*self.mk[k,w,p,t] for p in range(args.P)) <= self.staging_area_capacity[w])

        # second-stage staging area delivery flow
        for w in range(args.W):
            for t in range(self.first_end_time_point,args.T):
                for k in range(args.K):
                    self.model.addConstr(sum(self.house_volumn_factor[p]*self.fk_wj[k,w,j,p,t] for p in range(args.P) for j in range(args.J)) <= self.mid_staging_area_flow[w] + self.z[k]*sum(self.house_volumn_factor[g]*self.demand[k][g][j] for j in range(args.J) for g in range(args.G))) 


        # emergency production
        for i in range(args.I):
            for t in range(self.first_end_time_point,args.T-1):
                for k in range(args.K):
                    self.model.addConstr(self.bk[k,i,t] + sum(self.nuk[k,i,p,t-self.low_supplier_prod_time[i][p]] for p in range(args.P)) == sum(self.nuk[k,i,p,t] for p in range(args.P)) + self.bk[k,i,t+1]) 

        # extra production line in emergency modality
        for i in range(args.I):
            for t in range(self.first_end_time_point,args.T):
                for k in range(args.K):
                    self.model.addConstr(self.bk[k,i,t] <= self.z[k]*self.extra_production_line[i])

        
        # novel house match
        for j in range(args.J):
            for t in range(args.T):
                for k in range(args.K):
                    self.model.addConstr(sum(self.fk_ij[k,i,j,0,t] for i in range(args.I)) + sum(self.fk_wj[k,w,j,0,t] for w in range(args.W)) == sum(self.fk0_j[k,j,p,t+p*self.house_install_time[0]] for p in range(1,args.P) if t + p*self.house_install_time[0] <= args.T-1)) 

        # match flow
        for j in range(args.J):
            for t in range(self.first_end_time_point,args.T):
                for k in range(args.K):
                    for p in range(1,args.P):
                        self.model.addConstr(1/self.house_0_match[p]*self.fk0_j[k,j,p,t] + sum(self.fk_wj[k,w,j,p,t] for w in range(args.W)) + sum(self.fk_ij[k,i,j,p,t] for i in range(args.I)) == sum(self.yk[k,j,p,g,t] for g in range(args.G))) 

        # demand flow
        for j in range(args.J):
            for t in range(args.T-1):
                for g in range(args.G):
                    for k in range(args.K):
                        self.model.addConstr(self.dk[k,j,g,t+1] == self.dk[k,j,g,t] + sum(self.yk[k,j,p,g,t] for p in range(1,args.P)))

        # demand limitation
        for j in range(args.J):
                for k in range(args.K):
                    for g in range(args.G):
                        for t in range(self.first_end_time_point,args.T):
                            self.model.addConstr(self.dk[k,j,g,t] + self.qk[k,j,g,t] == self.demand[k][g][j])

        # big M
        for j in range(args.J):
            for i in range(args.I):
                for p in range(args.P):
                    for k in range(args.K):
                        for t in range(args.T):
                            self.model.addConstr(self.fk_ij[k,i,j,p,t] <= self.z[k]*sum(self.house_0_match[g+1]*self.demand[k][g][j] for g in range(args.G)))


        self.model.setParam("OutputFlag", 0)

    def run(self,args,xx=None,evaluation=False,name="TSCC.csv"):
        if(evaluation == True):
            for i in range(args.I):
                for w in range(args.W):
                    for p in range(args.P):
                        for t in range(args.T):
                            self.model.addConstr(self.x[i,w,p,t] == xx[i][w][p][t])

            for i in range(args.I):
                for p in range(args.P):
                    for t in range(args.T):
                        self.model.addConstr(self.s[i,p,t] == 0)
        
        # self.model.write("model.lp")
        self.model.update()
        self.model.optimize()

        print(self.model.ObjVal)



        if self.model.status == GRB.OPTIMAL:
            print(self.model.ObjVal)

            count = 0
            shortage_1 = 0
            shortage_2 = 0
            unmet_cost_1 = 0
            unmet_cost_2 = 0
            pre_0 = 0
            pre_1 = 0
            pre_2 = 0
            first_stage_cost = 0
            second_stage_trans = 0
            emergency_cost = 0
            unused_0 = 0
            unused_1 = 0
            unused_2 = 0
            unused_0_cost = 0
            unused_1_cost = 0
            unused_2_cost = 0
            mismatch_cost = 0
            deprivation_cost = 0

            
            for k in range(args.K):
                for j in range(args.J):
                    # print(self.demand[k][0][j],self.dk[k,j,0,args.T-1].x)
                    # print(self.demand[k][1][j],self.dk[k,j,1,args.T-1].x)
                    shortage_1 = shortage_1 + (1/args.K)*(self.demand[k][0][j] - self.dk[k,j,0,args.T-1].x)
                    unmet_cost_1 = unmet_cost_1 + (1/args.K)*self.unmet[0]*self.house_price[1]*(self.demand[k][0][j] - self.dk[k,j,0,args.T-1].x)
                    shortage_2 = shortage_2 + (1/args.K)*(self.demand[k][1][j] - self.dk[k,j,1,args.T-1].x)
                    unmet_cost_2 = unmet_cost_2 + (1/args.K)*self.unmet[1]*self.house_price[2]*(self.demand[k][1][j] - self.dk[k,j,1,args.T-1].x)
                                

            for k in range(args.K):
                for j in range(args.J):
                    for p in range(1,args.P):
                        for t in range(self.first_end_time_point,args.T):
                            for g in range(args.G):
                                mismatch_cost = mismatch_cost + (1/args.K)*(self.mismatch[p-1][g])*self.house_price[p]*self.yk[k,j,p,g,t].x
                                
            for i in range(args.I):
                for w in range(args.W):
                    for p in range(args.P):
                        for t in range(args.T):
                            first_stage_cost = first_stage_cost + (self.supplier_price[i][p] + self.supplier_area_distance[i][w]*self.house_volumn_factor[p]*self.trans_price)*self.x[i,w,p,t].x
                            

            for k in range(args.K):
                for w in range(args.W):
                    # print(self.mk[k,w,0,args.T-1].x,self.mk[k,w,1,args.T-1].x,self.mk[k,w,2,args.T-1].x)
                    unused_0 = unused_0 + (1/args.K)*self.mk[k,w,0,args.T-1].x
                    unused_0_cost = unused_0_cost + (1/args.K)*self.mk[k,w,0,args.T-1].x*self.unused[0]*self.house_price[0]
                    unused_1 = unused_1 + (1/args.K)*self.mk[k,w,1,args.T-1].x
                    unused_1_cost = unused_1_cost + (1/args.K)*self.mk[k,w,1,args.T-1].x*self.unused[1]*self.house_price[1]
                    unused_2 = unused_2 + (1/args.K)*self.mk[k,w,2,args.T-1].x
                    unused_2_cost = unused_2_cost + (1/args.K)*self.mk[k,w,2,args.T-1].x*self.unused[2]*self.house_price[2]
                    
            for k in range(args.K):
                for j in range(args.J):
                    for g in range(args.G):
                        for t in range(self.deprivation_time_point,args.T):
                            deprivation_cost = deprivation_cost + (1/args.K)*((self.deprivation_a0[0] + self.deprivation_a1[0]*(args.T-t))*self.house_price[g+1]*(self.demand[k][g][j]-self.dk[k,j,g,t].x))
                            
            for t in range(self.first_end_time_point,args.T):
                for k in range(args.K):
                    for w in range(args.W):
                        for j in range(args.J):
                            for p in range(args.P):
                                second_stage_trans = second_stage_trans + (1/args.K)*self.area_region_distance[w][j]*self.house_volumn_factor[p]*self.trans_price*self.fk_wj[k,w,j,p,t].x

            for p in range(args.P):
                for k in range(args.K):
                    for j in range(args.J):
                        for i in range(args.I):
                    	    for t in range(self.first_end_time_point,args.T):
                                # print(k,i,j,p,t,self.fk_ij[k,i,j,p,t].x)
                                emergency_cost = emergency_cost + (1/args.K)*(args.emergency_price_factor*self.house_price[p] + self.supplier_region_distance[i][j]*self.house_volumn_factor[p]*self.trans_price)*self.fk_ij[k,i,j,p,t].x
                            
            # for w in range(self.args.W):
            #     for p in range(self.args.P):
            #         for t in range(self.args.T):
            #             temp = temp + self.mk[0,w,p,t].x
            # print(temp)

            # temp = 0
            # for i in range(self.args.I):
            #     for w in range(self.args.W):
            #         for p in range(self.args.P):
            #             for t in range(self.args.T):
            #                 temp = temp + self.x[i,w,p,t].x
            # print(temp)


            # for i in range(self.args.I):
            #     for t in range(self.args.T):
            #         print("bk:",i,p,t,self.bk[0,i,t].x)

            # for i in range(self.args.I):
            #     for p in range(self.args.P):
            #         for t in range(self.args.T):
            #             print("nuk:",i,p,t,self.nuk[0,i,p,t].x)

            # for k in range(self.args.K):    
            #     for i in range(self.args.I):
            #         temp = 0
            #         for j in range(self.args.J):
            #             for p in range(self.args.P):
            #                 for t in range(self.args.T):
            #                     temp = temp + self.fk_ij[k,i,j,p,t].x
            #     print("fij:",k,i,j,p,temp)

            # print(sum(self.unmet[g]*self.house_price[g+1]*(self.demand[0][g][j] - self.dk[0,j,g,args.T-1].x) for j in range(args.J) for g in range(args.G)))
            # print(sum((self.mismatch[p-1][g])*self.house_price[p]*self.yk[0,j,p,g,t].x for j in range(args.J) for p in range(1,args.P) for g in range(args.G) for t in range(self.first_end_time_point,args.T)))
            # print(sum(self.unused[p]*self.house_price[p]*self.mk[k,w,p,args.T-1].x for w in range(args.W) for p in range(args.P)))
            # print(sum((self.deprivation_a0[0] + self.deprivation_a1[0]*(self.args.T-t))*self.house_price[g+1]*(self.demand[0][g][j]-self.dk[0,j,g,t].x) for j in range(self.args.J) for t in range(self.deprivation_time_point,self.args.T) for g in range(self.args.G)))           
            # print(sum((self.args.emergency_price_factor*self.house_price[p] + self.supplier_region_distance[i][j]*self.house_volumn_factor[p]*self.trans_price)*self.fk_ij[0,i,j,p,t].x for i in range(self.args.I) for j in range(self.args.J) for t in range(self.first_end_time_point,self.args.T) for p in range(self.args.P)))
   

            # import pdb;pdb.set_trace()

            # for k in range(args.K):
            #     temp1 = 0
            #     temp2 = 0
            #     for j in range(args.J):
            #         temp1 = temp1 + self.demand[k][0][j]
            #         temp2 = temp2 + self.demand[k][1][j]
            #     print(temp1,temp2)


            # flow = np.zeros((40,args.T))

            # for k in range(args.K):
            #     for p in range(args.P):
            #         print(k*3+p)
            #         for t in range(args.T):
            #             if(t <= self.first_end_time_point):
            #                 for w in range(args.W):
            #                     flow[k*3+p][t] = flow[k*3+p][t] +self.m[w,p,t].x
            #             else:
            #                 for w in range(args.W):
            #                     flow[k*3+p][t] = flow[k*3+p][t] +self.mk[k,w,p,t].x


            # for k in range(args.K):
            #     for g in range(args.G):
            #         print(15+k*2+g)
            #         for t in range(args.T):
            #             for j in range(args.J):
            #                 flow[15+k*2+g][t] = flow[15+k*2+g][t] + self.dk[k,j,g,t].x



            # for k in range(args.K):
            #     for p in range(args.P):
            #         print(25+k*3+p)
            #         for t in range(args.T):
            #             for i in range(args.I):
            #                 for j in range(args.J):
            #                     flow[25+k*3+p][t] = flow[25+k*3+p][t] + self.fk_ij[k,i,j,p,t].x


            # df = pd.DataFrame(np.transpose(flow))
            # df.to_excel("flow_TS_2.xlsx")



            # for p in range(args.P):
            #     for t in range(args.T):
            #         temp = 0
            #         for i in range(args.I):
            #             for w in range(args.W):
            #                 temp = self.x[i,w,p,t].x + temp
            #         print(p,t,temp)

            # print("------")

            # for k in range(args.K):
            #     for p in range(args.P):
            #         for t in range(args.T):
            #             temp = 0
            #             for j in range(args.J):
            #                 for w in range(args.W):
            #                     temp = self.fk_wj[k,w,j,p,t].x + temp
            #             print(k,p,t,temp)

            # print("------")

            # for k in range(args.K):
            #     for p in range(args.P):
            #         for t in range(args.T):
            #             temp = 0
            #             for j in range(args.J):
            #                 temp = self.fk0_j[k,j,p,t].x + temp
            #             print(k,p,t,1/self.house_0_match[p],temp)

            # print("------")

            # for k in range(args.K):
            #     for p in range(1,args.P):
            #         for g in range(args.G):
            #             for t in range(args.T):
            #                 temp = 0
            #                 for j in range(args.J):
            #                     temp = self.yk[k,j,p,g,t].x + temp
            #                 print(k,p,g,t,temp)


            # print("------")

            # for k in range(args.K):
            #     for g in range(args.G):
            #         for t in range(args.T):
            #             temp = 0
            #             for j in range(args.J):
            #                 temp = temp + self.dk[k,j,g,t].x
            #             print(k,g,t,temp)

            # print("------")
            # for k in range(args.K):
            #     for p in range(args.P):
            #         for t in range(args.T):
            #             temp = 0
            #             for i in range(args.I):
            #                 for j in range(args.J):
            #                     temp = temp + self.fk_ij[k,i,j,p,t].x
            #             print(k,p,t,temp)
            
            # self.model.write("model.lp")
            df_name = ["back up active","OPT","first_stage_trans_cost","second_trans_cost","Emergency_cost","unused_cost","unused0","unused1","unused2","mismatch_cost","unmet_cost","shortage 1","shortage 2","deprivation"]
            data = [[args.error, 
                    self.model.ObjVal,
                    first_stage_cost, 
                    second_stage_trans, 
                    emergency_cost,
                    unused_0_cost+unused_1_cost+unused_2_cost,
                    unused_0,
                    unused_1,
                    unused_2, 
                    mismatch_cost, 
                    unmet_cost_1+unmet_cost_2,
                    shortage_1, 
                    shortage_2,
                    deprivation_cost,]]
            df = pd.DataFrame(data, columns=[df_name])
            df.to_csv(name)
            # import pdb;pdb.set_trace()
            print(self.model.ObjVal)
     
        else:
            print("infesible or unbounded")

