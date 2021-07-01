import numpy as np
import geatpy as ea
import time


"""=======================目标函数====================="""
def aim(Phen): # 传入种群染色体矩阵解码后的基因表现型
    x1 = Phen[:, [0]] # 取出第一列，得到所有个体的第一个自变量
    x2 = Phen[:, [1]] # 取出第二列，得到所有个体的第二个自变量
    rt_reality = []
    modality_reality = []
    # rt_predict, modality_predict = abm(x1, x2)
    # return mse(rt_reality, rt_predict), mse(modality_reality, rt_predict)
    return np.sin(x1+x2) + (x1-x2)**2 - 1.5*x1 + 2.5*x2 + 1

"""======================= range of vars ====================="""
infect_coeff = [1, 3]
ratio_people_obedient = [0, 1]
x1 = [-1.5, 4] # 第一个决策变量范围
x2 = [-3, 4] # 第二个决策变量范围
b1 = [1, 1] # 第一个决策变量边界，1表示包含范围的边界，0表示不包含
b2 = [1, 1] # 第二个决策变量边界，1表示包含范围的边界，0表示不包含
# 生成自变量的范围矩阵，使得第一行为所有决策变量的下界，第二行为上界
ranges=np.vstack([x1, x2]).T
# 生成自变量的边界矩阵
borders=np.vstack([b1, b2]).T
varType = np.array([0, 0]) # 决策变量的类型，0表示连续，1表示离散

"""===================== settings of chrom encoding ==================="""
Encoding = 'BG' # 'BG'表示采用二进制/格雷编码
codes = [1, 1] # 决策变量的编码方式，两个1表示变量均使用各类编码
precisions = [6, 6] # 决策变量的编码精度，表示解码后能表示的决策变量的精度可达小数点6位
scales = [0, 0] #0表示采用算术刻度，1表示采用对数刻度
# 调用函数创建译码矩阵
FieldD = ea.crtfld(Encoding, varType, ranges, borders, precisions, codes, scales)
"""====================遗传算法参数设置=================="""
NIND = 20 # 种群个体数目
MAXGEN = 100 # 最大遗传代数
maxormins = [1] #表示目标函数是最小化，元素为-1则表示对应的目标函数是最大化
selectStyle = 'sus' # 采用随机抽样选择
recStyle = 'xovdp' # 采用两点交叉
mutStyle = 'mutbin' # 采用二进制染色体的变异算子
pc = 0.9 # 交叉概率
pm = 1 #整条染色体的变异概率（每一位的变异概率=pm/染色体长度）
Lind = int(np.sum(FieldD[0, :])) # 计算染色体长度
print("种群个体数目：", NIND)
print("最大遗传代数：",MAXGEN)
print("交叉概率", pc)
print("染色体长度：",Lind,"\n每一位的变异概率：",pm/Lind)
obj_trace = np.zeros((MAXGEN, 2)) # 定义目标函数值记录器
var_trace = np.zeros((MAXGEN, Lind)) # 染色体记录器，记录历代最优个题的染色体

"""====================开始遗传算法进化=================="""
start_time = time.time() # 开始计时
Chrom = ea.crtpc(Encoding,NIND,FieldD) # 生成种群染色体矩阵
variable = ea.bs2real(Chrom, FieldD) # 对初始种群进行解码
ObjV = aim(variable) # 计算初始种群个体的目标函数值
best_ind = np.argmin(ObjV) # 计算当代最优个体序号，最大：argmax

"""========================= evolution begins ==============================="""
for gen in range(MAXGEN):
    FitnV = ea.ranking(maxormins * ObjV) # assign the fitness according to the objective function
    SelCh = Chrom[ea.selecting(selectStyle, FitnV, NIND-1), :] # selection
    SelCh = ea.recombin(recStyle, SelCh, pc) # recombination
    SelCh = ea.mutate(mutStyle, Encoding, SelCh, pm) # variation

    # 把父代精英个体与子代的染色体进行合并，得到新一代种群
    Chrom = np.vstack([Chrom[best_ind, :], SelCh])
    Phen = ea.bs2real(Chrom, FieldD) # 对种群进行解码（二进制转十进制）
    ObjV = aim(Phen) # get the objective function value of the individuals

    # 记录
    best_ind = np.argmin(ObjV) # get the index of the optimal individual
    obj_trace[gen,0]=np.sum(ObjV)/ObjV.shape[0]
    # record the objective function value of the population
    obj_trace[gen,1]=ObjV[best_ind] # 记录当代种群最优个体的染色体
    var_trace[gen,:]=Chrom[best_ind,:] # 记录当代种群最优个体的染色体

"""========================= Evolution Finished ========================="""
end_time = time.time()
ea.trcplot(obj_trace, [['avg objective value in population','optimal objective value in population']])

"""======================= Result ====================="""
best_gen = np.argmin(obj_trace[:, [1]])
print('Optimal objective function value: ', obj_trace[best_gen, 1])
variable = ea.bs2real(var_trace[[best_gen], :], FieldD) # 解码得到的表现型（即对应的决策变量值）
print('Optimal decision vars: ')
for i in range(variable.shape[1]):
    print('x'+str(i)+'=',variable[0,i])
print('it takes：',end_time - start_time,"seconds")