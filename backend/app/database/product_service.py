from pickle import DICT
from typing import List, Optional, Dict
from .chat_history_service import get_connection
from decimal import Decimal
import re
import unicodedata
import requests

def create_product_table():
    """
    Create the product table in the database.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    color VARCHAR(100) NOT NULL,
                    capacity VARCHAR(100) NOT NULL,
                    price DECIMAL(12,2) NOT NULL,
                    original_price DECIMAL(12,2) NOT NULL,
                    policy TEXT,
                    specifications TEXT NOT NULL,
                    address TEXT,
                    image_url TEXT,
                    product_information TEXT
                )
            """)
            conn.commit()
            print("Product table created successfully.")

def format_currency_vn(amount_str):
    amount = Decimal(amount_str)
    # Định dạng số với dấu phẩy làm phân cách hàng nghìn
    formatted = f"{amount:,.0f}"
    # Thay dấu phẩy bằng dấu chấm và thêm ký hiệu tiền tệ
    return formatted.replace(",", ".") + " vnđ"

def slugify(name: str) -> str:
    """Chuyển đổi tên thành slug an toàn cho tên file/thư mục"""
    # Chuẩn hóa Unicode về NFKD (tách ký tự và dấu)
    normalized = unicodedata.normalize('NFKD', name)
    # Loại bỏ các combining marks (dấu)
    without_accents = ''.join(
        c for c in normalized
        if not unicodedata.combining(c)
    )
    # Chuyển về chữ thường
    lowercased = without_accents.lower()
    # Loại bỏ ký tự không phải chữ, số, gạch dưới hoặc khoảng trắng
    cleaned = re.sub(r'[^\w\s-]', '', lowercased)
    # Thay thế nhóm khoảng trắng/gạch ngang thành dấu gạch dưới và cắt bỏ đầu/cuối
    slug = re.sub(r'[-\s]+', '_', cleaned).strip('_')
    return slug

def get_product_by_name(name: str) -> Optional[Dict]:
    """
    Get a product by its name.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, capacity, color, price, image_url FROM products WHERE LOWER(name) LIKE LOWER(%s)", (f"%{name}%",))
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    if not any(unit in row['capacity'] for unit in ['MB', 'GB', 'TB']):
                        row.pop('capacity', None)
                    
                    row['price'] = format_currency_vn(row['price'])

                    color = row['color'].strip().split(",")[0]

                    image_path = f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/{row['image_url']}/{slugify(color)}/{color}.png?raw=true".replace(" ", "%20")

                    row['image_url'] = image_path

                    # Gửi yêu cầu get để kiểm tra sự tồn tại của tệp
                    # response = requests.get(image_path)

                    # if response.status_code == 200:
                    #     row['image_url'] = image_path
                    # else:
                    #     row.pop('image_url', None)

                    

            return rows

def get_products_by_price(price: float) -> List[Dict]:
    """
    Get products within a specified price range.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, capacity, color, price, image_url FROM products WHERE price BETWEEN %s AND %s", (price - 500000, price + 500000))
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    if not any(unit in row['capacity'] for unit in ['MB', 'GB', 'TB']):
                        row.pop('capacity', None)
                    
                    row['price'] = format_currency_vn(row['price'])
                    
                    color = row['color'].strip().split(",")[0]

                    image_path = f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/{row['image_url']}/{slugify(color)}/{color}.png?raw=true".replace(" ", "%20")

                        # Gửi yêu cầu get để kiểm tra sự tồn tại của tệp
                    response = requests.get(image_path)

                    if response.status_code == 200:
                        row['image_url'] = image_path
                    else:
                        row.pop('image_url', None)
                            

            return rows

