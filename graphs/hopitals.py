import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from flask_babel import gettext
from plotly.subplots import make_subplots

from graphs import register_plot_for_embedding

df_hospi = pd.read_csv('static/csv/be-covid-hospi.csv')



def df_hospi_death():
    df_hospi = pd.read_csv('static/csv/be-covid-hospi.csv')
    idx = pd.date_range(df_hospi.DATE.min(), df_hospi.DATE.max())
    df_hospi = df_hospi.groupby(['DATE']).agg({'TOTAL_IN': 'sum','TOTAL_IN_ICU': 'sum','NEW_IN': 'sum'})
    df_hospi.index = pd.DatetimeIndex(df_hospi.index)
    df_hospi = df_hospi.reindex(idx, fill_value=0)

    df_mortality = pd.read_csv('static/csv/be-covid-mortality.csv', keep_default_na=False)
    idx = pd.date_range(df_mortality.DATE.min(), df_mortality.DATE.max())
    df_mortality = df_mortality.groupby(['DATE']).agg({'DEATHS': 'sum'})
    df_mortality.index = pd.DatetimeIndex(df_mortality.index)
    df_mortality = df_mortality.reindex(idx, fill_value=0)

    df = df_mortality.merge(df_hospi, how='left', left_index=True, right_index=True)

    df = df[df.index >= '2020-03-15']
    return df

import numpy as np

def moving_average(a, n=1) :
    a = a.astype(np.float)
    ret = np.cumsum(a)
    ret[n:] = ret[n:] - ret[:-n]
    ret[:n-1] = ret[:n-1]/range(1,n)
    ret[n-1:] = ret[n - 1:] / n
    return ret

df = df_hospi_death()

@register_plot_for_embedding("hospi_bar")
def bar_hospitalization():
    """
    bar plot hospitalization
    """
    df = df_hospi.groupby(['DATE']).agg({'TOTAL_IN': 'sum', 'NEW_OUT': 'sum', 'NEW_IN': 'sum','TOTAL_IN_ICU': 'sum'})

    newin_bar = go.Bar(x=df.index, y=df.NEW_IN, name=gettext('#New Hospitalized'))
    newout_bar = go.Bar(x=df.index, y=df.NEW_OUT, name=gettext('#New Discharged'))
    totin_bar = go.Bar(x=df.index, y=df.TOTAL_IN, name=gettext('#Total Hospitalized'))
    icu_bar = go.Bar(x=df.index, y=df.TOTAL_IN_ICU, name=gettext('#Total ICU'))
    fig_hospi = go.Figure(data=[newin_bar, newout_bar, totin_bar,icu_bar], layout=go.Layout(barmode='group'), )
    fig_hospi.update_layout(template="plotly_white", height=500, margin=dict(l=0, r=0, t=30, b=0),
                            title=gettext("Hospitalizations"))

    fig_hospi.update_layout(xaxis_title=gettext('Day'),
                            yaxis_title=gettext('Number of / Day'))

    return fig_hospi


df_prov = pd.read_csv('static/csv/be-covid-provinces.csv')

# compute number of hospi / case in each province
df_tot_provinces_hospi = df_hospi.groupby(['PROVINCE_NAME']).agg({'NEW_IN': 'sum'})
df_tot_provinces_cases = df_prov.groupby(['PROVINCE_NAME']).agg({'CASES': 'sum'})
df_tot_provinces_hospi["NEW_IN_PER_CASES"] = df_tot_provinces_hospi['NEW_IN']/df_tot_provinces_cases["CASES"] #nombre d'hospi/nombre de cas
df_tot_provinces_hospi.reset_index(level=0, inplace=True)
df_tot_provinces_hospi.sort_values(by=["NEW_IN_PER_CASES"],inplace=True)
range_min = df_tot_provinces_hospi["NEW_IN_PER_CASES"].min()
range_max = df_tot_provinces_hospi["NEW_IN_PER_CASES"].max()


@register_plot_for_embedding("hospi_per_case_per_province")
def bar_hospi_per_case_per_province():
    fig = px.bar(df_tot_provinces_hospi,
                 y='PROVINCE_NAME',
                 x='NEW_IN_PER_CASES',
                 color='NEW_IN_PER_CASES',
                 orientation='h',
                 color_continuous_scale="deep",
                 range_color=(range_min, range_max),
                 hover_name="PROVINCE_NAME",
                 labels={'NEW_IN_PER_CASES': gettext('Total Hospitalisation per positive case')},
                 height=400)
    fig.update_traces(
        hovertemplate=gettext("<b>%{y}</b><br>%{x:.3f} hospitalisation per positive case"),
        textposition='outside',
        texttemplate='%{x:.3f}'
    )
    fig.layout.coloraxis.colorbar.titleside = 'right'
    fig.layout.yaxis.title = ""
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=5, b=0))
    return fig


@register_plot_for_embedding("hospi_over_death_smooth")
def hospi_over_death_smooth():
    data_y = moving_average(df.DEATHS.values, 7) / moving_average(df.TOTAL_IN.values, 7)
    return px.line(x=df.index, y=data_y, labels={'x': 'date', 'y': 'ratio death/hospi'})


@register_plot_for_embedding("hospi_over_death_smooth")
def icu_over_hospi():
    data_y = df.TOTAL_IN_ICU / df.TOTAL_IN
    return px.line(x=df.index, y=data_y, labels={'x': 'date', 'y': 'ratio ICU/Hospi'})

@register_plot_for_embedding("hospi_smooth")
def hospi_smooth():
    return px.line(x=df.index,y=moving_average(df.TOTAL_IN.values, 7),labels={'x':'date', 'y':'total hospitals'})

@register_plot_for_embedding("newin_smooth")
def newin_smooth():
    return px.line(x=df.index,y=moving_average(df.NEW_IN.values, 7),labels={'x':'date', 'y':'daily new in hospitals'})

@register_plot_for_embedding("death_smooth")
def death_smooth():
    return px.line(x=df.index, y=moving_average(df.DEATHS.values, 7), labels={'x': 'date', 'y': 'deaths'})
