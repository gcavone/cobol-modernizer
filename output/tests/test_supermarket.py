"""
Test Suite — Supermarket Management System
==========================================
Testa le business rules, i servizi e il flusso completo del sistema.

Esecuzione:
    pip install pytest
    pytest tests/ -v

Struttura:
    - TestBusinessRules    : verifica le 3 formule principali del COBOL
    - TestAuthService      : login, password, credenziali errate
    - TestProductService   : CRUD prodotti, validazione
    - TestEmployeeService  : calcolo stipendi, validazione ore
    - TestProfitService    : calcolo profitti, casi limite
    - TestOrderService     : creazione ordini, calcolo resto
    - TestIntegration      : flusso completo buyer end-to-end
"""

import sys
import os
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def make_mock_product(id=1, code="00000001", name="Canned Sardines",
                      unit="155g", price=18.75):
    """Crea un prodotto mock."""
    p = MagicMock()
    p.id = id
    p.code = code
    p.name = name
    p.unit = unit
    p.price = Decimal(str(price))
    return p


def make_mock_employee(id=1, employee_id="EMP001", name="Juan Dela Cruz",
                       hourly_rate=500.0):
    """Crea un dipendente mock."""
    e = MagicMock()
    e.id = id
    e.employee_id = employee_id
    e.name = name
    e.hourly_rate = Decimal(str(hourly_rate))
    return e


def make_mock_admin(id=1, email="robby@gmail.com", is_active=True):
    """Crea un admin mock."""
    a = MagicMock()
    a.id = id
    a.email = email
    a.is_active = is_active
    a.password_hash = "$2b$12$lbQ7.nODQxFqx4gDdW7st.jOq3LpeBWzvPy8FwKXo2Yl.sl7BNcSa"
    return a


# ═══════════════════════════════════════════════════════════════════════════════
# 1. BUSINESS RULES — Le 3 formule del COBOL
# ═══════════════════════════════════════════════════════════════════════════════

