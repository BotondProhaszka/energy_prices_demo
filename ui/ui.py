import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect

import tkinter as tk
from tkinter import Listbox, MULTIPLE
from tkcalendar import DateEntry

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

START = None
END = None

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

def date_picker(root, init_start=None, init_end=None):
    # Add date pickers
    start_date_label = tk.Label(root, text="Start Date")
    start_date_label.grid(row=0, column=3)
    start_date_picker = DateEntry(root)
    start_date_picker.grid(row=0, column=4)

    end_date_label = tk.Label(root, text="End Date")
    end_date_label.grid(row=1, column=3)
    end_date_picker = DateEntry(root)
    end_date_picker.grid(row=1, column=4)

    if init_start:
        start_date_picker.set_date(init_start)
    if init_end:
        end_date_picker.set_date(init_end)

    def on_select_date():
        global START, END
        START = start_date_picker.get_date()
        END = end_date_picker.get_date()
        # to datetime
        START = pd.to_datetime(START)
        END = pd.to_datetime(END)

        print(f"Selected dates: {START} - {END}")
    return on_select_date

def create_figure():
    fig = Figure()
    ax = fig.add_subplot(111)
    return fig, ax

def show_figure():
    global DF, AX_DF, CANVAS_DF, DF_Y_COLS

    AX_DF.clear()
    df = DF.loc[START:END]

    X_col = pd.to_datetime(df.index)

    for y_col_name in DF_Y_COLS:
        y = df[y_col_name]
        AX_DF.plot(X_col, y, label=y_col_name)


    AX_DF.legend()
    AX_DF.set_xlabel('Datetime')
    AX_DF.set_ylabel('Y')
    AX_DF.set_title('Demo plot')

    # rotate x ticks
    for tick in AX_DF.get_xticklabels():
        tick.set_rotation(90)


    CANVAS_DF.get_tk_widget().grid(row=2, column=0, columnspan=5)
    CANVAS_DF.draw()

def show_corr_matrix():
    global CORR_DF, AX_CORR, FIG_CORR, CANVAS_CORR, DF_Y_COLS, COLORBAR_CORR
    try:
        print(CORR_DF.columns)
        corr_df = CORR_DF.loc[DF_Y_COLS, DF_Y_COLS]
        AX_CORR.clear()
        cax = AX_CORR.matshow(corr_df, cmap='coolwarm', vmin=-1, vmax=1)
        AX_CORR.set_xticks(np.arange(len(corr_df.columns)))
        AX_CORR.set_yticks(np.arange(len(corr_df.index)))
        AX_CORR.set_xticklabels(corr_df.columns, rotation=90)
        AX_CORR.set_yticklabels(corr_df.index)

        if 'COLORBAR_CORR' not in globals():
            COLORBAR_CORR = FIG_CORR.colorbar(cax)
        else:
            COLORBAR_CORR.update_normal(cax)

        AX_CORR.set_title('Correlation matrix')

        CANVAS_CORR.get_tk_widget().grid(row=2, column=7, columnspan=5)
        CANVAS_CORR.draw()
        
    except Exception as e:
        print(f"Error: {e}")


def update_figure(on_select_date):
    global DF_Y_COUNTRIES, DF_Y_TYPES, DF_Y_COLS

    on_select_date()

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
    CORR_DF.set_index('index', inplace=True)
    # set index to datetime in df
    DF['Datetime'] = pd.to_datetime(DF['Datetime'])
    DF.set_index('Datetime', inplace=True)

    df_cols = DF.columns
    root = create_ui(df_cols)

    # create a plot
    fig_df, AX_DF = create_figure()
    FIG_CORR, AX_CORR = create_figure()
    CANVAS_DF = FigureCanvasTkAgg(fig_df, master=root)
    CANVAS_CORR = FigureCanvasTkAgg(FIG_CORR, master=root)
    on_select_date = date_picker(root, init_start=DF.index[0], init_end=DF.index[-1])
    show_figure()
    show_corr_matrix()

    #button to update the plot
    update_button = tk.Button(root, text="Update Plot", command=lambda: update_figure(on_select_date))
    update_button.grid(row=0, column=6, columnspan=2)
    
    # a label nex to the button
    firs_date = DF.index[0]
    last_date = DF.index[-1]
    info_label = tk.Label(root, text="First date: " + str(firs_date) + " Last date: " + str(last_date))
    info_label.grid(row=0, column=7, columnspan=5)

    #run the GUI
    root.mainloop()

if __name__ == "__main__":
    main()

