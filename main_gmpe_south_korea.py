# -*- coding: utf-8 -*-
# Written by Jisong Kim (jisong@unist.ac.kr)

import PySimpleGUI as sg
from pickle import load
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

######################
##### Load model #####
######################
model = load(open("model.dat", "rb"))

sg.theme('Dark Blue 3')

part_00 = sg.Frame(layout=
                [
                    [sg.Text('VS30',size=(20, 1)), sg.Input('',key='-IN1-',size=(10, 1)),sg.Text('m/s')],
                    [sg.Text('Slope angle',size=(20, 1)), sg.Input('',key='-IN2-',size=(10, 1)),sg.Text('°')],
                    [sg.Text('Local Magnitude',size=(20, 1)), sg.Input('',key='-IN3-',size=(10, 1)),sg.Text('')],
                    [sg.Text('Epicentral distance',size=(20, 1)), sg.Input('',key='-IN4-',size=(10, 1)),sg.Text('km')],
                    [sg.Text('Focal depth',size=(20, 1)), sg.Input('',key='-IN5-',size=(10, 1)),sg.Text('km')]
                ], title='Input variables',title_color='white',)

part_01 = sg.Frame(layout=
                  [
                      [sg.Text('Software developed by Jisong Kim (jisong@unist.ac.kr)')],
                      [sg.Text('Ulsan National Institute of Science and Technology (UNIST)')],
                      [sg.Text('Ulsan, South Korea, 44919')]
                  ], title='Profile', title_color='white')

part_10 = [sg.Button('Predict'), sg.Button('Clear all')]

part_20 = sg.Table(values=[[None, None]], 
                   headings=['periods', 'values'], 
                   num_rows=27, 
                   auto_size_columns=False, 
                   key='-TABLE-')

part_21 = sg.Frame(layout=
                   [
                       [sg.Canvas(size=(480, 400), key='-FIGURE-')]
                   ],title='Figure', title_color='white')

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')

layout = [
    [        
        [part_00, sg.VSeperator(), part_01], 
        [part_10],
        [part_20, part_21]
    ]
]

window = sg.Window('Predict spectral acceleration at 27 periods in South Korea', layout)

while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED:
        break
        
    elif event == 'Predict':
        x = [list(map(float, [values.get(i) for i in ['-IN1-', '-IN2-', '-IN3-', '-IN4-', '-IN5-']]))]
        
        df = pd.DataFrame(index=['periods']) 
        for t in model.keys():
            df[t] = np.exp(model.get(t).predict(x))
        df = df.T
        df = df.round(10)
        
        window['-TABLE-'].update(values=list(zip(df.index, df['periods'])))
        
        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(df.index.map(float), df['periods'].values, marker=None)
        
        plt.grid()

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xticks([1e-2, 1e-1, 1, 10])
        ax.set_yticks([1e-8, 1e-6, 1e-4, 1e-2, 1])
    
        locminx = mpl.ticker.LogLocator(base=10,subs=(0.2,0.4,0.6,0.8),numticks=12)
        locminy = mpl.ticker.LogLocator(base=10,subs=(0.2,0.4,0.6,0.8),numticks=12)
        
        ax.xaxis.set_minor_locator(locminx)
        ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        ax.yaxis.set_minor_locator(locminy)
        ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())   

        ax.set_xlabel('Period (s)')
        ax.set_ylabel('PSA (g)')
        
        for tick in ax.get_xticklabels():
            tick.set_rotation(0)
        plt.tight_layout()
        
        fig_canvas_agg = draw_figure(window['-FIGURE-'].TKCanvas, fig)
        
    elif event == 'Clear all':
        window['-TABLE-'].update('')
        delete_figure_agg(fig_canvas_agg)
