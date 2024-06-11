"""trying out different visualizations"""

"""load the dictionary with average minutename times"""
import pickle
with open('realgametime_final_dict.pkl', 'rb') as fp:
    final_dict = pickle.load(fp)
    print('uploaded dictionary from file')

"""select only the relevant minutes (remove -12's and OT)"""
removal_keys = ['1-12','2-12','3-12','4-12','5-5','5-4','5-3','5-2','5-1','5-0','6-5','6-4','6-3','6-2','6-1','6-0']
for key in removal_keys:
    final_dict.pop(key, None)



"""making the chart"""
import matplotlib.pyplot as plt
fig, ax = plt.subplots(facecolor=('linen'))
ax.set_facecolor('linen')
plt.bar(range(len(final_dict)), final_dict.values(), color='tab:blue')
ax.set_xlim(-1,48)

"""vertical lines"""
vlinecoords = [11.5, 23.5, 35.5]
for vcoord in vlinecoords:
    plt.axvline(x=vcoord, color='g', linestyle='--', linewidth=1)
"""ticks"""
minute_labels = [x.partition("-")[2] for x in final_dict.keys()]
plt.xticks(range(len(final_dict)), labels=minute_labels)

"""add annotations for quarter"""
plt.annotate('Q1', xy=(1.5, 4.5), color='green', bbox=dict(facecolor='none', edgecolor='green'))
plt.annotate('Q2', xy=(12.5, 4.5), color='green', bbox=dict(facecolor='none', edgecolor='green'))
plt.annotate('Q3', xy=(24.5, 4.5), color='green', bbox=dict(facecolor='none', edgecolor='green'))
plt.annotate('Q4', xy=(36.5, 4.5), color='green', bbox=dict(facecolor='none', edgecolor='green'))

"""add annotations fo TV timeouts - the x-coordinates need changing"""
plt.annotate('TV', xy=(4.7, list(final_dict.values())[5]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(8.7, list(final_dict.values())[9]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(16.7, list(final_dict.values())[17]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(20.7, list(final_dict.values())[21]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(28.7, list(final_dict.values())[29]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(32.7, list(final_dict.values())[33]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(40.7, list(final_dict.values())[41]+.1), color='tab:orange', fontsize=7)
plt.annotate('TV', xy=(44.7, list(final_dict.values())[45]+.1), color='tab:orange', fontsize=7)

"""axis labels/title"""
plt.xlabel("Minutes Remaining In Quarter")
plt.ylabel("Real Time Elapsed (mins)")
plt.title("Mean Real Time Elapsed per Minute of Gametime")
plt.show()



