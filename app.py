import streamlit as st
from datetime import datetime
import time
import pandas as pd

# ---------------- Blockchain Class ----------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.balances = {"Bank Network": 1_000_000}
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append({
            "index": 0,
            "timestamp": str(datetime.now()),
            "transactions": [],
            "previous_hash": "0"
        })

    def ensure_user_balance(self, user, default_balance=100):
        if user not in self.balances:
            self.balances[user] = default_balance

    def add_transaction(self, sender, receiver, amount):
        self.ensure_user_balance(sender)
        self.ensure_user_balance(receiver)
        if amount <= 0:
            return False, "Amount must be greater than 0."
        if sender != "Bank Network" and self.balances[sender] < amount:
            return False, f"{sender} has insufficient balance."
        if sender != "Bank Network":
            self.balances[sender] -= amount
        self.balances[receiver] += amount
        self.pending_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })
        return True, f"{sender} → {receiver}: {amount} coins"

    def mine_block(self, miner_name):
        self.ensure_user_balance(miner_name)
        block = {
            "index": len(self.chain),
            "timestamp": str(datetime.now()),
            "transactions": self.pending_transactions.copy(),
            "previous_hash": str(len(self.chain) - 1)
        }
        self.chain.append(block)
        self.pending_transactions = []
        reward_amount = 10
        self.balances[miner_name] += reward_amount
        return block, f"Block mined by {miner_name}, reward: {reward_amount} coins"

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="CoinFlow - Bank Blockchain Simulator", layout="wide")

# ---------------- Custom CoinFlow Theme CSS ----------------
st.markdown("""
<style>
body {background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif;}
h1, h2, h3 {color: #facc15;}
.stSidebar .css-1d391kg {background-color: #1e293b; color: #e2e8f0;}
.stButton>button {background-color: #facc15; color: #0f172a; font-weight: bold; border-radius: 8px; padding: 0.5em 1em;}
.stTextInput>div>div>input, .stNumberInput>div>div>input {background-color: #1e293b; color: #e2e8f0; border-radius: 5px; padding: 0.5em;}
.stExpanderHeader {background-color: #1e293b !important; color: #facc15 !important; border-radius: 8px;}
div.stDataFrame>div>div>div>div {background-color: #1e293b; color: #e2e8f0;}
</style>
""", unsafe_allow_html=True)

# ---------------- Initialize Blockchain ----------------
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

# ---------------- CoinFlow Header ----------------
st.markdown("<h1 style='text-align:center;'>💸 CoinFlow</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "Navigate:",
    [
        "Home",
        f"Pending Transactions ({len(blockchain.pending_transactions)})",
        f"Blockchain Overview ({len(blockchain.chain)} blocks)"
    ]
)

# ---------------- Home Page ----------------
if "Home" in menu:
  
    # Layout: Transactions & Mining
    tx_col, miner_col = st.columns(2)

    # --- Transactions ---
    with tx_col:
        st.markdown("### New Transaction")
        sender = st.text_input("Sender", key="tx_sender")
        receiver = st.text_input("Receiver", key="tx_receiver")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, key="tx_amount")
        if st.button("Submit Transaction"):
            # Validation
            if not sender.strip():
                st.error("Sender cannot be empty.")
            elif not receiver.strip():
                st.error("Receiver cannot be empty.")
            elif sender == receiver:
                st.error("Sender and Receiver cannot be the same.")
            else:
                success, msg = blockchain.add_transaction(sender, receiver, amount)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

    # --- Mining ---
    with miner_col:
        st.markdown("### ⛏️ Mine Block")
        miner_name = st.text_input("Miner Name", value="Bank Network", key="miner_name")
        if st.button("Start Mining"):
            if not miner_name.strip():
                st.error("Miner name cannot be empty.")
            else:
                progress_text = f"Mining block by {miner_name}..."
                progress_bar = st.progress(0, text=progress_text)
                for percent_complete in range(101):
                    time.sleep(0.02)
                    progress_bar.progress(percent_complete, text=progress_text)
                block, msg = blockchain.mine_block(miner_name)
                st.success(msg)

    # Account Balances Table
    st.markdown("### Account Balances")
    balances_df = pd.DataFrame(
        blockchain.balances.items(), columns=["User", "Balance"]
    ).sort_values(by="Balance", ascending=False)
    st.dataframe(balances_df, use_container_width=True)

# ---------------- Pending Transactions Page ----------------
elif "Pending Transactions" in menu:
    st.subheader("Pending Transactions")
    if blockchain.pending_transactions:
        for idx, tx in enumerate(blockchain.pending_transactions, start=1):
            with st.expander(f"Transaction #{idx}"):
                st.write(f"**Sender:** {tx['sender']}")
                st.write(f"**Receiver:** {tx['receiver']}")
                st.write(f"**Amount:** {tx['amount']} coins")
    else:
        st.info("No pending transactions.")

# ---------------- Blockchain Overview Page ----------------
elif "Blockchain Overview" in menu:
    st.subheader(" Blockchain Overview")
    for block in blockchain.chain:
        with st.expander(f"Block #{block['index']} - {len(block['transactions'])} tx"):
            st.write(f"**Timestamp:** {block['timestamp']}")
            st.write(f"**Previous Hash:** {block['previous_hash']}")
            if block['transactions']:
                for tx in block['transactions']:
                    st.write(f"- {tx['sender']} → {tx['receiver']}: {tx['amount']} coins")
            else:
                st.write("No transactions in this block.")

