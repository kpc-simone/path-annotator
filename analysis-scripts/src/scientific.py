import matplotlib.pyplot as plt
from scipy.stats import shapiro
import scipy.stats as stats
import pandas as pd
import numpy as np
import itertools
import datetime
import sys,os

def plot_scattermeans(gdf,feature,ax,ylabel = None,colors = None,xlabels = None,min=0.0,max=1.5):

    print('stats for {}'.format(feature))
    means = gdf[feature].mean()
    errors = gdf[feature].std()
    
    print('means :')
    print(means)
    print('errors :')
    print(errors)

    x = [x for x in range(1,len(gdf.groups)+1)]

    w = 0.8
    ax.bar(x,
           height=means,
           yerr=errors,         # error bars
           capsize=6,           # error bar cap width in points
           width=w,             # bar width
           tick_label=xlabels,
           color=(0,0,0,0),     # face color transparent
           edgecolor=None,
           )

    for i,group in enumerate(gdf.groups):
        y = gdf.get_group(group)[feature]
        
        # distribute scatter randomly across whole width of bar
        ax.scatter(x[i] + np.random.random(len(y)) * w / 2 - w / 4, y, color=colors[i],edgecolors='k',alpha = 0.8)
        ax.plot([x[i] - w / 4, x[i] + w / 4], [y.mean(),y.mean()], color='k',linewidth=2.0)

    # run stats and add the significance bar
    r = 2
    groups = [g for g,df in gdf]
    for subset,i in zip(itertools.combinations(groups,r),x):    
        xs = np.sort(np.roll(x,i-1)[:2])
        gs = np.sort(np.roll(np.asarray(groups),i-1)[:2])
        
        data_is_gaussian = True
        for d,data in enumerate((gdf.get_group(gs[0])[feature].dropna(),gdf.get_group(gs[1])[feature].dropna())):
            s_stat,p = shapiro(data)
            
            if p < 0.05:
                print('distribution for {} violates normality assumption; Shapiro-Wilks test, S = {:6.5f}, P = {:6.5f}'.format(xlabels[d],s_stat,p))
                data_is_gaussian = False
            else:
                print('distribution for {} is normal; Shapiro-Wilks test, S = {:6.5f}, P = {:6.5f}'.format(xlabels[d],s_stat,p))
                
        if data_is_gaussian:
            statistic,p_value = stats.ttest_ind(gdf.get_group(gs[0])[feature].dropna(),gdf.get_group(gs[1])[feature].dropna(),equal_var='False')
            print('two-tailed independent samples t-test, t = {:6.5f}, P = {:6.5f}'.format(statistic,p_value))
        else:
            statistic,p_value = stats.mannwhitneyu(gdf.get_group(gs[0])[feature].dropna(),gdf.get_group(gs[1])[feature].dropna())
            print('Mann-Whitney U-test, U = {:6.5f}, P = {:6.5f}'.format(statistic,p_value))
        if i == 2:
            h = 1.5
        else:
            h = 0.8
        
        ax.plot([xs[0]+0.1,xs[1]-0.1],(max-min)*h*np.ones(len(xs))+min,color='k',linewidth = 1.0)
        if p_value < 0.05:
            if p_value < 0.00001:
                ax.annotate('$P$ ={:.3e}'.format(p_value), ( (xs[0]+xs[1]) /2,(max-min)*(h + 0.25*(1-h) )+min),ha='center')
            else:
                ax.annotate('$P$ ={:6.5f}'.format(p_value), ( (xs[0]+xs[1]) /2,(max-min)*(h + 0.25*(1-h) )+min),ha='center')
        else:    
            ax.annotate('n.s.', ( (xs[0]+xs[1]) /2,(max-min)*(h + 0.25*(1-h) )+min),ha='center')
        ax.set_ylabel(ylabel)
    ylim = [min,max]
    ax.set_ylim(ylim)    
    
