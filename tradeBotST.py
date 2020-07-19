import yahoodata
import logging
import numpy as np
import supertrend
import cmd

class Terminal(cmd.Cmd):

    intro = 'Welcome to kr0nos Algo Trading.   Type help or ? to list commands.\n'
    prompt = 'kr0n0sAlgoTrader => '
    tickers = ''
    period = ''
    startDate = ''
    endDate = ''
    stPeriod = 0
    stFactor = 0
    
    '''
    Business Logic Functions
    '''
    def signal(self, c):
        if c['Close'] > c['SuperTrend']:
            return 'Buy'
        else:
            return 'Sell'

    def analyseTrade(self):
        df = yahoodata.getData(tickers=self.tickers, startDate=self.startDate, endDate=self.endDate, interval=self.period)
        dfSt = supertrend.ST(df=df, f=int(self.stFactor), n=int(self.stPeriod))
        dfSt['Signal'] = dfSt.apply(self.signal, axis=1)
        print(dfSt)

    '''
    Command Control Functions
    '''
    def do_help(self, line):
        print('Documented commands:\n')
        print("\tconfig -> let's make this happen")
        print('\trun  -> power up')
        print("\tsummary -> let's  see waht we made")
        print('\texit -> see you soon')
        
    def do_exit(self, line):
        logging.info('Gain gain gain')
        return True
    
    def do_config(self, line):
        self.tickers = str(input('Tickers [VALE3.SA PETR4.SA]: ') or 'VALE3.SA')
        self.period =  str(input('Period [1d, 15m]: ') or '60m')
        self.startDate = str(input('Start Date [YYYY-MM-DD]: ') or '2020-07-10')
        self.endDate = str(input('End Date [YYYY-MM-DD]: ') or '2020-07-17')
        self.stPeriod = int(input('SuperTrend Period [7]: ') or 7)
        self.stFactor = int(input('SuperTrend Factor [3]: ') or 3)

    def do_simulate(self, line):
        return True

    def do_autoconfig(self, line):
        return True

    def do_run(self, line):
        self.analyseTrade()

        
if __name__ == '__main__':
    logging.basicConfig(level=20)
    Terminal().cmdloop()