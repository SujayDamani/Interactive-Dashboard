import pandas as pd
import io
import math
import numpy as np
import re

import pandas as pd

import dash  # (version 1.12.0) pip install dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)


# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
file_location = r'netflix.xlsx'
netflix = pd.read_excel(file_location)
netflix = netflix.drop_duplicates()

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("Simple Data explorer",
            style={'text-align': 'center'}),

    #a html Div created to have two drop downs next to each other
    html.Div([

        html.Div(
            [dcc.Dropdown(
                id="min year",
                        multi=False,
                        clearable=False,
                        options=[{'label': year, 'value': year}
                                   for year in np.sort(netflix['release year'].unique())],
                        placeholder="Start Year",
                        ), ], style={'width': '29%', 'display': 'inline-block'}
        ),

        html.Div(
            [dcc.Dropdown(
                id="max year",
                multi=False,
                clearable=False,
                #value=max([i for i in netflix['release year'].unique()])
                placeholder="End Year",
            ), ], style={'width': '29%', 'display': 'inline-block'}
        ),

    ]),
    # a dynamic drop down that is depened on the year range thats been selected
    html.Div(
        [dcc.Dropdown(id="rating",
                      multi=True,
                      placeholder="Select Ratings"
                      ), ], style={'width': '70%', 'display': 'inline-block'}
    ),
    html.Div([
        #drop down to select a column to sort by
        html.Div(
            [dcc.Dropdown(id="sort by",
                          multi=False,
                          options=[{'label': col, 'value': col}
                                   for col in netflix.columns],
                          placeholder="Order by Column..",
                          ), ], style={'width': '49%', 'display': 'inline-block'}
        ),
        #drop to select if the sorting should be increasing or decreasing order
        html.Div(
            [dcc.Dropdown(id="increasing_or_decreasing",
                          multi=False,
                          options=[
                              {'label': 'ascending', 'value': 'ascending'},
                              {'label': 'descending', 'value': 'descending'}
                          ],
                          value='ascending',
                          clearable=False,
                          )], style={'width': '19%', 'display': 'inline-block'}
        ),

    ]),
    
    
                 
    
    

    html.H2("Data Table",
            style={'text-align': 'center'}),
    #displaying the data table
    dash_table.DataTable(
    
    id='table',
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    columns=[{"name": i, "id": i} for i in netflix.columns],
    data=netflix.to_dict('records'),
    editable=False,
    ),
    #website the data was taken
    html.H4("Data set from : https://data.world/chasewillden/netflix-shows",
            style={'text-align': 'right'}),
    
])

#updating the table according to the filters selected
@app.callback(Output('table', 'data'), [Input('min year', 'value'), 
                                        Input('max year', 'value'), 
                                        Input('rating', 'value'), 
                                        Input('sort by', 'value'),
                                        Input('increasing_or_decreasing', 'value')])
def update_rows(min_year, max_year, ratings, sort_by, increasing_or_decreasing):
    #logical NAND condition if atleast one of start or end year is selected else display all data
    if not(min_year is None and max_year is None):
        if min_year is None:
            new_df1 = netflix[(netflix['release year'] <= max_year)]
        elif max_year is None:
            new_df1 = netflix[(netflix['release year'] >= min_year)]
        
        else:
            new_df1 = netflix[(netflix['release year'] >= min_year) &
                              (netflix['release year'] <= max_year)]
        
        new_df2 = pd.DataFrame(columns=[col for col in netflix.columns])
        if ratings is not None:
            for rating in ratings:
                temp = new_df1[ (netflix['rating'] == rating)]
                new_df2 = new_df2.append(temp)

            if sort_by is not None:
                if increasing_or_decreasing == "decreasing":
                    new_df2 = new_df2.sort_values(by=[sort_by], ascending=False)
                else:
                    new_df2 = new_df2.sort_values(by=[sort_by])


            return new_df2.to_dict('records')
        
        else:
            if sort_by is not None:
                new_df1 = new_df1.sort_values(by=[sort_by])
            return new_df1.to_dict('records')
    else:
        return netflix.to_dict('records')
    
    
#dynamically updating values displayed in ratings according to the selected years
@app.callback(
    dash.dependencies.Output('rating', 'options'),
    [dash.dependencies.Input('min year', 'value'),
     dash.dependencies.Input('max year', 'value')]
)
def update_rating_dropdown(min_year, max_year):
    if min_year is None:
        dff = netflix[(netflix['release year'] <= max_year)]

    elif max_year is None:
        dff = netflix[(netflix['release year'] >= min_year)]
    
    else:
        dff = netflix[(netflix['release year'] >= min_year) &
                              (netflix['release year'] <= max_year)]

    return [{"label": i, "value": i}
            for i in sorted(dff['rating'].unique())]

#call back to make sure only options greater than equal to start year are displayed for end year 
@app.callback(
    dash.dependencies.Output('max year', 'options'),
    [dash.dependencies.Input('min year', 'value')]
)
def update_rating_dropdown(min_year):
    #print(years)
    dff = netflix[(netflix['release year'] >= min_year)]
    return [{"label": i, "value": i}
            for i in sorted(dff['release year'].unique())]






if __name__ == '__main__':
    app.run_server(debug=True)