def plot_beforeafter(data_before,data_after,ax,ylabel = None,xlabels = None,colors = None,min=0.0,max=1.5):    
  
    data_is_gaussian = True
    for d,data in enumerate((data_before,data_after)):
        try:
            s_stat,p = shapiro(data)
            
            if p < 0.05:
                print('distribution for {} violates normality assumption; Shapiro-Wilks test, S = {:6.5f}, P = {:6.5f}'.format(xlabels[d],s_stat,p))
                data_is_gaussian = False
            else:
                print('distribution for {} is normal; Shapiro-Wilks test, S = {:6.5f}, P = {:6.5f}'.format(xlabels[d],s_stat,p))
        except:
            print('cannot determine normality')
            data_is_gaussian = False                

    if data_is_gaussian:
        statistic,p_value = stats.ttest_rel(data_before,data_after)
        print('two-tailed paired t-test, t = {:6.5f}, P = {:6.5f}, n = {}'.format(statistic,p_value,len(data_before)))
    else:
        #print('data is not gaussian, testing for statistical significance with wilcoxon signed rank test')
        statistic,p_value = stats.wilcoxon(data_before,data_after)
        print('two-tailed Wilcoxon signed-rank test, W = {:6.5f}, P = {:6.5f}, n = {}'.format(statistic,p_value,len(data_before)))
    
    xs = [ x for x in [1,2] ]
    data_before = data_before.to_numpy()
    data_after = data_after.to_numpy()
    for i in range(0,len(data_before)):    
        ax.plot( xs, [data_before[i],data_after[i]], color='dimgray')
    ax.scatter( xs[0]*np.ones((len(data_before),)), data_before, color = colors[0], edgecolor='k',zorder=10)
    ax.scatter( xs[1]*np.ones((len(data_after),)), data_after, color = colors[1], edgecolor='k', zorder=10)
    ylim = [min,max]
    ax.set_xticks(xs)
    ax.set_xlim( (0.25,2.75) )
    ax.set_xticklabels(xlabels)
    
    ax.set_ylim(ylim)    
    ax.set_ylabel(ylabel)    
    
    ax.plot( xs, np.ones(2)*0.8*max, color='k', linewidth = 1.0)
    if p_value < 0.0001:
        ax.annotate('$P$ ={:.3e}'.format(p_value), ( (xs[0]+xs[1])/2, 0.85*max ),ha='center')        
    elif p_value < 0.05:
        ax.annotate('$P$ ={:6.5f}'.format(p_value), ( (xs[0]+xs[1])/2, 0.85*max ),ha='center')                
    else:    
        ax.annotate('n.s.'.format(p_value), ( (xs[0]+xs[1])/2, 0.85*max ),ha='center')        
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
def plot_beforeaftermulti(df,features,ax,ylabel = None,xlabels = None,colors = ['silver','dimgray','black'],min=0.0,max=1.5):    
    indexes = [x for x in range(1,len(features)+1)]
    r = 2
    data_is_gaussian = True
    
    subsets = [s for s in itertools.combinations(features,r)]
    max_level = len(subsets) // 2
    maxh = (max-min) * (1.25 + 0.2*max_level) + min
    
    for c,xs in enumerate(itertools.combinations(indexes,r)):    
        f_idx0 = xs[0] - 1
        f_idx1 = xs[1] - 1
        
        data_before = df[features[f_idx0]]
        data_after = df[features[f_idx1]]
        
        print('{}: {} +/- {}'.format(features[f_idx0],data_before.mean(),data_before.std()))
        print('{}: {} +/- {}'.format(features[f_idx1],data_after.mean(),data_after.std()))
        
        for d,data in enumerate([data_before,data_after]):
            try:
                s_stat,p = shapiro(data)
                
                if p < 0.05:
                    #print('distribution for {} violates normality assumption; Shapiro-Wilks test, S = {:6.5f}, P = {:6.5f}'.format(xlabels[d],s_stat,p))
                    data_is_gaussian = False
                else:
                    data_is_gaussian = True
                    #print('distribution for {} is normal; Shapiro-Wilks test, S = {:6.5f}, P = {:6.5f}'.format(xlabels[d],s_stat,p))
            except:
                #print('cannot determine normality')
                data_is_gaussian = False                

        if data_is_gaussian:
            statistic,p_value = stats.ttest_rel(data_before,data_after)
            print('two-tailed paired t-test, t = {:6.5f}, P = {:6.5f}, n = {}'.format(statistic,p_value,len(data_before)))
        else:
            statistic,p_value = stats.wilcoxon(data_before,data_after)
            print('two-tailed Wilcoxon signed-rank test, W = {:6.5f}, P = {:6.5f}, n = {}'.format(statistic,p_value,len(data_before)))
        
        level = xs[1] - xs[0]
        bh = (max-min) * (1 + 0.2 * level) + min
        ph = (max-min) * (1.05 + 0.2 * level) + min
        
        ax.plot( [ xs[0]+0.1,xs[1]-0.1], np.ones(2)*bh, color='k', linewidth = 1.0)
        if p_value < 0.001:
            ax.annotate('$P$={:.1e}'.format(p_value), ( (xs[0]+xs[1])/2, ph ),ha='center')        
        elif p_value < 0.05:
            ax.annotate('$P$={:4.3f}'.format(p_value), ( (xs[0]+xs[1])/2, ph ),ha='center')                
        else:    
            ax.annotate('n.s.'.format(p_value), ( (xs[0]+xs[1])/2, ph ),ha='center')        
        
        data_before = data_before.to_numpy()
        data_after = data_after.to_numpy()
        if ( abs(xs[1]-xs[0]) == 1 ):
            for i in range(0,len(data_before)):    
                ax.plot( xs, [data_before[i],data_after[i]], color='dimgray')
        ax.scatter( xs[0]*np.ones((len(data_before),)), data_before, color = colors[xs[0]-1], edgecolor='k',zorder=10)
        ax.scatter( xs[1]*np.ones((len(data_after),)), data_after, color = colors[xs[1]-1], edgecolor='k', zorder=10)
    
    ax.set_xticks(indexes)
    ax.set_xlim( (0.0, len(features) + 1.0) )

    ylim = [min,maxh]    
    ax.set_ylim(ylim)    
    if xlabels is not None:
        ax.set_xticklabels(xlabels)    
    if ylabel is not None:
        ax.set_ylabel(ylabel)    
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)    
    
    
    
    
    
    
    
    
    
    