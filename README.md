# python-glicko2
A simple python implementation of Glicko-2 intended for use in a chess club.

A notebook for calculating changes in player's Glicko-2 rating. See: http://www.glicko.net/glicko/glicko2.pdf

Initial values are taken from a txt file of comma-separated values of the form: user,rating,RD,volatility and an output file is generated to be used in calculations for the next rating period.

Game results are to be entered using the game() function in the appropiate cell.

I recommend restarting the kernel and re-running the whole notebook everytime this code is used, to avoid any unforseen complications.
