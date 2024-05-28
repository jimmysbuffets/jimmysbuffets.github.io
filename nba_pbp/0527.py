"""altering the new quarter starters checker to ensure it works right
it should be the first 5 player1IDs to do anything, unless it's a substitution in which case it's Player2, and unless that player was already subbed in"""
def get_teamdata(full_name):
    """Using a team's full name (e.g. 'Boston Celtics'), return team id# (int), games with some basic info (df), team roster (df)"""

    #imports
    import pandas as pd

    # using nba api, get df of all teams names and ids
    from nba_api.stats.static import teams
    refdf_teams = pd.DataFrame(teams.get_teams()).sort_values(by='full_name')

    # team id
    team_id = refdf_teams[refdf_teams['full_name'] == full_name]['id'].item()

    # list of games for the current season
    from nba_api.stats.endpoints import leaguegamefinder
    from nba_api.stats.library.parameters import Season
    from nba_api.stats.library.parameters import SeasonType
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id,
                                                   season_nullable=Season.default,
                                                   season_type_nullable=SeasonType.regular)
    games = gamefinder.get_data_frames()[0]

    sorted_games = games[['GAME_ID', 'GAME_DATE', 'MATCHUP']].sort_values(by=['GAME_DATE'])
    sorted_games['GAME_NUM'] = range(1, len(sorted_games) + 1)
    sorted_games["HvV"] = sorted_games["MATCHUP"].map(
        lambda x: "HOME" if "vs." in x else "VISITOR" if "@" in x else NameError)

    # roster
    from nba_api.stats.endpoints import playerindex
    team_roster = playerindex.PlayerIndex(team_id_nullable=team_id).get_data_frames()[0]

    return team_id, sorted_games, team_roster
# example: team_id, games, team_roster = get_teamdata("Boston Celtics")

