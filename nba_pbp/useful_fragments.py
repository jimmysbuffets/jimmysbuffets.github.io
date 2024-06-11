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
