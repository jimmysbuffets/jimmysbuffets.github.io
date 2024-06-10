"""for calculating seconds_left maybe"""

    timegame = pd.Series([np.abs((minute * 60 + sec) - 720 * period) if period < 5 \
                              else np.abs((minute * 60 + sec) - (2880 + 300 * (period - 4))) \
                          for (minute, sec, period) in zip(s["MIN"], s["SEC"], data["PERIOD"])])
