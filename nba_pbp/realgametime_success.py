"""remaking realtime/gametime using the LAST index of the PREVIOUS minutename"""

"""get every game_id from the 23-24 season"""
from nba_api.stats.endpoints import leaguegamefinder
gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable='00', season_nullable='2023-24', season_type_nullable='Regular Season')
all_games = gamefinder.get_data_frames()[0]

"""this is from each team's perspective, get a list of every unique game_id, order doesn't matter"""
all_gameids = list(all_games['GAME_ID'].unique())

"""get pbp for a single game_id, feature engineer total time elapsed, which minute we're in"""
"""single game pbp"""
game_id = all_gameids[0]
from nba_api.stats.endpoints import playbyplayv2
pbp_df = playbyplayv2.PlayByPlayV2(game_id).get_data_frames()[0]








"""add time columns for gameclock"""
import pandas as pd
pbp_df.insert(7, 'PCMINUTES', pd.Series(map(int, pbp_df['PCTIMESTRING'].str.partition(':')[0])))
pbp_df.insert(8, 'PCSECONDS', pd.Series(map(int, pbp_df['PCTIMESTRING'].str.partition(':')[2])))
pbp_df.insert(9, 'PCMINUTENAME', pbp_df['PERIOD'].astype(str) + "-" + pbp_df['PCMINUTES'].astype(str))


"""turn worldclock into 24-hour time"""
pbp_df.insert(6, 'WCDATETIME', pd.to_datetime(pbp_df['WCTIMESTRING'], format='%I:%M %p'))
pbp_df.insert(7, 'WCHOURS', pbp_df['WCDATETIME'].dt.hour)
pbp_df.insert(8, 'WCMINUTES', pbp_df['WCDATETIME'].dt.minute)
pbp_df.insert(9, 'WCHOURMINUTES', pbp_df['WCHOURS'] * 60 + pbp_df['WCMINUTES'])



"""loop through the single pbp to get the game_id, minutename, wc_start"""
minutename_df = pd.DataFrame(index = range(0,100),
                             columns = ['game_id', 'minutename','wc_start','wc_end'])

loop_number = -1
for minutename in pbp_df['PCMINUTENAME'].unique():

    loop_number += 1
    minutename_idx = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.min()
    minutename_idx_max = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.max()

    if minutename == '1-12':
        game_id = pbp_df.loc[minutename_idx, ['GAME_ID']].item()
        wc_start = pbp_df.loc[minutename_idx, ['WCHOURMINUTES']].item()
        wc_end = pbp_df.loc[minutename_idx_max, ['WCHOURMINUTES']].item()

        previous_idx = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.max()

    else:
        game_id = pbp_df.loc[minutename_idx, ['GAME_ID']].item()
        wc_start = pbp_df.loc[previous_idx, ['WCHOURMINUTES']].item()
        wc_end = pbp_df.loc[minutename_idx_max, ['WCHOURMINUTES']].item()

        previous_idx = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.max()


    minutename_df.loc[loop_number, ['game_id']] = game_id
    minutename_df.loc[loop_number, ['minutename']] = minutename
    minutename_df.loc[loop_number, ['wc_start']] = wc_start
    minutename_df.loc[loop_number, ['wc_end']] = wc_end

minutename_df = minutename_df[:minutename_df['minutename'].isnull().idxmax()]



"""BIG LOOP"""

"""loop for every game in all_gameids"""

"""get every game_id from the 23-24 season"""
from nba_api.stats.endpoints import leaguegamefinder
gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable='00', season_nullable='2023-24', season_type_nullable='Regular Season')
all_games = gamefinder.get_data_frames()[0]

"""this is from each team's perspective, get a list of every unique game_id, order doesn't matter"""
all_gameids = list(all_games['GAME_ID'].unique())


"""big loop"""
import pandas as pd
all_minutename_df = pd.DataFrame()

