"""trying to combine 01 and 02"""

"""team and game id, team roster (not sure if needed)"""

import pandas as pd

# get celtics_id from teams list
from nba_api.stats.static import teams
nba_teams = teams.get_teams()
celtics = [team for team in nba_teams if team['abbreviation'] == 'BOS'][0]
celtics_id = celtics['id']
del(nba_teams, celtics)

# get dataframe with all of celtics games this season (mostly for game ids and HvV, add
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.library.parameters import Season
from nba_api.stats.library.parameters import SeasonType
gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=celtics_id,
                                               season_nullable=Season.default,
                                               season_type_nullable=SeasonType.regular)
games = gamefinder.get_data_frames()[0]
del(gamefinder)

# sort the games and add home or visitor, remove extra columns
sorted_games = games[['GAME_ID', 'GAME_DATE', 'MATCHUP']].sort_values(by=['GAME_DATE'])
sorted_games['GAME_NUM'] = range(1, len(sorted_games) + 1)
sorted_games["HvV"] = sorted_games["MATCHUP"].map(
    lambda x: "HOME" if "vs." in x else "VISITOR" if "@" in x else NameError)
del(games)

# get the celtics roster
from nba_api.stats.endpoints import playerindex
BOS_roster = playerindex.PlayerIndex(team_id_nullable=celtics_id).get_data_frames()[0]

# get the game_id for a single game of the year
single_game_id = sorted_games.loc[sorted_games['GAME_NUM'] == 79, 'GAME_ID'].item()
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""get the playbyplay for that game"""

from nba_api.stats.endpoints import playbyplayv2
pbp_df = playbyplayv2.PlayByPlayV2(single_game_id).get_data_frames()[0]
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""modifying the playbyplay into a new df with new columns"""
# copy the df
pbp2_df = pbp_df.copy()

#time
pbp2_df.insert(7, 'SECONDS_LEFT', (4-pbp2_df['PERIOD']) * 12 * 60 + pd.Series(map(int, pbp2_df['PCTIMESTRING'].str.partition(':')[0])) * 60 + pd.Series(map(int, pbp2_df['PCTIMESTRING'].str.partition(':')[2])))

