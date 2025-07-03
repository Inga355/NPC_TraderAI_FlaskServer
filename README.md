# 🧠 NPC Trader AI – Flask Backend with OpenAI & SQLite

🚧 *This project is a work in progress. Core features are functional, but certain elements (e.g. ChromaDB integration and heuristic trade inference) are still under development.*

This project implements a dynamic NPC trading system for role-playing games using Flask, OpenAI's function calling, SQLite-based inventory management and memory summarization. Optional semantic memory via vector database integration in testing.

---

## 🚀 Features

* Chat interface via HTML + Flask
* Intelligent NPC conversations powered by GPT-4o
* Tool use with OpenAI Function Calling:

  * `parse_trade_intent`: Detects whether the player wants to buy or sell items
  * `trade_consent`: Confirms a trade with the player
* Persistent inventory using SQLite (NPC & Player separation)
* Memory system: chat history saved and summarized
* Vector database support (ChromaDB – *experimental*)

---

## 🧰 Tech Stack

| Layer      | Tool/Library            |
| ---------- | ----------------------- |
| Backend    | Flask, Flask-CORS       |
| AI / LLM   | OpenAI GPT-4o API       |
| Database   | SQLite                  |
| Embeddings | ChromaDB (*test phase*) |
| Frontend   | Plain HTML + JS         |

---

## 📦 Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Add your OpenAI key as environment variable:

```bash
export OPENAI_API_KEY=your-key-here
```

Or create a `.env` file (if using `python-dotenv`).

---

## 💬 Usage

Start the server:

```bash
python app.py
```

Then open [http://localhost:5000/npc/chat](http://localhost:5000/npc/chat) in your browser to talk to your NPC.

---

## 🧪 API Endpoints

### `POST /npc/chat`

* Input: `userpromt` (form value)
* Output: NPC response
* Internally routes through GPT-4o, uses tools if needed

### `GET /api/inventory/<entity_id>`

* Returns inventory of specified player or NPC

---

## ⚠️ Experimental

* The use of **ChromaDB** for semantic long-term memory and vector search is currently in testing
* The helper function `infer_trade_items()` is also under experimental evaluation

---

## 📁 Project Structure

```
|── inventory
    |── inventory.sqlite3   # Database file
|── testfrontend
    |── chatwindow.html     # Minimal front-end chat UI
|── vectordb
    |── ChromaDB            # Vector Database file
├── app.py                  # Flask routes and tool integration
├── agent_tools.py          # Tool definitions for OpenAI function calling
├── memory_store.py         # Chat history and memory management
├── inventory_store.py      # DB operations for inventory and trades
├── prompt_generator.py     # Prompt templates for NPC behavior
|── README.md               # Everythin you need to know about the poject
└── requirements.txt        # Dependency list
```

---

## 📝 License

This code is free to use for **private** or **non-commercial community projects**.
If you intend to use it for **monetary or commercial purposes**, please contact the author for permission.
Author attribution is required in all cases.

---

## 🎮 Game Engine Integration

This backend is designed to be used as a modular AI system in any game engine via HTTP API.

For example, in **Unreal Engine 5**, you can:

* Use HTTP Request nodes to communicate with `/npc/chat`
* Display inventory from `/api/inventory/<id>`
* Trigger trade confirmation dialogs dynamically

Integration requires:

* A running Flask backend (this project)
* UE5 Blueprint logic for requests and UI binding

🧩 The backend is decoupled and can be used in any engine supporting HTTP communication.

## 🙋‍♀️ Author

Crafted with care by Inga 💡
