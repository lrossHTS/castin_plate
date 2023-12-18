import numpy as np

x = [1,2,3,4,5]

x = np.array(x)
x = x+3


# option 1
y = [] # set up empty list

# for j in x: # step through 
# #     y.append(j+3)

    
y = [j + 3 for j in x]


pass