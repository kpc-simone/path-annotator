import pandas as pd

def get_interval(asdf,indexcol,index,timing='normal'):
    
    if timing == 'defensive':
        outcome = asdf[asdf['trial'] == index]['defensive strategy'].iloc[0]
        if outcome == 'escape':    
            t0 = float(asdf[asdf['trial'] == index]['run-abs'])
            pos_0 = float(t0 - 0.5)
            pos_f = float(asdf[asdf['trial'] == index]['hide-abs'] + 1.0)
        elif outcome == 'panic':           
            t0 = float(asdf[asdf['trial'] == index]['run-abs'])
            pos_0 = float(t0 - 0.5)
            pos_f = float(asdf[asdf['trial'] == index]['freeze-start-abs'] + 1.0)
        elif outcome == 'freeze':           
            t0 = float(asdf[asdf['trial'] == index]['shadowON-abs'])
            pos_0 = float(t0 - 0.5)
            pos_f = float(asdf[asdf['trial'] == index]['shadowOFF-abs'] + 1.0)
    
    elif timing == 'full':
        outcome = asdf[asdf['trial'] == index]['defensive strategy'].iloc[0]
        t0 = float(asdf[asdf['trial'] == index]['shadowON-abs'])
        pos_0 = float(t0 - 1.0)
        pos_f = float(asdf[asdf['trial'] == index]['shadowOFF-abs'] + 1.0)    
    
    return t0,pos_0,pos_f,outcome