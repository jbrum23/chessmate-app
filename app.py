import streamlit as st

# Title and description
st.title("ChessMate")
st.write("Welcome to ChessMate! Play chess against an AI opponent. Choose your settings below to get started.")

st.divider()

# Input 1 - Player name
st.subheader("Player Setup")
player_name = st.text_input("Enter your name:")

# Input 2 - Difficulty
difficulty = st.radio(
    "Select a difficulty level:",
    ["Easy", "Medium", "Hard"]
)

st.divider()

# Dynamic output based on user input
if player_name:
    st.subheader("Game Summary")
    st.write(f"**Player:** {player_name}")
    st.write(f"**Difficulty:** {difficulty}")

    if difficulty == "Easy":
        st.success("Good luck, " + player_name + "! Easy mode is great for beginners!")
    elif difficulty == "Medium":
        st.info("Nice choice, " + player_name + "! Medium mode will give you a real challenge!")
    elif difficulty == "Hard":
        st.error("Bold choice, " + player_name + "! Hard mode is extremely difficult to beat.")
else:
    st.info("Enter your name above to see your game summary.")