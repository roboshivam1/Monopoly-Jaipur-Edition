import csv
import streamlit as st
import pandas as pd
from jaipur_properties import JAIPUR_PROPERTIES
from pathlib import Path


# Game configuration
players = {}
initial_cash = 1500
CSV_FILE = "monopoly_data.csv"


#----------------------------------------
#   INITIALIZE SESSION STATE
#----------------------------------------
if 'players' not in st.session_state:
    st.session_state.players = {}

players = st.session_state.players

if 'selling' not in st.session_state:
    st.session_state.selling = False

if 'bought' not in st.session_state:
    st.session_state.bought = []

bought = st.session_state.bought

#------------------------------------------
#   SAVE TO CSV FUNCTION
#------------------------------------------

def save_to_csv():
    with open(CSV_FILE, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Player", "Cash", "Properties"])
        for player, info in players.items():
            properties = ', '.join(info["properties"]) if info["properties"] else "None"
            writer.writerow([player, info['cash'], properties])

#--------------------------------------------------
#   TOTAL WORTH FUNCTION
#--------------------------------------------------
def calculate_total_worth(player):
    return player["cash"] + sum(JAIPUR_PROPERTIES.get(p, 0) for p in player["properties"])
#--------------------------------------------------
#   UI
#--------------------------------------------------

# --- THEME SELECTOR ---
theme = st.selectbox(
    "🎨 Choose Edition Theme",
    ["Normal Streamlit", "Classic Edition", "Deluxe Edition", "Ultimate Banking Edition"]
)

# --- APPLY CSS FUNCTION ---
def load_css(theme_name):
    css_files = {
        "Classic Edition": "classic_design.css",
        "Deluxe Edition": "deluxe_design.css",
        "Ultimate Banking Edition": "ultimate_design.css"
    }

    if theme_name in css_files:
        css_path = Path(css_files[theme_name])
        if css_path.exists():
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ CSS file for {theme_name} not found!")

# --- APPLY SELECTED THEME ---
if theme != "Normal Streamlit":
    load_css(theme)


st.title("Monopoly Jaipur 🎲")
st.set_page_config(page_title="Monopoly Jaipur Manager", page_icon="🎲", layout="wide")



#   PLAYER STATUS PLACEHOLDER
status_placeholder = st.empty()


tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Player", "💰 Update Cash", "🏠 Property Management", "🔁 Player-to-Player payment"])


#   ADD PLAYER
with tab1:
    st.subheader("➕ Add Player")
    new_player = st.text_input("Enter Player Name").strip().lower()
    if st.button("Add Player"):
        if not new_player:
            st.error("Please enter a name")
        elif new_player in players:
            st.error("Player already exists!")
        else:
            players[new_player] = {'cash':  initial_cash, 'properties': []}
            st.success(f"Added new player with ₹{initial_cash}.")
            save_to_csv()

#   UPDATE CASH
with tab2:
    st.subheader("💰 Update Cash")
    selected_player_t1 = st.selectbox("Select player for transaction", list(players.keys()))
    amount = st.number_input("Amount", min_value=0, step=50)
    operation = st.radio("Operation", ["Add", "Subtract"])
    if st.button("Update Cash"):
        if operation == 'Add':
            players[selected_player_t1]["cash"] += amount
            st.success(f"Added ₹{amount} to {selected_player_t1}. Balance: {players[selected_player_t1]['cash']}.")
        
        if operation == 'Subtract':
            if players[selected_player_t1]['cash'] >= amount:
                players[selected_player_t1]["cash"] -= amount
                st.success(f"Deducted ₹{amount} from {selected_player_t1}. Balance: {players[selected_player_t1]['cash']}.")
            else:
                st.error(f"Insufficient balance! Current balance: {players[selected_player_t1]['cash']}")
        save_to_csv()
    if st.button("Add ₹200"):
        players[selected_player_t1]["cash"] += 200
        st.success(f"Added ₹{200} to {selected_player_t1}. Balance: {players[selected_player_t1]['cash']}.")

with tab3:
    st.subheader("🏠 Property Management")
    selected_player_t2 = st.selectbox("Select player", list(players.keys()))
    property_choice = st.selectbox('Property', list(JAIPUR_PROPERTIES.keys()))
    default_price = JAIPUR_PROPERTIES[property_choice]
    property_price = st.number_input("Price", value = default_price, step=10)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Buy Property"):
            if players[selected_player_t2]['cash'] >= property_price:
                if property_choice  not in bought:
                    players[selected_player_t2]["cash"] -= property_price
                    players[selected_player_t2]["properties"].append(property_choice)
                    bought.append(property_choice)
                    st.success(f"{selected_player_t2} bought {property_choice} for ₹{property_price}")
                    save_to_csv()
                else:
                    st.error('Property already owned')
            else:
                st.error("Not enough cash!")
    with col2:
        if st.button("Sell Property"):
            if players[selected_player_t2]["properties"]:
                st.session_state.selling = True
            else:
                st.info("No properties to sell.")
        if st.session_state.selling:
            prop_to_sell = st.selectbox("Select owned property", players[selected_player_t2]["properties"])
            sell_price = st.number_input("Sell Price", min_value=0, step=10, key="sell_price")
            if st.button("Confirm Sell"):
                players[selected_player_t2]["properties"].remove(prop_to_sell)
                players[selected_player_t2]["cash"] += sell_price
                st.success(f"Sold {prop_to_sell} for ₹{sell_price}")
                save_to_csv()
                st.session_state.selling = False  # reset after confirming

with tab4:
    st.subheader("🔁 Player to Player Transactions")
    sender = st.selectbox("Sender", list(players.keys()), key="sender")
    receiver = st.selectbox("Reciever", list(players.keys()), key="reciever")
    pay_amount = st.number_input("Amount to pay", min_value=0, step=50)
    if st.button("Pay"):
        if players[sender]["cash"] >= pay_amount:
            players[sender]["cash"] -= pay_amount
            players[receiver]["cash"] += pay_amount
            st.success(f"{receiver} received ₹{pay_amount} from {sender}")
            save_to_csv()
        else:
            st.error("Insufficient balance!")



#   PLAYER STATUS
with status_placeholder.container():
    st.subheader("Player Status")
    players_df = pd.DataFrame(players).T
    if not players_df.empty:
        players_df["Total Worth"] = [calculate_total_worth(players[name]) for name in players_df.index]
        st.dataframe(players_df, width='stretch')
    else:
        st.info("👋 Add players to start your Monopoly Jaipur game!")
