import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect
import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def get_path(foldername, filename):
    running_dir = os.getcwd()
    parent_dir = os.path.dirname(running_dir)
    full_filename = os.path.join(parent_dir, foldername, filename)
    full_filename = full_filename.replace('\\', '/')
    full_filename = full_filename[0].upper() + full_filename[1:]

    return full_filename

def get_out_filename():
    filename = 'data/final.sqlite'
    full_filename = get_path('data_processing', filename)
    return full_filename

def get_engine(filename):
    try:
        engine = create_engine(f'sqlite:///{filename}')
        print(engine)
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error creating engine')
    return engine

def get_table_names(engine):
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        print(f"Table names: {table_names}")
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error getting table names')
    return table_names

def get_data(engine, table_name):
    try:
        df = pd.read_sql_table(table_name, engine)
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error getting df')
    return df

def show_figure(fig, X, y_list, plot):
    
    ax = fig.add_subplot(111)
    for y in y_list:
        ax.plot(X, y)
    canvas = FigureCanvasTkAgg(fig, master=plot)
    canvas.get_tk_widget().pack()

def show():
    print("Button clicked")


def main():
    #read in the data
    filename = get_out_filename()
    engine = get_engine(filename)
    table_names = get_table_names(engine)

    dfs = {}
    for table_name in table_names:
        df = get_data(engine, table_name)
        dfs[table_name] = df

    #create the GUI
    root = tk.Tk()
    root.title("Data Viewer")
    root.geometry("200x200")

    #create the listbox
    listbox = tk.Listbox(root)
    listbox.pack()

    #add the table names to the listbox
    for table_name in table_names:
        listbox.insert(tk.END, table_name)

    #create the button
    button = tk.Button(root, text="Show", command=show)
    button.pack()

    # create a plot
    plot = tk.Canvas(root, width=200, height=100)
    plot.pack()

    #add data to plot: from dfs['df'] x is the index, y is the 'HU'
    fig = Figure(figsize=(5, 4), dpi=100)
    show_figure(fig, dfs['df'].index, [dfs['df']['HU'], dfs['df']['FR']], plot)
    
    
    #run the GUI
    root.mainloop()

if __name__ == "__main__":
    main()

