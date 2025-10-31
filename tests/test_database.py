import pytest
import sqlite3
import os
from unittest.mock import patch

from src.divvy import database

# Path to the schema file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCHEMA_FILE = os.path.join(PROJECT_ROOT, 'src', 'divvy', 'schema.sql')


class DatabaseConnection:
    """Context manager wrapper for database connection."""
    def __init__(self, conn):
        self.conn = conn
    
    def __enter__(self):
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Don't close in tests - fixture handles it
        pass


@pytest.fixture
def db_connection():
    """Fixture for a temporary, in-memory SQLite database connection."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def mock_get_db_connection(db_connection):
    """Mock database.get_db_connection to use the in-memory test database."""
    def get_connection():
        return DatabaseConnection(db_connection)
    
    with patch('src.divvy.database.get_db_connection', side_effect=get_connection):
        yield


def test_add_member():
    """Test adding a member."""
    member_id = database.add_member("TestMember")
    assert member_id is not None
    
    member = database.get_member_by_name("TestMember")
    assert member is not None
    assert member['name'] == "TestMember"
    assert member['is_active'] == 1


def test_add_duplicate_member():
    """Test that adding duplicate member returns None."""
    database.add_member("Duplicate")
    member_id = database.add_member("Duplicate")
    assert member_id is None


def test_get_member_by_id():
    """Test getting member by ID."""
    member_id = database.add_member("TestMember")
    member = database.get_member_by_id(member_id)
    assert member is not None
    assert member['name'] == "TestMember"


def test_get_all_members():
    """Test getting all members."""
    database.add_member("Member1")
    database.add_member("Member2")
    
    members = database.get_all_members()
    assert len(members) >= 2
    names = [m['name'] for m in members]
    assert "Member1" in names
    assert "Member2" in names


def test_get_active_members():
    """Test getting active members only."""
    database.add_member("Active1")
    database.add_member("Active2")
    
    active = database.get_active_members()
    names = [m['name'] for m in active]
    assert "Active1" in names
    assert "Active2" in names


def test_get_current_period():
    """Test getting current period."""
    period = database.get_current_period()
    assert period is not None
    assert period['is_settled'] == 0


def test_create_new_period():
    """Test creating a new period."""
    period_id = database.create_new_period("Test Period")
    assert period_id is not None
    
    period = database.get_period_by_id(period_id)
    assert period is not None
    assert period['name'] == "Test Period"
    assert period['is_settled'] == 0


def test_settle_period():
    """Test settling a period."""
    period_id = database.create_new_period("To Settle")
    result = database.settle_period(period_id)
    assert result is True
    
    period = database.get_period_by_id(period_id)
    assert period['is_settled'] == 1
    assert period['end_date'] is not None


def test_add_transaction():
    """Test adding a transaction."""
    member_id = database.add_member("Payer")
    category = database.get_category_by_name("Groceries")
    
    period = database.get_current_period()
    tx_id = database.add_transaction(
        'expense',
        5000,
        description="Test expense",
        payer_id=member_id,
        category_id=category['id'],
        period_id=period['id']
    )
    assert tx_id is not None
    
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        tx = cursor.fetchone()
        assert tx is not None
        assert tx['amount'] == 5000
        assert tx['description'] == "Test expense"
        assert tx['period_id'] == period['id']


def test_add_transaction_auto_period():
    """Test adding transaction without period_id (auto-assigns to current)."""
    member_id = database.add_member("Payer")
    category = database.get_category_by_name("Groceries")
    
    current_period = database.get_current_period()
    tx_id = database.add_transaction(
        'expense',
        3000,
        description="Auto period",
        payer_id=member_id,
        category_id=category['id']
        # period_id not provided
    )
    assert tx_id is not None
    
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        tx = cursor.fetchone()
        assert tx is not None
        assert tx['period_id'] == current_period['id']


def test_get_transactions_by_period():
    """Test getting transactions for a period."""
    period = database.get_current_period()
    member_id = database.add_member("Payer")
    category = database.get_category_by_name("Groceries")
    
    tx1_id = database.add_transaction('expense', 1000, period_id=period['id'], payer_id=member_id, category_id=category['id'])
    tx2_id = database.add_transaction('expense', 2000, period_id=period['id'], payer_id=member_id, category_id=category['id'])
    
    transactions = database.get_transactions_by_period(period['id'])
    assert len(transactions) >= 2
    tx_ids = [tx['id'] for tx in transactions]
    assert tx1_id in tx_ids
    assert tx2_id in tx_ids


def test_get_category_by_name():
    """Test getting category by name."""
    category = database.get_category_by_name("Groceries")
    assert category is not None
    assert category['name'] == "Groceries"


def test_get_category_by_id():
    """Test getting category by ID."""
    category = database.get_category_by_name("Groceries")
    category_by_id = database.get_category_by_id(category['id'])
    assert category_by_id is not None
    assert category_by_id['name'] == "Groceries"


def test_get_all_categories():
    """Test getting all categories."""
    categories = database.get_all_categories()
    assert len(categories) > 0
    names = [c['name'] for c in categories]
    assert "Groceries" in names
    assert "Rent" in names


def test_update_member_remainder_status():
    """Test updating member remainder status."""
    member_id = database.add_member("TestMember")
    
    database.update_member_remainder_status(member_id, True)
    member = database.get_member_by_id(member_id)
    assert member['paid_remainder_in_cycle'] == 1
    
    database.update_member_remainder_status(member_id, False)
    member = database.get_member_by_id(member_id)
    assert member['paid_remainder_in_cycle'] == 0


def test_reset_all_member_remainder_status():
    """Test resetting all member remainder status."""
    member1_id = database.add_member("Member1")
    member2_id = database.add_member("Member2")
    
    database.update_member_remainder_status(member1_id, True)
    database.update_member_remainder_status(member2_id, True)
    
    database.reset_all_member_remainder_status()
    
    member1 = database.get_member_by_id(member1_id)
    member2 = database.get_member_by_id(member2_id)
    assert member1['paid_remainder_in_cycle'] == 0
    assert member2['paid_remainder_in_cycle'] == 0

