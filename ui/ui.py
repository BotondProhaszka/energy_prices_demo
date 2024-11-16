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

DF = None
CORR_DF = None

AX_DF = None
FIG_DF = None
CANVAS_DF = None

AX_CORR = None
FIG_CORR = None
CANVAS_CORR = None

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
    cols.extend(countries)
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

    for col in countries:
        listbox_country.insert(tk.END, col)
    listbox_country.grid(row=0, column=0)
    
    for col in col_types:
        listbox_type.insert(tk.END, col)
    listbox_type.grid(row=1, column=0)

    # Create Listboxes for displaying selected columns
    selected_country_listbox = Listbox(root)
    selected_type_listbox = Listbox(root)

    selected_country_listbox.grid(row=0, column=2)
    selected_type_listbox.grid(row=1, column=2)

    def on_select_country():
        global DF_Y_COUNTRIES
        selected_indices = listbox_country.curselection()
        DF_Y_COUNTRIES = [listbox_country.get(i) for i in selected_indices]
        print(f"Selected countries: {DF_Y_COUNTRIES}")
        
        # Update the selected country listbox
        selected_country_listbox.delete(0, tk.END)
        for col in DF_Y_COUNTRIES:
            selected_country_listbox.insert(tk.END, col)

    select_country_button = tk.Button(root, text="Select countries", command=on_select_country)
    select_country_button.grid(row=0, column=1)

    def on_select_type():
        global DF_Y_TYPES
        selected_indices = listbox_type.curselection()
        DF_Y_TYPES = [listbox_type.get(i) for i in selected_indices]
        print(f"Selected types: {DF_Y_TYPES}")
        
        # Update the selected type listbox
        selected_type_listbox.delete(0, tk.END)
        for col in DF_Y_TYPES:
            selected_type_listbox.insert(tk.END, col)

    select_type_button = tk.Button(root, text="Select types", command=on_select_type)
    select_type_button.grid(row=1, column=1)

    return root

def create_figure():
    fig = Figure(figsize=(7, 5), dpi=100)
    ax = fig.add_subplot(111)
    return fig, ax

def show_figure():
    global DF, AX_DF, CANVAS_DF, DF_Y_COLS
    print(f"y_col_names: {DF_Y_COLS}")

    X_col = pd.to_datetime(DF.index)

    for y_col_name in DF_Y_COLS:
        y = DF[y_col_name]
        AX_DF.plot(X_col, y, label=y_col_name)
    AX_DF.legend()
    AX_DF.set_xlabel('Datetime')
    AX_DF.set_ylabel('Y')
    AX_DF.set_title('Demo plot')
    CANVAS_DF.get_tk_widget().grid(row=2, column=0, columnspan=5)
    CANVAS_DF.draw()

def show_corr_matrix():
    global CORR_DF, AX_CORR, FIG_CORR, CANVAS_CORR, DF_Y_COLS
    try:
        corr_df = CORR_DF[DF_Y_COLS].loc[DF_Y_COLS]

        AX_CORR.matshow(corr_df)
        FIG_CORR.colorbar(AX_CORR.matshow(corr_df))
        CANVAS_CORR.get_tk_widget().grid(row=2, column=5, columnspan=5)
        CANVAS_CORR.draw()
        
    except Exception as e:
        print(f"Error: {e}")


def update_figure():
    global DF_Y_COUNTRIES, DF_Y_TYPES, DF_Y_COLS

    DF_Y_COLS = get_col_names(DF_Y_COUNTRIES, DF_Y_TYPES)
    print(f"Selected columns: {DF_Y_COLS}")

    show_figure()

    show_corr_matrix()


def main():
    global DF, CORR_DF, AX_DF, FIG_CORR, CANVAS_DF, AX_CORR, FIG_CORR, CANVAS_CORR, DF_Y_COLS
    #read in the data
    filename = get_out_filename()
    engine = get_engine(filename)
    table_names = get_table_names(engine)

    dfs = read_in_dfs(engine, table_names)
    DF = dfs['df']
    CORR_DF = dfs['corr']

    df_cols = DF.columns
    root = create_ui(df_cols)

    # create a plot
    fig_df, AX_DF = create_figure()
    FIG_CORR, AX_CORR = create_figure()
    CANVAS_DF = FigureCanvasTkAgg(fig_df, master=root)
    CANVAS_CORR = FigureCanvasTkAgg(FIG_CORR, master=root)

    show_figure()
    show_corr_matrix()

    #button to update the plot
    update_button = tk.Button(root, text="Update Plot", command=lambda: update_figure())
    update_button.grid(row=3, column=0, columnspan=5)
    
    #run the GUI
    root.mainloop()

if __name__ == "__main__":
    main()

