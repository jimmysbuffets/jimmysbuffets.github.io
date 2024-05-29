"""there is an issue with plusminus because of subs happening between 2 free throws"""
"""need to change the get_gamestints function to account for the FT following the sub"""
"""options are (all same timestring? think you can use):
FT then sub then FT
made shot then sub then FT
FT then FT then sub
something else then sub then FT
haven't seen it but presumably FT then multiple subs then FT"""
""""my guess is to collect and use the PCTIMESTRING for every sub"""
"""actually my guess is to totally remake the subs function and the get gamestints function"""


"""each gamestint needs to start on the next PCTIMESTRING after the PCTIMESTRING of the sub"""
"""actually you just need to replace the sub_index with a sub_next_timestring_index"""

# pbpcheck[pbpcheck['EVENTMSGTYPE'] == 8].index

"""after get_gamepbp, get_quarterstarters, qs_checker. maybe can replace subs_df"""

#get the indexes for substituion or quarter change
pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 8) | (pbp2_df['EVENTMSGTYPE'] == 12)].index
#declare the variable of the timestring for that index
idx = 41 # this will be the loop
sub_period = pbp2_df.loc[idx, ['PERIOD']].item()
sub_timestring = pbp2_df.loc[idx, ['PCTIMESTRING']].item()
#find the highest index that matches both sub_period and sub_timestring
pbp2_df[(pbp2_df['PERIOD'] == sub_period) & (pbp2_df['PCTIMESTRING'] == sub_timestring)].index.max()

#get the first and last indexes of the game_stints

# get a list of all the final timestrings where there was a sub or quarter change (skip idxs already part of that stint)
last_idx=0
stint_end_idxs = []
for idx in pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 8) | (pbp2_df['EVENTMSGTYPE'] == 12)].index:
    sub_period = pbp2_df.loc[idx, ['PERIOD']].item()
    sub_timestring = pbp2_df.loc[idx, ['PCTIMESTRING']].item()

    if idx <= last_idx:
        continue
    elif idx > last_idx:
        last_idx = pbp2_df[(pbp2_df['PERIOD'] == sub_period) & (pbp2_df['PCTIMESTRING'] == sub_timestring)].index.max()

    stint_end_idxs.append(last_idx)
print(stint_end_idxs)
# this list is the last row of a stint (and i guess the first??)

#let's just make subs_df with these indexes and skip changing the whole gamestints function

#old function
def get_subs(pbp2_df):
    """make a df made up of the rows containing substutions or quarter changes from the playbyplay data"""

    # in pbp_df, find all the subs/quarters, and make a new df with them (8 is sub, 12 is start of quarter)
    subs_df = pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 8) | (pbp2_df['EVENTMSGTYPE'] == 12)]

    # add a column for sub_stints, where the group of subs all count as one (this will separate game stints)
    subs_df.insert(3, 'subs_stint_bool', subs_df.EVENTNUM == subs_df.EVENTNUM.shift() + 1)
    subs_df.insert(3, 'subs_stint', subs_df['subs_stint_bool'].eq(False).cumsum())

    return subs_df
# example: subs_df = get_subs(pbp2_df)

#new function
def get_subs(pbp2_df):
    """make a df made up of the rows containing substutions or quarter changes from the playbyplay data"""

    # in pbp_df, find all the subs/quarters, and make a new df with them (8 is sub, 12 is start of quarter)
    subs_df = pbp2_df.iloc[stint_end_idxs]

    # add a column for sub_stints, where the group of subs all count as one (this will separate game stints)
    subs_df.insert(3, 'subs_stint_bool', subs_df.EVENTNUM == subs_df.EVENTNUM.shift() + 1)
    subs_df.insert(3, 'subs_stint', subs_df['subs_stint_bool'].eq(False).cumsum())

    return subs_df

# how will you do this
a = pbp2_df[pbp2_df['EVENTMSGTYPE'] == 12].index
b = pbp2_df[pbp2_df['EVENTMSGTYPE'] == 8].index
c = pbp2_df.iloc[stint_end_idxs].index

resulting_list = list(a)
resulting_list.extend(x for x in b if x not in resulting_list)
resulting_list.extend(x for x in c if x not in resulting_list)
resulting_list.sort()

check = pbp2_df.iloc[resulting_list]
check.insert(3, 'subs_stint_bool', check.PCTIMESTRING == check.PCTIMESTRING.shift())
check.insert(3, 'subs_stint', check['subs_stint_bool'].eq(False).cumsum())