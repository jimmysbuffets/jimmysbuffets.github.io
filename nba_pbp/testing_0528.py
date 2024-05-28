import pandas as pd
BOS_gamestints = pd.read_csv('BOS_game_stints_all.csv', index_col=0)

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
team_id, games, team_roster = get_teamdata("Boston Celtics")

"""make a table of celtics players and the minutes played in game 37 of the season"""

#id the game and home/visitor
game_id = games.loc[games['GAME_NUM'] == 37, 'GAME_ID'].item()
game_hvv = games.loc[games['GAME_NUM'] == 37, 'HvV'].item()

# get the ids, names, and minutes of every celtics player in this game
boxscore_minutes = pd.DataFrame()
for row in team_roster.index:
    id, last, first = team_roster.loc[row, ['PERSON_ID', 'PLAYER_LAST_NAME', 'PLAYER_FIRST_NAME']]
    player_in_df = BOS_gamestints[(BOS_gamestints['game_id'] == int(game_id)) & (BOS_gamestints['lineup_long'].str.contains(str(id)))]

    if len(player_in_df) > 0:
        minutes_string = "{}:{:02d}".format(divmod(player_in_df['duration_s'].sum().item(), 60)[0],
                                            divmod(player_in_df['duration_s'].sum().item(), 60)[1])
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), minutes_string]])
    else:
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), "DNP"]])

    #boxscore_minutes._append(player_summary)
    boxscore_minutes = pd.concat([boxscore_minutes, player_summary])
boxscore_minutes.columns = [['player_id', 'last, first', 'minutes']]
del(row, id, last, first, player_in_df, minutes_string, player_summary)

# same but for plusminus
boxscore_plusminus = pd.DataFrame()
for row in team_roster.index:
    id, last, first = team_roster.loc[row, ['PERSON_ID', 'PLAYER_LAST_NAME', 'PLAYER_FIRST_NAME']]
    player_in_df = BOS_gamestints[(BOS_gamestints['game_id'] == int(game_id)) & (BOS_gamestints['lineup_long'].str.contains(str(id)))]

    if len(player_in_df) > 0:
        plusminus = player_in_df['plusminus'].sum().item()
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), plusminus]])
    else:
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), "DNP"]])

    #boxscore_minutes._append(player_summary)
    boxscore_plusminus = pd.concat([boxscore_plusminus, player_summary])
boxscore_plusminus.columns = [['player_id', 'last, first', 'plusminus']]
del(row, id, last, first, player_in_df, plusminus, player_summary)
#well...the plusminus are slightly off...
#my guess is it has to do with subs happening between FTs, and that it will even out over the season

# same but for OffRtg and DefRtg
boxscore_ratings = pd.DataFrame()
for row in team_roster.index:
    id, last, first = team_roster.loc[row, ['PERSON_ID', 'PLAYER_LAST_NAME', 'PLAYER_FIRST_NAME']]
    player_in_df = BOS_gamestints[(BOS_gamestints['game_id'] == int(game_id)) & (BOS_gamestints['lineup_long'].str.contains(str(id)))]

    if len(player_in_df) > 0:
        OffRtg = round(player_in_df['pts_for'].sum().item() / (player_in_df['possessions'].sum().item()/2) * 100, 2)
        DefRtg = round(player_in_df['pts_against'].sum().item() / (player_in_df['possessions'].sum().item() / 2) * 100, 2)
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), OffRtg, DefRtg]])
    else:
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), "DNP", "DNP"]])

    #boxscore_minutes._append(player_summary)
    boxscore_ratings = pd.concat([boxscore_ratings, player_summary])
boxscore_ratings.columns = [['player_id', 'last, first', 'OffRtg', 'DefRtg']]
#del(row, id, last, first, player_in_df, plusminus, player_summary)

# next do for the whole season and check
# according to https://www.nba.com/stats/team/1610612738/onoffcourt-traditional?SeasonType=Regular+Season&PerMode=Per100Possessions the BOS per 100 +/- is 11.5
(BOS_gamestints['pts_for'].sum() - BOS_gamestints['pts_against'].sum()) / (BOS_gamestints['possessions'].sum() / 2) * 100
# gets 11.11
# pretty close? the difference is in possessions I think? but shouldn't mine be better

# how about team totals
BOS_gamestints['pts_for'].sum()
# good
BOS_gamestints['plusminus'].sum()
# i get 933, nba gets 930. what's up with that
# Derrick White's +/- 619
player_id = team_roster[team_roster['PLAYER_LAST_NAME'] == 'White']['PERSON_ID'].item()
BOS_gamestints[BOS_gamestints['lineup_long'].str.contains(str(player_id))]['plusminus'].sum()
# i got 617...close but why the difference (again probably the FT sub order)
#here is for all the players

season_plusminus = pd.DataFrame()
for row in team_roster.index:
    id, last, first = team_roster.loc[row, ['PERSON_ID', 'PLAYER_LAST_NAME', 'PLAYER_FIRST_NAME']]
    player_in_df = BOS_gamestints[BOS_gamestints['lineup_long'].str.contains(str(id))]

    if len(player_in_df) > 0:
        plusminus = player_in_df['plusminus'].sum()
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), plusminus]])
    else:
        player_summary = pd.DataFrame([[id, "{}, {}".format(last, first), "DNP"]])

    #boxscore_minutes._append(player_summary)
    season_plusminus = pd.concat([season_plusminus, player_summary])
season_plusminus.columns = [['player_id', 'last, first', 'season +/-']]