def get_product_by_address(name:str) -> Optional[Dict]:
    """
    Get a product by its address.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, capacity, color, price,  FROM products WHERE LOWER(name) LIKE LOWER(%s)", (f"%{name}%", ))
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    if not any(unit in row['capacity'] for unit in ['MB', 'GB', 'TB']):
                        row.pop('capacity', None)
                    
                    row['price'] = format_currency_vn(row['price'])

                    color = row['color'].strip().split(",")[0]

                    image_path = f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/{row['image_url']}/{slugify(color)}/{color}.png?raw=true".replace(" ", "%20")

                        # Gửi yêu cầu get để kiểm tra sự tồn tại của tệp
                    response = requests.get(image_path)

                    if response.status_code == 200:
                        row['image_url'] = image_path
                    else:
                        row.pop('image_url', None)
                            
            return row
        
def get_product_by_specs(specs: str) -> Optional[Dict]:
    """
    Get a product by its specifications.
    """
    pattern = f"%{specs}%"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, specifications FROM products WHERE LOWER(specifications) like LOWER(%s)", (pattern,))
            rows = cursor.fetchall()
            
            return rows
        
def get_policy_by_name(name: str) -> Optional[Dict]:
    """
    Get a product by its name.
    """
    pattern = f"%{name}%"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, policy FROM products WHERE LOWER(name) = LOWER(%s)", (pattern,))
            rows = cursor.fetchall()
            
            return rows

def get_specs_by_name(name: str) -> Optional[Dict]:
    """
    Get a product by its name.
    """
    pattern = f"%{name}%"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, specifications FROM products WHERE LOWER(name) = LOWER(%s)", (pattern,))
            rows = cursor.fetchall()
            
            return rows

 # Thử cả hai đuôi file
def get_valid_image_url(base_path, filename, extensions=['png', 'jpg']):
    for ext in extensions:
        image_path = f"{base_path}/{filename}.{ext}?raw=true".replace(" ", "%20")
        # Có thể thêm logic kiểm tra tồn tại của file ở đây
        return image_path
    return None  # Trả về None nếu không tìm thấy file nào

# def get_flexible_product_search(
#     names: List[str] = None,
#     price: float = 0,
#     addresses: List[str] = None,
#     use_address: bool = False,
#     information_products: List[str] = None,
#     use_specs: bool = False,
#     policies: List[str] = None,
#     use_policy: bool = False,
#     colors: List[str] = None,
#     capacities: List[str] = None,
#     sort_by: str = "",
#     limit: int = 0,
#     price_range: List[float] = None,
#     discount_percent: List[float] = None
# ) -> str:
#     """Flexible product search with multiple parameters and conditions.
#     Returns the complete SQL query with values substituted.
#     """
#     parameters = []

#     # Helper to add LIKE ANY conditions for a list of strings
#     def add_like_any(field: str, items: List[str]):
#         patterns = [f"%{item.lower()}%" for item in items]
#         placeholders = ", ".join([f"'{p}'" for p in patterns])
#         parameters.append(f"LOWER({field}) LIKE ANY (ARRAY[{placeholders}])")

#     # Process name list
#     if names:
#         add_like_any('name', names)

#     # Process list-based text fields with use flags
#     if addresses and use_address:
#         add_like_any('address', addresses)
#     if information_products and use_specs:
#         add_like_any('information_products::text', information_products)
#     if policies and use_policy:
#         add_like_any('policy', policies)
#     if colors:
#         add_like_any('color', colors)
#     if capacities:
#         add_like_any('capacity', capacities)

#     # Process exact price range
#     if price_range and len(price_range) == 2:
#         parameters.append(f"price BETWEEN {price_range[0]} AND {price_range[1]}")

#     # Process discount percent range
#     if discount_percent and len(discount_percent) == 2:
#         parameters.append(f"(original_price - price) / original_price * 100 BETWEEN {discount_percent[0]} AND {discount_percent[1]}")

#     # Build base query and WHERE clause
#     base_query = "SELECT * FROM products"
#     where_clause = f" WHERE {' AND '.join(parameters)}" if parameters else ''

#     # Determine order and limit for price proximity if price given
#     if price and price > 0:
#         # Order by absolute difference in price, closest first
#         order_clause = f" ORDER BY ABS(price - {price}) ASC"
#         # Always limit to top 20 nearest
#         limit_clause = " LIMIT 20"
#     else:
#         # Fallback to sort_by or no ordering
#         if sort_by == 'price_asc':
#             order_clause = ' ORDER BY price ASC'
#         elif sort_by == 'price_desc':
#             order_clause = ' ORDER BY price DESC'
#         else:
#             order_clause = ''
#         limit_clause = f' LIMIT {limit}' if limit and limit > 0 else ''

#     # Combine query
#     query = f"{base_query}{where_clause}{order_clause}{limit_clause}"

#     return query

