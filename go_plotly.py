import pandas as pd
import streamlit as st
from plotly import graph_objs as go


class Graph:
    @staticmethod
    def params_fig(fig) -> go.Figure:
        fig.update_layout(
            width=700,
            height=400,
            margin=dict(l=0, r=0, t=0, b=0, pad=0),
            legend=dict(
                x=0,
                y=0.99,
                traceorder="normal",
                font=dict(size=12),
            ),
            autosize=False,
            template="plotly_dark")
        return fig

    @staticmethod
    def add_feature(fig, data: pd.DataFrame = None, y_data: pd.Series = None, symbol: str = None) -> go.Figure:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=y_data,
                mode="lines",
                name=symbol,
            )
        )
        return fig

    @staticmethod
    def plot_line_data(data=None, field=None) -> go.Figure:
        fig = go.Figure()
        if field is None:
            if type(data) == pd.Series:
                fig = Graph.add_feature(fig, data, data)
            else:
                field = list(data.columns)
                for _ in field:
                    y_data = data[_]
                    fig = Graph.add_feature(fig, data, y_data, _)
        else:
            fig = Graph.add_feature(fig, data, data[field])
        fig = Graph.params_fig(fig)
        fig.update_layout(xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

    @staticmethod
    def plot_hist_data(data: pd.Series = None) -> go.Figure:
        fig = go.Figure(data=[go.Histogram(x=data, histnorm='probability')])
        fig = Graph.params_fig(fig)
        st.plotly_chart(fig)
