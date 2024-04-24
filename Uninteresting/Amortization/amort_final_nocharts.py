#this is going to be the final attempt, where I check, clarify, and describe all the code elements
#still need to clean up once

import pandas as pd
from datetime import date

def periodic_interest_rate(i, n):
    """periodic interest rate is the annual interest rate divided by the number of compounding periods
    pir = periodic interest rate
    i = annual interest rate (nominal interest rate)
    n = number of compounding periods per year (compounding frequency)
    """
    pir = i/n
    return pir
def periodic_payment_amount(P, pir, n, y):
    """the periodic payment amount is the total amount owed (principal + interest) per compounding period
    ppa = periodic payment amount
    P = initial Principal (loan amount)
    pir = periodic interest rate
    n = compounding periods per year
    y = length of loan in years
    """
    ppa = P * (pir*(1+pir)**(n*y)) / (((1+pir)**(n*y))-1)
    return ppa


def amortization_table(nominal_interest_rate, years, compounding_frequency, payment_frequency, principal, start_date):
    """generates the complete amortization table for the duration of the loan
    df = the final amortization table
    nominal_interest_rate = yearly interest rate of loan
    years = number of years of the loan
    compounding_frequency = compounding periods per year
    payment_frequency = payment periods per year (monthly = 12, "biweekly" = 26)
    principal = initial loan amaount
    start_date = first day of the loan in date(YYYY,MM,D) format
    """
    pir = periodic_interest_rate(i=nominal_interest_rate, n=compounding_frequency)

    # getting compounding period dates for the length of the loan - monthly for American mortgages
    compounding_date_range = pd.date_range(start=start_date, periods=years * compounding_frequency, freq='MS')

    # set up the df with compounding dates as index
    df = pd.DataFrame(index=compounding_date_range,
                      columns=['Payments_per_Period', 'Principal', 'Additional_Principal', 'Interest',
                               'Total_Payment_Due', 'Balance_In', 'Balance_Out'],
                      dtype='float')
    df.reset_index(names='Compound_Date', inplace=True)
    df.index += 1

    # getting payment period dates for the length of the loan
    # we may have a regular pay schedule that differs from the compounding schedule (e.g. biweekly payment vs monthly compounding)
    # find the day of the week of the first day of the loan
    first_day_integer = start_date.weekday()  # 0=Monday, 1=Tuesday, etc
    weekdays_dict = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
    first_day_name = weekdays_dict[first_day_integer]
    # declare the frequency variable for the date_range function depending on payment frequency and day of week
    if payment_frequency == 12:
        frequency_variable = 'MS'
    elif payment_frequency == 26:
        frequency_variable = f"2W-{first_day_name}"
    else:
        frequency_variable = None
    payment_date_range = pd.date_range(start=start_date, periods=years * payment_frequency, freq=frequency_variable)

    dates_df = pd.DataFrame(columns=['pay_date', 'compound_period'],
                            dtype='float')
    dates_df['pay_date'] = payment_date_range
    dates_df['compound_period'] = payment_date_range.to_period('M')

    # how many biweekly payments happen in each month
    payments_per_period_list = list(dates_df.groupby('compound_period').count()['pay_date'])
    # manually input the last month because the biweekly payment ends before 2053-10-01 (won't matter anyway)
    if payment_frequency == 26:
        payments_per_period_list.append(2)
    else:
        pass

    # add Payments_Per_Period
    df['Payments_per_Period'] = payments_per_period_list

    # inputting the periodic total monthly payment (what you owe each month, not including an additional you pay)
    periodic_total_payment = periodic_payment_amount(P=principal, pir=pir, n=compounding_frequency,
                                                     y=years)
    df['Total_Payment_Due'] = periodic_total_payment

    # add Additional Principal based on if there is an extra payment per period
    df.loc[df['Payments_per_Period'] == 3, 'Additional_Principal'] = periodic_total_payment * payment_frequency / 52
    df.fillna({'Additional_Principal': 0}, inplace=True)

    # fill in the first row
    df.loc[1, 'Balance_In'] = principal
    df.loc[1, 'Interest'] = pir * df.loc[1, 'Balance_In']
    df.loc[1, 'Principal'] = df.loc[1, 'Total_Payment_Due'] - df.loc[1, 'Interest']
    df.loc[1, 'Balance_Out'] = df.loc[1, 'Balance_In'] - df.loc[1, 'Principal'] - df.loc[1, 'Additional_Principal']
    new_balance = df.loc[1, 'Balance_Out']  # this value is needed to run the subsequent loop

    for index, row in df.iloc[1:].iterrows():
        df.loc[index, 'Balance_In'] = new_balance
        df.loc[index, 'Interest'] = pir * df.loc[index, 'Balance_In']
        df.loc[index, 'Principal'] = df.loc[index, 'Total_Payment_Due'] - df.loc[index, 'Interest']
        df.loc[index, 'Balance_Out'] = df.loc[index, 'Balance_In'] - df.loc[index, 'Principal'] - df.loc[index, 'Additional_Principal']
        new_balance = df.loc[index, 'Balance_Out']

    # find where the Balance_Out goes negative, end the df there, make sure the last payment adds up
    if payment_frequency == 26:
        last_payment_row = df.query("Balance_Out <= 0")["Balance_Out"].idxmax(skipna=True)
        df = df.loc[0:last_payment_row].copy()
        # make sure the last principal payment isn't too much (could also use df.loc[len(df), 'Principal] eg)
        df.iloc[-1, df.columns.get_loc("Principal")] = df.iloc[-1, df.columns.get_loc("Principal")] + df.iloc[-1, df.columns.get_loc("Balance_Out")]
        df.iloc[-1, df.columns.get_loc("Balance_Out")] = 0
        df.iloc[-1, df.columns.get_loc("Total_Payment_Due")] = df.iloc[-1, df.columns.get_loc("Balance_In")] + df.iloc[-1, df.columns.get_loc("Interest")]
        # this isn't exactly right but whatever
    else:
        pass


    # remove some variables?

    return df

# generate amortization tables for monthly and biweekly payments of an American monthly compounding mortgage
monthly = amortization_table(.0725, 30, 12, 12, 462000, date(2023,11,1))
biweekly = amortization_table(.0725, 30, 12, 26, 462000, date(2023,11,1))

#round the dataframes for clarity
monthly = monthly.round(2).copy()
biweekly = biweekly.round(2).copy()

#need to do summary stats and charts