# def get_flexible_product_search(
#     use_columns: List[str] = None,
#     name: List[str] = None,
#     price: float = 0,
#     capacity: List[str] = None,
#     color: List[str] = None,
#     policy: List[str] = None,
#     product_information: List[str] = None,
#     address: List[str] = None,
#     operator_flags: Dict[str, str] = None,
#     condition_groups: Dict[str, List[str]] = None,
#     group_operator: str = "AND",
#     price_range: List[float] = None,
#     discount_percent: List[float] = None,
#     sort_by: str = "",
#     limit: int = 0
# ) -> str:
#     # Initialize parameters
#     parameters = []
#     condition_groups = condition_groups or {}
#     operator_flags = operator_flags or {}

#     # Helper to add conditions for a list of strings with specified operator
#     def add_conditions(field: str, items: List[str], operator: str = "OR"):
#         if not items:
#             return

#         op = operator_flags.get(field, operator).upper()
#         patterns = [f"%{item.lower()}%" for item in items]
        
#         if op == "AND":
#             # Create individual LIKE conditions with values directly
#             conditions = [f"LOWER({field}) LIKE '{pattern}'" for pattern in patterns]
#             return f"({' AND '.join(conditions)})"
#         else:
#             # Use LIKE ANY with array of values directly
#             array_values = "ARRAY[" + ", ".join([f"'{p}'" for p in patterns]) + "]"
#             return f"LOWER({field}) LIKE ANY ({array_values})"

#     # Process condition groups
#     group_conditions = []
#     for group_name, group_fields in condition_groups.items():
#         field_conditions = []

#         for field in group_fields:
#             condition = None
#             if field == 'name' and name:
#                 condition = add_conditions('name', name)
#             elif field == 'capacity' and capacity:
#                 condition = add_conditions('capacity', capacity)
#             elif field == 'color' and color:
#                 condition = add_conditions('color', color)
#             elif field == 'policy' and policy:
#                 condition = add_conditions('policy', policy)
#             elif field == 'product_information' and product_information:
#                 condition = add_conditions('product_information', product_information)
#             elif field == 'address' and address:
#                 condition = add_conditions('address', address)

#             if condition:
#                 field_conditions.append(condition)

#         if field_conditions:
#             group_op = operator_flags.get(group_name, 'OR').upper()
#             group_conditions.append(f"({' ' + group_op + ' '.join(field_conditions)})")

#     # Process ungrouped conditions
#     used_fields = [f for fields in condition_groups.values() for f in fields]
    
#     if name and 'name' not in used_fields:
#         condition = add_conditions('name', name)
#         if condition:
#             parameters.append(condition)
#     if capacity and 'capacity' not in used_fields:
#         condition = add_conditions('capacity', capacity)
#         if condition:
#             parameters.append(condition)
#     if color and 'color' not in used_fields:
#         condition = add_conditions('color', color)
#         if condition:
#             parameters.append(condition)
#     if policy and 'policy' not in used_fields:
#         condition = add_conditions('policy', policy)
#         if condition:
#             parameters.append(condition)
#     if product_information and 'product_information' not in used_fields:
#         condition = add_conditions('product_information', product_information)
#         if condition:
#             parameters.append(condition)
#     if address and 'address' not in used_fields:
#         condition = add_conditions('address', address)
#         if condition:
#             parameters.append(condition)

#     # Process price and discount conditions
#     if price_range and len(price_range) == 2:
#         parameters.append(f"price BETWEEN {price_range[0]} AND {price_range[1]}")

#     if discount_percent and len(discount_percent) == 2:
#         parameters.append(f"(original_price - price) / original_price * 100 BETWEEN {discount_percent[0]} AND {discount_percent[1]}")

#     # Build base query
#     if use_columns:
#         base_query = f"SELECT {', '.join(use_columns)} FROM products"
#     else:
#         base_query = "SELECT name, capacity, color, price FROM products"

#     # Combine all conditions with group_operator
#     where_clause = ""
#     if parameters or group_conditions:
#         all_conditions = group_conditions + parameters
#         where_clause = f" WHERE {f' {group_operator} '.join(all_conditions)}"

#     # Determine order and limit for price proximity if price given
#     if price and price > 0:
#         order_clause = f" ORDER BY ABS(price - {price}) ASC"
#         limit_clause = " LIMIT 10"
#     else:
#         if sort_by == 'price_asc':
#             order_clause = ' ORDER BY price ASC'
#         elif sort_by == 'price_desc':
#             order_clause = ' ORDER BY price DESC'
#         else:
#             order_clause = ''
#         limit_clause = f' LIMIT {limit}' if limit and limit > 0 else ''

