import pandas as pds
import matplotlib.pyplot as mplt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as strlit
import urllib
from func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency
sns.set(style='dark')
strlit.set_option('deprecation.showPyplotGlobalUse', False)

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
df_all = pds.read_csv("../Dashboard/all_data.csv")
df_all.sort_values(by="order_approved_at", inplace=True)
df_all.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pds.read_csv('../Dashboard/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for i in datetime_cols:
    df_all[i] = pds.to_datetime(df_all[i])

date_max = df_all["order_approved_at"].max()
date_min = df_all["order_approved_at"].min()

# Sidebar
with strlit.sidebar:
    # Title
    strlit.title("Tubagus Lingga Qolbuwasi")

    # Date Range
    start_date, end_date = strlit.date_input(
        label="Date Range",
        value=[date_min, date_max],
        min_value=date_min,
        max_value=date_max
    )

# Main
df_main = df_all[(df_all["order_approved_at"] >= str(start_date)) & 
                 (df_all["order_approved_at"] <= str(end_date))]

get_function = DataAnalyzer(df_main)
plot_map = BrazilMapPlotter(data, mplt, mpimg, urllib, strlit)

df_sum_spend = get_function.create_sum_spend_df()
df_sum_order_items = get_function.create_sum_order_items_df()
score_review, score_common = get_function.review_score_df()
state, common_state = get_function.create_bystate_df()
status_order, common_status = get_function.create_order_status()
df_bycity, most_common_city = get_function.customer_count_by_city()
 

# Title
strlit.header("Dashboard E-Commerce")

# Order Items
strlit.subheader("Order Items")
col_1, col_2 = strlit.columns(2)

with col_1:
    items_total = df_sum_order_items["product_count"].sum()
    strlit.markdown(f"Total Items: **{items_total}**")

with col_2:
    items_avg = df_sum_order_items["product_count"].mean()
    strlit.markdown(f"Average Items: **{items_avg}**")

figr, a_x = mplt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors_all = ["blue", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=df_sum_order_items.head(5), palette=colors_all, ax=a_x[0], hue="product_category_name_english", legend=False)
a_x[0].set_ylabel(None)
a_x[0].set_xlabel("Angka Yang Terjual", fontsize=30)
a_x[0].set_title("Produk paling Laku", loc="center", fontsize=50)
a_x[0].tick_params(axis ='y', labelsize=35)
a_x[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english", data=df_sum_order_items.sort_values(by="product_count", ascending=True).head(5), palette=colors_all, ax=a_x[1], hue="product_category_name_english", legend=False)
a_x[1].set_ylabel(None)
a_x[1].set_xlabel("Angka Yang Terjual", fontsize=30) 
a_x[1].invert_xaxis()
a_x[1].yaxis.set_label_position("right")
a_x[1].yaxis.tick_right()
a_x[1].set_title("Produk paling Tidak Laku", loc="center", fontsize=50)
a_x[1].tick_params(axis='y', labelsize=35)
a_x[1].tick_params(axis='x', labelsize=30)

strlit.pyplot(figr)

# Customer Spend Money
strlit.subheader("Customer Spend Money")
col_1, col_2 = strlit.columns(2)

with col_1:
    spend_total = format_currency(df_sum_spend["total_spend"].sum(), "IDR", locale="id_ID")
    strlit.markdown(f"Total Spend: **{spend_total}**")

with col_2:
    avg_spend = format_currency(df_sum_spend["total_spend"].mean(), "IDR", locale="id_ID")
    strlit.markdown(f"Average Spend: **{avg_spend}**")


fig, a_x = mplt.subplots(figsize=(12, 6))
a_x.plot(
    df_sum_spend["order_approved_at"],
    df_sum_spend["total_spend"],
    marker="o",
    linewidth=2,
    color="blue"
)
a_x.tick_params(axis="x", rotation=45)
a_x.tick_params(axis="y", labelsize=15)
strlit.pyplot(fig)

# Review Score
strlit.subheader("Review Score")
col_1,col_2 = strlit.columns(2)

with col_1:
    score_avg = score_review.mean()
    strlit.markdown(f"Average Review Score: **{score_avg}**")

with col_2:
    score_most_common = score_review.value_counts().index[0]
    strlit.markdown(f"Most Common Review Score: **{score_most_common}**")

figr, a_x = mplt.subplots(figsize=(12, 6))
sns.barplot(x=score_review.index, 
            y=score_review.values, 
            order=score_review.index,
            color="blue"
            )

mplt.title("Rating by customers for service", fontsize=15)
mplt.xlabel("Rating")
mplt.ylabel("Count")
mplt.xticks(fontsize=12)
strlit.pyplot(figr)


# Customer Demographic
strlit.subheader("Customer Demographic")
tab_1, tab_2, tab_3, tab_4 = strlit.tabs(["State", "City", "Order Status", "Geolocation"])

with tab_1:
    strlit.subheader("Customer Count by state")
    figr, ax = mplt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                color="blue"
                    )

    mplt.title("Number customers from State", fontsize=15)
    mplt.xlabel("State")
    mplt.ylabel("Number of Customers")
    mplt.xticks(fontsize=12)
    strlit.pyplot(figr)

with tab_2:
    strlit.subheader("Customer Count by City")
    figr, a_x = mplt.subplots(figsize=(12, 6))
    sns.barplot(x=df_bycity.index,
                y=df_bycity.values,
                color="blue"
                )
    mplt.title("Customer Count by City", fontsize=15)
    mplt.xlabel("City")
    mplt.ylabel("Number of Customers")
    mplt.xticks(rotation=45, fontsize=10)
    strlit.pyplot(figr)

with tab_3:
    status_common = status_order.value_counts().index[0]
    strlit.markdown(f"Most Common Order Status: **{status_common}**")

    figr, a_x = mplt.subplots(figsize=(12, 6))
    sns.barplot(x=status_order.index,
                y=status_order.values,
                order=status_order.index,
                color = "blue"
                )
    
    mplt.title("Order Status", fontsize=15)
    mplt.xlabel("Status")
    mplt.ylabel("Count")
    mplt.xticks(fontsize=12)
    strlit.pyplot(figr)

with tab_4:
    plot_map.plot()

    with strlit.expander("See Explanation"):
        strlit.write('Berdasarkan grafik yang tealh dibuat, Dapat dilihat  terdapat konsentrasi pelanggan yang lebih tinggi di wilayah tenggara dan selatan. Selain itu, jumlah pelanggan lebih banyak di kota-kota besar yang juga berfungsi sebagai pusat pemerintahan, seperti São Paulo, Rio de Janeiro, Porto Alegre, dan lain-lain).')

strlit.caption('by Tubagus Lingga Q') 


