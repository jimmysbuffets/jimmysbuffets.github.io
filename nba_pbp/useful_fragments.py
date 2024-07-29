"""for calculating seconds_left maybe"""

    timegame = pd.Series([np.abs((minute * 60 + sec) - 720 * period) if period < 5 \
                              else np.abs((minute * 60 + sec) - (2880 + 300 * (period - 4))) \
                          for (minute, sec, period) in zip(s["MIN"], s["SEC"], data["PERIOD"])])


"""pickle code"""
"""save (and read) dictionary to/from pickle file"""

import pickle

# Write dictionary pkl file
with open('df_dictionary.pkl', 'wb') as fp:
    pickle.dump(df_dict, fp)
    print('dictionary saved successfully to file')


# Read dictionary pkl file
with open('df_dictionary.pkl', 'rb') as fp:
    df_dict = pickle.load(fp)
    print('uploaded dictionary from file')



"""rc Params"""

import numpy as np
import matplotlib.pyplot as plt

params = {"figure.facecolor": "#cad9e1",
              "axes.facecolor": "#cad9e1",
              "axes.grid" : True,
              "axes.grid.axis" : "y",
              "axes.spines.left" : False,
              "axes.spines.right" : False,
              "axes.spines.top" : False,
              "ytick.major.size": 0,
              "ytick.minor.size": 0,
              "xtick.direction" : "in",
              "xtick.major.size" : 7,
              "xtick.color"      : "#191919",
              "axes.edgecolor"    :"#191919",
              "axes.prop_cycle" : plt.cycler('color',
                                    ['#006767', '#ff7f0e', '#2ca02c', '#d62728',
                                     '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                                     '#bcbd22', '#17becf'])}
plt.rcParams.update(params)


x = np.random.randn(1000)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(12, 10))
ax.scatter(x, y)

plt.show()


plt.rcParams.update(plt.rcParamsDefault)
