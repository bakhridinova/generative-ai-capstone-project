import streamlit as st
from db import init_db, save_uploaded_csv, create_and_load_table, get_stats
from agent import get_answer
from ticket import create_support_ticket

st.set_page_config(page_title="Chat with Your Data", layout="wide")
st.title("Chat with Your CSV → Database")

init_db()
if "db_ready" not in st.session_state:
    st.session_state.db_ready = False
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload your data in CSV or XLSX", type=["csv", "xlsx"], key="csv_uploader")

if uploaded_file is not None:
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get("last_file_id") != current_file_id:
        with st.spinner("Processing your data... (this happens only once)"):
            csv_path = save_uploaded_csv(uploaded_file)
            create_and_load_table(csv_path)
            st.session_state.last_file_id = current_file_id
            st.session_state.db_ready = True
        st.success("Data loaded! You can now chat with your data.")
        st.rerun()
else:
    if st.session_state.db_ready:
        st.info("Your data is already loaded. Ready to chat!")

with st.sidebar:
    if st.session_state.db_ready:
        stats = get_stats()
        st.metric("Rows", f"{stats['rows']:,}")
        st.metric("Total (numeric)", f"{stats['revenue']:,.2f}" if stats['revenue'] else "N/A")
        st.write("Ask anything about your data!")

        st.markdown("---")
        st.subheader("Support")

        ticket_description = st.text_area(
            "Describe your issue",
            placeholder="Write the problem you want to report...",
            key="ticket_description"
        )

        if st.button("Create Support Ticket"):
            last_q = next(
                (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
                "—"
            )
            last_a = next(
                (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"),
                "—"
            )

            link = create_support_ticket(last_q, last_a, ticket_description)
            st.success(link)
    else:
        st.warning("Upload a CSV/XLSX to start")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"], width=700)
        else:
            st.markdown(msg["content"], unsafe_allow_html=True)

if st.session_state.db_ready and (prompt := st.chat_input("Ask about your data...")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = get_answer(prompt)

        if answer.strip().startswith("data:image/png;base64,"):
            st.image(answer, width=700)
        else:
            st.markdown(answer, unsafe_allow_html=True)
    
    if answer.strip().startswith("data:image/png;base64,"):
        st.session_state.messages.append({
            "role": "assistant",
            "type": "image",
            "content": answer
        })
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "type": "text",
            "content": answer
        })

if st.session_state.db_ready and st.button("Create Support Ticket"):
    last_q = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "—")
    last_a = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), "—")
    link = create_support_ticket(last_q, last_a)
    st.success(link)