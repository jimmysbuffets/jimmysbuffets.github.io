#trying some charts WITH DESCRIPTIONS

# import libraries
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
import numpy as np

#create the standard lineplot with shading
plt.plot(monthly['Compound_Date'], monthly['Principal'], color='tab:orange')
plt.plot(monthly['Compound_Date'], monthly['Total_Payment_Due'], color='tab:blue', alpha=0.5)
plt.fill_between(monthly['Compound_Date'], monthly['Principal'], monthly['Total_Payment_Due'], alpha=0.5)
plt.fill_between(monthly['Compound_Date'], 0, monthly['Principal'], alpha=0.5)
plt.xlim(monthly.loc[monthly['Compound_Date'].idxmin()]['Compound_Date'], monthly.loc[monthly['Compound_Date'].idxmax()]['Compound_Date'])
plt.ylim(0,monthly.loc[monthly['Total_Payment_Due'].idxmax()]['Total_Payment_Due'])
plt.xlabel('Date')
plt.ylabel("Monthly Payment")
plt.title('Mortgage Amortization Table, Principal and Interest')
plt.legend(['Principal', 'Interest'], loc='center left', bbox_to_anchor = (1,.5))
plt.show()

#lineplot with lines for the principal and interest and noting where they cross
plt.plot(monthly['Compound_Date'], monthly['Principal'], color='tab:orange')
plt.plot(monthly['Compound_Date'], monthly['Interest'], color='tab:blue')
plt.axvline(monthly.loc[monthly.query("Principal > Interest")['Compound_Date'].idxmin(skipna=True), 'Compound_Date'],
            color='lightgrey',
            linestyle=':')
plt.annotate(text=monthly.loc[monthly.query("Principal > Interest")['Compound_Date'].idxmin(skipna=True), 'Compound_Date'].strftime("%x"),
             xy=[monthly.loc[monthly.query("Principal > Interest")['Compound_Date'].idxmin(skipna=True) + 4, 'Compound_Date'], 100],
             color='lightgrey')
plt.xlim(monthly.loc[monthly['Compound_Date'].idxmin()]['Compound_Date'], monthly.loc[monthly['Compound_Date'].idxmax()]['Compound_Date'])
plt.ylim(0,monthly.loc[monthly['Total_Payment_Due'].idxmax()]['Total_Payment_Due'])
plt.xlabel('Date')
plt.ylabel("Monthly Payment")
plt.title('Mortgage Amortization Table, Principal and Interest')
plt.legend(['Principal', 'Interest'], loc='center left', bbox_to_anchor = (1,.5))
plt.show()
#need to do with background color (do fig, ax)

#replicating above with fig, ax so you can do background colors
fig, ax = plt.subplots(facecolor=('linen'))
plt.plot(monthly['Compound_Date'], monthly['Principal'], color='tab:orange')
plt.plot(monthly['Compound_Date'], monthly['Interest'], color='tab:blue')
plt.axvline(monthly.loc[monthly.query("Principal > Interest")['Compound_Date'].idxmin(skipna=True), 'Compound_Date'],
            color='lightgrey',
            linestyle=':')
plt.annotate(text=monthly.loc[monthly.query("Principal > Interest")['Compound_Date'].idxmin(skipna=True), 'Compound_Date'].strftime("%x"),
             xy=[monthly.loc[monthly.query("Principal > Interest")['Compound_Date'].idxmin(skipna=True) + 4, 'Compound_Date'], 100],
             color='lightgrey')
ax.set_facecolor('mintcream')
plt.xlim(monthly.loc[monthly['Compound_Date'].idxmin()]['Compound_Date'], monthly.loc[monthly['Compound_Date'].idxmax()]['Compound_Date'])
plt.ylim(0,monthly.loc[monthly['Total_Payment_Due'].idxmax()]['Total_Payment_Due'])
plt.xlabel('Date')
plt.ylabel("Monthly Payment")
plt.title('Mortgage Amortization Table, Principal and Interest')
plt.legend(['Principal', 'Interest'], loc='center left', bbox_to_anchor = (1,.5))
plt.show()

