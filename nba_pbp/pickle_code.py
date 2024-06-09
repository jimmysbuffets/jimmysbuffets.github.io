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
