import numpy as np
import matplotlib.pyplot as plt

class Job:
    def __init__(self,jobId:int,minfo:list,tinfo:list,productType:str) -> None:
        self.id = jobId    #工件编号
        self.osNum = len(minfo) #工件的工序数
        self.minfo = self.list_to_array(minfo) #工件每个工序可选择的加工机器
        self.tinfo = self.list_to_array(tinfo,infotype='t') #工件每个工序在不同机器上的加工时间
        self.productType = productType #工件所属产品型号
        self.osCount = 0 #加工工序次序
        self.startTs = [0] #工序开始加工时间
        self.endTs = [0]   #工序加工结束时间
    

    def list_to_array(self,listinfo:list,infotype='m'):
        info = listinfo.copy()
        if infotype == 'm':
            for i in range(self.osNum):
                info[i] = np.array(info[i]) - 1 #python的索引从0开始
        else:
            for i in range(self.osNum):
                info[i] = np.array(info[i])
        return info
    
    def decode(self,ms:np.array):
        '''解码机器顺序矩阵和时间矩阵顺序'''
        Jm,T = [],[]
        for i in range(self.osNum):
            Jm.append(self.minfo[i][ms[i]])
            T.append(self.tinfo[i][ms[i]])
        self.Jm,self.T = Jm,T
        return Jm,T
    
    def updateT(self,startT,endT):
        '''更新工件工序的加工开始时间和加工结束时间
        startT:工序加工开始时间
        operationT:工序加工结束时间
        '''
        self.startTs.append(startT)
        self.endTs.append(endT)
        self.osCount += 1


    def reset(self):
        '''重置时间'''
        self.startTs = [0]
        self.endTs = [0]
        self.osCount = 0

class WorkInfo:
    def __init__(self,startT=None,duration=None,endT=None,jobid=None,joboreder=None,jobtype=None):
        self.startT = startT            #状态开始时间
        self.duration = duration        #状态持续时间
        self.endT = endT                #状态结束时间
        self.jobid = jobid              #工件编号
        self.joborder = joboreder       #工件次序
        self.jobtype = jobtype          #工件类属产品
    
    def __str__(self):
        return f"开始加工时间:{self.startT},加工持续时间:{self.duration},加工结束时间:{self.endT},工件编号:{self.jobid},工件次序:{self.joborder},工件类属产品:{self.jobtype}"
class Machine:
    def __init__(self,id):
        self.id = id #机器编号
        self.processInfo = [] #[开始加工时间,加工时间,加工结束时间,工件编号,工件工序号,工件产品类型]

    def process(self,job,mot):
        '''工件工序的加工操作
        jobid:工件编号
        mot:机器加工该工件当前工序的耗时
        '''
        if self.processInfo:
            startT = max(job.endTs[-1],self.processInfo[-1].endT)
            if startT == self.processInfo[-1].endT and \
                job.productType == self.processInfo[-1].jobtype:#连续
                mot *= 0.75
        else:
            startT = job.endTs[-1]
        endT = startT + mot
        job.updateT(startT,endT)    
        workinfo = WorkInfo(startT,mot,endT,jobid=job.id,joboreder=job.osCount,jobtype=job.productType)
        self.processInfo.append(workinfo)
    
    def reset(self):
        '''重置'''
        self.processInfo = []

# 绘制甘特图
def visualization(machines,completionT,ptocolor,machines_num=5):
    '''绘制甘特图
    '''
    plt.figure(figsize=(len(machines)*5,len(machines)))
    for i in range(machines_num):
        for osProcessInfo in machines[i].processInfo:
            plt.barh(i, width=osProcessInfo.duration, height=0.8, left=osProcessInfo.startT,align='center',
                         color=ptocolor[osProcessInfo.jobtype], edgecolor='k')
            plt.text(x=osProcessInfo.startT + osProcessInfo.duration/2, y=i, s=f"{osProcessInfo.jobid}/{osProcessInfo.joborder}",
                         horizontalalignment='center',fontsize=8)
    plt.yticks(list(range(machines_num)),
           ['machine%d'%i for i in range(machines_num)])
    plt.title('the completion time of those current Jobs is:%.2f'%completionT)
    plt.show()