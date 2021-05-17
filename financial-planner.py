#!/usr/bin/env python
# coding: utf-8

# # Unit 5 - Financial Planning
# 

# In[1]:


# Initial imports
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from MCForecastTools import MCSimulation

get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# Load .env enviroment variables
load_dotenv()


# ## Part 1 - Personal Finance Planner

# ### Collect Crypto Prices Using the `requests` Library

# In[3]:


# Set current amount of crypto assets
my_btc = 1.2
my_eth = 5.3


# In[4]:


# Crypto API URLs
btc_url = "https://api.alternative.me/v2/ticker/Bitcoin/?convert=CAD"
eth_url = "https://api.alternative.me/v2/ticker/Ethereum/?convert=CAD"


# In[7]:


def get_crypto_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    response = requests.get(url,headers=headers)
    return response.json()["data"]


# In[12]:


btc_data = get_crypto_data(btc_url)
btc_data


# In[15]:


eth_data = get_crypto_data(eth_url)
eth_data


# In[18]:


# Fetch current BTC price
btc_price = btc_data['1']['quotes']['USD']['price']
# Fetch current ETH price
eth_price = eth_data['1027']['quotes']['USD']['price']

# Compute current value of my crpto
my_btc_value = btc_price * my_btc
my_eth_value = eth_price * my_eth

# Print current crypto wallet balance
print(f"The current value of your {my_btc} BTC is ${my_btc_value:0.2f}")
print(f"The current value of your {my_eth} ETH is ${my_eth_value:0.2f}")


# ### Collect Investments Data Using Alpaca: `SPY` (stocks) and `AGG` (bonds)

# In[19]:


# Current amount of shares
my_agg = 200
my_spy = 50


# In[23]:


# Set Alpaca API key and secret
alpaca_api_key = os.getenv("ALPACA_API_KEY") 
alpaca_secret_key = os.getenv("ALPACA_API_SECRET")

# Create the Alpaca API object
alpaca = tradeapi.REST(alpaca_api_key,alpaca_secret_key,api_version="v2")


# In[24]:


# Format current date as ISO format
today = pd.Timestamp("2021-05-14", tz="America/New_York").isoformat()

# Set the tickers
tickers = ["AGG", "SPY"]

# Set timeframe to '1D' for Alpaca API
timeframe = "1D"

# Get current closing prices for SPY and AGG
df_portfolio = alpaca.get_barset(
    tickers,
    timeframe,
    start = today,
    end = today
).df
# Preview DataFrame
df_portfolio.head()


# In[25]:


# Pick AGG and SPY close prices
agg_close_price = float(df_portfolio["AGG"]["close"])
spy_close_price = float(df_portfolio["SPY"]["close"])

# Print AGG and SPY close prices
print(f"Current AGG closing price: ${agg_close_price}")
print(f"Current SPY closing price: ${spy_close_price}")


# In[26]:


# Compute the current value of shares
my_spy_value = spy_close_price * my_spy
my_agg_value = agg_close_price * my_agg

# Print current value of share
print(f"The current value of your {my_spy} SPY shares is ${my_spy_value:0.2f}")
print(f"The current value of your {my_agg} AGG shares is ${my_agg_value:0.2f}")


# ### Savings Health Analysis

# In[35]:


# Set monthly household income
monthly_income = 12000

# Create savings DataFrame
total_crypto = my_btc_value + my_eth_value
total_shares = my_spy_value + my_agg_value
value_data = {
    "amount": {
       "crypto": total_crypto,
       "shares": total_shares
    }
}

df_savings = pd.DataFrame(value_data)
df_savings
# Display savings DataFrame
display(df_savings)


# In[36]:


# Plot savings pie chart
df_savings.plot.pie(y="amount", title="Composition of Personal Saving")


# In[37]:


# Set ideal emergency fund
emergency_fund = monthly_income * 3

# Calculate total amount of savings
total_savings = total_crypto + total_shares

# Validate saving health
if (total_savings > emergency_fund):
    print("Congratulations! You have enough money in this fund")
elif (total_savings == emergency_fund):
    print("Congratualtions on reaching this financial goal!")
else:
    diff = emergency_fund - total_savings
    print(f"You are ${diff} away from reaching your financial goal")


# ## Part 2 - Retirement Planning
# 
# ### Monte Carlo Simulation

# In[42]:


# Set start and end dates of five years back from today.
# Sample results may vary from the solution based on the time frame chosen
start_date = pd.Timestamp('2015-05-14', tz='America/New_York').isoformat()
end_date = pd.Timestamp('2021-05-14', tz='America/New_York').isoformat()


