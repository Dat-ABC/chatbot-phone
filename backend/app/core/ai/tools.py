from ast import List
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Annotated, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.database.product_service import get_product_by_name, get_products_by_price, get_product_by_address, get_product_by_specs, get_flexible_product_search
from decimal import Decimal
from tavily import TavilyClient
import requests
from dotenv import load_dotenv

load_dotenv()

class FlexibleProductSearch(BaseModel):
    use_columns: Optional[List[str]] = Field(
        default=["name", "color", "capacity", "price", "image_url", "specifications"],
        description= "List of specific columns to return in the result."
    )
    name: Optional[List[str]] = Field(
        default=None,
        description="List of product names to search for (fuzzy match)"
    )
    capacity: Optional[List[str]] = Field(
        default=None,
        description="List of capacity values to filter by (fuzzy match)"
    )
    color: Optional[List[str]] = Field(
        default=None,
        description="List of colors to filter by (fuzzy match)"
    )
    policy: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of policy-related texts to filter (fuzzy match) "
            "Includes: offers, shipping, warranties, etc."
        )
    )
    product_information: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of product information strings to filter (fuzzy match) "
            "eg: specifications, product details"
        )
    )
    address: Optional[List[str]] = Field(
        default=None,
        description="List of addresses to filter by (fuzzy match)"
    )
    condition_groups: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description=(
            "Dictionary to group related conditions. Keys are group names, "
            "values are lists of field names to group together. "
            "Example: {'device_specs': ['name', 'product_information']}"
        )
    )
    group_operator: Optional[str] = Field(
        default="AND",
        description=(
            "Operator to use between condition groups. "
            "Must be either 'AND' or 'OR'."
        )
    )
    price_range: Optional[List[float]] = Field(
        default=None,
        description= "Filter by exact price range [min_price, max_price]"
    )
    discount_percent: Optional[List[float]] = Field(
        default=None,
        description="Discount percent range filter as [min_pct, max_pct]"
    )
    sort_by: Optional[str] = Field(
        default="",
        description="Sort order when price not specified: 'price_asc' or 'price_desc'"
    )
    limit: Optional[int] = Field(
        default=10,
        description="Max number of results"
    )

class FlexibleProductSearchTool(BaseTool):
    name: str = Field(
        default="flexible_product_search",
        description="Tool for flexible product search"
    )
    description: str = (
        "Search products with flexible filters: fuzzy name, address, specifications, policy, color, capacity, "
        "price proximity or range, discount percent range, sort and limit results"
    )
    args_schema: type[BaseModel] = FlexibleProductSearch

    def _run(
        self,
        use_columns: Optional[List[str]] = None,
        name: Optional[List[str]] = None,
        capacity: Optional[List[str]] = None,
        price: float = 0,
        color: Optional[List[str]] = None,
        policy: Optional[List[str]] = None,
        product_information: Optional[List[str]] = None,
        address: Optional[List[str]] = None,
        operator_flags: Optional[Dict[str, str]] = None,
        condition_groups: Optional[Dict[str, List[str]]] = None,
        group_operator: str = "AND",
        price_range: Optional[List[float]] = None,
        discount_percent: Optional[List[float]] = None,
        sort_by: str = "",
        limit: int = 0
    ) -> Optional[List[Dict]]:
        return get_flexible_product_search(
            use_columns=use_columns,
            name=name,
            capacity=capacity,
            price=price,
            color=color,
            policy=policy,
            product_information=product_information,
            address=address,
            operator_flags=operator_flags,
            condition_groups=condition_groups,
            group_operator=group_operator,
            price_range=price_range,
            discount_percent=discount_percent,
            sort_by=sort_by,
            limit=limit
        )

def get_phone_news_by_tavily(q="latest iphone", **kwargs):
    """
    Fetches news articles from Google Custom Search API based on the given query, language, and country.
    Args:
        q (str): The phone search query term (default is "latest iphone").
    Returns:
        result string.
    """

    try:
        TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") 

        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        
        # Thực hiện tìm kiếm với các tham số bổ sung
        response = tavily_client.search(
            query=q,
            include_answer=True,
            max_results=5,
            include_raw_content=True
        )

        result_str = ""

        # Thêm câu trả lời tổng quan nếu có
        if 'answer' in response and response['answer']:
            result_str += f"🔎 Tóm tắt: {response['answer']}\n\n"

        # Duyệt qua từng kết quả và thêm thông tin chi tiết
        for idx, result in enumerate(response.get("results", []), 1):
            title = result.get('title', 'Không có tiêu đề')
            url = result.get('url', 'Không có URL')
            content = result.get('content', 'Không có nội dung')
            result_str += f"{idx}. {title}\nURL: {url}\n{content}\n\n"

        print("---------search web:\n", result_str)
        return result_str

    except requests.exceptions.RequestException as e:
        print('error', e)
        return f"Error: {e}"

class SearchWeb(BaseModel):
    q: str = Field(
        ...,
        description=(
            "Search query for the latest mobile phone news, announcements, and trends. "
            "Can request market advice, feature comparisons, product evaluations, "
            "or background information on retailers such as Hoàng Hà Mobile."
        )
    )

class SearchWebTool(BaseTool):
    name: Annotated[str, Field(description="Unique tool identifier")] = "search_web"
    description: str = (
        "Fetch the latest news and information about mobile phones: "
        "- Market trends and announcements  "
        "- Feature comparisons and product evaluations  "
        "- Background on retailers like Hoàng Hà Mobile  \n"
        "Excludes content about non-phone products."
    )
    args_schema: type[BaseModel] = SearchWeb

    def _run(self, q: str) -> Optional[Dict]:
        return get_phone_news_by_tavily(q)




class ProductSearch(BaseModel):
    product_name: str = Field(..., description="Name of the product to search for")

class ProductSearchTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "product_search"
    description: str = "Search for product information by name"
    args_schema: type[BaseModel] = ProductSearch

    def _run(self, product_name: str) -> Optional[Dict]:
        return get_product_by_name(product_name)

class ProductPrice(BaseModel):
    price: Decimal = Field(..., description="Price of the product")

class ProductPriceTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "product_price"
    description: str = "The product has a price range within the range that the user is looking for"
    args_schema: type[BaseModel] = ProductPrice

    def _run(self, price: Decimal) -> Optional[Dict]:
        product = get_products_by_price(price)
        return product

class ProductAddress(BaseModel):
    product_name: str = Field(..., description="Name of the product")

class ProductAddressTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "product_address"
    description: str = "A tool to get the address of a product"
    args_schema: type[BaseModel] = ProductAddress

    def _run(self, product_name: str) -> Optional[Dict]:
        product = get_product_by_address(product_name)
        return product

class ProductSpecs(BaseModel):
    specs: str = Field(..., description="Specifications of the product")

class ProductSpecsTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "product_specs"
    description: str = "Get products according to specifications"
    args_schema: type[BaseModel] = ProductSpecs

    def _run(self, specs: str) -> Optional[Dict]:
        product = get_product_by_specs(specs)
        return product
    

class ProductPolicy(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    policy: str = Field(..., description="Policy of the product")

class ProductPolicyTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "product_policy"
    description: str = "A tool to get the policy of a product."
    args_schema: type[BaseModel] = ProductPolicy

    def _run(self, product_name: str, policy: str) -> Optional[Dict]:
        product = get_product_by_name(product_name)
        return product
    
