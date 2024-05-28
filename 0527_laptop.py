'"C:\Users\alexr\Desktop\maybe_final_gamestints_all.csv"'
import pandas as pd

gamestints_all = pd.read_csv('maybe_final_gamestints_all.csv', index_col=0)

game_id = games.loc[games['GAME_NUM'] == 37, 'GAME_ID'].item()
game_hvv = games.loc[games['GAME_NUM'] == 37, 'HvV'].item()

JB_ID = '1627759'

gamestints_all[(gamestints_all['game_id'] == int(game_id)) & (gamestints_all['lineup_long'].str.contains(JB_ID))]
Jaylen_in = gamestints_all[(gamestints_all['game_id'] == int(game_id)) & (gamestints_all['lineup_long'].str.contains(JB_ID))]

#how many seconds was Jaylen in
Jaylen_in['duration_s'].sum().item()
#seconds divmod
secs_div = divmod(Jaylen_in['duration_s'].sum().item(), 60)
#
min_string = f"{divmod(Jaylen_in['duration_s'].sum().item(), 60)[0]}:{divmod(Jaylen_in['duration_s'].sum().item(), 60)[0]}"

#print minutes:seconds string
"{}:{:02d}".format(divmod(Jaylen_in['duration_s'].sum().item(), 60)[0],
                   divmod(Jaylen_in['duration_s'].sum().item(), 60)[1])

# get the ids, names, and minutes of every celtics player in this game
boxscore_minutes = pd.DataFrame()
for row in team_roster.index:
    id, last, first = team_roster.loc[row, ['PERSON_ID', 'PLAYER_LAST_NAME', 'PLAYER_FIRST_NAME']]

    if any(gamestints_all['lineup_long'].str.contains(str(id))):
        player_in_df = gamestints_all[(gamestints_all['game_id'] == int(game_id)) &
                                  (gamestints_all['lineup_long'].str.contains(str(id)))]
        minutes_string = "{}:{:02d}".format(divmod(player_in_df['duration_s'].sum().item(), 60)[0],
                                            divmod(player_in_df['duration_s'].sum().item(), 60)[1])
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), minutes_string]])
    else:
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), "DNP"]])

    #boxscore_minutes._append(player_summary)
    boxscore_minutes = pd.concat([boxscore_minutes, player_summary])

# something like this is cool