def get_gamepbp(game_id, game_hvv):
    """Using a game_id, from the games output of get_teamdata, get that game's play-play-play log (df) pbp2_df"""
    #imports
    import pandas as pd
    import numpy as np

    #using nba_api, pull the raw playbyplay as a df
    from nba_api.stats.endpoints import playbyplayv2
    pbp_df = playbyplayv2.PlayByPlayV2(game_id).get_data_frames()[0]

    # copy the df (as pbp2_df, which will have modified data)
    pbp2_df = pbp_df.copy()

    # add a column for time (taking into account whether there is OT or not)
    if len(pbp2_df['PERIOD'].unique()) == 4:
        pbp2_df.insert(7, 'SECONDS_LEFT', (4 - pbp2_df['PERIOD']) * 12 * 60 + pd.Series(map(int, pbp2_df['PCTIMESTRING'].str.partition(':')[0])) * 60 + pd.Series(map(int, pbp2_df['PCTIMESTRING'].str.partition(':')[2])))
    elif len(pbp2_df['PERIOD'].unique()) == 5:
        pbp2_df.insert(7, 'SECONDS_LEFT', (4 - pbp2_df['PERIOD']) * 12 * 60 + pd.Series(
            map(int, pbp2_df['PCTIMESTRING'].str.partition(':')[0])) * 60 + pd.Series(
            map(int, pbp2_df['PCTIMESTRING'].str.partition(':')[2]))+300)
        pbp2_df.loc[pbp2_df['PERIOD'] == 5, 'SECONDS_LEFT'] += 420

    # modify columns relating to score (filling the first row, forward filling columns, replacing TIE with 0)
    pbp2_df.loc[0, ['SCORE', 'SCOREMARGIN']] = '0 - 0', 0
    pbp2_df[['SCORE', 'SCOREMARGIN']] = pbp2_df[['SCORE', 'SCOREMARGIN']].ffill()
    pbp2_df.loc[pbp2_df['SCOREMARGIN'] == 'TIE', 'SCOREMARGIN'] = 0

    # add a column for defensive rebounds, which will be needed later for possessions
    # get rebound indexes and initialize column
    rebound_idxs = pbp2_df[pbp2_df.EVENTMSGTYPE == 4].index
    pbp2_df['def_reb'] = int(0)

    # within a loop of the rebound_idxs, get the rebounding team and the shooting team
    for idx in rebound_idxs:

        # get the rebounding team in variable
        if pbp2_df.loc[idx, ['VISITORDESCRIPTION']].str.contains('REBOUND').item():
            rebound_team = 'VISITOR'
        elif pbp2_df.loc[idx, ['HOMEDESCRIPTION']].str.contains('REBOUND').item():
            rebound_team = 'HOME'
        else:
            rebound_team = NameError

        # get the previous shot team
        # first have to find the closest EVENTMSGTYPE of 2 or 3 before the index
        prev_shot_bool_list = pbp2_df[0:idx]['EVENTMSGTYPE'].isin([2, 3])
        prev_shot_idx = max(np.where(prev_shot_bool_list == True)[0].tolist())

        # get the previous shot's team
        if pbp2_df.loc[prev_shot_idx, ['PLAYER1_TEAM_ID']].item() == team_id:
            prev_shot_team = game_hvv
        elif pbp2_df.loc[prev_shot_idx, ['PLAYER1_TEAM_ID']].item() != team_id:
            if game_hvv == 'HOME':
                prev_shot_team = 'VISITOR'
            elif game_hvv == 'VISITOR':
                prev_shot_team = 'HOME'

        # if the previous shot team != rebounding team, def_reb is recorded
        if rebound_team == prev_shot_team:
            pbp2_df.loc[idx, ['def_reb']] = 0
        elif rebound_team != prev_shot_team:
            pbp2_df.loc[idx, ['def_reb']] = 1
        else:
            pbp2_df.loc[idx, ['def_reb']] = 0


    #final FT made (totally ignores 1 shot FTs that come after a make, whether they miss or make)
    import re
    ft_idxs = pbp2_df[pbp2_df.EVENTMSGTYPE == 3].index
    pbp2_df['finalFT_make'] = int(0)
    pbp2_df[['HOMEDESCRIPTION', 'VISITORDESCRIPTION']] = pbp2_df[['HOMEDESCRIPTION', 'VISITORDESCRIPTION']].fillna(
        value='')

    for idx in ft_idxs:
        if pbp2_df.loc[idx, ['VISITORDESCRIPTION']].item() != '':
            if re.search('Free Throw \d of \d', pbp2_df.loc[idx, ["VISITORDESCRIPTION"]].item()) != None:
                ft_before_of = re.findall(r'[\d]+', re.search('Free Throw \d of \d',
                                                              pbp2_df.loc[idx, ["VISITORDESCRIPTION"]].item()).group())[
                    0]
                ft_after_of = re.findall(r'[\d]+', re.search('Free Throw \d of \d',
                                                             pbp2_df.loc[idx, ["VISITORDESCRIPTION"]].item()).group())[
                    1]
                if pbp2_df.loc[idx, ["VISITORDESCRIPTION"]].str.contains('MISS').item():
                    ft_result = 'MISS'
                else:
                    ft_result = 'MAKE'

                if any(ele in ft_after_of for ele in list(['2','3'])) and ft_before_of == ft_after_of and ft_result == 'MAKE':
                    pbp2_df.loc[idx, ['finalFT_make']] = 1
                else:
                    pbp2_df.loc[idx, ['finalFT_make']] = 0
            else:
                pbp2_df.loc[idx, ['finalFT_make']] = 0
        elif pbp2_df.loc[idx, ['HOMEDESCRIPTION']].item() != '':
            if re.search('Free Throw \d of \d', pbp2_df.loc[idx, ["HOMEDESCRIPTION"]].item()) != None:
                ft_before_of = re.findall(r'[\d]+', re.search('Free Throw \d of \d',
                                                              pbp2_df.loc[idx, ["HOMEDESCRIPTION"]].item()).group())[0]
                ft_after_of = re.findall(r'[\d]+', re.search('Free Throw \d of \d',
                                                             pbp2_df.loc[idx, ["HOMEDESCRIPTION"]].item()).group())[1]
                if pbp2_df.loc[idx, ["HOMEDESCRIPTION"]].str.contains('MISS').item():
                    ft_result = 'MISS'
                else:
                    ft_result = 'MAKE'

                if any(ele in ft_after_of for ele in list(['2','3'])) and ft_before_of == ft_after_of and ft_result == 'MAKE':
                    pbp2_df.loc[idx, ['finalFT_make']] = 1
                else:
                    pbp2_df.loc[idx, ['finalFT_make']] = 0
            else:
                pbp2_df.loc[idx, ['finalFT_make']] = 0
        else:
            pbp2_df.loc[idx, ['finalFT_make']] = 0

    return pbp2_df
# example: pbp2_df = get_gamepbp(game_id, game_hvv)