#score (filling the first row, forward filling columns, replacing TIE with 0)
pbp2_df.loc[0, ['SCORE', 'SCOREMARGIN']] = '0 - 0', 0
pbp2_df[['SCORE', 'SCOREMARGIN']] = pbp2_df[['SCORE', 'SCOREMARGIN']].ffill()
pbp2_df.loc[pbp2_df['SCOREMARGIN'] == 'TIE', 'SCOREMARGIN'] = 0
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""get the starters for each quarter using an entirely different method, store in dictionary"""
# imports
import json
import pandas as pd
import urllib3
header_data  = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-token': 'true',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

# endpoints, helper functions
def play_by_play_url(game_id):
    return "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14".format(game_id)
def advanced_boxscore_url(game_id, start, end):
    return "https://stats.nba.com/stats/boxscoretraditionalv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2".format(game_id, start, end)
http = urllib3.PoolManager()
def extract_data(url):
    print(url)
    r = http.request('GET', url, headers=header_data)
    resp = json.loads(r.data)
    results = resp['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    frame = pd.DataFrame(rows)
    frame.columns = headers
    return frame
def calculate_time_at_period(period):
    if period > 5:
        return (720 * 4 + (period - 5) * (5 * 60)) * 10
    else:
        return (720 * (period - 1)) * 10
def split_subs(df, tag):
    subs = df[[tag, 'PERIOD', 'EVENTNUM']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']
    return subs

# actual function
def quartersstarters(game_id):
    game_id = game_id
    frame = extract_data(play_by_play_url(game_id))

    substitutionsOnly = frame[frame["EVENTMSGTYPE"] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID']]
    substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN']

    subs_in = split_subs(substitutionsOnly, 'IN')
    subs_out = split_subs(substitutionsOnly, 'OUT')

    full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']]
    first_event_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['EVENTNUM'].idxmin()]
    players_subbed_in_at_each_period = first_event_of_period[first_event_of_period['SUB'] == 'IN'][
        ['PLAYER_ID', 'PERIOD', 'SUB']]

    periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()

    frames = []
    for period in periods:
        low = calculate_time_at_period(period) + 5
        high = calculate_time_at_period(period + 1) - 5
        boxscore = advanced_boxscore_url(game_id, low, high)
        boxscore_players = extract_data(boxscore)[['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION']]
        boxscore_players['PERIOD'] = period

        players_subbed_in_at_period = players_subbed_in_at_each_period[
            players_subbed_in_at_each_period['PERIOD'] == period]

        joined_players = pd.merge(boxscore_players, players_subbed_in_at_period, on=['PLAYER_ID', 'PERIOD'], how='left')
        joined_players = joined_players[pd.isnull(joined_players['SUB'])][
            ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'PERIOD']]
        frames.append(joined_players)

    quarter_starters = pd.concat(frames)
    return quarter_starters

qs = quartersstarters('0022301148')

BOS_qs1 = list(qs.loc[(qs['TEAM_ABBREVIATION'] == 'BOS') & (qs['PERIOD'] == 1), 'PLAYER_ID'])
BOS_qs2 = list(qs.loc[(qs['TEAM_ABBREVIATION'] == 'BOS') & (qs['PERIOD'] == 2), 'PLAYER_ID'])
BOS_qs3 = list(qs.loc[(qs['TEAM_ABBREVIATION'] == 'BOS') & (qs['PERIOD'] == 3), 'PLAYER_ID'])
BOS_qs4 = list(qs.loc[(qs['TEAM_ABBREVIATION'] == 'BOS') & (qs['PERIOD'] == 4), 'PLAYER_ID'])
OPP_qs1 = list(qs.loc[(qs['TEAM_ABBREVIATION'] != 'BOS') & (qs['PERIOD'] == 1), 'PLAYER_ID'])
OPP_qs2 = list(qs.loc[(qs['TEAM_ABBREVIATION'] != 'BOS') & (qs['PERIOD'] == 2), 'PLAYER_ID'])
OPP_qs3 = list(qs.loc[(qs['TEAM_ABBREVIATION'] != 'BOS') & (qs['PERIOD'] == 3), 'PLAYER_ID'])
OPP_qs4 = list(qs.loc[(qs['TEAM_ABBREVIATION'] != 'BOS') & (qs['PERIOD'] == 4), 'PLAYER_ID'])

qs_dict = {'BOS_qs1':BOS_qs1, 'BOS_qs2':BOS_qs2, 'BOS_qs3':BOS_qs3, 'BOS_qs4':BOS_qs4, 'OPP_qs1':OPP_qs1, 'OPP_qs2':OPP_qs2, 'OPP_qs3':OPP_qs3, 'OPP_qs4':OPP_qs4}
del(BOS_qs1, BOS_qs2, BOS_qs3, BOS_qs4, OPP_qs1, OPP_qs2, OPP_qs3, OPP_qs4)
del(header_data, http, qs)
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""from pbp2_df, find all the subs or quarter delineations"""
# in pbp_df, find all the subs/quarters, and make a new df with them (8 is sub, 12 is start of quarter)
subs_df = pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 8) | (pbp2_df['EVENTMSGTYPE'] == 12)]
# add a column for sub_stints, where the group of subs all count as one (this will separate game stints)
subs_df.insert(3, 'subs_stint_bool', subs_df.EVENTNUM == subs_df.EVENTNUM.shift() + 1)
subs_df.insert(3, 'subs_stint', subs_df['subs_stint_bool'].eq(False).cumsum())
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""creating a df to hold each game_stint (everything that happens between substitutions"""

# start a df that will hold all the game stints (lineups)
game_stints_df = pd.DataFrame(index=range(0, 100),
                              columns=['Stint_id', 'start_period', 'end_period', 'start_time', 'end_time', 'start_seconds', 'end_seconds', 'duration_s',
                                       'start_score', 'end_score', 'start_margin', 'end_margin', 'plusminus',
                                       'player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id',
                                       'lineup_long', 'lineup_id_ingame',
                                       'player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id',
                                       'OPP_lineup_long', 'OPP_lineup_id_ingame'])

#
for sub_stint in subs_df['subs_stint'].unique():
    sub_index = subs_df[subs_df['subs_stint'] == sub_stint].index[0]

    game_stints_df.loc[sub_stint - 1, ['Stint_id']] = sub_stint
    game_stints_df.loc[sub_stint - 1, ['start_period']] = subs_df.loc[sub_index, ['PERIOD']].item()
    game_stints_df.loc[sub_stint - 1, ['start_time']] = subs_df.loc[sub_index, ['PCTIMESTRING']].item()
    game_stints_df.loc[sub_stint - 1, ['start_seconds']] = subs_df.loc[sub_index, ['SECONDS_LEFT']].item()
    game_stints_df.loc[sub_stint - 1, ['start_score']] = subs_df.loc[sub_index, ['SCORE']].item()
    game_stints_df.loc[sub_stint - 1, ['start_margin']] = subs_df.loc[sub_index, ['SCOREMARGIN']].item()

    # subs portion (manually putting in the quarter starters whenever there's a new quarter)
    if subs_df.loc[sub_index, ['EVENTMSGTYPE']].item() == 12:
        period = subs_df.loc[sub_index, ['PERIOD']].item()

        game_stints_df.loc[sub_stint - 1, ['lineup_long']] = "-".join(map(str, qs_dict[f"BOS_qs{period}"]))
        game_stints_df.loc[sub_stint - 1, ['player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id']] = qs_dict[f"BOS_qs{period}"]

        game_stints_df.loc[sub_stint - 1, ['OPP_lineup_long']] = "-".join(map(str, qs_dict[f"OPP_qs{period}"]))
        game_stints_df.loc[sub_stint - 1, ['player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id']] = qs_dict[f"OPP_qs{period}"]

    elif subs_df.loc[sub_index, ['EVENTMSGTYPE']].item() == 8:
        new_lineup_long_str = game_stints_df.loc[sub_stint - 2, ['lineup_long']].item()
        new_OPP_lineup_long_str = game_stints_df.loc[sub_stint - 2, ['OPP_lineup_long']].item()

        for row in subs_df[subs_df['subs_stint'] == sub_stint].index:
            sub_out = subs_df.loc[row, ['PLAYER1_ID']].item()
            sub_in = subs_df.loc[row, ['PLAYER2_ID']].item()
            if sub_out.astype(str) in new_lineup_long_str:
                new_lineup_long_str = new_lineup_long_str.replace(sub_out.astype(str), sub_in.astype(str))
            elif sub_out.astype(str) in new_OPP_lineup_long_str:
                new_OPP_lineup_long_str = new_OPP_lineup_long_str.replace(sub_out.astype(str), sub_in.astype(str))

        new_lineup_long_str.split("-")
        lineup_IDs = [int(x) for x in new_lineup_long_str.split("-")]
        game_stints_df.loc[sub_stint - 1, ['player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id']] = lineup_IDs
        game_stints_df.loc[sub_stint - 1, ['lineup_long']] = new_lineup_long_str

        new_OPP_lineup_long_str.split("-")
        OPP_lineup_IDs = [int(x) for x in new_OPP_lineup_long_str.split("-")]
        game_stints_df.loc[sub_stint - 1, ['player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id']] = OPP_lineup_IDs
        game_stints_df.loc[sub_stint - 1, ['OPP_lineup_long']] = new_OPP_lineup_long_str

    else:
        game_stints_df.loc[sub_stint - 1, ['lineup_long']] = NameError

del(OPP_lineup_IDs, lineup_IDs, new_OPP_lineup_long_str, new_lineup_long_str, period, row, sub_in, sub_index, sub_out, sub_stint)
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""finalize df: calculate the info for the missing columns (don't need any other dfs but the active game_stints_df, mostly) and last row"""

#shorten df
game_stints_df = game_stints_df[:game_stints_df['Stint_id'].isnull().idxmax()]

#calculate the 'end_' columns that require looking to the next 'start_' rows
game_stints_df['end_period'] = game_stints_df['start_period'].shift(-1)
game_stints_df['end_time'] = game_stints_df['start_time'].shift(-1)
game_stints_df['end_seconds'] = game_stints_df['start_seconds'].shift(-1)
game_stints_df['end_score'] = game_stints_df['start_score'].shift(-1)
game_stints_df['end_margin'] = game_stints_df['start_margin'].shift(-1)

# fill in the last row
game_stints_df.loc[len(game_stints_df)-1, ['end_score']] = pbp2_df[(pbp_df['EVENTMSGTYPE'] == 13) & (pbp2_df['PERIOD'] == 4)]['SCORE'].item()
game_stints_df.loc[len(game_stints_df)-1, ['end_period']] = pbp2_df.loc[len(pbp2_df)-1, ['PERIOD']].item()
game_stints_df.loc[len(game_stints_df)-1, ['end_time']] = '0:00'
game_stints_df.loc[len(game_stints_df)-1, ['end_seconds']] = 0
game_stints_df.loc[len(game_stints_df)-1, ['end_margin']] = int(game_stints_df.loc[len(game_stints_df)-1, ['end_score']].item().partition(' - ')[2]) - \
                                                            int(game_stints_df.loc[len(game_stints_df)-1, ['end_score']].item().partition(' - ')[0])

# calculate the row-wise columns
game_stints_df['duration_s'] = game_stints_df['start_seconds'] - game_stints_df['end_seconds']
#need to change columns to numeric first (should you do this earlier?, are there other columns that need this?)
game_stints_df[["start_margin", "end_margin"]] = game_stints_df[["start_margin", "end_margin"]].apply(pd.to_numeric)
#calculate plusminus
game_stints_df['plusminus'] = game_stints_df['start_margin'] - game_stints_df['end_margin']

# giving ids to the lineups (the order of players may be different in different instances)
# i don't yet know how to do this, i think it involves making sets, but may need iterrows, maybe not
# game_stints_df[['player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id']].values.tolist()
# game_stints_df.insert(game_stints_df.columns.get_loc('lineup_id_ingame'), 'lineup_set', SOMEKINDOFSET)