for game_id in all_gameids:

    """get pbp"""
    from nba_api.stats.endpoints import playbyplayv2
    pbp_df = playbyplayv2.PlayByPlayV2(game_id).get_data_frames()[0]

    """add time columns for gameclock"""
    import pandas as pd
    pbp_df.insert(7, 'PCMINUTES', pd.Series(map(int, pbp_df['PCTIMESTRING'].str.partition(':')[0])))
    pbp_df.insert(8, 'PCSECONDS', pd.Series(map(int, pbp_df['PCTIMESTRING'].str.partition(':')[2])))
    pbp_df.insert(9, 'PCMINUTENAME', pbp_df['PERIOD'].astype(str) + "-" + pbp_df['PCMINUTES'].astype(str))

    """turn worldclock into 24-hour time"""
    pbp_df.insert(6, 'WCDATETIME', pd.to_datetime(pbp_df['WCTIMESTRING'], format='%I:%M %p'))
    pbp_df.insert(7, 'WCHOURS', pbp_df['WCDATETIME'].dt.hour)
    pbp_df.insert(8, 'WCMINUTES', pbp_df['WCDATETIME'].dt.minute)
    pbp_df.insert(9, 'WCHOURMINUTES', pbp_df['WCHOURS'] * 60 + pbp_df['WCMINUTES'])

    """loop through the single pbp to get the game_id, minutename, wc_start"""
    minutename_df = pd.DataFrame(index=range(0, 100),
                                 columns=['game_id', 'minutename', 'wc_start', 'wc_end'])

    loop_number = -1
    for minutename in pbp_df['PCMINUTENAME'].unique():

        loop_number += 1
        minutename_idx = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.min()
        minutename_idx_max = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.max()

        if minutename in ['1-12', '2-12', '3-12', '4-12']:
            game_id = pbp_df.loc[minutename_idx, ['GAME_ID']].item()
            wc_start = pbp_df.loc[minutename_idx, ['WCHOURMINUTES']].item()
            wc_end = pbp_df.loc[minutename_idx_max, ['WCHOURMINUTES']].item()

            previous_idx = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.max()

        else:
            game_id = pbp_df.loc[minutename_idx, ['GAME_ID']].item()
            wc_start = pbp_df.loc[previous_idx, ['WCHOURMINUTES']].item()
            wc_end = pbp_df.loc[minutename_idx_max, ['WCHOURMINUTES']].item()

            previous_idx = pbp_df[pbp_df['PCMINUTENAME'] == minutename].index.max()

        minutename_df.loc[loop_number, ['game_id']] = game_id
        minutename_df.loc[loop_number, ['minutename']] = minutename
        minutename_df.loc[loop_number, ['wc_start']] = wc_start
        minutename_df.loc[loop_number, ['wc_end']] = wc_end

    minutename_df = minutename_df[:minutename_df['minutename'].isnull().idxmax()]

    #concat the outside-the-loop df
    all_minutename_df = pd.concat([all_minutename_df, minutename_df])

# find all the times that wc_start is 4 digits and wc_end is 1 or 2 digits and add 1440 to wc_end

all_minutename_df.reset_index(drop=True,inplace=True)

copy_df = all_minutename_df.copy()
copy_df[(copy_df['wc_start'] > 999) & (copy_df['wc_end'] < 99)]['wc_end'].index
copy_df.loc[copy_df[(copy_df['wc_start'] > 999) & (copy_df['wc_end'] < 99)]['wc_end'].index, ['wc_end']] += 1440

# find the difference in wc

copy_df['wc_diff'] = copy_df['wc_end'] - copy_df['wc_start']

final_dict = {}
for minutename in copy_df['minutename'].unique():
    mean_time = copy_df[copy_df['minutename'] == minutename]['wc_diff'].mean()

    final_dict.update({f"{minutename}": round(mean_time, 3)})

import matplotlib.pyplot as plt
plt.bar(range(len(final_dict)), final_dict.values())
plt.xticks(range(len(final_dict)), final_dict.keys())
plt.show()
