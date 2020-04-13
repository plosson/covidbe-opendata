from datetime import datetime, date

import geopandas
import plotly.express as px
import pandas as pd
import numpy as np
from flask_babel import gettext

df_communes_tot = pd.merge(pd.read_csv("static/csv/be-covid-totcases.csv", dtype={"NIS5": str}),
                           pd.read_csv("static/csv/ins_pop.csv", dtype={"NIS5": str}),
                           left_on='NIS5',
                           right_on='NIS5',
                           how='left')
df_communes_tot["CASES_PER_1000_POP"] = 1000.0*df_communes_tot.CASES/df_communes_tot.POP
df_communes_timeseries = pd.read_csv('static/csv/be-covid-timeseries.csv')
geojson_communes = geopandas.read_file('static/json/communes/be-geojson.json')

df_communes_tot['colorbase'] = df_communes_tot.apply(lambda row: np.log2(row.CASES) if row.CASES != 0 else 0, axis=1)
df_communes_tot['name'] = df_communes_tot.apply(
    lambda row: (row.FR if row.FR == row.NL else f"{row.FR}/{row.NL}").replace("_", " "), axis=1)


def map_communes_per_inhabitant():
    fig = px.choropleth_mapbox(df_communes_tot, geojson=geojson_communes,
                               locations="NIS5",
                               color='CASES_PER_1000_POP', color_continuous_scale="magma_r",
                               #range_color=(3, 10),
                               featureidkey="properties.AdMuKey",
                               center={"lat": 50.641111, "lon": 4.668889},
                               hover_name="CASES_PER_1000_POP",
                               hover_data=["name", "CASES_PER_1000_POP", "NIS5"],
                               height=500,
                               mapbox_style="carto-positron", zoom=6)
    fig.update_geos(fitbounds="locations")
    fig.layout.coloraxis.colorbar.title=gettext("Number of cases per 1000 inhabitants")
    fig.layout.coloraxis.colorbar.titleside="right"
    fig.layout.coloraxis.colorbar.ticks="outside"
    fig.layout.coloraxis.colorbar.tickmode="array"
    fig.update_traces(
        hovertemplate=gettext(gettext("<b>%{customdata[0]}</b><br>%{customdata[1]:.2f} cases per 1000 inhabitants"))
    )
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=5, b=0))

    return fig


def map_communes():
    fig = px.choropleth_mapbox(df_communes_tot, geojson=geojson_communes,
                               locations="NIS5",
                               color='colorbase', color_continuous_scale="deep",
                               range_color=(3, 10),
                               featureidkey="properties.AdMuKey",
                               center={"lat": 50.641111, "lon": 4.668889},
                               hover_name="CASES",
                               hover_data=["name", "CASES", "NIS5"],
                               height=500,
                               mapbox_style="carto-positron", zoom=6)
    fig.update_geos(fitbounds="locations")
    NB_TICKS = 12
    fig.layout.coloraxis.colorbar = dict(
        title=gettext("Number of cases"),
        titleside="right",
        tickmode="array",
        tickvals=list(range(1, NB_TICKS + 1)),
        ticktext=[str(2 ** i) for i in range(1, NB_TICKS + 1)],
        ticks="outside"
    )
    fig.update_traces(
        hovertemplate=gettext("<b>%{customdata[0]}</b><br>%{customdata[1]} cases")
    )
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=5, b=0))
    return fig


def barplot_communes(commune_nis=73006):
    [nis, cases, fr, nl, _, title_text, _, _] = df_communes_tot.loc[df_communes_tot['NIS5'] == str(commune_nis)].values[0]
    title = title_text

    orig_first_date = datetime.strptime(
        df_communes_timeseries.loc[df_communes_timeseries[str(commune_nis)] > 0]["DATE"].min(), "%Y-%m-%d").date()
    first_date = date(year=orig_first_date.year, month=orig_first_date.month, day=1)
    last_date = datetime.strptime(df_communes_timeseries["DATE"].max(), "%Y-%m-%d").date()

    range_y_stop = max(10, df_communes_timeseries[str(commune_nis)].max())

    fig = px.bar(df_communes_timeseries, x='DATE', y=str(commune_nis), height=400,
                 range_x=(first_date, last_date),
                 range_y=(0, range_y_stop),
                 color=str(commune_nis), color_continuous_scale="deep",
                 labels={"DATE": "Date", str(commune_nis): "# Cases"})

    fig.update_layout(title_text=gettext("Number of cases in {title}: {cases}").format(title=title, cases=cases),
                      height=500, template="plotly_white", margin=dict(l=20, r=0, t=60, b=0))
    fig.layout.coloraxis.showscale = False
    fig.update_traces(
        hovertemplate=gettext("<b>%{x}</b><extra>%{y} cases</extra>"),
    )
    return fig