# In[44]:


# Get 5 years' worth of historical data for SPY and AGG
tickers = ["AGG", "SPY"]
# Set timeframe to '1D' for Alpaca API
timeframe = "1D"

# Get current closing prices for SPY and AGG
df_stock_data = alpaca.get_barset(
    tickers,
    timeframe,
    start=start_date,
    end=end_date,
    limit=1000
).df

# Display sample data
df_stock_data.head()


# In[45]:


df_stock_data.shape


# In[46]:


# Configuring a Monte Carlo simulation to forecast 30 years cumulative returns
MC_stocks_dist = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [0.4, 0.6],
    num_simulation = 500,
    num_trading_days = 252*30
)


# In[47]:


# Printing the simulation input data
MC_stocks_dist.portfolio_data.head()


# In[48]:


# Running a Monte Carlo simulation to forecast 30 years cumulative returns
MC_stocks_dist.calc_cumulative_return()


# In[49]:


# Plot simulation outcomes
MC_stocks_dist.plot_simulation()


# In[50]:


# Plot probability distribution and confidence intervals
MC_stocks_dist.plot_distribution()


# ### Retirement Analysis

# In[51]:


# Fetch summary statistics from the Monte Carlo simulation results
summary = MC_stocks_dist.summarize_cumulative_return()

# Print summary statistics
print(summary)


# ### Calculate the expected portfolio return at the 95% lower and upper confidence intervals based on a `$20,000` initial investment.

# In[52]:


# Set initial investment
initial_investment = 20000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $20,000
ci_lower = round(summary[8]*initial_investment,2)
ci_upper = round(summary[9]*initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 30 years will end within in the range of"
      f" ${ci_lower} and ${ci_upper}")


# ### Calculate the expected portfolio return at the `95%` lower and upper confidence intervals based on a `50%` increase in the initial investment.

# In[54]:


# Set initial investment
initial_investment = 20000 * 1.5

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $30,000
ci_lower = round(summary[8]*initial_investment,2)
ci_upper = round(summary[9]*initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 30 years will end within in the range of"
      f" ${ci_lower} and ${ci_upper}")


# ## Optional Challenge - Early Retirement
# 
# 
# ### Five Years Retirement Option

# In[55]:


# Configuring a Monte Carlo simulation to forecast 5 years cumulative returns
MC_stocks_5 = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [0.2, 0.8],
    num_simulation = 500,
    num_trading_days = 252*5
)


# In[56]:


# Running a Monte Carlo simulation to forecast 5 years cumulative returns
MC_stocks_5.calc_cumulative_return()


# In[57]:


# Plot simulation outcomes
MC_stocks_5.plot_simulation()


# In[58]:


# Plot probability distribution and confidence intervals
MC_stocks_5.plot_distribution()


# In[65]:


# Fetch summary statistics from the Monte Carlo simulation results
summary_five_yrs = MC_stocks_5.summarize_cumulative_return()

# Print summary statistics
print(summary_five_yrs)


# In[66]:


##### Set initial investment
initial_investment = 60000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower_five = round(summary_five_yrs[8]*initial_investment, 2)
ci_upper_five = round(summary_five_yrs[9]*initial_investment, 2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 5 years will end within in the range of"
      f" ${ci_lower_five} and ${ci_upper_five}")


# ### Ten Years Retirement Option

# In[63]:


# Configuring a Monte Carlo simulation to forecast 10 years cumulative returns
MC_stocks_10 = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [0.3, 0.7],
    num_simulation = 500,
    num_trading_days = 252*10
)


# In[64]:


# Running a Monte Carlo simulation to forecast 10 years cumulative returns
MC_stocks_10.calc_cumulative_return()


# In[67]:


# Plot simulation outcomes
MC_stocks_10.plot_simulation()


# In[68]:


# Plot probability distribution and confidence intervals
MC_stocks_10.plot_distribution()


# In[69]:


# Fetch summary statistics from the Monte Carlo simulation results
summary_ten_yrs = MC_stocks_10.summarize_cumulative_return()


# Print summary statistics
print(summary_ten_yrs)


# In[70]:


# Set initial investment
initial_investment = 60000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower_ten = round(summary_ten_yrs[8]*initial_investment, 2)
ci_upper_ten = round(summary_ten_yrs[9]*initial_investment, 2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 10 years will end within in the range of"
      f" ${ci_lower_ten} and ${ci_upper_ten}")


# In[ ]:




