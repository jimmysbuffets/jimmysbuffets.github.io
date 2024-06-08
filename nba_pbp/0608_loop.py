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

BOS_gamestints = game_stints_all.copy()
#BOS_gamestints.reset_index(inplace=True)
