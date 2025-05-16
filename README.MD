# 🧀 Cheese Product Reasoning Chatbot

An interactive AI-powered chatbot that assists with complex queries about a cheese production database. Built with **LangChain-style reasoning**, **SQL tools**, **Vector DB search**, and a clean **Streamlit UI** supporting chat history, reasoning visualization, and clarifying questions.

---

## 🚀 Features

- 🔍 Intelligent product search using SQL and vector similarity tools.
- 🧠 Step-by-step reasoning with state tracking (`sql_query`, `vectordb_query`, `both`, `complete`, `self`).
- 💬 Conversational memory and chat history sidebar.
- 🧾 Clarification prompts when user queries are ambiguous.
- 🌐 Uses GPT-4o (or any OpenAI-compatible LLM) for reasoning and tool selection.
- 🧊 Pinecone as vector DB, MySQL for structured data.

---

## 🏗️ Architecture
```sql
User → Streamlit UI → LangChain-style Reasoning Engine → Tools:
                                                          ├── SQLQueryTool → MySQL DB
                                                          ├── VectorDBTool → Pinecone
                                                          └── ClarificationTool → User
```

---

## 🧩 Components

### Backend
- **LangChain-style Reasoning Agent**: Determines when to use SQL, vectordb, or ask the user.
- **Tools**:
  - `sql_query`: Executes SQL against MySQL cheese product database.
  - `vectordb_query`: Uses Pinecone to search semantically.
  - `clarification`: Requests more info from user if query is vague.

### Frontend (Streamlit)
- **Chat interface**: Display user & agent messages with markdown and role distinction.
- **Sidebar**: Chat history list (like ChatGPT).
- **Reasoning trace**: Each step (tool usage, thoughts, final answer) is shown interactively.

---

## 🗃️ Database Schema

MySQL table: `cheese_product`
- sku VARCHAR(20) PRIMARY KEY,
- name TEXT,
- brand VARCHAR(100),
- department VARCHAR(100),
- each_item_counts VARCHAR(50),
- each_dimensions VARCHAR(100),
- each_weights VARCHAR(50),
- case_item_counts VARCHAR(50),
- case_dimensions VARCHAR(100),
- case_weights VARCHAR(50),
- images JSON,
- relateds JSON,
- each_prices DECIMAL(10,2),
- case_prices DECIMAL(10,2),
- price_per VARCHAR(20),
- discount VARCHAR(100),
- empty BOOLEAN,
- href TEXT,
- price_order INT,
- popularity_order INT
---

## 💻 Installation

```bash
# Clone the repo
git clone https://github.com/benjamin-wilson7812/cheese-production-agent.git
cd cheese-production-agent

# Install dependencies
pip install -r requirements.txt
```
##### Set up your .env with the following keys:
```env
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
LANGCHAIN_API_KEY=
DB_NAME="cheese"
DB_HOST=
DB_PASSWORD=
DB_USER=
DB_PORT=
```
## ▶️ Running the App
```bash
streamlit run main.py
```
The app will launch in your browser at http://localhost:8501.
## 📂 Project Structure
```pgsql
├── app/
│ ├── core/
│ │ ├── prompt_templates/
│ │ │ └── generate_reasoning_step.py
│ │ └── config.py
│ ├── db/
│ │ ├── mysql.py
│ │ └── vectordb.py
│ ├── schemas/
│ │ ├── cheese_products.py
│ │ └── sentence_embedded.py
│ └── services/
│  ├── chat.py
│  └── graph/
│     ├── graph_nodes.py
│     └── graph_state.py
├── scripts/
│ └── data_preprocess.py
├── main.py
├── graph.png
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```
## 📜 License
MIT License