#     # Combine query
#     query = f"{base_query}{where_clause}{order_clause}{limit_clause}"

#     return query

def get_flexible_product_search(
    use_columns: List[str] = None,
    name: List[str] = None,
    price: float = 0,
    capacity: List[str] = None,
    color: List[str] = None,
    policy: List[str] = None,
    product_information: List[str] = None,
    address: List[str] = None,
    operator_flags: Dict[str, str] = None,
    condition_groups: Dict[str, List[str]] = None,
    group_operator: str = "AND",
    price_range: List[float] = None,
    discount_percent: List[float] = None,
    sort_by: str = "",
    limit: int = 0
) -> Optional[List[Dict]]:
    # Initialize parameters and values
    parameters = []
    values = []
    condition_groups = condition_groups or {}
    operator_flags = operator_flags or {}

    # Helper to add conditions for a list of strings with specified operator
    def add_conditions(field: str, items: List[str], operator: str = "OR"):
        if not items:
            return

        # Get operator from flags or use default
        op = operator_flags.get(field, operator).upper()
        
        # Generate patterns
        patterns = [f"%{item.lower()}%" for item in items]
        
        if op == "AND":
            # Create individual LIKE conditions joined by AND
            conditions = [f"LOWER({field}) LIKE %s" for _ in patterns]
            return f"({' AND '.join(conditions)})", patterns
        else:
            # Use LIKE ANY for OR conditions
            placeholders = ", ".join(["%s"] * len(patterns))
            return f"LOWER({field}) LIKE ANY (ARRAY[{placeholders}])", patterns

    # Process condition groups
    group_conditions = []
    for group_name, group_fields in condition_groups.items():
        field_conditions = []
        field_values = []

        for field in group_fields:
            if field == 'name' and name:
                condition, values_list = add_conditions('name', name)
                field_conditions.append(condition)
                field_values.extend(values_list)
            elif field == 'capacity' and capacity:
                condition, values_list = add_conditions('capacity', capacity)
                field_conditions.append(condition)
                field_values.extend(values_list)
            elif field == 'color' and color:
                condition, values_list = add_conditions('color', color)
                field_conditions.append(condition)
                field_values.extend(values_list)
            elif field == 'policy' and policy:
                condition, values_list = add_conditions('policy', policy)
                field_conditions.append(condition)
                field_values.extend(values_list)
            elif field == 'product_information' and product_information:
                condition, values_list = add_conditions('product_information', product_information)
                field_conditions.append(condition)
                field_values.extend(values_list)
            elif field == 'address' and address:
                condition, values_list = add_conditions('address', address)
                field_conditions.append(condition)
                field_values.extend(values_list)

        if field_conditions:
            group_op = operator_flags.get(group_name, 'OR').upper()
            group_conditions.append(f"({' ' + group_op + ' '.join(field_conditions)})")
            values.extend(field_values)

    # Process ungrouped conditions
    used_fields = [f for fields in condition_groups.values() for f in fields]
    
    if name and 'name' not in used_fields:
        condition, values_list = add_conditions('name', name)
        parameters.append(condition)
        values.extend(values_list)
    if capacity and 'capacity' not in used_fields:
        condition, values_list = add_conditions('capacity', capacity)
        parameters.append(condition)
        values.extend(values_list)
    if color and 'color' not in used_fields:
        condition, values_list = add_conditions('color', color)
        parameters.append(condition)
        values.extend(values_list)
    if policy and 'policy' not in used_fields:
        condition, values_list = add_conditions('policy', policy)
        parameters.append(condition)
        values.extend(values_list)
    if product_information and 'product_information' not in used_fields:
        condition, values_list = add_conditions('product_information', product_information)
        parameters.append(condition)
        values.extend(values_list)
    if address and 'address' not in used_fields:
        condition, values_list = add_conditions('address', address)
        parameters.append(condition)
        values.extend(values_list)

    # Process price and discount conditions
    if price_range and len(price_range) == 2:
        parameters.append("price BETWEEN %s AND %s")
        values.extend(price_range)

    if discount_percent and len(discount_percent) == 2:
        parameters.append("(original_price - price) / original_price * 100 BETWEEN %s AND %s")
        values.extend(discount_percent)

    # Build base query
    if use_columns:
        base_query = f"SELECT {', '.join(use_columns)} FROM products"
    else:
        base_query = "SELECT name, capacity, color, price, image_url, specifications FROM products"

    # Combine all conditions with group_operator
    where_clause = ""
    if parameters or group_conditions:
        all_conditions = group_conditions + parameters
        where_clause = f" WHERE {f' {group_operator} '.join(all_conditions)}"

    # Determine order and limit for price proximity if price given
    if price and price > 0:
        # Order by absolute difference in price, closest first
        order_clause = " ORDER BY ABS(price - %s) ASC"
        values.append(price)
        # Always limit to top 10 nearest
        limit_clause = " LIMIT 10"
    else:
        # Fallback to sort_by or no ordering
        if sort_by == 'price_asc':
            order_clause = ' ORDER BY price ASC'
        elif sort_by == 'price_desc':
            order_clause = ' ORDER BY price DESC'
        else:
            order_clause = ''
        limit_clause = f' LIMIT {limit}' if limit and limit > 0 else ''

    # Combine query
    query = f"{base_query}{where_clause}{order_clause}{limit_clause}"

    # Execute and post-process
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(values))
            rows = cursor.fetchall()

    # Format results
    for row in rows:
        # Clean capacity if unit missing
        cap = row.get('capacity', '')
        if cap and not any(unit in cap for unit in ['MB', 'GB', 'TB']):
            row.pop('capacity', None)

        if row.get("product_information", ""):
            row.pop("product_information", None)

        # Format prices
        price = row.get('price', '')
        if price:
            row['price'] = format_currency_vn(row['price'])
        
        if 'original_price' in row:
            row['original_price'] = format_currency_vn(row['original_price'])

        # Build image URLs per color
        image_path = row.get('image_url', '')
        if image_path:
            image_path = image_path.split(",")[0]
            row['image_url'] = f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/{image_path}?raw=true".replace(" ", "%20")
        # color_list = [c.strip() for c in row.get('color', '').split(',') if c.strip()]
        # base_img = row.get('image_url', '')
        # row['image_url'] = [
        #     (
        #         f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/"
        #         f"{base_img}/{slugify(c)}/{c}.png?raw=true".replace(' ', '%20')
        #     )
        #     for c in color_list
        # ]

    return rows

