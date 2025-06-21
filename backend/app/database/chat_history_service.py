import os
from dotenv import load_dotenv, find_dotenv
import psycopg
from psycopg.rows import dict_row
from typing import List, Dict, Any

load_dotenv(find_dotenv())

DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        row_factory=dict_row
    )


def create_chat_history_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Enable UUID extension if not exists
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

            # Create chat_history table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    thread_id VARCHAR(255) NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on thread_id for faster queries
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_thread_id ON chat_history (thread_id)
            """)

        
        conn.commit()

def insert_chat_history(thread_id: str, question: str, answer: str):
    """
    Lưu lịch sử chat vào database
    
    Args:
        thread_id (str): ID của cuộc trò chuyện
        question (str): Câu hỏi của người dùng
        answer (str): Câu trả lời của chatbot
        
    Returns:
        Dict: Thông tin lịch sử chat vừa được lưu
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (thread_id, question, answer) 
                VALUES (%s, %s, %s) RETURNING id::text
            """, (thread_id, question, answer))
            result = cur.fetchone()
        conn.commit()
        return result['id']

def get_chat_history(thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id::text, question, answer, created_at
                FROM chat_history
                WHERE thread_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (thread_id, limit))
            
            return cur.fetchall()

def format_chat_history(chat_history: List[Dict[str, Any]]) -> str:
    formatted_history = []
    
    for msg in reversed(chat_history):  # Reverse to get chronological order
        formatted_history.extend([
            {"role": "human", "content": msg["question"]},
            {"role": "assistant", "content": msg["answer"]}
        ])
    
    return formatted_history