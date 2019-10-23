import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import flask
# the data
df = pd.read_csv("dataset.csv")

meta_df = pd.read_csv('metadata.csv')

# segmenting main jobs
df_main_jobs = meta_df['Primary Column Names:'].tolist()

# segmenting sub-jobs

sub_jobs = meta_df['Secondary Column Names:']

sub_lists = []
for i in range(len(sub_jobs)):
    var = sub_jobs[i]
    varsplit = var.split(',')
    sub_lists.append(varsplit)




# functions to be used for data transformations
def job_sorter(input, dict):
    sub_only = []
    for key in dict:
    
        if key in input:
            for val in dict.values():
                values = list(val)
                for i in values:
                    sub_only.append({'label':i, 'value':i, 'disabled': False})
                return sub_only
        else:
            for val in dict.values():
                values = list(val)
                for i in values:
                    sub_only.append({'label':i, 'value':i, 'disabled': True})
                return sub_only

def returner(word, subset):
	job_dict = {word:subset}
	return job_dict

dict_list = []
for i in range(len(sub_lists)):
    dict_piece = returner(df_main_jobs[i], sub_lists[i])
    dict_list.append(dict_piece)

# making things pretty because UX is important
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# actual app
server = flask.Flask(__name__)

app = dash.Dash(__name__,server=server, external_stylesheets=external_stylesheets)

# This adds a scrollbar if the app is too small
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
# Visual Components:
app.layout = html.Div([
        html.Img(src='/assets/logo.svg'),

        html.Div(children='''
            Select Primary Client Skills:
        '''),

        dcc.Dropdown(
            id='Main Job',
            options=[{'label': i, 'value': i} for i in df_main_jobs],
            value=None,
            multi=True,
            style={'width': '60%', 'display': 'inline-block'}
            ),
        html.Hr(),

        html.Div(children='''
            Select Client Sub-Skills:
        '''),
        dcc.Dropdown(
            id='Sub Jobs',
            multi=True
            ),
        html.Hr(),
        
	dcc.RangeSlider(
		id='Preferred Hours',
		min=df['Preferred Hours'].min(),
		max=df['Preferred Hours'].max(),
		value=[df['Preferred Hours'].min(), df['Preferred Hours'].max()],
		step=1
		),
        
	html.Div(id='slider-output-container'),
        html.Hr(),
	dash_table.DataTable(
			id='table',
			columns=[{"name": i, "id": i} for i in df.columns],

		)
])

# Indicates how many hours have been selected
@app.callback(
	Output('slider-output-container', 'children'),
	[Input('Preferred Hours', 'value')])
def update_output(value):
	return 'Preferred Hours: {}'.format(str(value)[1:-1])

# the hardest piece of the puzzle: getting slider A to influence the behaviour of slider B, while also being a 'multi' slider

@app.callback(
	Output('Sub Jobs', 'options'),
	[Input('Main Job', 'value')]
	)
def the_answer(val):
    big_list = []
    for i in dict_list:
            result = job_sorter(val, i)
            for i in result:
                big_list.append(i)
    return big_list


# The 'data filter' for table

@app.callback(
    Output('table', 'data'),
    [Input('Preferred Hours', 'value'), Input('Main Job', 'value'), Input('Sub Jobs', 'value')]
)
def time_selector(hours, main_job, sub_job):
    x = hours[0]
    y = hours[1]
    z = main_job
    a = sub_job
    # filter hours
    df_f1 = df.loc[(df['Preferred Hours'] >= x) & (df['Preferred Hours'] <= y)]
    # function for filtering jobs


    if z is None:
                df_f2 = df_f1
    else:
                df_f2 = df_f1.dropna(axis=0, how='any', subset=z)
    
    if a is None:
    		df_f3 = df_f2
    else:
    		df_f3 = df_f2.dropna(axis=0, how='any',subset=a)
    return df_f3.to_dict('rows')

# Calling app

if __name__ == '__main__':
    app.run_server(debug=False)
