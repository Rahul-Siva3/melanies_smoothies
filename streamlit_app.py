#CH.SC.U4AIE23056

import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# -------------------------------
# App Title & Description
# -------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------------
# Name input
# -------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -------------------------------
# Snowflake connection (SniS style)
# -------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------------
# Fruit options (GUI label + search term)
# -------------------------------
my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark DF → Pandas DF
pd_df = my_dataframe.to_pandas()

# -------------------------------
# Multiselect (shows FRUIT_NAME)
# -------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=6
)

# -------------------------------
# Submit Order
# -------------------------------
submit_order = st.button("Submit Order")

if submit_order and ingredients_list and name_on_order:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # 🔑 Get SEARCH_ON value for API lookup
        search_on = (
            pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]
        )

        st.write("The search value for", fruit_chosen, "is", search_on)

        # -------------------------------
        # SmoothieFroot API call
        # -------------------------------
        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefruit_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            smoothiefruit_response.json(),
            use_container_width=True
        )

    # -------------------------------
    # Insert order into Snowflake
    # -------------------------------
    my_insert_stmt = (
        "insert into smoothies.public.orders (ingredients, name_on_order) "
        "values ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    session.sql(my_insert_stmt).collect()

    st.success(
        f"Your Smoothie is ordered, {name_on_order}!",
        icon="✅"
    )
