from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


class ChatHistory(BaseModel):
    id: int = Field(..., title="ID", description="Unique identifier for the chat history")
    thread_id: int = Field(..., title="Thread ID", description="ID of the thread associated with the chat history")
    question: str = Field(..., title="Question", description="The question asked in the chat")
    answer: str = Field(..., title="Answer", description="The answer provided in the chat")
    created_at: datetime = Field(default_factory=datetime.now, title="Created At", description="Timestamp when the chat history was created")

class Product(BaseModel):
    id: int = Field(..., title="ID", description="Unique identifier for the product")
    name: str = Field(..., title="Product Name", description="Name of the product")
    price: Decimal = Field(..., title="Product Price", description="Price of the product")
    original_price: Decimal = Field(..., title="Original Price", description="Original price of the product")
    color: str = Field(..., title="Product Color", description="Color of the product")
    capacity: str = Field(..., title="Product Capacity", description="Capacity of the product")
    policy: str = Field(..., title="Product Policy", description="Policy related to the product")
    specifications: str = Field(..., title="Product Specification", description="Specifications of the product")
    address: str = Field(..., title="Product Address", description="Address related to the product")
    image_url: str = Field(..., title="Product Image URL", description="URL of the product image")
    product_information: str = Field(..., title="Product Information", description="Information of the product")