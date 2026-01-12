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
# Snowflake connection (SniS style)
# -------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------------
# Fruit options from Snowflake
# -------------------------------
my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
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

    my_insert_stmt = (
        "insert into smoothies.public.orders (ingredients, name_on_order) "
        "values ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    session.sql(my_insert_stmt).collect()

    st.success(
        f"Your Smoothie is ordered, {name_on_order}!",
        icon="✅"
    )

# =====================================================
# NEW SECTION — SmoothieFruit API (Lesson 10)
# =====================================================

st.markdown("---")
st.subheader("🍉 SmoothieFruit Nutrition Info")

smoothiefruit_response = requests.get(
    "https://my.smoothiefruit.com/api/fruit/watermelon"
)

# Convert JSON response into a Streamlit dataframe
st.dataframe(
    data=smoothiefruit_response.json(),
    use_container_width=True
)
