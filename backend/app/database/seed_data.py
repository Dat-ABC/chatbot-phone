from app.database.chat_history_service import get_connection
from app.database.product_service import create_product_table
from app.database.chat_history_service import create_chat_history_table
import pandas as pd
import re
from decimal import InvalidOperation

def clean_price(value):
    if pd.isnull(value):
        return None
    # Loại bỏ tất cả các ký tự không phải số và dấu chấm
    cleaned_value = re.sub(r'[^\d.]', '', str(value))
    try:
        return int(cleaned_value)
    except InvalidOperation:
        return None

def prepare_data():
    # Đọc dữ liệu từ file CSV
    df = pd.read_csv('app/database/hoanghamobile_products.csv')

    # 1. Kết hợp các cột
    # Tạo Series để lưu các mô tả
    descriptions = {
        'exclusively_for_Hoang_Ha_members': 'Ưu đãi dành riêng cho thành viên Hoàng Hà:\n',
        'new_customer_offer': 'Ưu đãi cho khách hàng mới:\n',
        'installment': 'Thông tin trả góp:\n',
        'hoang_ha_offers': 'Ưu đãi từ Hoàng Hà:\n',
        'other_information': 'Thông tin khác:\n',
        'additional_offers': 'Ưu đãi bổ sung:\n'
    }
    
    # Xử lý từng dòng
    for index, row in df.iterrows():
        row_policies = []
        for col, desc in descriptions.items():
            if pd.notna(row[col]) and str(row[col]).strip().lower() != 'nan':
                row_policies.append(desc + str(row[col]))
        df.at[index, 'policy'] = '\n'.join(row_policies)
    
    # 2. Kết hợp các cột specs
    product_descriptions = {
        'specs': 'Thông số kỹ thuật:\n',
        'product_information': 'Thông tin sản phẩm:\n'
    }
    
    # Xử lý từng dòng cho thông tin sản phẩm
    for index, row in df.iterrows():
        row_info = []
        for col, desc in product_descriptions.items():
            if pd.notna(row[col]) and str(row[col]).strip().lower() != 'nan':
                row_info.append(desc + str(row[col]))
        df.at[index, 'product_information'] = '\n'.join(row_info)

    # policy_columns = []
    
    # # Chỉ thêm thông tin cho cột có dữ liệu
    # if not df['exclusively_for_Hoang_Ha_members'].isna().all():
    #     policy_columns.append('Ưu đãi dành riêng cho thành viên Hoàng Hà:\n' + df['exclusively_for_Hoang_Ha_members'].fillna(''))
    
    # if not df['new_customer_offer'].isna().all():
    #     policy_columns.append('Ưu đãi cho khách hàng mới:\n' + df['new_customer_offer'].fillna(''))
    
    # if not df['installment'].isna().all():
    #     policy_columns.append('Thông tin trả góp:\n' + df['installment'].fillna(''))
    
    # if not df['hoang_ha_offers'].isna().all():
    #     policy_columns.append('Ưu đãi từ Hoàng Hà:\n' + df['hoang_ha_offers'].fillna(''))
    
    # if not df['other_information'].isna().all():
    #     policy_columns.append('Thông tin khác:\n' + df['other_information'].fillna(''))
    
    # if not df['additional_offers'].isna().all():
    #     policy_columns.append('Ưu đãi bổ sung:\n' + df['additional_offers'].fillna(''))
    
    # df['policy'] = pd.Series(['\n'.join(row) for row in zip(*policy_columns)]).str.strip()
    # # 2. Kết hợp các cột specs

    # # df['product_information'] = (
    # #     df['specs'].fillna('') + '\n' +
    # #     df['product_information'].fillna('')
    # # )

    # product_info_columns = []
    
    # # Chỉ thêm thông tin cho cột có dữ liệu
    # if not df['specs'].isna().all():
    #     product_info_columns.append('Thông số kỹ thuật:\n' + df['specs'].fillna(''))
    
    # if not df['product_information'].isna().all():
    #     product_info_columns.append('Thông tin sản phẩm:\n' + df['product_information'].fillna(''))
    
    # df['product_information'] = pd.Series(['\n'.join(row) for row in zip(*product_info_columns)]).str.strip()
    
    # 2. Đổi tên cột để khớp bảng products
    df_renamed = df.rename(columns={
        'current_price': 'price',
        'original_price': 'original_price',
        'colors': 'color',
        'specs': 'specifications',
        'address_available': 'address'
    })[['name', 'color', 'capacity', 'price', 'original_price',
        'policy', 'specifications', 'address', 'image_url', 'product_information']]
    
    # df_renamed['price'] = df_renamed['price'].apply(clean_price)
    # df_renamed['original_price'] = df_renamed['original_price'].apply(clean_price)
    
    # df_renamed['price'] = df_renamed['price'].apply(lambda x: Decimal(str(x)) if pd.notnull(x) else None)
    # df_renamed['original_price'] = df_renamed['original_price'].apply(lambda x: Decimal(str(x)) if pd.notnull(x) else None)
    
    return df_renamed

def seed_data_to_database():
    # Tạo bảng products nếu chưa tồn tại
    create_product_table()
    create_chat_history_table()

    # Chuẩn bị dữ liệu
    df_renamed = prepare_data()

    # Kết nối đến cơ sở dữ liệu và xử lý transaction
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        insert_sql = """
            INSERT INTO products
            (name, color, capacity, price, original_price,
             policy, specifications, address, image_url, product_information)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """
        for index, row in df_renamed.iterrows():
            cur.execute(insert_sql, tuple(row))
        print(f"Inserted {len(df_renamed)} rows into products table.")
        
        conn.commit()
        print("Database seeded successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Tạo bảng và chèn dữ liệu
    seed_data_to_database()