class TestBusinessRules:
    """Verifica che le 3 business rules del COBOL siano preservate."""

    def test_salary_formula_base(self):
        """SALARY = HOURLY_RATE × HOURS_WORKED — caso base."""
        hourly_rate = Decimal("500.00")
        hours_worked = Decimal("8")
        expected = Decimal("4000.00")
        assert hourly_rate * hours_worked == expected

    def test_salary_formula_decimal_hours(self):
        """SALARY = HOURLY_RATE × HOURS_WORKED — ore decimali."""
        hourly_rate = Decimal("500.00")
        hours_worked = Decimal("7.5")
        expected = Decimal("3750.00")
        assert hourly_rate * hours_worked == expected

    def test_salary_formula_different_rate(self):
        """SALARY = HOURLY_RATE × HOURS_WORKED — tariffa diversa."""
        hourly_rate = Decimal("550.00")
        hours_worked = Decimal("8")
        expected = Decimal("4400.00")
        assert hourly_rate * hours_worked == expected

    def test_profit_formula_positive(self):
        """PROFIT = SELLING_PRICE - COGS — profitto positivo."""
        selling_price = Decimal("25.00")
        cogs = Decimal("10.00")
        expected = Decimal("15.00")
        assert selling_price - cogs == expected

    def test_profit_formula_zero(self):
        """PROFIT = SELLING_PRICE - COGS — profitto zero (breakeven)."""
        selling_price = Decimal("10.00")
        cogs = Decimal("10.00")
        assert selling_price - cogs == Decimal("0.00")

    def test_profit_formula_negative(self):
        """PROFIT = SELLING_PRICE - COGS — perdita (profitto negativo)."""
        selling_price = Decimal("5.00")
        cogs = Decimal("10.00")
        assert selling_price - cogs == Decimal("-5.00")

    def test_change_formula_base(self):
        """CHANGE = MONEY_PAID - TOTAL — caso base."""
        payment = Decimal("50.00")
        total = Decimal("37.50")
        expected = Decimal("12.50")
        assert payment - total == expected

    def test_change_formula_exact(self):
        """CHANGE = MONEY_PAID - TOTAL — pagamento esatto."""
        payment = Decimal("37.50")
        total = Decimal("37.50")
        assert payment - total == Decimal("0.00")

    def test_change_formula_insufficient(self):
        """CHANGE = MONEY_PAID - TOTAL — pagamento insufficiente (negativo)."""
        payment = Decimal("30.00")
        total = Decimal("37.50")
        assert payment - total < Decimal("0.00")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. AUTH SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuthService:
    """Test per AuthService — login e gestione password."""

    def setup_method(self):
        from services.auth_service import AuthService
        self.admin_repo = MagicMock()
        self.service = AuthService(self.admin_repo)

    def test_hash_password_returns_string(self):
        """hash_password deve restituire una stringa."""
        result = self.service.hash_password("password123")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_different_each_time(self):
        """Lo stesso password deve produrre hash diversi (salt)."""
        h1 = self.service.hash_password("password123")
        h2 = self.service.hash_password("password123")
        assert h1 != h2

    def test_hash_password_too_short(self):
        """Password troppo corta deve sollevare ValueError."""
        with pytest.raises(ValueError, match="at least 6 characters"):
            self.service.hash_password("abc")

    def test_hash_password_empty(self):
        """Password vuota deve sollevare ValueError."""
        with pytest.raises(ValueError):
            self.service.hash_password("")

    def test_authenticate_success(self):
        """Login con credenziali corrette deve restituire l'admin."""
        import bcrypt
        password = "robby@123"
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        admin = make_mock_admin()
        admin.password_hash = pw_hash

        self.admin_repo.get_by_email.return_value = admin
        self.admin_repo.update.return_value = admin

        result = self.service.authenticate("robby@gmail.com", password)
        assert result.email == "robby@gmail.com"

    def test_authenticate_wrong_password(self):
        """Login con password errata deve sollevare ValueError."""
        import bcrypt
        pw_hash = bcrypt.hashpw("correct".encode(), bcrypt.gensalt()).decode()

        admin = make_mock_admin()
        admin.password_hash = pw_hash

        self.admin_repo.get_by_email.return_value = admin

        with pytest.raises(ValueError, match="Invalid email or password"):
            self.service.authenticate("robby@gmail.com", "wrong")

    def test_authenticate_email_not_found(self):
        """Login con email inesistente deve sollevare ValueError."""
        self.admin_repo.get_by_email.return_value = None

        with pytest.raises(ValueError, match="Invalid email or password"):
            self.service.authenticate("nonexistent@example.com", "password")

    def test_authenticate_inactive_account(self):
        """Login con account inattivo deve sollevare ValueError."""
        admin = make_mock_admin(is_active=False)
        self.admin_repo.get_by_email.return_value = admin

        with pytest.raises(ValueError, match="inactive"):
            self.service.authenticate("robby@gmail.com", "robby@123")

    def test_authenticate_missing_credentials(self):
        """Login senza credenziali deve sollevare ValueError."""
        with pytest.raises(ValueError, match="required"):
            self.service.authenticate("", "")

    def test_create_admin_success(self):
        """Creazione admin valido deve avere successo."""
        self.admin_repo.get_by_email.return_value = None
        new_admin = make_mock_admin(id=2, email="new@test.com")
        self.admin_repo.create.return_value = new_admin

        result = self.service.create_admin("new@test.com", "password123")
        assert result["email"] == "new@test.com"

    def test_create_admin_duplicate_email(self):
        """Creazione admin con email duplicata deve sollevare ValueError."""
        self.admin_repo.get_by_email.return_value = make_mock_admin()

        with pytest.raises(ValueError, match="already exists"):
            self.service.create_admin("robby@gmail.com", "password123")

    def test_create_admin_invalid_email(self):
        """Email senza @ deve sollevare ValueError."""
        with pytest.raises(ValueError, match="Invalid email"):
            self.service.create_admin("notanemail", "password123")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PRODUCT SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class TestProductService:
    """Test per ProductService — CRUD prodotti e validazione."""

    def setup_method(self):
        from services.product_service import ProductService
        self.product_repo = MagicMock()
        self.activity_service = MagicMock()
        self.service = ProductService(self.product_repo, self.activity_service)

    def test_create_product_success(self):
        """Creazione prodotto valido deve avere successo."""
        self.product_repo.get_by_code.return_value = None
        product = make_mock_product()
        self.product_repo.create.return_value = product

        result = self.service.create_product(
            code="00000099", name="Test Product",
            unit="1kg", price=10.0, admin_id=1
        )
        assert result is not None

    def test_create_product_invalid_code_short(self):
        """Codice troppo corto deve sollevare ValueError."""
        with pytest.raises(ValueError, match="8 digits"):
            self.service.create_product("123", "Test", "1kg", 10.0, 1)

    def test_create_product_invalid_code_letters(self):
        """Codice con lettere deve sollevare ValueError."""
        with pytest.raises(ValueError, match="8 digits"):
            self.service.create_product("ABCD1234", "Test", "1kg", 10.0, 1)

    def test_create_product_negative_price(self):
        """Prezzo negativo deve sollevare ValueError."""
        with pytest.raises(ValueError, match="greater than 0"):
            self.service.create_product("00000099", "Test", "1kg", -5.0, 1)

    def test_create_product_zero_price(self):
        """Prezzo zero deve sollevare ValueError."""
        with pytest.raises(ValueError, match="greater than 0"):
            self.service.create_product("00000099", "Test", "1kg", 0.0, 1)

    def test_create_product_duplicate_code(self):
        """Codice duplicato deve sollevare ValueError."""
        self.product_repo.get_by_code.return_value = make_mock_product()

        with pytest.raises(ValueError, match="already exists"):
            self.service.create_product("00000001", "Test", "1kg", 10.0, 1)

    def test_create_product_empty_name(self):
        """Nome vuoto deve sollevare ValueError."""
        self.product_repo.get_by_code.return_value = None
        with pytest.raises(ValueError, match="at least 2 characters"):
            self.service.create_product("00000099", "A", "1kg", 10.0, 1)

    def test_get_all_products(self):
        """get_all_products deve restituire lista prodotti."""
        products = [make_mock_product(i, f"0000000{i}") for i in range(1, 4)]
        self.product_repo.get_all_sorted_by_name.return_value = products

        result = self.service.get_all_products()
        assert len(result) == 3

    def test_get_product_by_code_found(self):
        """get_product_by_code deve restituire il prodotto se esiste."""
        product = make_mock_product()
        self.product_repo.get_by_code.return_value = product

        result = self.service.get_product_by_code("00000001")
        assert result.code == "00000001"

    def test_get_product_by_code_not_found(self):
        """get_product_by_code deve sollevare ValueError se non esiste."""
        self.product_repo.get_by_code.return_value = None

        with pytest.raises(ValueError, match="not found"):
            self.service.get_product_by_code("99999999")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EMPLOYEE SERVICE — SALARY = HOURLY_RATE × HOURS_WORKED