def get_quarterstarters(pbp2_df):
    qstarters = {}
    for period in pbp2_df['PERIOD'].unique():
        whos_in = []
        subbed_in = []
        for row in pbp2_df[(pbp2_df['PERIOD'] == period) & (pbp2_df['PLAYER1_TEAM_ID'] == team_id)].index:
            if pbp2_df.loc[row, ['EVENTMSGTYPE']].item() == 8:
                player = pbp2_df.loc[row, ['PLAYER1_ID']].item().item()
                player_subbed_in = pbp2_df.loc[row, ['PLAYER2_ID']].item().item()
                subbed_in.append(player_subbed_in)
            else:
                player = pbp2_df.loc[row, ['PLAYER1_ID']].item().item()
            if player not in whos_in and player not in subbed_in:
                whos_in.append(player)
        qstarters.update({f"BOS_qs{period}": whos_in[0:5]})

    for period in pbp2_df['PERIOD'].unique():
        whos_in = []
        subbed_in = []
        for row in pbp2_df[(pbp2_df['PERIOD'] == period) & (
                (pbp2_df['PLAYER1_TEAM_ID'] != team_id) & (pbp2_df['PLAYER1_TEAM_ABBREVIATION'].notna()))].index:
            if pbp2_df.loc[row, ['EVENTMSGTYPE']].item() == 8:
                player = pbp2_df.loc[row, ['PLAYER1_ID']].item().item()
                player_subbed_in = pbp2_df.loc[row, ['PLAYER2_ID']].item().item()
                subbed_in.append(player_subbed_in)
            else:
                player = pbp2_df.loc[row, ['PLAYER1_ID']].item().item()
            if player not in whos_in and player not in subbed_in:
                whos_in.append(player)
        qstarters.update({f"OPP_qs{period}": whos_in[0:5]})

    return qstarters
# example qs_dict = get_quarterstarters(pbp2_df)

def qs_checker(qs_dict):
    if any(len(v) < 5 for v in qs_dict.values()):
        replacement_key = [k for k, v in qs_dict.items() if len(v) < 5][0]
        if 'BOS' in replacement_key:
            qs_dict.update({replacement_key: qs_dict['BOS_qs1']})
        elif 'OPP' in replacement_key:
            qs_dict.update({replacement_key: qs_dict['OPP_qs1']})
    else:
        pass

def get_subs(pbp2_df):
    """make a df made up of the rows containing substutions or quarter changes from the playbyplay data"""

    # in pbp_df, find all the subs/quarters, and make a new df with them (8 is sub, 12 is start of quarter)
    subs_df = pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 8) | (pbp2_df['EVENTMSGTYPE'] == 12)]

    # add a column for sub_stints, where the group of subs all count as one (this will separate game stints)
    subs_df.insert(3, 'subs_stint_bool', subs_df.EVENTNUM == subs_df.EVENTNUM.shift() + 1)
    subs_df.insert(3, 'subs_stint', subs_df['subs_stint_bool'].eq(False).cumsum())

    return subs_df
# example: subs_df = get_subs(pbp2_df)

