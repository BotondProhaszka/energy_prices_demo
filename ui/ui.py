import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect

import tkinter as tk
from tkinter import Listbox, MULTIPLE

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DF_Y_TYPES = []
DF_Y_COUNTRIES = []
DF_Y_COLS = []
AX_DF = None
CANVAS_DF = None
DF = None

# Helper functions

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

def read_in_dfs(engine, table_names):
    dfs = {}
    for table_name in table_names:
        df = get_data(engine, table_name)
        dfs[table_name] = df
    return dfs

def get_2char_columns(cols):
    return [col for col in cols if len(col) == 2]

def unique_col_types(columns, countries):
    # get the cols from coumns where the first two characters is from countries
    col_types = [col[3:] for col in columns if col[:2] in countries]
    col_types_set = list(set(col_types))
    col_types_set.remove('') # remove empty string
    return col_types_set

def get_col_names(countries, col_types):
    cols = [country + '_' + col_type for country in countries for col_type in col_types]
    # apepnd countries to cols
    cols.append(countries)
    print(f"Selected columns: {cols}")
    return cols

## GUI functions

def create_ui(columns):
    global DF_Y_COLS, DF_Y_COUNTRIES, DF_Y_TYPES
    root = tk.Tk()
    root.title("Demo app")

    # Create a Listbox for selecting multiple columns
    listbox_type = Listbox(root, selectmode=MULTIPLE)
    listbox_country = Listbox(root, selectmode=MULTIPLE)

    countries = get_2char_columns(columns)
    col_types = unique_col_types(columns, countries)

    for col in col_types:
        listbox_type.insert(tk.END, col)
    listbox_type.pack(side=tk.LEFT)

    for col in countries:
        listbox_country.insert(tk.END, col)
    listbox_country.pack(side=tk.LEFT)

    # Create Listboxes for displaying selected columns
    selected_type_listbox = Listbox(root)
    selected_country_listbox = Listbox(root)

    selected_type_listbox.pack(side=tk.LEFT)
    selected_country_listbox.pack(side=tk.LEFT)

    def on_select_type():
        global DF_Y_TYPES
        selected_indices = listbox_type.curselection()
        DF_Y_TYPES = [listbox_type.get(i) for i in selected_indices]
        print(f"Selected types: {DF_Y_TYPES}")
        
        # Update the selected type listbox
        selected_type_listbox.delete(0, tk.END)
        for col in DF_Y_TYPES:
            selected_type_listbox.insert(tk.END, col)

    select_type_button = tk.Button(root, text="Select Columns", command=on_select_type)
    select_type_button.pack(side=tk.LEFT)

    def on_select_country():
        global DF_Y_COUNTRIES
        selected_indices = listbox_country.curselection()
        DF_Y_COUNTRIES = [listbox_country.get(i) for i in selected_indices]
        print(f"Selected countries: {DF_Y_COUNTRIES}")
        
        # Update the selected country listbox
        selected_country_listbox.delete(0, tk.END)
        for col in DF_Y_COUNTRIES:
            selected_country_listbox.insert(tk.END, col)

    select_country_button = tk.Button(root, text="Select Columns", command=on_select_country)
    select_country_button.pack(side=tk.LEFT)

    return root

def create_figure():
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    return fig, ax

def show_figure(ax, df, X_col, y_col_names, canvas):
    print(f"X_col: {X_col}")
    print(f"y_col_names: {y_col_names}")

    for y_col_name in y_col_names:
        y = df[y_col_name]
        ax.plot(X_col, y, label=y_col_name)
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Demo plot')
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def update_figure(ax, df, X_col, canvas):
    global DF_Y_COUNTRIES, DF_Y_TYPES, DF_Y_COLS

    DF_Y_COLS = get_col_names(DF_Y_COUNTRIES, DF_Y_TYPES)
    print(f"Selected columns: {DF_Y_COLS}")

    ax.clear()
    show_figure(ax, df, X_col, DF_Y_COLS, canvas)
    canvas.draw()

def main():
    #read in the data
    filename = get_out_filename()
    engine = get_engine(filename)
    table_names = get_table_names(engine)

    dfs = read_in_dfs(engine, table_names)
    DF = dfs['df']
    df_cols = DF.columns
    root = create_ui(df_cols)

    # create a plot
    fig_df, AX_DF = create_figure()
    CANVAS_DF = FigureCanvasTkAgg(fig_df, master=root)

    show_figure(AX_DF, DF, DF.index, DF_Y_COLS, CANVAS_DF)
    #button to update the plot
    update_button = tk.Button(root, text="Update Plot", command=lambda: update_figure(AX_DF, DF, DF.index, CANVAS_DF))
    update_button.pack(side=tk.BOTTOM)


    
    #run the GUI
    root.mainloop()

if __name__ == "__main__":
    main()