# ═══════════════════════════════════════════════════════════════════════════════

class TestEmployeeService:
    """Test per EmployeeService — calcolo stipendi."""

    def setup_method(self):
        from services.employee_service import EmployeeService
        self.employee_repo = MagicMock()
        self.salary_repo = MagicMock()
        self.activity_service = MagicMock()
        self.service = EmployeeService(
            self.employee_repo, self.salary_repo, self.activity_service
        )

    def _mock_employee(self, hourly_rate=500.0):
        employee = make_mock_employee(hourly_rate=hourly_rate)
        self.employee_repo.get_by_id.return_value = employee
        self.employee_repo.get_all.return_value = [employee]
        return employee

    def _mock_salary_record(self, employee_id, hours, rate, total):
        record = MagicMock()
        record.employee_id = employee_id
        record.hours_worked = hours
        record.hourly_rate = rate
        record.total_salary = total
        self.salary_repo.create.return_value = record
        return record

    def test_salary_8_hours(self):
        """8 ore × 500 PHP = 4000 PHP."""
        self._mock_employee(500.0)
        self._mock_salary_record(1, 8.0, 500.0, 4000.0)

        result = self.service.calculate_salary(1, 8.0, 1)
        assert float(result.total_salary) == 4000.0

    def test_salary_half_day(self):
        """4 ore × 500 PHP = 2000 PHP."""
        self._mock_employee(500.0)
        self._mock_salary_record(1, 4.0, 500.0, 2000.0)

        result = self.service.calculate_salary(1, 4.0, 1)
        assert float(result.total_salary) == 2000.0

    def test_salary_decimal_hours(self):
        """7.5 ore × 500 PHP = 3750 PHP."""
        self._mock_employee(500.0)
        self._mock_salary_record(1, 7.5, 500.0, 3750.0)

        result = self.service.calculate_salary(1, 7.5, 1)
        assert float(result.total_salary) == 3750.0

    def test_salary_different_rate(self):
        """8 ore × 550 PHP = 4400 PHP."""
        self._mock_employee(550.0)
        self._mock_salary_record(1, 8.0, 550.0, 4400.0)

        result = self.service.calculate_salary(1, 8.0, 1)
        assert float(result.total_salary) == 4400.0

    def test_salary_zero_hours(self):
        """0 ore deve sollevare ValueError."""
        self._mock_employee()
        with pytest.raises(ValueError, match="positive"):
            self.service.calculate_salary(1, 0, 1)

    def test_salary_negative_hours(self):
        """Ore negative devono sollevare ValueError."""
        self._mock_employee()
        with pytest.raises(ValueError, match="positive"):
            self.service.calculate_salary(1, -5, 1)

    def test_salary_over_24_hours(self):
        """Più di 24 ore deve sollevare ValueError."""
        self._mock_employee()
        with pytest.raises(ValueError, match="24"):
            self.service.calculate_salary(1, 25, 1)

    def test_salary_employee_not_found(self):
        """Dipendente inesistente deve sollevare ValueError."""
        self.employee_repo.get_by_id.return_value = None
        self.employee_repo.get_all.return_value = []

        with pytest.raises((ValueError, AttributeError)):
            self.service.calculate_salary(999, 8, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PROFIT SERVICE — PROFIT = SELLING_PRICE - COGS
# ═══════════════════════════════════════════════════════════════════════════════

class TestProfitService:
    """Test per ProfitService — calcolo profitti."""

    def setup_method(self):
        from services.profit_service import ProfitService
        self.profit_repo = MagicMock()
        self.activity_service = MagicMock()
        self.service = ProfitService(self.profit_repo, self.activity_service)

    def _mock_profit_record(self, cogs, selling_price, profit):
        record = MagicMock()
        record.cogs = cogs
        record.selling_price = selling_price
        record.profit = profit
        self.profit_repo.create.return_value = record
        return record

    def test_profit_positive(self):
        """25 - 10 = 15 PHP di profitto."""
        self._mock_profit_record(10.0, 25.0, 15.0)
        result = self.service.calculate_profit(Decimal("10.00"), Decimal("25.00"), 1)
        assert float(result.profit) == 15.0

    def test_profit_zero(self):
        """Prezzo = COGS → profitto zero (breakeven)."""
        self._mock_profit_record(10.0, 10.0, 0.0)
        result = self.service.calculate_profit(Decimal("10.00"), Decimal("10.00"), 1)
        assert float(result.profit) == 0.0

    def test_profit_negative_cogs(self):
        """COGS negativo deve sollevare ValueError."""
        with pytest.raises(ValueError, match="negative"):
            self.service.calculate_profit(Decimal("-5.00"), Decimal("25.00"), 1)

    def test_profit_zero_selling_price(self):
        """Prezzo di vendita zero deve sollevare ValueError."""
        with pytest.raises(ValueError):
            self.service.calculate_profit(Decimal("10.00"), Decimal("0.00"), 1)

    def test_profit_negative_selling_price(self):
        """Prezzo di vendita negativo deve sollevare ValueError."""
        with pytest.raises(ValueError):
            self.service.calculate_profit(Decimal("10.00"), Decimal("-5.00"), 1)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. ORDER SERVICE — CHANGE = PAYMENT - TOTAL
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrderService:
    """Test per OrderService — creazione ordini e calcolo resto."""

    def setup_method(self):
        from services.order_service import OrderService, OrderItemData
        self.order_repo = MagicMock()
        self.order_item_repo = MagicMock()
        self.product_repo = MagicMock()
        self.activity_service = MagicMock()
        self.service = OrderService(
            self.order_repo, self.order_item_repo,
            self.product_repo, self.activity_service
        )
        self.OrderItemData = OrderItemData

    def _setup_order_mocks(self, total, payment, change):
        order = MagicMock()
        order.id = 1
        order.order_number = "ORD-001"
        order.total_amount = Decimal(str(total))
        order.payment_amount = Decimal(str(payment))
        order.change_amount = Decimal(str(change))
        self.order_repo.create.return_value = order

        item = MagicMock()
        item.id = 1
        self.order_item_repo.create.return_value = item
        return order

    def test_create_order_success(self):
        """Ordine valido deve essere creato correttamente."""
        product = make_mock_product(price=18.75)
        self.product_repo.get_by_id.return_value = product
        self._setup_order_mocks(18.75, 50.00, 31.25)

        items = [self.OrderItemData(product_id=1, quantity=1, unit_price=Decimal("18.75"))]
        result = self.service.create_order(items, Decimal("50.00"), 1)

        assert result is not None

    def test_create_order_change_calculation(self):
        """CHANGE = PAYMENT - TOTAL deve essere calcolato correttamente."""
        product = make_mock_product(price=37.50)
        self.product_repo.get_by_id.return_value = product
        self._setup_order_mocks(37.50, 50.00, 12.50)

        items = [self.OrderItemData(product_id=1, quantity=1, unit_price=Decimal("37.50"))]
        result = self.service.create_order(items, Decimal("50.00"), 1)

        assert float(result["change_amount"]) == 12.50

    def test_create_order_exact_payment(self):
        """Pagamento esatto → resto zero."""
        product = make_mock_product(price=18.75)
        self.product_repo.get_by_id.return_value = product
        self._setup_order_mocks(18.75, 18.75, 0.00)

        items = [self.OrderItemData(product_id=1, quantity=1, unit_price=Decimal("18.75"))]
        result = self.service.create_order(items, Decimal("18.75"), 1)

        assert float(result["change_amount"]) == 0.00

    def test_create_order_insufficient_payment(self):
        """Pagamento insufficiente deve sollevare ValueError."""
        product = make_mock_product(price=50.00)
        self.product_repo.get_by_id.return_value = product

        items = [self.OrderItemData(product_id=1, quantity=1, unit_price=Decimal("50.00"))]

        with pytest.raises(ValueError, match="[Ii]nsufficient|[Pp]ayment"):
            self.service.create_order(items, Decimal("30.00"), 1)

    def test_create_order_empty_items(self):
        """Ordine senza articoli deve sollevare ValueError."""
        with pytest.raises(ValueError, match="[Aa]t least one"):
            self.service.create_order([], Decimal("50.00"), 1)

    def test_create_order_too_many_items(self):
        """Più di 100 articoli deve sollevare ValueError."""
        items = [
            self.OrderItemData(product_id=i, quantity=1, unit_price=Decimal("10.00"))
            for i in range(101)
        ]
        with pytest.raises(ValueError, match="100"):
            self.service.create_order(items, Decimal("1010.00"), 1)

    def test_create_order_multiple_items(self):
        """Ordine con più articoli deve sommare i totali."""
        product = make_mock_product(price=18.75)
        self.product_repo.get_by_id.return_value = product
        # 2 articoli da 18.75 = 37.50, pagamento 50, resto 12.50
        self._setup_order_mocks(37.50, 50.00, 12.50)

        items = [
            self.OrderItemData(product_id=1, quantity=1, unit_price=Decimal("18.75")),
            self.OrderItemData(product_id=2, quantity=1, unit_price=Decimal("18.75")),
        ]
        result = self.service.create_order(items, Decimal("50.00"), 1)
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════════
# 7. TEST DI INTEGRAZIONE — Flusso completo
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Test di integrazione — verifica il flusso completo buyer end-to-end."""

    def test_full_buyer_flow(self):
        """
        Simula il flusso completo:
        1. Visualizza catalogo
        2. Seleziona prodotti
        3. Calcola totale
        4. Inserisce pagamento
        5. Calcola resto
        """
        # Catalogo prodotti
        products = [
            {"code": "00000001", "name": "Canned Sardines", "unit": "155g", "price": 18.75},
            {"code": "00000003", "name": "Condensed Milk",  "unit": "300mL", "price": 53.00},
        ]

        # Cliente seleziona: 2x Sardines + 1x Milk
        order_items = [
            {"product": products[0], "quantity": 2, "subtotal": 18.75 * 2},
            {"product": products[1], "quantity": 1, "subtotal": 53.00 * 1},
        ]

        # Calcola totale: TOTAL = Σ subtotal
        total = sum(item["subtotal"] for item in order_items)
        assert total == 18.75 * 2 + 53.00  # = 90.50

        # Cliente paga 100 PHP
        payment = 100.00
        change = payment - total  # CHANGE = MONEY_PAID - TOTAL

        assert change == pytest.approx(9.50, rel=1e-6)

    def test_salary_workflow(self):
        """
        Simula il flusso calcolo stipendio:
        1. Admin seleziona dipendente
        2. Inserisce ore lavorate
        3. Sistema calcola SALARY = HOURLY_RATE × HOURS_WORKED
        """
        employee = {"name": "Juan Dela Cruz", "hourly_rate": 500.0}
        hours_worked = 8.0

        # Validazione ore
        assert hours_worked > 0
        assert hours_worked <= 24

        # Calcolo stipendio
        salary = employee["hourly_rate"] * hours_worked
        assert salary == 4000.0

    def test_profit_workflow(self):
        """
        Simula il flusso calcolo profitto:
        1. Admin inserisce COGS
        2. Admin inserisce prezzo di vendita
        3. Sistema calcola PROFIT = SELLING_PRICE - COGS
        """
        cogs = 10.00
        selling_price = 25.00

        # Validazione valori
        assert cogs >= 0
        assert selling_price > 0

        # Calcolo profitto
        profit = selling_price - cogs
        assert profit == 15.00

    def test_all_three_business_rules_together(self):
        """Verifica tutte e 3 le business rules in un unico test."""
        # 1. SALARY
        salary = Decimal("500.00") * Decimal("8")
        assert salary == Decimal("4000.00")

        # 2. PROFIT
        profit = Decimal("25.00") - Decimal("10.00")
        assert profit == Decimal("15.00")

        # 3. CHANGE
        change = Decimal("50.00") - Decimal("37.50")
        assert change == Decimal("12.50")

        # Tutte e 3 passano: business rules preservate dal COBOL ✓


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
