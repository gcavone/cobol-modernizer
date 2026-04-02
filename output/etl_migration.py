# etl_migration.py
"""
Script ETL per migrare dati da file COBOL a PostgreSQL.

Flusso:
1. Legge DATABASE.txt (formato COBOL 60 caratteri)
2. Legge products.txt (formato più pulito)
3. Deduplica e valida
4. Inserisce in PostgreSQL
5. Genera report
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Legge dal .env se disponibile
_db_url = os.getenv("DATABASE_URL", "")
if _db_url:
    import re
    m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)", _db_url)
    if m:
        _user, _pw, _host, _port, _db = m.groups()
    else:
        _user, _pw, _host, _port, _db = "supermarket_user", "supermarket_pass", "localhost", "5432", "supermarket_db"
else:
    _user    = os.getenv("DB_USER", "supermarket_user")
    _pw      = os.getenv("DB_PASSWORD", "supermarket_pass")
    _host    = os.getenv("DB_HOST", "localhost")
    _port    = os.getenv("DB_PORT", "5432")
    _db      = os.getenv("DB_NAME", "supermarket_db")

import re
import logging
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

# ============================================================================
# CONFIGURAZIONE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAZIONE DATABASE
# ============================================================================

DB_CONFIG = {
    'host': _host,
    'port': int(_port),
    'database': _db,
    'user': _user,
    'password': _pw
}

# ============================================================================
# CLASSI DATI
# ============================================================================

class Product:
    """Rappresenta un prodotto"""
    
    def __init__(self, code: str, name: str, unit: str, price: Decimal):
        self.code = code.strip()
        self.name = name.strip()
        self.unit = unit.strip()
        self.price = price
    
    def validate(self) -> Tuple[bool, str]:
        """Valida il prodotto"""
        # Codice
        if not self.code or len(self.code) != 8:
            return False, f"Invalid code: {self.code}"
        
        if not self.code.isdigit():
            return False, f"Code must be numeric: {self.code}"
        
        # Nome
        if not self.name or len(self.name) < 2:
            return False, f"Name too short: {self.name}"
        
        if len(self.name) > 100:
            return False, f"Name too long: {self.name}"
        
        # Unità
        if not self.unit or len(self.unit) < 1:
            return False, f"Unit missing: {self.unit}"
        
        if len(self.unit) > 20:
            return False, f"Unit too long: {self.unit}"
        
        # Prezzo
        if self.price <= 0:
            return False, f"Price must be positive: {self.price}"
        
        if self.price > 999999.99:
            return False, f"Price too high: {self.price}"
        
        return True, "OK"
    
    def __repr__(self):
        return f"Product(code={self.code}, name={self.name}, price={self.price})"

# ============================================================================
# PARSER COBOL
# ============================================================================

class CobolParser:
    """Parsa file COBOL in formato record fisso 60 caratteri"""
    
    # Posizioni campi (1-based in COBOL, 0-based in Python)
    PCODE_START = 0
    PCODE_END = 8
    PNAME_START = 8
    PNAME_END = 45
    UNIT_START = 45
    UNIT_END = 52
    PRICE_START = 52
    PRICE_END = 60
    
    @staticmethod
    def parse_price(price_str: str) -> Decimal:
        """
        Parsa prezzo da formato COBOL.
        
        Formato: 8 cifre con decimali impliciti
        Esempi:
        - "00001875" → 18.75
        - "00007000" → 70.00
        - "00000725" → 7.25
        """
        price_str = price_str.strip()
        
        # Se vuoto, ritorna None
        if not price_str:
            return None
        
        # Se contiene lettere, è malformato
        if not price_str.isdigit():
            logger.warning(f"Non-numeric price: {price_str}")
            return None
        
        # Se ha meno di 4 cifre, è incompleto
        if len(price_str) < 4:
            logger.warning(f"Price too short: {price_str}")
            return None
        
        try:
            # Converti a intero
            price_int = int(price_str)
            
            # Dividi per 100 per ottenere decimali
            price_decimal = Decimal(price_int) / Decimal(100)
            
            return price_decimal
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing price {price_str}: {e}")
            return None
    
    @staticmethod
    def parse_record(line: str) -> Product:
        """
        Parsa una riga di 60 caratteri in un Product.
        
        Formato:
        - Posizioni 1-8: PCODE (8 cifre)
        - Posizioni 9-45: PNAME (37 caratteri)
        - Posizioni 46-52: UNIT (7 caratteri)
        - Posizioni 53-60: PRICE (8 cifre)
        """
        # Valida lunghezza
        if len(line) < 60:
            logger.warning(f"Record too short ({len(line)} chars): {line}")
            return None
        
        try:
            # Estrai campi
            code = line[CobolParser.PCODE_START:CobolParser.PCODE_END]
            name = line[CobolParser.PNAME_START:CobolParser.PNAME_END]
            unit = line[CobolParser.UNIT_START:CobolParser.UNIT_END]
            price_str = line[CobolParser.PRICE_START:CobolParser.PRICE_END]
            
            # Parsa prezzo
            price = CobolParser.parse_price(price_str)
            if price is None:
                logger.warning(f"Invalid price in record: {line}")
                return None
            
            # Crea Product
            product = Product(code, name, unit, price)
            
            # Valida
            is_valid, msg = product.validate()
            if not is_valid:
                logger.warning(f"Invalid product: {msg}")
                return None
            
            return product
        
        except Exception as e:
            logger.error(f"Error parsing record: {line} - {e}")
            return None

# ============================================================================
# PARSER CSV (per products.txt)
# ============================================================================

class CsvParser:
    """Parsa file CSV (products.txt)"""
    
    @staticmethod
    def parse_line(line: str) -> Product:
        """
        Parsa una riga di products.txt.
        
        Formato: PCODE PNAME UNIT PRICE (separati da spazi)
        Esempio: 00000001 Canned Sardines                     155g   18.75
        """
        parts = line.split()
        
        if len(parts) < 4:
            logger.warning(f"Invalid CSV line (too few fields): {line}")
            return None
        
        try:
            code = parts[0]
            # Nome è tutto tra il codice e l'unità (ultimi 2 campi)
            unit = parts[-2]
            price_str = parts[-1]
            name = ' '.join(parts[1:-2])
            
            # Parsa prezzo
            try:
                price = Decimal(price_str)
            except:
                logger.warning(f"Invalid price: {price_str}")
                return None
            
            # Crea Product
            product = Product(code, name, unit, price)
            
            # Valida
            is_valid, msg = product.validate()
            if not is_valid:
                logger.warning(f"Invalid product: {msg}")
                return None
            
            return product
        
        except Exception as e:
            logger.error(f"Error parsing CSV line: {line} - {e}")
            return None

# ============================================================================
# ETL PROCESSOR
# ============================================================================

class EtlProcessor:
    """Processa i dati e li inserisce in PostgreSQL"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}  # code -> Product
        self.duplicates = 0
        self.invalid = 0
        self.valid = 0
    
    def load_database_txt(self, filepath: str) -> int:
        """Carica DATABASE.txt (formato COBOL)"""
        logger.info(f"Loading DATABASE.txt from {filepath}")
        
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Salta linee vuote
                    if not line.strip():
                        continue
                    
                    # Salta record incompleti (es. "2")
                    if len(line.strip()) < 20:
                        logger.warning(f"Line {line_num}: Record too short, skipping")
                        continue
                    
                    # Parsa record
                    product = CobolParser.parse_record(line)
                    if product is None:
                        self.invalid += 1
                        continue
                    
                    # Deduplica
                    if product.code in self.products:
                        logger.debug(f"Duplicate product code: {product.code}")
                        self.duplicates += 1
                        continue
                    
                    # Aggiungi
                    self.products[product.code] = product
                    self.valid += 1
                    count += 1
        
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return 0
        
        logger.info(f"Loaded {count} valid products from DATABASE.txt")
        logger.info(f"Duplicates: {self.duplicates}, Invalid: {self.invalid}")
        
        return count
    
    def load_products_txt(self, filepath: str) -> int:
        """Carica products.txt (formato CSV) come fallback"""
        logger.info(f"Loading products.txt from {filepath}")
        
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Salta linee vuote
                    if not line.strip():
                        continue
                    
                    # Parsa record
                    product = CsvParser.parse_line(line)
                    if product is None:
                        self.invalid += 1
                        continue
                    
                    # Se il codice non esiste già, aggiungilo
                    if product.code not in self.products:
                        self.products[product.code] = product
                        self.valid += 1
                        count += 1
                    else:
                        logger.debug(f"Product {product.code} already loaded from DATABASE.txt")
        
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return 0
        
        logger.info(f"Loaded {count} additional products from products.txt")
        
        return count
    
    def insert_into_postgresql(self) -> bool:
        """Inserisce prodotti in PostgreSQL"""
        logger.info(f"Inserting {len(self.products)} products into PostgreSQL")
        
        try:
            # Connetti al database
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Prepara dati
            data = [
                (p.code, p.name, p.unit, float(p.price))
                for p in self.products.values()
            ]
            
            # Inserisci con ON CONFLICT per gestire duplicati
            query = """
                INSERT INTO products (code, name, unit, price)
                VALUES %s
                ON CONFLICT (code) DO UPDATE
                SET name = EXCLUDED.name,
                    unit = EXCLUDED.unit,
                    price = EXCLUDED.price,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            execute_values(cursor, query, data)
            conn.commit()
            
            logger.info(f"Successfully inserted {len(data)} products")
            
            cursor.close()
            conn.close()
            
            return True
        
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def generate_report(self) -> str:
        """Genera report della migrazione"""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║           MIGRATION REPORT - PRODUCTS                      ║
╚════════════════════════════════════════════════════════════╝

Total Products Loaded:     {self.valid}
Duplicates Removed:        {self.duplicates}
Invalid Records:           {self.invalid}

Products by Price Range:
  < 10.00 PHP:             {sum(1 for p in self.products.values() if p.price < 10)}
  10.00 - 50.00 PHP:       {sum(1 for p in self.products.values() if 10 <= p.price <= 50)}
  50.00 - 100.00 PHP:      {sum(1 for p in self.products.values() if 50 < p.price <= 100)}
  > 100.00 PHP:            {sum(1 for p in self.products.values() if p.price > 100)}

Sample Products:
"""
        for i, product in enumerate(list(self.products.values())[:5], 1):
            report += f"  {i}. {product.code} | {product.name:30} | {product.unit:10} | PHP {product.price}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Esegue la migrazione"""
    logger.info("="*60)
    logger.info("STARTING ETL MIGRATION: COBOL → PostgreSQL")
    logger.info("="*60)
    
    # Crea processor
    processor = EtlProcessor()
    
    # Carica dati
    processor.load_database_txt('DATABASE.txt')
    processor.load_products_txt('products.txt')
    
    # Inserisci in PostgreSQL
    success = processor.insert_into_postgresql()
    
    # Genera report
    report = processor.generate_report()
    print(report)
    logger.info(report)
    
    if success:
        logger.info("✓ Migration completed successfully!")
    else:
        logger.error("✗ Migration failed!")
    
    logger.info("="*60)

if __name__ == "__main__":
    main()
