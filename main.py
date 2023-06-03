import random
import copy
from problem import Job,visualization
from coding import encoding,decoding
from GA import *
import matplotlib.pyplot as plt

######## 生成算例 ######
machines_num = 5
jobs_num = 10
machine_list = list(range(1,machines_num+1))
products = ['A','B','C']    #设置每一种产品对应一种颜色
colors = ['r','g','b','c','m','y','k','w']
ptocolor = dict(zip(products,colors))
Jobs = []
Joblists = []
Ts = []
for i in range(jobs_num):
    onum = random.randint(1,5) #工序数
    candMs = []
    candTs = []
    for j in range(onum):
        mnum = random.randint(1,machines_num) #工序可选机器数
        candm = random.sample(machine_list,mnum)
        candMs.append(candm)
        #工序在不同机器上对应的加工时间
        candt = [random.randint(1,10) for _ in candm]
        candTs.append(candt)
    Joblists.append(candMs)
    Ts.append(candTs)
    productType = products[random.randint(0,len(products)-1)]
    Jobs.append(Job(i+1,candMs,candTs,productType))

jobSequence = list(range(jobs_num))
allOT = []
for job in Jobs:
    allOT.extend(job.tinfo)
os = []
for i,job in enumerate(Jobs):
    for j in range(job.osNum):
        os.append(i)
os = np.array(os)
rs = list(range(len(os))) #位点列表

######## 算法求解 #######

# 遗传算法参数
popSize = 50 #总群大小
maxGen = 1000 #迭代次数
pc = 0.75  #交叉概率
pm = 0.2  #变异概率


# 生成初始种群


population = initializePopulation(Jobs,os,machines_num,popSize)
for individual in population:
    if individual.fit is None:
        _,individual.fit = decoding(individual.s,Jobs,machines_num)
bestS = copy.deepcopy(getbest(population))
bestfits = [bestS.fit]
gen = 0
while gen < maxGen:
    fitness = [ 1 / individual.fit for individual in population]
    cumSum = np.cumsum(fitness)
    fitnessratio = cumSum / cumSum[-1]
    parents = [] 
    for i in range(popSize):
        parents.append(selection(population,fitnessratio))
    population = parents.copy()
    # 交叉
    for i in range(popSize):
        if random.random() < pc:
            P1 = population[i].s
            j = random.randint(0,popSize-1)
            P2 = population[j].s
            C1,C2 = cross(P1,P2,rs,jobSequence)
            population[i].s,population[i].fit = C1,None
            population[j].s,population[j].fit = C2,None

    # 变异
    for i in range(popSize):
        if random.random() < pm:
            population[i].s = mutation(population[i].s,rs,allOT)
            population[i].fit = None
    
        if population[i].fit is None:
            _,population[i].fit = decoding(population[i].s,Jobs,machines_num)
    
    curbestS = getbest(population)
    if curbestS.fit <= bestS.fit:
        bestS = copy.deepcopy(curbestS)
    else:
        population[0] = copy.deepcopy(bestS)
    bestfits.append(bestS.fit)
    gen += 1

machines,completionT = decoding(bestS.s,Jobs,machines_num)
plt.plot(bestfits)
plt.show()
# for machine in machines:
#     for info in machine.processInfo:
#         print(info)
# 可视化车间调度结果
visualization(machines,completionT,ptocolor,machines_num)