# def get_flexible_product_search(
#     use_columns: List[str] = None,
#     names: List[str] = None,
#     price: float = 0,
#     capabilities: List[str] = None,
#     colors: List[str] = None,
#     policies: List[str] = None,
#     product_information: List[str] = None,
#     addresses: List[str] = None,
#     operator_flags: Dict[str, str] = None,
#     price_range: List[float] = None,
#     discount_percent: List[float] = None,
#     sort_by: str = "",
#     limit: int = 0
# ) -> Optional[List[Dict]]:
#     """
#     Flexible product search with multiple parameters and conditions,
#     including fetching 10 products closest in price to the target.
#     """
#     # Initialize parameters and values
#     parameters = []
#     values = []

#     # Helper to add LIKE ANY conditions for a list of strings
#     def add_like_any(field: str, items: List[str]):
#         patterns = [f"%{item.lower()}%" for item in items]
#         placeholders = ", ".join(["%s"] * len(patterns))
#         parameters.append(f"LOWER({field}) LIKE ANY (ARRAY[{placeholders}])")
#         values.extend(patterns)

#     # Process name list
#     if names:
#         add_like_any('name', names)
    
#     if capabilities:
#         add_like_any('capacity', capabilities)
    
#     if colors:
#         add_like_any('color', colors)

#     if policies:
#         add_like_any('policy', policies)

#     if product_information:
#         add_like_any('product_information', product_information)

#     # Process list-based text fields
#     if addresses:
#         add_like_any('address', addresses)
    
#     # Process exact price range
#     if price_range and len(price_range) == 2:
#         parameters.append("price BETWEEN %s AND %s")
#         values.extend(price_range)

#     # Process discount percent range
#     if discount_percent and len(discount_percent) == 2:
#         parameters.append("(original_price - price) / original_price * 100 BETWEEN %s AND %s")
#         values.extend(discount_percent)

#     # Build base query and WHERE clause
#     if use_columns :
#         base_query = f"SELECT {', '.join(use_columns)} FROM products"
#     else:
#         base_query = "SELECT * FROM products"
    
#     where_clause = f" WHERE {' AND '.join(parameters)}" if parameters else ''

