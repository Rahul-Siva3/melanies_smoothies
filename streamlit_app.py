import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

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
# Snowflake connection (SniS)
# -------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------------
# Fruit options (FRUIT_NAME + SEARCH_ON)
# -------------------------------
my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert to Pandas for .loc usage
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -------------------------------
# Submit Order
# -------------------------------
submit_order = st.button("Submit Order")

if submit_order and ingredients_list and name_on_order:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value using Pandas
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on
        )

        # SmoothieFroot API call
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            st.subheader(f"{fruit_chosen} Nutrition Information")
            st.dataframe(
                response.json(),
                use_container_width=True
            )
        else:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    # Insert order into Snowflake
    my_insert_stmt = (
        "insert into smoothies.public.orders (ingredients, name_on_order) "
        "values ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    session.sql(my_insert_stmt).collect()

    st.success(
        f"Your Smoothie is ordered, {name_on_order}!",
        icon="✅"
    )
