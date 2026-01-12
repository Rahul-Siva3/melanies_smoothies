#CH.SC.U4AIE23056
import streamlit as st
from snowflake.snowpark.functions import col
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
# Snowflake connection (SniS)
# -------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------------
# Fruit options (GUI vs Search)
# -------------------------------
fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# Show GUI names only
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df.select(col("FRUIT_NAME")),
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

        # Lookup SEARCH_ON value
        search_value = (
            fruit_df
            .filter(col("FRUIT_NAME") == fruit_chosen)
            .select(col("SEARCH_ON"))
            .collect()[0][0]
        )

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothie_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_value}"
        )

        st.dataframe(
            data=smoothie_response.json(),
            use_container_width=True
        )

    # Insert order into Snowflake
    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    session.sql(my_insert_stmt).collect()

    st.success(
        f"Your Smoothie is ordered, {name_on_order}!",
        icon="✅"
    )
