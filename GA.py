import numpy as np
import random
from coding import encoding,decoding


class Solution:
    def __init__(self,s) -> None:
        self.s = s
        self.fit = None


###### 遗传算法求解FJSP算子设计 ######

#1.种群初始化
def initializePopulation(Jobs,os,machines_num=5,popSize=100):
    '''初始化总群'''
    population = [Solution(encoding(Jobs,os,machines_num,stype='GS')),
                  Solution(encoding(Jobs,os,machines_num,stype='LS'))
                  ]    
    for i in range(2,popSize):
        population.append(Solution(encoding(Jobs,os,machines_num,stype='RS')))
    
    return population

#2.选择
def selection(population:list,fitnessratio):
    '''轮盘赌选择
    population:种群[individual]
    fitness:种群个体对应的适应度
    return:
        best:当前锦标赛中最好的个体
    '''
    r = random.random()
    target_idx = np.where(fitnessratio >= r)[0][0]
    return population[target_idx]

def getbest(population):
    '''找出当前种群中最好的个体及其适应度
    '''
    fitness = [individual.fit for individual in population]
    bestidx = np.argmin(fitness)
    bestS = population[bestidx]
    return bestS

#3.交叉
def cross(P1:list,P2:list,rs:list,jobSequence:list):
    '''
    P1,P2 [ms,os]
    rs:机器选择位点rs=list(range(工序总数))
    jobSequence:工件当前在Jobs列表中的的相对顺序=list(range(工件总数))
    '''
    def mscross(ms1:np.array,ms2:np.array,rs:list):
        '''均匀交叉
        ms1,ms2:父代机器选择部分
        rs:机器选择位点rs=list(range(工序总数))
        '''
        r = random.randint(1,len(rs))
        # crossIndex = sorted(random.sample(rs,r)) #交叉位点
        crossIndex = random.sample(rs,r) #交叉位点
        c1,c2 = ms1.copy(),ms2.copy()
        c1[crossIndex],c2[crossIndex] = c2[crossIndex],c1[crossIndex]
        
        return c1,c2
    def oscross(os1:np.array,os2:np.array,jobSequence:list):
        '''POX交叉'''
        def generate_offspring(os1,os2,c):
            i,j = 0,0
            while i < len(os2):
                if os2[i] not in crossIds:
                    while j < len(os1):
                        if os1[j] not in crossIds:
                            c[j] = os2[i]
                            j += 1
                            break
                        j += 1
                i += 1
            return c
        r = random.randint(1,len(jobSequence)) #将工作集合一分为2
        crossIds = sorted(random.sample(jobSequence,r)) #交叉元素
        c1,c2 = os1.copy(),os2.copy()
        c1 = generate_offspring(os1,os2,c1)
        c2 = generate_offspring(os2,os1,c2)
        
        return c1,c2
    
    msc1,msc2 = mscross(P1[0],P2[0],rs)
    osc1,osc2 = oscross(P1[1],P2[1],jobSequence)
    C1,C2 = [msc1,osc1],[msc2,osc2]
    return C1,C2

#4.变异
def mutation(s,rs,allOT):
    def msmutation(ms,rs,allOT):
        '''
        Step1:在变异染色体中随机选择r个位置
        Step2:依次选择每一个位置,对每一个位置的机器设置为当前工序可选机器集合加工时间最短的机器
        ms:机器选择部分编码
        rs:list(range(工序总数))
        allOT:当前排序下所有工序的时间矩阵
        '''
        r = random.randint(1,len(rs))
        mutaionIndex = random.sample(rs,r) #变异位点        
        for i in mutaionIndex:
            ms[i] = np.argmin(allOT[i])
        
        return ms
        
    def osmutation(os):
        '''
        随机选择两个位点进行转置
        '''
        osIndex = list(range(len(os)))
        a,b = sorted(random.sample(osIndex,2))
        if b == len(osIndex):
            b += 1
        temp = list(os[a:b])
        temp.reverse()
        os[a:b] = temp
        return os
    s[0] = msmutation(s[0],rs,allOT)
    s[1] = osmutation(s[1])
    return s