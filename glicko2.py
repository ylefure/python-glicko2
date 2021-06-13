#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from math import *
import csv
from tabulate import tabulate


# In[ ]:


tau = 0.2 #System constant


# In[ ]:


# Step 1:
# We extract player info. from a .txt csv
# assuming player,rating,RD,volatility
with open('ratingstest.txt','r') as datafile:
    separatedata = csv.reader(datafile, delimiter=',')
    player_rows = [row for row in separatedata]
    player_list = [player_data[0] for player_data in player_rows]

#    Notice:
#    player_row[j][0]: user
#    player_row[j][1]: rating
#    player_row[j][2]: RD
#    player_row[j][3]: volatility


# In[ ]:


# Create a dictionary for ratings, RDs and volatilities
rating = {player_data[0]:float(player_data[1]) for player_data in player_rows}
RD = {player_data[0]:float(player_data[2]) for player_data in player_rows}
volatility = {player_data[0]:float(player_data[3]) for player_data in player_rows}

# Add dictionaries with empty lists as values to store match data: opponent ratings, RDs and game score.
# If there are no problems, each player must have the same amount of list elements for each of the following,
# and they must be well-ordered
opp_ratings = {player_data[0]:[] for player_data in player_rows}
opp_RD = {player_data[0]:[] for player_data in player_rows}
score = {player_data[0]:[] for player_data in player_rows}


# In[ ]:


# For comparison, a table with initial values:
initial_table = [['Player', 'Rating', 'RD']]
for player in player_list:
    initial_table.append([player, rating[player], RD[player]])
print(tabulate(initial_table,headers='firstrow'))


# In[ ]:


# Update dictionaries for ratings and RDs
# in Glicko-2 scale (step 2)
for player in player_list:
    rating[player] = (rating[player] - 1500)/173.7178
    RD[player] = RD[player]/173.7178


# In[ ]:


#Defining useful functions
def game(white, black, result):
    """
    Stores the results of a game between white and black in their corresponding dictionary value.
    'white' and 'black' are strings (and must be written in "" or '') of player names
    reult is 1 if white won, -1 if black won, 0 if draw
    """
    
    opp_ratings[white].append(rating[black])
    opp_ratings[black].append(rating[white])
    
    opp_RD[white].append(RD[black])
    opp_RD[black].append(RD[white])
    
    if result == 1:
        score[white].append(1)
        score[black].append(0)
    elif result == -1:
        score[black].append(1)
        score[white].append(0)
    elif result == 0:
        score[black].append(0.5)
        score[white].append(0.5)

def g(phi):
    """
    Defines the g() function described in step 3 of Glickman's paper.
    """
    return 1/sqrt(1 + 3*phi*phi/pi/pi)

def E(mu, mu_j, phi_j):
    """
    Defines the E() function described in step 3 of Glickman's paper.
    """
    return 1/(1 + exp(-g(phi_j)*(mu - mu_j)))


# In[ ]:


# where the new values will be stored:
rating_new = {}
RD_new = {}
volatility_new = {}


# In[ ]:


# Game results in this cell. Always specify game details (date, players, event, round, etc.) in notes.
game('coriollis','smarterchess',-1)
game('ChessPriyome','coriollis',1)
game('smarterchess','ChessPriyome',0.5)


# In[ ]:


# Main algorithm:

for player in player_list:
    
    m = len(score[player]) #number of games played by player
    
    if m == 0: # in case a player played no games
        rating_new[player] = rating[player]
        volatility_new[player] = volatility[player]
        RD_new[player] = sqrt(RD[player]**2 + volatility[player]**2)
        
        continue # go to next player
    
    # Step 3:
    v = 0 #initial variance value
    for j in range(m):
        v = v + g(opp_RD[player][j])**2 * E(rating[player], opp_ratings[player][j], opp_RD[player][j]) * (1 - E(rating[player], opp_ratings[player][j], opp_RD[player][j]))
    v = 1/v

    # Step 4:
    Delta = 0 #init. value
    for j in range(m):
        Delta = Delta + g(opp_RD[player][j])*(score[player][j] - E(rating[player], opp_ratings[player][j], opp_RD[player][j]))
    Delta = Delta * v

    # Step 5:
    a = log(volatility[player]**2)
    def f(x):
        return (exp(x)*(Delta**2 - RD[player]**2 - v - exp(x)))/(2*(RD[player]**2 + v + exp(x))**2) - (x - a)/(tau**2)
    epsilon = 0.000001
    
    A = a
    k = 1
    if Delta**2 > RD[player]**2 + v:
        B = log(Delta**2 - RD[player]**2 - v)
    else:
        while f(a - k*tau) < 0:
            k = k + 1
        B = a - k*tau
        
    f_A = f(A)
    f_B = f(B)
    
    while abs(B-A) > epsilon:
        C = A + (A-B)*f_A/(f_B - f_A)
        f_C = f(C)
        if f_C*f_B < 0:
            A = B
            f_A = f_B
        else:
            f_A = f_A/2
        B = C
        f_B = f_C
        
    volatility_new[player] = exp(A/2)

    # Step 6
    phi_star = sqrt(RD[player]**2 + volatility_new[player]**2)

    # Step 7:
    
    RD_new[player] = 1/sqrt(1/phi_star/phi_star + 1/v)
    
    mu_prime = 0 #init. value
    for j in range(m):
        mu_prime = mu_prime + g(opp_RD[player][j])*(score[player][j] - E(rating[player], opp_ratings[player][j], opp_RD[player][j]))
    mu_prime = mu_prime*RD_new[player]**2 + rating[player]
    rating_new[player] = mu_prime


# In[ ]:


# Glicko-2 to Glicko conversion (step 8):
for player in player_list:
    rating_new[player] = round(rating_new[player]*173.7178 + 1500)
    RD_new[player] = round(RD_new[player]*173.7178)
    volatility_new[player] = round(volatility_new[player], 3)


# In[ ]:


# creating output txt file
with open('testoutput.txt', 'w') as output_file:
    result_writer = csv.writer(output_file, delimiter=',')
    for player in player_list:
        result_writer.writerow([player, rating_new[player], RD_new[player], volatility_new[player]])


# In[ ]:


# creating table to share on Discord:
table_rows = [['Player', 'Rating', 'RD']]
for player in player_list:
    table_rows.append([player, rating_new[player], RD_new[player]])
print(tabulate(table_rows,headers='firstrow'))