#linechart getting the cumulative sum of principal and interest within monthly
fig, ax = plt.subplots(facecolor=('linen'))
plt.plot(monthly['Compound_Date'], np.cumsum(monthly['Principal']), color='tab:orange', linestyle='dotted')
plt.plot(monthly['Compound_Date'], np.cumsum(monthly['Interest']), color='tab:blue', linestyle='dotted')
plt.plot(monthly['Compound_Date'], np.cumsum(monthly['Total_Payment_Due']), color='black')
plt.show()
#add labels

#linecharts getting the cumulative sum of principal and interest within biweekly
fig, ax = plt.subplots(facecolor=('linen'))
plt.plot(biweekly['Compound_Date'], np.cumsum(biweekly['Principal'] + biweekly['Additional_Principal']), color='tab:orange', linestyle='dotted')
plt.plot(biweekly['Compound_Date'], np.cumsum(biweekly['Interest']), color='tab:blue', linestyle='dotted')
plt.plot(biweekly['Compound_Date'], np.cumsum(biweekly['Total_Payment_Due'] + biweekly['Additional_Principal']), color='black')
plt.show()
#add labels

#make an image with both linecharts next to each other
f, (ax1, ax2) = plt.subplots(1,2, sharey=True, facecolor='linen')
ax1.plot(monthly['Compound_Date'], np.cumsum(monthly['Principal']), color='tab:orange', linestyle='dotted')
ax1.plot(monthly['Compound_Date'], np.cumsum(monthly['Interest']), color='tab:blue', linestyle='dotted')
ax1.plot(monthly['Compound_Date'], np.cumsum(monthly['Total_Payment_Due']), color='black')
ax2.plot(biweekly['Compound_Date'], np.cumsum(biweekly['Principal'] + biweekly['Additional_Principal']), color='tab:orange', linestyle='dotted')
ax2.plot(biweekly['Compound_Date'], np.cumsum(biweekly['Interest']), color='tab:blue', linestyle='dotted')
ax2.plot(biweekly['Compound_Date'], np.cumsum(biweekly['Total_Payment_Due'] + biweekly['Additional_Principal']), color='black')
plt.show()
#add labels

#make a chart with both types of data in one, have to merge dfs first
merged_df = monthly.merge(biweekly, on="Compound_Date", how="left")
merged_df = merged_df[['Compound_Date', 'Principal_x', 'Additional_Principal_x', 'Interest_x', 'Principal_y', 'Additional_Principal_y', 'Interest_y']].copy()
#merged_df.fillna(0, inplace=True)

fig, ax = plt.subplots(facecolor='linen')
plt.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_x'] + merged_df['Additional_Principal_x']), color='tab:orange', linestyle='dotted')
plt.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_y'] + merged_df['Additional_Principal_y']), color='tab:orange')
plt.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Interest_x']), color='tab:blue', linestyle='dotted')
plt.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Interest_y']), color='tab:blue')
plt.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_x'] + merged_df['Additional_Principal_x'] + merged_df['Interest_x']), color='black', linestyle='dotted')
plt.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_y'] + merged_df['Additional_Principal_y'] + merged_df['Interest_y']), color='black')
ax.set_facecolor('mintcream')
plt.axvline(merged_df.loc[merged_df['Principal_y'].isnull().idxmax(), 'Compound_Date'], color='lightgrey', linestyle=':', alpha=.1)
plt.annotate(text=merged_df.loc[merged_df['Principal_y'].isnull().idxmax(), 'Compound_Date'].strftime("%x"),
             xy=[merged_df.loc[merged_df['Principal_y'].isnull().idxmax(), 'Compound_Date'], 100], #i don't think this will work right at full size
             color='lightgrey')
plt.xlabel('Date')
plt.ylabel('Cumulative Payment')
plt.title('Mortgage Amortization, Monthly vs Biweekly Payments, Cumulative Principal and Interest')
ax.legend(['Monthly Principal', 'Biweekly Principal', 'Monthly Interest', 'Biweekly Interest', 'Monthly Total', 'Biweekly Total'], loc='center left', bbox_to_anchor = (1,.5))
plt.show()
#maybe want to change color scheme, add xlim and ylim, and add labels to the end of the liens

#bar chart to pair with the previous chart showing totals
#get the totals
x=np.arange(3)
width=.4
monthly_totals = [np.sum(merged_df['Principal_x'] + merged_df['Additional_Principal_x']), np.sum(merged_df['Interest_x']), np.sum(merged_df['Principal_x'] + merged_df['Additional_Principal_x'] + merged_df['Interest_x'])]
biweekly_totals = [np.sum(merged_df['Principal_y'] + merged_df['Additional_Principal_y']), np.sum(merged_df['Interest_y']), np.sum(merged_df['Principal_y'] + merged_df['Additional_Principal_y'] + merged_df['Interest_y'])]
#plot the pseudo grouped bar chart
fig, ax = plt.subplots(facecolor='linen')
plt.bar(x-.2, biweekly_totals, width, color='dimgrey')
plt.bar(x+.2, monthly_totals, width, color='gainsboro', hatch='/')
plt.xticks(x, ['Principal', 'Interest', 'Total'])
ax.set_facecolor('mintcream')
plt.ylabel('Total Payment')
plt.title('Monthly vs Biweekly, Total Payments')
ax.legend(['Biweekly','Monthly'], loc='center left', bbox_to_anchor = (1,.5))
plt.show()

#ok last thing, put the previous two charts together in one image
fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, facecolor='linen')

ax1.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_x'] + merged_df['Additional_Principal_x']), color='tab:orange', linestyle='dotted')
ax1.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_y'] + merged_df['Additional_Principal_y']), color='tab:orange')
ax1.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Interest_x']), color='tab:blue', linestyle='dotted')
ax1.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Interest_y']), color='tab:blue')
ax1.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_x'] + merged_df['Additional_Principal_x'] + merged_df['Interest_x']), color='black', linestyle='dotted')
ax1.plot(merged_df['Compound_Date'], np.cumsum(merged_df['Principal_y'] + merged_df['Additional_Principal_y'] + merged_df['Interest_y']), color='black')
ax1.set_facecolor('mintcream')
ax1.axvline(merged_df.loc[merged_df['Principal_y'].isnull().idxmax(), 'Compound_Date'], color='lightgrey', linestyle=':', alpha=.1)
ax1.annotate(text=merged_df.loc[merged_df['Principal_y'].isnull().idxmax(), 'Compound_Date'].strftime("%x"),
             xy=[merged_df.loc[merged_df['Principal_y'].isnull().idxmax(), 'Compound_Date'], 100], #i don't think this will work right at full size
             color='lightgrey')
ax1.set_xlabel('Date')
ax1.set_ylabel('Cumulative Payment')
ax1.set_title('Mortgage Amortization, Monthly vs Biweekly Payments, Cumulative Principal and Interest')
ax1.legend(['Monthly Principal', 'Biweekly Principal', 'Monthly Interest', 'Biweekly Interest', 'Monthly Total', 'Biweekly Total'], loc='upper left')

x=np.arange(3)
width=.4
monthly_totals = [np.sum(merged_df['Principal_x'] + merged_df['Additional_Principal_x']), np.sum(merged_df['Interest_x']), np.sum(merged_df['Principal_x'] + merged_df['Additional_Principal_x'] + merged_df['Interest_x'])]
biweekly_totals = [np.sum(merged_df['Principal_y'] + merged_df['Additional_Principal_y']), np.sum(merged_df['Interest_y']), np.sum(merged_df['Principal_y'] + merged_df['Additional_Principal_y'] + merged_df['Interest_y'])]
#plot the pseudo grouped bar chart
ax2.bar(x-.2, biweekly_totals, width, color='dimgrey')
ax2.bar(x+.2, monthly_totals, width, color='gainsboro', hatch='/')
ax2.set_xticks(x, ['Principal', 'Interest', 'Total'])
ax2.set_facecolor('mintcream')
ax2.set_ylabel('Total Payment')
ax2.set_title('Monthly vs Biweekly, Total Payments')
ax2.legend(['Biweekly','Monthly'], loc='center left', bbox_to_anchor = (1,.5))

fig.tight_layout()
#fig.savefig('grid_figure.pdf')
plt.show()
