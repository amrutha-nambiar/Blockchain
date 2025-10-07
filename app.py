import streamlit as st
from datetime import datetime
import time

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
st.set_page_config(page_title="Bank Blockchain Simulator", layout="wide")

# ---------------- Initialize Blockchain ----------------
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

# ---------------- Header ----------------
st.title("🏦 Bank Blockchain Simulator")
st.markdown("---")

# ---------------- Sidebar Navigation ----------------
menu = st.sidebar.selectbox("Navigate", ["Home", "Pending Transactions", "Blockchain Overview"])

# ---------- Home: Transactions & Mining ----------
if menu == "Home":
    tx_col, miner_col = st.columns(2)

    # Transactions
    with tx_col:
        st.header("💳 New Transaction")
        sender = st.text_input("Sender", key="tx_sender")
        receiver = st.text_input("Receiver", key="tx_receiver")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, key="tx_amount")
        if st.button("Submit Transaction"):
            success, msg = blockchain.add_transaction(sender, receiver, amount)
            st.success(msg) if success else st.error(msg)

    # Mining
    with miner_col:
        st.header("⛏️ Mine Block")
        miner_name = st.text_input("Miner Name", value="Bank Network", key="miner_name")
        if st.button("Start Mining"):
            progress_text = f"Mining block by {miner_name}..."
            progress_bar = st.progress(0, text=progress_text)
            for percent_complete in range(101):
                time.sleep(0.03)
                progress_bar.progress(percent_complete, text=progress_text)
            block, msg = blockchain.mine_block(miner_name)
            st.success(msg)

    # Account Balances
    st.header("👥 Account Balances")
    for user, bal in blockchain.balances.items():
        st.write(f"**{user}**: {bal:.2f} coins")

# ---------- Pending Transactions ----------
elif menu == "Pending Transactions":
    st.header("📄 Pending Transactions")
    if blockchain.pending_transactions:
        for tx in blockchain.pending_transactions:
            st.write(f"{tx['sender']} → {tx['receiver']} : {tx['amount']} coins")
    else:
        st.write("No pending transactions")

# ---------- Blockchain Overview ----------
elif menu == "Blockchain Overview":
    st.header("📦 Blockchain Overview")
    for block in blockchain.chain:
        st.markdown(f"**Block #{block['index']}**")
        st.write(f"Timestamp: {block['timestamp']}")
        st.write(f"Previous Hash: {block['previous_hash']}")
        if block['transactions']:
            st.write("Transactions:")
            for tx in block['transactions']:
                st.write(f"- {tx['sender']} → {tx['receiver']} : {tx['amount']} coins")
        else:
            st.write("No transactions")
        st.markdown("---")
