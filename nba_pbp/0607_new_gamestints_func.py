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
        sub_index = subs_df[subs_df['subs_stint'] == sub_stint].index.max()

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
        if subs_df.loc[sub_index, ['EVENTMSGTYPE']].item() == 12 or subs_df.loc[sub_index, ['EVENTMSGTYPE']].item() == 18:
            period = subs_df.loc[sub_index, ['PERIOD']].item()

            game_stints_df.loc[sub_stint - 1, ['lineup_long']] = "-".join(map(str, qs_dict[f"BOS_qs{period}"]))
            game_stints_df.loc[sub_stint - 1, ['player1_id', 'player2_id', 'player3_id', 'player4_id', 'player5_id']] = \
            qs_dict[f"BOS_qs{period}"]

            game_stints_df.loc[sub_stint - 1, ['OPP_lineup_long']] = "-".join(map(str, qs_dict[f"OPP_qs{period}"]))
            game_stints_df.loc[sub_stint - 1, ['player6_id', 'player7_id', 'player8_id', 'player9_id', 'player10_id']] = \
            qs_dict[f"OPP_qs{period}"]

        else:
            new_lineup_long_str = game_stints_df.loc[sub_stint - 2, ['lineup_long']].item()
            new_OPP_lineup_long_str = game_stints_df.loc[sub_stint - 2, ['OPP_lineup_long']].item()

            for row in subs_df[subs_df['subs_stint'] == sub_stint].index:
                if subs_df.loc[row, ['EVENTMSGTYPE']].item() == 8:
                    sub_out = subs_df.loc[row, ['PLAYER1_ID']].item()
                    sub_in = subs_df.loc[row, ['PLAYER2_ID']].item()
                    if sub_out.astype(str) in new_lineup_long_str:
                        new_lineup_long_str = new_lineup_long_str.replace(sub_out.astype(str), sub_in.astype(str))
                    elif sub_out.astype(str) in new_OPP_lineup_long_str:
                        new_OPP_lineup_long_str = new_OPP_lineup_long_str.replace(sub_out.astype(str),
                                                                                  sub_in.astype(str))
                else:
                    continue

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
