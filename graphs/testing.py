import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from flask_babel import gettext
from plotly.subplots import make_subplots



df_testing = pd.read_csv('static/csv/be-covid-testing.csv')


def bart_plot_cases_testing():
    """
    bar plot cases and testing everyday
    """
    # ---------bar plot age groups death---------------------------

    test_bar = go.Bar(x=df_testing.DATE, y=df_testing.TESTS, name='#Tests')
    case_bar = go.Bar(x=df_testing.DATE, y=df_testing.CASES, name='#Cases')

    fig_testing = go.Figure(data=[test_bar, case_bar], layout=go.Layout(barmode='group'), )
    fig_testing.update_layout(template="plotly_white", height=500, margin=dict(l=0, r=0, t=30, b=0),
                              title="Number of Tests and Cases each day")

    fig_testing.update_layout(xaxis_title='Day',
                              yaxis_title='Number of / Day')

    return fig_testing



def plot_ration_cases_over_testing():
    """
    plot of the ration cases over testing everyday
    """
    fig = px.line(x=df_testing.DATE,y=df_testing.CASES/df_testing.TESTS,title="#Cases/#Tests each day")
    fig.update_layout(xaxis_title='Day',
                   yaxis_title='#Cases/#Tests')
    return fig


def plot_cumulated_testing():
    """
    plot of the cumulated tests cases of days everyday
    """
    fig = go.Figure(data=[go.Scatter(x=df_testing.DATE, y=df_testing.TESTS.cumsum(), name='Cumulated #Test'),
                          go.Scatter(x=df_testing.DATE, y=df_testing.CASES.cumsum(), name='Cumulated #Cases')]
                    )
    fig.update_layout(xaxis_title='Day',
                      yaxis_title='#Cases/#Tests', title="Cumulated number of Tests and Cases")

    return fig






