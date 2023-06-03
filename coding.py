import numpy as np
import random
from problem import Machine
def encoding(Jobs:list,os:np.array,machines_num:int,stype='GS'):
    '''初始化得到一个解
    机器选择部分有三种初始化方式：全局搜索GS，局部搜索LS，随机搜索RS
    工序排序部分采用随机搜索
    Jobs:工件集
    machines_num:机器总数
    os:初始工序排序部分
    stype:ms初始化方式{GS,LS,RS}
    '''
    ms = np.zeros(len(os),dtype=int) #机器选择编码
    mt = np.zeros(machines_num,dtype=float) #整型数组
    osRecord = 0
    # print('ms:',ms)
    for job in Jobs:
        # 遍历当前工件的工序
        if stype == 'RS':
            for i in range(job.osNum):
                ms[osRecord] = random.randint(0,len(job.minfo[i])-1)
                osRecord += 1
        else:
            for i in range(job.osNum):
                candM = job.minfo[i] #候选机器
                tmpm = mt[candM] + job.tinfo[i] #加工时间相加
                min_val = np.min(tmpm)  # 最小负荷
                min_index = np.argmin(tmpm)  # 获取最小值索引
                mt[candM[min_index]] = min_val
                ms[osRecord] = min_index
                osRecord += 1
            if stype == 'LS':
                mt = np.zeros(machines_num,dtype=float) 
    indexList = list(range(len(os)))
    random.shuffle(indexList)
    return [ms,os[indexList]]



def decoding(s:list,Jobs:list,machines_num=5):
    '''
    s=[ms,os] solution
    ms:机器编码部分
    os:工序排序编码
    Jobs:待加工工件集
    machines_num:机器总数
    returns:
        machines:机器加工信息
        completionT:最后一道工序完工时间
    '''
    ms,os = s[0],s[1]
    machines = [Machine(i) for i in range(machines_num)]
    osCumSum = list(np.cumsum([job.osNum for job in Jobs])) #工件ms分割点
    osCumSum.insert(0,0)

    for num in os:
        # num决定了是第几个工件，job.osCount决定了是工件的第几个工序
        job = Jobs[num]
        if job.osCount == 0:
            jobms = ms[osCumSum[num]:osCumSum[num+1]].copy()
            job.decode(jobms) #解码得到job.Jm和job.T
        
        mId = job.Jm[job.osCount] #工序的机器编号
        mot = job.T[job.osCount]  #工序在该机器上的加工时间
        machines[mId].process(job,mot) #机器加工

 
    completionT = 0
    for machine in machines:
        if machine.processInfo and machine.processInfo[-1].endT > completionT:
            completionT = machine.processInfo[-1].endT

    for job in Jobs:
        job.reset()

    return machines,completionT