#     # Determine order and limit for price proximity if price given
#     if price and price > 0:
#         # Order by absolute difference in price, closest first
#         order_clause = " ORDER BY ABS(price - %s) ASC"
#         values.append(price)
#         # Always limit to top 10 nearest
#         limit_clause = " LIMIT 10"
#     else:
#         # Fallback to sort_by or no ordering
#         if sort_by == 'price_asc':
#             order_clause = ' ORDER BY price ASC'
#         elif sort_by == 'price_desc':
#             order_clause = ' ORDER BY price DESC'
#         else:
#             order_clause = ''
#         limit_clause = f' LIMIT {limit}' if limit and limit > 0 else ''

#     # Combine query
#     query = f"{base_query}{where_clause}{order_clause}{limit_clause}"

#     # Execute and post-process
#     with get_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(query, tuple(values))
#             rows = cursor.fetchall()

#     # Format results
#     for row in rows:
#         # Clean capacity if unit missing
#         cap = row.get('capacity', '')
#         if cap and not any(unit in cap for unit in ['MB', 'GB', 'TB']):
#             row.pop('capacity', None)

#         # Format prices
#         price = row.get('price', '')
#         if price:
#             row['price'] = format_currency_vn(row['price'])
        
#         if 'original_price' in row:
#             row['original_price'] = format_currency_vn(row['original_price'])

#         # Build image URLs per color
#         image_path = row.get('image_url', '')
#         if image_path:
#             row['image_url'] = f"https://github.com/Dat-ABC/share-host-files/tree/main/product_images/{image_path}?raw=true".replace(" ", "%20")
#         # color_list = [c.strip() for c in row.get('color', '').split(',') if c.strip()]
#         # base_img = row.get('image_url', '')
#         # row['image_url'] = [
#         #     (
#         #         f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/"
#         #         f"{base_img}/{slugify(c)}/{c}.png?raw=true".replace(' ', '%20')
#         #     )
#         #     for c in color_list
#         # ]

#     return rows


# def get_flexible_product_search(name: str = "", price: float = 0, address: str = "", specs: str = "", policy: str = "") -> Optional[Dict]:
#     """
#     Get a product by its name.
#     """
#     # Kiểm tra và xử lý các tham số
#     print(name, price, address, specs, policy)
#     name = name if name else None
#     price = float(price) if price else None
#     address = address if address else None
#     specs = specs if specs else None
#     policy = policy if policy else None

#     # Tính toán khoảng giá chỉ khi có giá
#     price_range_min = price - 500000 if price is not None else None
#     price_range_max = price + 500000 if price is not None else None

#     parameters = []
#     if name:
#         parameters.append(f"LOWER(name) LIKE LOWER(%s)")
#     if price:
#         parameters.append("price BETWEEN %s AND %s")
#     if address:
#         parameters.append(f"LOWER(address) LIKE LOWER(%s)")
#     if specs:
#         parameters.append(f"LOWER(specifications::text) LIKE LOWER(%s)")
#     if policy:
#         parameters.append(f"LOWER(policy) LIKE LOWER(%s)")
#     if not parameters:
#         return None
    
#     # Tạo câu truy vấn SQL
#     query = "SELECT * FROM products WHERE " + " AND ".join(parameters)

#     # Tạo danh sách giá trị
#     values = []
#     if name:
#         values.append(f"%{name}%")
#     if price:
#         values.extend([price_range_min, price_range_max])
#     if address:
#         values.append(f"%{address}%")
#     if specs:
#         values.append(f"%{specs}%")
#     if policy:
#         values.append(f"%{policy}%")

#     # Thực hiện truy vấn
#     with get_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(query, tuple(values))
#             rows = cursor.fetchall()
#             if rows:
#                 for row in rows:
#                     if not any(unit in row['capacity'] for unit in ['MB', 'GB', 'TB']):
#                         row.pop('capacity', None)
                    
#                     if not address:
#                         row.pop('address', None)
#                     if not specs:
#                         row.pop('specifications', None)
#                     if not policy:
#                         row.pop('policy', None)

#                     row['price'] = format_currency_vn(row['price'])

#                     # Lấy danh sách các màu từ cột color
#                     colors = row['color'].strip().split(",")
#                     image_url = row['image_url']
#                     row['image_url'] = []
#                     for color in colors:
#                         color = color.strip()
#                         image_path = f"https://raw.githubusercontent.com/Dat-ABC/share-host-files/main/product_images/{image_url}/{slugify(color)}/{color}.png?raw=true".replace(" ", "%20")
#                         row['image_url'].append(image_path)

#             return rows