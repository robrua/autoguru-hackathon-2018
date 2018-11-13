# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 20:36:52 2018

@author: Matthew
 
creates multicolored hover over movable graph with bokeh,
make sure to change the syspath for autoguru and the model location on your run
"""

import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
import bokeh.plotting as bk
from bokeh.models import HoverTool
from copy import deepcopy
import json
import random
from itertools import compress
import collections


import sys
# manually adds auto guru to my python path
sys.path.append(r'E:\hackathon\autoguru\question-answering')
from questionanswering.embeddings import Embedder
#change this for your program

def main():
    model = 'E:\\hackathon\\answer\\embedder.npz'
    # eembedder model location, change for yourprogram
    embedder = Embedder.load(model)
    
    with open('E://hackathon//final//question-answers.json') as f:
        pracDic = collections.OrderedDict(json.load(f))
    # load json dict    
    embedded = np.zeros((len(pracDic),300))
    ind = 0
    question = []
    answers = []
    # initialize data structures
    for x in pracDic.items():
        question.append(x[0])
        answers.append(x[1])
        embedded[ind,:] = embedder.embed(x[0])
        ind += 1
    #construct structures from dictionary
    
    embedded = pd.DataFrame(embedded) # make embedded a dataframe
    
    # not needed, nothing should be null
    #pracDic = dict(compress(list(pracDic.items()),list(~embedded.isnull().any(axis=1))))
    #embedded = embedded.loc[~embedded.isnull().any(axis=1),:]
    
    tsne = TSNE(n_components =2,verbose=0,perplexity=12,n_iter=10000, early_exaggeration =15)
    tsne_results = np.array(tsne.fit_transform(embedded))
    # creates tsne model and fits our data to it
    finalQuest = pd.DataFrame({'quest':question,'ans':answers,'origVects':np.array(embedded).tolist(),
                               'vectX':tsne_results[:,0],'vectY':tsne_results[:,1]})
    df = deepcopy(finalQuest)
    # this isnt needed i didnt want to mess with finalQuest while debugging
        
    def splitFrame(df):
        ''' created a list of dataframes with each df having different questions'''
        ansSet = list(set(df['ans']))
        dfList = []
        for x in ansSet:
            manipDf = df.loc[df['ans'] == x,:]
            dfList.append(manipDf)            
        return(dfList)
    splits = splitFrame(df)
    
    bk.output_file("toolbar.html")
    #sets the output url    
    TOOLTIPS = ''' 
        <div>
            <div> 
                <span style="font-size: 17px; font-weight: bold;">Question:</span> 
            </div>
            <div> 
                <span style="font-size: 17px;">@quest{safe}</span> 
            </div>
            <div> 
                <span style="font-size: 17px; font-weight: bold;">Answer:</span> 
            </div>
            <div> 
                <span style="font-size: 17px;">@ans{safe}</span> 
            </div>
        </div>'''
    #creates the hover over text
    
    p = bk.figure(plot_width=850, plot_height=700,title='Questions and Answers')
    p.title.text_color = 'black'
    p.title.text_font = 'helvetica'
    p.title.text_font_size = '24pt'
    p.background_fill_color = '#f4f3ef'
    p.xaxis.visible =False
    p.yaxis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    #sets details for graph
    
    
    color = []
    for x in range(1000):
        color.append("#%06x" % random.randint(0, 0xFFFFFF))
    colors = list(set(color))
    #generates a list of colors
    
    # manually selecting colors, this is just for hte demo, comment out this line if using more
    #colors = ['firebrick','royalblue','peru','teal','seagreen','darkmagenta','gold','black','orange']
    
    for x in range(len(splits)):
        r = p.scatter('vectX','vectY', size=10,source=bk.ColumnDataSource(splits[x]),color=colors[x])
        p.add_tools(HoverTool(renderers=[r], tooltips=TOOLTIPS))
        #plots all of the different colored points with their respective hover text
        
    bk.show(p)
    return (splits,pracDic)
    #shows the plot
if __name__ == '__main__':
    (splits,pracDic) = main()
