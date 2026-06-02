import sqlite3
from typing import List, Optional, Dict, Any

class ProductDatabase:
    """SQLite를 사용한 제품 관리 클래스"""
    
    def __init__(self, db_name: str = "products.db"):
        """데이터베이스 연결 초기화"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()
    
    def connect(self) -> None:
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print(f"✓ 데이터베이스 '{self.db_name}'에 연결되었습니다.")
    
    def create_table(self) -> None:
        """Products 테이블 생성"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Products (
            productID INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            productPrice INTEGER NOT NULL,
            productStock INTEGER DEFAULT 0,
            productCategory TEXT,
            createdDate TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()
        print("✓ Products 테이블이 준비되었습니다.")
    
    def insert_product(self, product_name: str, product_price: int, 
                      product_stock: int = 0, product_category: str = None) -> int:
        """
        새 제품 추가
        
        Args:
            product_name: 제품 이름
            product_price: 제품 가격
            product_stock: 재고 수량 (기본값: 0)
            product_category: 제품 카테고리
            
        Returns:
            삽입된 제품의 ID
        """
        insert_query = """
        INSERT INTO Products (productName, productPrice, productStock, productCategory)
        VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(insert_query, (product_name, product_price, product_stock, product_category))
        self.conn.commit()
        product_id = self.cursor.lastrowid
        print(f"✓ 제품 '{product_name}'이(가) 추가되었습니다. (ID: {product_id})")
        return product_id
    
    def search_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        ID로 제품 검색
        
        Args:
            product_id: 검색할 제품 ID
            
        Returns:
            제품 정보 딕셔너리 또는 None
        """
        search_query = "SELECT * FROM Products WHERE productID = ?"
        self.cursor.execute(search_query, (product_id,))
        row = self.cursor.fetchone()
        
        if row:
            return {
                'productID': row[0],
                'productName': row[1],
                'productPrice': row[2],
                'productStock': row[3],
                'productCategory': row[4],
                'createdDate': row[5]
            }
        return None
    
    def search_by_name(self, product_name: str) -> List[Dict[str, Any]]:
        """
        이름으로 제품 검색 (부분 일치)
        
        Args:
            product_name: 검색할 제품 이름
            
        Returns:
            제품 정보 리스트
        """
        search_query = "SELECT * FROM Products WHERE productName LIKE ?"
        self.cursor.execute(search_query, (f"%{product_name}%",))
        rows = self.cursor.fetchall()
        
        products = []
        for row in rows:
            products.append({
                'productID': row[0],
                'productName': row[1],
                'productPrice': row[2],
                'productStock': row[3],
                'productCategory': row[4],
                'createdDate': row[5]
            })
        return products
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        모든 제품 조회
        
        Returns:
            모든 제품 정보 리스트
        """
        select_query = "SELECT * FROM Products ORDER BY productID"
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()
        
        products = []
        for row in rows:
            products.append({
                'productID': row[0],
                'productName': row[1],
                'productPrice': row[2],
                'productStock': row[3],
                'productCategory': row[4],
                'createdDate': row[5]
            })
        return products
    
    def update_product(self, product_id: int, product_name: str = None, 
                      product_price: int = None, product_stock: int = None,
                      product_category: str = None) -> bool:
        """
        제품 정보 수정
        
        Args:
            product_id: 수정할 제품 ID
            product_name: 새 제품 이름 (선택)
            product_price: 새 제품 가격 (선택)
            product_stock: 새 재고 수량 (선택)
            product_category: 새 제품 카테고리 (선택)
            
        Returns:
            성공 여부
        """
        # 먼저 제품이 존재하는지 확인
        if not self.search_by_id(product_id):
            print(f"✗ ID {product_id}인 제품을 찾을 수 없습니다.")
            return False
        
        # 업데이트할 필드만 구성
        updates = []
        params = []
        
        if product_name is not None:
            updates.append("productName = ?")
            params.append(product_name)
        if product_price is not None:
            updates.append("productPrice = ?")
            params.append(product_price)
        if product_stock is not None:
            updates.append("productStock = ?")
            params.append(product_stock)
        if product_category is not None:
            updates.append("productCategory = ?")
            params.append(product_category)
        
        if not updates:
            print("✗ 수정할 정보가 없습니다.")
            return False
        
        params.append(product_id)
        update_query = f"UPDATE Products SET {', '.join(updates)} WHERE productID = ?"
        self.cursor.execute(update_query, params)
        self.conn.commit()
        print(f"✓ ID {product_id}인 제품이 수정되었습니다.")
        return True
    
    def delete_product(self, product_id: int) -> bool:
        """
        제품 삭제
        
        Args:
            product_id: 삭제할 제품 ID
            
        Returns:
            성공 여부
        """
        # 먼저 제품이 존재하는지 확인
        product = self.search_by_id(product_id)
        if not product:
            print(f"✗ ID {product_id}인 제품을 찾을 수 없습니다.")
            return False
        
        delete_query = "DELETE FROM Products WHERE productID = ?"
        self.cursor.execute(delete_query, (product_id,))
        self.conn.commit()
        print(f"✓ ID {product_id}인 제품 '{product['productName']}'이(가) 삭제되었습니다.")
        return True
    
    def display_products(self, products: List[Dict[str, Any]] = None) -> None:
        """
        제품 목록을 보기 좋게 출력
        
        Args:
            products: 출력할 제품 리스트 (None이면 모든 제품)
        """
        if products is None:
            products = self.get_all_products()
        
        if not products:
            print("✗ 제품이 없습니다.")
            return
        
        print("\n" + "="*100)
        print(f"{'ID':<5} {'제품명':<20} {'가격':<10} {'재고':<8} {'카테고리':<15} {'생성일':<20}")
        print("="*100)
        
        for product in products:
            print(f"{product['productID']:<5} {product['productName']:<20} "
                  f"{product['productPrice']:<10} {product['productStock']:<8} "
                  f"{str(product['productCategory']):<15} {product['createdDate']:<20}")
        
        print("="*100 + "\n")
    
    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            print("✓ 데이터베이스 연결이 종료되었습니다.")


# 사용 예제
if __name__ == "__main__":
    # 데이터베이스 초기화
    db = ProductDatabase("products.db")
    
    print("\n" + "="*50)
    print("1. 제품 추가 테스트")
    print("="*50)
    
    # 제품 추가
    db.insert_product("노트북", 1500000, 10, "전자제품")
    db.insert_product("마우스", 50000, 20, "전자제품")
    db.insert_product("키보드", 80000, 15, "전자제품")
    db.insert_product("모니터", 300000, 8, "전자제품")
    db.insert_product("USB 허브", 35000, 25, "액세서리")
    
    print("\n" + "="*50)
    print("2. 모든 제품 조회")
    print("="*50)
    db.display_products()
    
    print("\n" + "="*50)
    print("3. ID로 제품 검색 (ID=2)")
    print("="*50)
    product = db.search_by_id(2)
    if product:
        print(f"제품 찾음: {product}")
    
    print("\n" + "="*50)
    print("4. 이름으로 제품 검색 ('노트북')")
    print("="*50)
    products = db.search_by_name("노트북")
    db.display_products(products)
    
    print("\n" + "="*50)
    print("5. 제품 정보 수정 (ID=1: 가격 수정)")
    print("="*50)
    db.update_product(1, product_price=1400000, product_stock=12)
    product = db.search_by_id(1)
    if product:
        print(f"수정된 제품: {product}")
    
    print("\n" + "="*50)
    print("6. 제품 삭제 (ID=5)")
    print("="*50)
    db.delete_product(5)
    
    print("\n" + "="*50)
    print("7. 최종 제품 목록")
    print("="*50)
    db.display_products()
    
    # 데이터베이스 연결 종료
    db.close()
