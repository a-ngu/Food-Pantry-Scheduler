
import pandas as pd
import numpy as np
from ortools.sat.python import cp_model

# data imports
def read_csvs(response_csv, shift_csv, recovery_csv):
    #responses = pd.read_csv("autoscheduler_Export.csv")
    #shifts = pd.read_csv("shifts.csv")
    #recovery_shifts = pd.read_csv('recoveryshifts.csv')
    responses = pd.read_csv(response_csv)
    shifts = pd.read_csv(shift_csv)
    recovery_shifts = pd.read_csv(recovery_csv)
    hours = responses[['Full Name', 'Volunteer Weekly Commitment']].set_index('Full Name')
    assignments = run_csp(responses, shifts, recovery_shifts, hours)
    return assignments

#data transformation
def Transform_Responses(shifts, response_df):
    all_shifts = list(shifts['Volunteer Shift'])
    columns = np.append(['Full Name'], all_shifts)
    availability = pd.DataFrame(columns=columns)
    for i in np.arange(response_df.shape[0]):
        mapping = []
        for j in all_shifts:
            if j in response_df.iloc[i,2]:
                mapping.append(1)
            else:
                mapping.append(0)
            row_data = np.append(response_df.iloc[i,0], mapping)
        availability.loc[len(availability)] = row_data
    return availability

def run_csp(responses, shifts, recovery_shifts, hours):
    availability = Transform_Responses(shifts, responses).set_index('Full Name')

    #define decision variables
    all_shifts = list(shifts['Volunteer Shift'])
    all_volunteers = list(responses['Full Name'])
    variables = []
    variable_domain = [0, 1]
    for s in all_shifts:
        for v in all_volunteers:
            if int(availability.loc[v,s]) == 1:
                variables.append(v + ';' + s)
                
    shift_Sum = []
    for i in all_shifts:
        one_shift = []
        for j in variables:
            if j.split(';')[1] in i:
                one_shift.append(j)
        shift_Sum.append(one_shift)
        
    vol_Sum = []
    for i in all_volunteers:
        one_user = []
        for j in variables:
            if j.split(';')[0] in i:
                one_user.append(j)
        vol_Sum.append(one_user)
        
    # CSP model
    model = cp_model.CpModel()

    gvars = list()
    for var in variables:
        var = model.NewIntVar(0, 1, var)
        gvars.append(var)

    vol_Sum = []
    for i in all_volunteers:
        one_user = []
        for j in gvars:
            if j.Name().split(';')[0] in i:
                one_user.append(j)
        vol_Sum.append(one_user)
        
    shift_Sum = []
    for i in all_shifts:
        one_shift = []
        for j in gvars:
            if j.Name().split(';')[1] in i:
                one_shift.append(j)
        shift_Sum.append(one_shift)
        
    #constraints based on volunteer hours (volunteer shifts)
    #lower bound of 1 on each volunteer (to ensure every volunteer has one shift):
    for vs in vol_Sum:
        model.Add(sum(vs) >= 1)
        

    #upper bound constraint for each user (volunteer weekly commitment)
    for vs in vol_Sum:
        vol = vs[0].Name().split(';')[0]
        k = hours.loc[vol][0]
        model.Add(sum(vs) <= k)

    print('volunteer constraints created!')

    #shift based constraints (filling each shift but not overfilling)
    #lower bound (of 1) on shifts
    for shift in shift_Sum:
        model.Add(sum(shift) >= 1)
        model.Add(sum(shift) <= 5)
        
        
    print('shift constraints created!')

    #Maximize number of volunteers working
    #Adding a term that maximizes median of each shift
    model.Maximize(sum(gvars))
        
    #Get solution
    #solutions = problem.getSolution()
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    #pull solutions into dataframe
    assigned = []
    for var in gvars:
        if solver.Value(var) == 1:
            assigned.append(var.Name())

    assigned_dict = {}
    for i in all_volunteers:
        assigned_dict[i] = []
        for j in assigned:
            splits = j.split(';')
            if splits[0] == i:
                assigned_dict[i].append(splits[1])
                
    for i in assigned_dict:
        assigned_dict[i] = ', '.join(assigned_dict[i])

    assignments = pd.DataFrame.from_dict(assigned_dict, orient='index',
                           columns=['Assigned Pantry Shifts'])

    assignments.reset_index(inplace=True)
    assignments.rename(columns={'index': 'Full Name'}, inplace=True)

    #Read file to csv.

    #assignments.to_csv('assignments.csv')
    return assignments