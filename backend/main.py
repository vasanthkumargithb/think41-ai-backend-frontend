import os # Added for environment variable access
from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel, Field
from typing import Optional
from groq import Groq # Added Groq import

app = FastAPI()

DATABASE_URL = "./ecommerce.db" # Using the same DB you already have

# Initialize Groq client
# IMPORTANT: It's best practice to use environment variables for API keys.
# Set GROQ_API_KEY in your terminal BEFORE running uvicorn:
# For PowerShell: $env:GROQ_API_KEY="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"
# For Git Bash/WSL/Linux/macOS: export GROQ_API_KEY="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"
# If you want to hardcode for temporary testing (NOT RECOMMENDED for production):
# groq_client = Groq(api_key="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")
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

def create_conversation_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        );
    """)

    # Create conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
            title TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender TEXT NOT NULL, -- 'user' or 'ai'
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        );
    """)
    conn.commit()
    conn.close()

# This function runs when the application starts up
@app.on_event("startup")
async def startup_event():
    create_conversation_tables()
    print("Database tables initialized (if they didn't exist).")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Conversational AI Backend!"}

@app.get("/products/")
async def get_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return {"products": [dict(product) for product in products]}


# --- Pydantic Models for Chat API ---

class ChatRequest(BaseModel):
    user_message: str = Field(..., example="What's the price of the 'Awesome Widget'?")
    conversation_id: Optional[int] = Field(None, example=123)

class ChatResponse(BaseModel):
    ai_response: str = Field(..., example="The 'Awesome Widget' costs $25.99.")
    conversation_id: int = Field(..., example=123)
    message_id: int = Field(..., example=456)


# --- Core Chat API Endpoint (Milestone 4 & 5) ---

@app.post("/api/chat/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Handle User: For simplicity, use a default user or create one if needed
    default_username = "default_user"
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (default_username,))
    conn.commit()
    user_id = cursor.execute("SELECT id FROM users WHERE username = ?", (default_username,)).fetchone()[0]

    # 2. Handle Conversation: Start new or continue existing
    conversation_id = request.conversation_id
    if conversation_id is None:
        # Start a new conversation
        cursor.execute(
            "INSERT INTO conversations (user_id) VALUES (?)",
            (user_id,)
        )
        conn.commit()
        conversation_id = cursor.lastrowid
        print(f"Started new conversation with ID: {conversation_id}")
    else:
        # Check if conversation exists for this user (more robust check needed in real app)
        existing_conversation = cursor.execute(
            "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id)
        ).fetchone()
        if not existing_conversation:
            print(f"Conversation ID {conversation_id} not found for user {user_id}. Starting new conversation.")
            cursor.execute(
                "INSERT INTO conversations (user_id) VALUES (?)",
                (user_id,)
            )
            conn.commit()
            conversation_id = cursor.lastrowid
        else:
            # Update last_updated for existing conversation
            cursor.execute(
                "UPDATE conversations SET last_updated = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
            conn.commit()
            print(f"Continuing conversation with ID: {conversation_id}")

    # 3. Persist User Message
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
        (conversation_id, "user", request.user_message)
    )
    conn.commit()
    user_message_id = cursor.lastrowid
    print(f"User message saved: {request.user_message}")

    # --- 4. LLM Integration & AI Response (Milestone 5 Logic) ---
    ai_response_content = "" # Initialize empty string

    try:
        # Fetch previous messages for context (last 5 messages + current user message for brevity)
        messages_from_db = cursor.execute(
            "SELECT sender, content FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 5",
            (conversation_id,)
        ).fetchall()
        # Reverse to get chronological order for LLM
        messages_from_db.reverse()

        # Format messages for the LLM
        llm_messages = [{"role": row['sender'], "content": row['content']} for row in messages_from_db]

        # Add a system prompt for the LLM
        llm_messages.insert(0, {
            "role": "system",
            "content": "You are a helpful AI assistant for an e-commerce store named Think41. "
                       "Your primary goal is to answer questions about products and orders. "
                       "You have access to product data (like name, price, stock) and order data. "
                       "If a user asks about product details, try to find it in the provided product information. "
                       "If a user asks about an order, state that you can look up order details if they provide an order ID. "
                       "Be concise and professional. If you don't know the answer based on available data, say so."
        })

        # Get product and order data from the database to augment the LLM's context
        products_data_raw = conn.execute("SELECT product_name, category, price, stock_quantity FROM products").fetchall()
        orders_data_raw = conn.execute("SELECT order_id, product_id, quantity, order_date, customer_id FROM orders").fetchall()

        products_info = "Available Products (Name, Category, Price, Stock):\n" + \
                        "\n".join([f"- {p['product_name']} ({p['category']}): ${p['price']:.2f}, Stock: {p['stock_quantity']}" for p in products_data_raw])

        orders_info = "Recent Orders (Order ID, Product ID, Quantity, Date, Customer ID):\n" + \
                      "\n".join([f"- Order {o['order_id']}: Product {o['product_id']} x{o['quantity']} on {o['order_date']} for Customer {o['customer_id']}" for o in orders_data_raw])

        # Add this contextual information to the LLM prompt as part of a tool/context message
        llm_messages.append({"role": "system", "content": f"Here is the current database information:\n\n{products_info}\n\n{orders_info}"})

        chat_completion = groq_client.chat.completions.create(
            messages=llm_messages,
            model="llama3-8b-8192",  # A good general-purpose Groq model
            temperature=0.7,
            max_tokens=200,
            stop=None,
            stream=False
        )
        ai_response_content = chat_completion.choices[0].message.content
    except Exception as e:
        ai_response_content = f"Sorry, I'm having trouble connecting to the AI at the moment. Error: {e}"
        print(f"Error calling Groq API: {e}")

    # --- 5. Persist AI Response ---
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
        (conversation_id, "ai", ai_response_content)
    )
    conn.commit()
    ai_message_id = cursor.lastrowid
    print(f"AI response saved: {ai_response_content}")

    conn.close() # Close connection after all operations

    return ChatResponse(
        ai_response=ai_response_content,
        conversation_id=conversation_id,
        message_id=ai_message_id
    )