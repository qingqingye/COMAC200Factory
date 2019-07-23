import os
import numpy as np
path = 'pic'
list = os.listdir(path)
ndarray = np.zeros(400)
totalNum = 0
for p in list:
    totalNum += 1
    time = int(int(p.split('_')[0])/60)
    ndarray[time] += 1

print("There are "+str(totalNum)+" images")
np.save('imageNames.npy',ndarray)
