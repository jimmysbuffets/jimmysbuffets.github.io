"""having created reference dfs, see if you can answer questions about the game and check against the nba box score to confirm all is well"""
import pandas as pd

# need code to list the event types in a df, for both EVENTMSGTYPE and EVENTMSGACTIONTYPE, use nba_api documentation to make it


"""How many minutes did Jaylen Brown play?"""

# first get the traditional box score from the game
from nba_api.stats.endpoints import boxscoretraditionalv2
game_boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]

# get some of Jaylen Brown's row
game_boxscore[game_boxscore['PLAYER_NAME'] == 'Jaylen Brown'][['GAME_ID', 'PLAYER_ID','PLAYER_NAME','MIN','PLUS_MINUS']]

# using game_stints_df and Jaylen's player id (1627759), how many minutes did Jaylen play?
# which rows have Jaylen in the lineup string
'1627759' in game_stints_df.loc[0]['lineup_long']
game_stints_df['lineup_long'].str.contains('1627759')

# select those rows
Jaylen_in = game_stints_df[game_stints_df['lineup_long'].str.contains('1627759')]
# sum the duration column
Jaylen_in['duration_s'].sum()
# convert to minutes using divmod (division and modulo)
f"{divmod(2132, 60)[0]}:{divmod(2132, 60)[1]}"


"""What was Jaylen's Plus Minus (uses some of above)"""
Jaylen_in['plusminus'].sum()



"""Check some other players, and more complicated stats, maybe a WOWY"""


"""How many points did Jaylen score (unfinished)"""
# this will require looking at the pbp2_df or subs_df - there are many simpler ways than the one I used, but this is more generalizable I think
# mind the parentheses and order in the .query method
pbp2_df.query('(EVENTMSGTYPE == 1 or (EVENTMSGTYPE == 3 and EVENTMSGACTIONTYPE == 11)) and (PLAYER1_ID == 1627759)').index
Jaylen_points = pbp2_df.query('(EVENTMSGTYPE == 1 or (EVENTMSGTYPE == 3 and EVENTMSGACTIONTYPE == 11)) and (PLAYER1_ID == 1627759)')
Jaylen_points

"""What was Middleton's plusmins"""

# may need to have every team's roster on hand for player ids etc
# '203114' is Middleton's ID

Middleton_in = game_stints_df[game_stints_df['OPP_lineup_long'].str.contains('203114')]
Middleton_in['plusminus'].sum()

# this is negative when it should be positive, because you need to suss out the Home v away, team v opp, score/margin situation
# maybe there really should be a new pbp_df(3?) where you can have clearer home and visitor? or is it already clear enough
# honestly you should be able to generate the boxscore from the playbyplay

"""Bobby Portis rebounds"""
# 1626171, 4 is the EVENTMSGTYPE for rebounds
len(pbp2_df.query('EVENTMSGTYPE == 4 and PLAYER1_ID == 1626171'))



"""celtics, various pseudo WOWYs"""
# recreate that sports_mediocre table which requires players on, players off, minutes, netrtg, offrtg, defrtg, plusminus
# 4 options, JB and JT on, JB on JT off, JT on JB off, both off
# for Rtg you need possessions...
# but first how about just simple plusminus for the 4 options

# get the lineups where both Jaylens are in (i don't understand this str.contains but i think it works)
game_stints_df[game_stints_df['lineup_long'].str.contains(r'^(?=.*1627759)(?=.*1628369)')]['plusminus'].sum()
#alternatively:
game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['plusminus'].sum()
# JB only in
game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['plusminus'].sum()
# JT only in
game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['plusminus'].sum()
# neither in
game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['plusminus'].sum()

#believe this is all right, make a little table
dict = {'Players On': [f"{BOS_roster.query('PERSON_ID == 1628369')['PLAYER_LAST_NAME'].item()}, {BOS_roster.query('PERSON_ID == 1627759')['PLAYER_LAST_NAME'].item()}",
                       f"{BOS_roster.query('PERSON_ID == 1627759')['PLAYER_LAST_NAME'].item()}",
                       f"{BOS_roster.query('PERSON_ID == 1628369')['PLAYER_LAST_NAME'].item()}",
                       ""],
        'Players Off': ["",
                        f"{BOS_roster.query('PERSON_ID == 1628369')['PLAYER_LAST_NAME'].item()}",
                        f"{BOS_roster.query('PERSON_ID == 1627759')['PLAYER_LAST_NAME'].item()}",
                        f"{BOS_roster.query('PERSON_ID == 1628369')['PLAYER_LAST_NAME'].item()}, {BOS_roster.query('PERSON_ID == 1627759')['PLAYER_LAST_NAME'].item()}"],
        'Time': [f"{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['duration_s'].sum(), 60)[0]}:{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['duration_s'].sum(), 60)[1]}",
                    f"{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['duration_s'].sum(), 60)[0]}:{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['duration_s'].sum(), 60)[1]}",
                    f"{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['duration_s'].sum(), 60)[0]}:{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['duration_s'].sum(), 60)[1]}",
                    f"{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['duration_s'].sum(), 60)[0]}:{divmod(game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['duration_s'].sum(), 60)[1]}"],
        'PlusMinus': [game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['plusminus'].sum(),
                      game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == True) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['plusminus'].sum(),
                      game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == True)]['plusminus'].sum(),
                      game_stints_df[(game_stints_df['lineup_long'].str.contains('1627759') == False) & (game_stints_df['lineup_long'].str.contains('1628369') == False)]['plusminus'].sum()]}

table = pd.DataFrame(data=dict)
print(table)
# divmod has a small issue with single digit seconds
# you should just make this into a function with the game_IDs as input (would have to account for lineup_long vs OPP_lineup_long)


# you need more stats per game stint (possessions, pts for, pts against, 3pt shots, rebs etc.)
# should you do this when collecting the stints or use the time to do it post hoc (probably this, i guess you would use SECONDS_LEFT)
# might need to collect the EVENTNUM when making the game stints (seems wisest)