def get_gamestints():
    """Using outputs from above, make a df of game stints, where each row shows the beginning and end result of the time between substitutions/quarters"""

    #imports
    import pandas as pd
    import numpy as np

    # start a df that will hold all the game stints (lineups)
    game_stints_df = pd.DataFrame(index=range(0, 100),
                                  columns=['game_id', 'Stint_id', 'start_period', 'end_period', 'start_time', 'end_time',
                                           'start_seconds', 'end_seconds', 'duration_s', 'start_eventnum', 'end_eventnum',
                                           'start_score', 'end_score', 'start_margin', 'end_margin', 'plusminus',
                                           'player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id',
                                           'lineup_long', 'lineup_id_ingame',
                                           'player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id',
                                           'OPP_lineup_long', 'OPP_lineup_id_ingame'])

    # loop through the stints in subs_df
    for sub_stint in subs_df['subs_stint'].unique():
        sub_index = subs_df[subs_df['subs_stint'] == sub_stint].index[0]

        game_stints_df.loc[sub_stint - 1, ['game_id']] = subs_df.loc[sub_index, ['GAME_ID']].item()
        game_stints_df.loc[sub_stint - 1, ['Stint_id']] = sub_stint
        game_stints_df.loc[sub_stint - 1, ['start_period']] = subs_df.loc[sub_index, ['PERIOD']].item()
        game_stints_df.loc[sub_stint - 1, ['start_time']] = subs_df.loc[sub_index, ['PCTIMESTRING']].item()
        game_stints_df.loc[sub_stint - 1, ['start_seconds']] = subs_df.loc[sub_index, ['SECONDS_LEFT']].item()
        game_stints_df.loc[sub_stint - 1, ['start_score']] = subs_df.loc[sub_index, ['SCORE']].item()
        if game_hvv == 'VISITOR':
            game_stints_df.loc[sub_stint - 1, ['start_margin']] = int(game_stints_df.loc[sub_stint - 1, ['start_score']].item().partition(' - ')[0]) - \
                                                                          int(game_stints_df.loc[sub_stint - 1, ['start_score']].item().partition(' - ')[2])
        elif game_hvv == 'HOME':
            game_stints_df.loc[sub_stint - 1, ['start_margin']] = int(game_stints_df.loc[sub_stint - 1, ['start_score']].item().partition(' - ')[2]) - \
                                                                          int(game_stints_df.loc[sub_stint - 1, ['start_score']].item().partition(' - ')[0])
        game_stints_df.loc[sub_stint - 1, ['start_eventnum']] = subs_df.loc[sub_index, ['EVENTNUM']].item()

        # subs portion (manually putting in the quarter starters whenever there's a new quarter)
        if subs_df.loc[sub_index, ['EVENTMSGTYPE']].item() == 12:
            period = subs_df.loc[sub_index, ['PERIOD']].item()

            game_stints_df.loc[sub_stint - 1, ['lineup_long']] = "-".join(map(str, qs_dict[f"BOS_qs{period}"]))
            game_stints_df.loc[sub_stint - 1, ['player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id']] = \
            qs_dict[f"BOS_qs{period}"]

            game_stints_df.loc[sub_stint - 1, ['OPP_lineup_long']] = "-".join(map(str, qs_dict[f"OPP_qs{period}"]))
            game_stints_df.loc[sub_stint - 1, ['player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id']] = \
            qs_dict[f"OPP_qs{period}"]

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
            game_stints_df.loc[
                sub_stint - 1, ['player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id']] = lineup_IDs
            game_stints_df.loc[sub_stint - 1, ['lineup_long']] = new_lineup_long_str

            new_OPP_lineup_long_str.split("-")
            OPP_lineup_IDs = [int(x) for x in new_OPP_lineup_long_str.split("-")]
            game_stints_df.loc[
                sub_stint - 1, ['player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id']] = OPP_lineup_IDs
            game_stints_df.loc[sub_stint - 1, ['OPP_lineup_long']] = new_OPP_lineup_long_str

        else:
            game_stints_df.loc[sub_stint - 1, ['lineup_long']] = NameError

    # shorten df
    game_stints_df = game_stints_df[:game_stints_df['Stint_id'].isnull().idxmax()]

    # calculate the 'end_' columns that require looking to the next 'start_' rows
    game_stints_df['end_period'] = game_stints_df['start_period'].shift(-1)
    game_stints_df['end_time'] = game_stints_df['start_time'].shift(-1)
    game_stints_df['end_seconds'] = game_stints_df['start_seconds'].shift(-1)
    game_stints_df['end_score'] = game_stints_df['start_score'].shift(-1)
    game_stints_df['end_margin'] = game_stints_df['start_margin'].shift(-1)
    game_stints_df['end_eventnum'] = game_stints_df['start_eventnum'].shift(-1)

    # fill in the last row
    if len(pbp2_df['PERIOD'].unique()) == 4:
        game_stints_df.loc[len(game_stints_df) - 1, ['end_score']] = pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 13) & (pbp2_df['PERIOD'] == 4)]['SCORE'].item()
    elif len(pbp2_df['PERIOD'].unique()) == 5:
        game_stints_df.loc[len(game_stints_df) - 1, ['end_score']] = pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 13) & (pbp2_df['PERIOD'] == 5)]['SCORE'].item()

    game_stints_df.loc[len(game_stints_df) - 1, ['end_period']] = pbp2_df.loc[len(pbp2_df) - 1, ['PERIOD']].item()
    game_stints_df.loc[len(game_stints_df) - 1, ['end_time']] = '0:00'
    game_stints_df.loc[len(game_stints_df) - 1, ['end_seconds']] = 0
    if game_hvv == 'VISITOR':
        game_stints_df.loc[len(game_stints_df) - 1, ['end_margin']] = int(game_stints_df.loc[len(game_stints_df) - 1, ['end_score']].item().partition(' - ')[0]) - \
                                                                      int(game_stints_df.loc[len(game_stints_df) - 1, ['end_score']].item().partition(' - ')[2])
    elif game_hvv == 'HOME':
        game_stints_df.loc[len(game_stints_df) - 1, ['end_margin']] = int(game_stints_df.loc[len(game_stints_df) - 1, ['end_score']].item().partition(' - ')[2]) - \
                                                                      int(game_stints_df.loc[len(game_stints_df) - 1, ['end_score']].item().partition(' - ')[0])
    if len(pbp2_df['PERIOD'].unique()) == 4:
        game_stints_df.loc[len(game_stints_df)-1, ['end_eventnum']] = pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 13) & (pbp2_df['PERIOD'] == 4)]['EVENTNUM'].item()
    elif len(pbp2_df['PERIOD'].unique()) == 5:
        game_stints_df.loc[len(game_stints_df) - 1, ['end_eventnum']] = \
        pbp2_df[(pbp2_df['EVENTMSGTYPE'] == 13) & (pbp2_df['PERIOD'] == 5)]['EVENTNUM'].item()

    # calculate the row-wise columns
    game_stints_df['duration_s'] = game_stints_df['start_seconds'] - game_stints_df['end_seconds']
    # need to change columns to numeric first (should you do this earlier?, are there other columns that need this?)
    game_stints_df[["start_margin", "end_margin"]] = game_stints_df[["start_margin", "end_margin"]].apply(pd.to_numeric)
    # calculate plusminus (this doesn't need to have an if any more, vestigial code)
    if game_hvv == 'VISITOR':
        game_stints_df['plusminus'] = game_stints_df['end_margin'] - game_stints_df['start_margin']
    elif game_hvv == 'HOME':
        game_stints_df['plusminus'] = game_stints_df['end_margin'] - game_stints_df['start_margin']

    # insert columns in game_stints_df
    game_stints_df['pts_for'] = int(0)
    game_stints_df['pts_against'] = int(0)
    # get the pts for and against from within the game_stints_df
    game_stints_df['pts_for'] = 0
    game_stints_df['pts_against'] = 0
    for row in game_stints_df.index:
        if game_hvv == 'VISITOR':
            game_stints_df.loc[row, ['pts_for']] = int(
                game_stints_df.loc[row, ['end_score']].item().partition(' - ')[0]) - int(
                game_stints_df.loc[row, ['start_score']].item().partition(' - ')[0])
            game_stints_df.loc[row, ['pts_against']] = int(
                game_stints_df.loc[row, ['end_score']].item().partition(' - ')[2]) - int(
                game_stints_df.loc[row, ['start_score']].item().partition(' - ')[2])
        elif game_hvv == 'HOME':
            game_stints_df.loc[row, ['pts_for']] = int(
                game_stints_df.loc[row, ['end_score']].item().partition(' - ')[2]) - int(
                game_stints_df.loc[row, ['start_score']].item().partition(' - ')[2])
            game_stints_df.loc[row, ['pts_against']] = int(
                game_stints_df.loc[row, ['end_score']].item().partition(' - ')[0]) - int(
                game_stints_df.loc[row, ['start_score']].item().partition(' - ')[0])

    """get possessions into game_stints_df"""

    # add column
    game_stints_df['possessions'] = int(0)

    # slice the pbp2 data into game stint slice for tallying possessions
    for row in game_stints_df.index:
        pbp_start_index = pbp2_df[
            pbp2_df['EVENTNUM'] == game_stints_df.loc[row, ['start_eventnum']].item()].index.item()
        pbp_end_index = pbp2_df[pbp2_df['EVENTNUM'] == game_stints_df.loc[row, ['end_eventnum']].item()].index.item()
        possession_slice = pbp2_df[pbp_start_index:pbp_end_index].copy()

        possession_tally = possession_slice[
            (possession_slice.EVENTMSGTYPE == 1) | (possession_slice.EVENTMSGTYPE == 5) | (
                    possession_slice.def_reb == 1) | (possession_slice.finalFT_make == 1)].shape[0]

        game_stints_df.loc[row, ['possessions']] = possession_tally

    # do variables need to be deleted?
    """i believe this works, although if there are 0 possession changes within a game_stint some errors may arise"""




    return game_stints_df
# example: game_stints_df = get_gamestints()

#actual loop to get a set of playbyplay data formatted into game_stints all in one df

import pandas as pd

team_id, games, team_roster = get_teamdata("Boston Celtics")
game_stints_all = pd.DataFrame()

for game_num in range(1,83):
    game_id = games.loc[games['GAME_NUM'] == game_num, 'GAME_ID'].item()
    game_hvv = games.loc[games['GAME_NUM'] == game_num, 'HvV'].item()

    pbp2_df = get_gamepbp(game_id, game_hvv)
    qs_dict = get_quarterstarters(pbp2_df)
    qs_checker(qs_dict)
    subs_df = get_subs(pbp2_df)
    game_stints_df = get_gamestints()

    game_stints_all = pd.concat([game_stints_all, game_stints_df])

# game_stints_all.to_csv('maybe_final_gamestints_all.csv')
# pd.read_csv('maybe_final_gamestints_all.csv', index_col=0)
