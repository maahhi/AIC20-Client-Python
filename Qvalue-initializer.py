import itertools
import pandas

# make sub set of unities
# you have to make a set from uniti's id and then cast in to string. now you have the action!
s = {0,1,2,3,4,5,6,7,8}
s_2 =list(map(str,itertools.combinations(s, 2)))
s_1 =list(map(str,itertools.combinations(s, 1)))
s_3 =list(map(str,itertools.combinations(s, 3)))
s_4 =list(map(str,itertools.combinations(s, 4)))
s_5 =list(map(str,itertools.combinations(s, 5)))
s_0 =list(map(str,itertools.combinations(s, 0)))
sub_s = s_0+s_1+s_2+s_3+s_4+s_5


d = pandas.DataFrame(index = pandas.Index([i for i in range(2048)]) ,columns=['self','enemy']+sub_s)
d2 = d.fillna(0.0)

self = [i for i in range(2**9)]
self = self+self
self = self+self
enemy = [0 for i in range(512)] + [1 for i in range(512)] + [2 for i in range(512)] + [3 for i in range(512)]

d2.self = self
d2.enemy = enemy

d2.to_csv('Q_value.csv',index=False)

#d.loc[(d['self']==1) & (d['enemy']==1)]
d.loc[(d['self']==0) & (d['enemy']==1)]['()'].index[0]
d._set_value(0,'()',1)

d = pandas.read_csv('Q_value.csv')
