import yahoodata
import logging
import numpy as np
import supertrend
import cmd

class Terminal(cmd.Cmd):

    intro = 'Welcome to kr0nos Algo Trading.   Type help or ? to list commands.\n'
    prompt = 'kr0n0sAlgoTrader => '

    def do_help(self, line):
        print('Documented commands:\n')
        print("\tconfig -> let's make this happen")
        print('\trun  -> power up')
        print("\tsummary -> let's  see waht we made")
        print('\tbye -> see you soon')
        
    def do_bye(self, line):
        logging.info('Gain gain gain')
        return True
    
    def do_config(self, line):
        tickers = input('Tickers [VALE3.SA PETR4.SA]: ')
        period =  input('Period [1d, 15m]: ')
        startDate = input('Start Date [YYYY-MM-DD]: ')
        EndDate = input('End Date [YYYY-MM-DD]: ')

    def do_run(self, line):
        print(self)
        print(line)

if __name__ == '__main__':
    logging.basicConfig(level=20)
    Terminal().cmdloop()
    #df = yahoodata.getData(tickers='VALE3.SA',startDate='2020-07-14', endDate='2020-07-17', interval='60m')
    #dfSt = supertrend.ST(df=df, f=3, n=7)
    #df['Signal']=np.nan
    #print(df)
    #for i in range(0, len(df)):
    #    if (df['Close'][i] > df['SuperTrend'][i]):
    #        print('Buy')
    #        df['Signal'][i] = 1
    #    else:
    #        df['Signal'][i] = 0
    #print(df)