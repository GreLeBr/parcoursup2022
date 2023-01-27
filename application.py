import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import plotly.express as px
import textwrap
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout="wide")

reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

df = pd.read_csv("./data/df.csv")
ville = df['ville_etab'].unique().tolist()
ville.insert(0, 'Sélectionnez la ville qui vous intéresse')
def customwrap(s,width=50):
    return "<br>".join(textwrap.wrap(s,width=width))

df_dropdown = df[['ville_etab']].drop_duplicates().rename(columns={"ville_etab":"Villes"})
drop_down = sorted(df_dropdown["Villes"].tolist())
selection = st.sidebar.selectbox(
                "Sélectionnez la ville qui vous intéresse", 
                options=drop_down, 
                )
max_rank = st.sidebar.number_input("Nombres de rangs (défaut 5)", min_value=1, max_value=50, value=5)
choix = st.sidebar.radio("Choix sélection", ["Sélective", "Non sélective", "Les deux"])
etablissement = st.sidebar.radio("Choix établissement", ["Public", "Privé", "Les deux"])
mesure = st.sidebar.radio("Choix de la mesure",
 ["Propositions/demandes",
  "Acceptations/propositions",
   "Pourcentage femmes",
    "Pourcentage néo Bacchelier de la même académie",
    "Pourcentage admis néo bacheliers",
    "Pourcentage admis avec mention",
    ])

def main():
  
  if choix == "Sélective":
    choice = ["formation sélective"]
  elif choix == "Non sélective":
    choice  = ["formation non sélective"]
  elif choix == "Les deux":
    choice = ["formation sélective", "formation non sélective"]
  if etablissement == "Public":
    status = ["Public"]
  elif etablissement == "Privé":
    status  = ["Privé sous contrat d'association", 
       'Privé enseignement supérieur']
  elif etablissement == "Les deux":
    status = ["Privé sous contrat d'association", 'Public',
       'Privé enseignement supérieur']  
  if mesure == "Propositions/demandes":
    metric = "prop_tot/voe_tot"
  if mesure == "Acceptations/propositions":
    metric = "acc_tot/prop_tot"
  if mesure == "Pourcentage femmes":
    metric = "pct_f"
  if mesure == "Pourcentage néo Bacchelier de la même académie":
    metric = "pct_aca_orig"
  if mesure == "Pourcentage admis néo bacheliers":
    metric = "pct_neobac"
  if mesure == "Pourcentage admis avec mention":
    metric = "pct_bg_mention"

  df_select = df[(df["ville_etab"]==selection) & (df["lien_form_psup"].isnull()==False)
                 & (df["select_form"].isin(choice))  & (df["contrat_etab"].isin(status))  ].copy()
  df_select["warp"] = df_select["combined"].map(customwrap)
  df_select["rank_fig"]=df_select[metric].rank(method="first")
  df_select["rank_fig1"]=df_select[metric].rank(method="first", ascending=False)

  fig = make_subplots(rows=1, cols=2, 
                    subplot_titles=(f'Croissant',  f'decroissant'))

  fig.add_trace(go.Bar(

            x=df_select.sort_values(metric, ascending=True).head(max_rank)[metric],
            y=df_select.sort_values("rank_fig", ascending=True).head(max_rank)["rank_fig"],
            orientation="h",
            text=df_select.sort_values("rank_fig", ascending=True).head(max_rank)["warp"],
            customdata = [mesure]*5,
            hovertemplate ='<br><b>%{customdata}</b>: %{x}%<br>' + '%{text}  <extra></extra>',
            textposition='outside',
            
            ),
            row=1,
            col=1
            
  )

  fig.add_trace(go.Bar(

             x=df_select.sort_values(metric, ascending=False).head(max_rank)[metric],
             y=df_select.sort_values("rank_fig1", ascending=True).head(max_rank)["rank_fig1"],
             orientation="h",
             text=df_select.sort_values("rank_fig1", ascending=True).head(max_rank)["warp"],
             customdata = [mesure]*5,
            hovertemplate ='<br><b>%{customdata}</b>: %{x}%<br>' + '%{text} <extra></extra>',
            textposition='inside',
            insidetextanchor="start",
            ),
            row=1,
            col=2
            
  )

  fig.update_xaxes( range=[0,110])

  fig.update_layout(yaxis=dict(autorange="reversed"), yaxis2=dict(autorange="reversed"),showlegend=False)

  st.plotly_chart(fig, theme="streamlit", use_container_width=True)

  df_concat = pd.concat([df_select.sort_values("rank_fig", ascending=True ).head(max_rank),  df_select.sort_values("rank_fig1", ascending=True ).head(max_rank) ] )
  AgGrid(df_concat[["lib_for_voe_ins", metric, "lien_form_psup", "rank_fig"]], fit_columns_on_grid_load=False,)

if __name__ == '__main__':
	main()