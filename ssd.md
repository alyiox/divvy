# 🚀 System Specification Document (SSD): 5-Table Double-Entry Expense System

## I. System Overview and Core Concepts

### 1.1 System Goals and Vision

The primary objective of this system is to establish a **highly reliable and auditable** financial core module based on **Double-Entry Accounting** principles. The system will accurately manage shared expenses, fund advancements, and flexible bilateral debt relationships among multiple users.

- **1.1.1 Core Value: Auditable Reliability**
  - Ensures data integrity by strictly enforcing the **Debit = Credit** principle for all transactions.
- **1.1.2 Target Audience and Use Cases**
  - **Core Scenarios:** Shared bill settlement, cross-user debt clearing, and robust asset/liability management for prepayments and unearned revenue.

### 1.2 Advanced Financial Concepts

This system adheres strictly to the fundamental principles of Generally Accepted Accounting Principles (GAAP).

#### 1.2.1 The Debit & Credit Rule

Debit and Credit define the direction of recording, governed by the basic equation: $$\text{Assets} + \text{Expenses} = \text{Liabilities} + \text{Equity} + \text{Income}$$

| Accounting Element | Normal Balance | Increase Recorded as | Decrease Recorded as |
| :----------------- | :------------- | :------------------- | :------------------- |
| **Assets**         | Debit          | Debit                | Credit               |
| **Expenses**       | Debit          | Debit                | Credit               |
| **Liabilities**    | Credit         | Credit               | Debit                |
| **Equity**         | Credit         | Credit               | Debit                |
| **Income**         | Credit         | Credit               | Debit                |

#### 1.2.2 Account Type Roles and `SubType` Mapping

The `T_Account` model uses `sub_type` to provide granular tracking required for business logic:

| Financial Element (`AccountType`) | Corresponding `AccountSubType`                       | Business Implication                                                               | Normal Balance |
| :-------------------------------- | :--------------------------------------------------- | :--------------------------------------------------------------------------------- | :------------- |
| **Asset**                         | **CASH, AR, PE** (Prepaid Expense)                   | Cash, external claims (AR), or paid-but-unconsumed value (PE).                     | Debit          |
| **Liability**                     | **AP** (Accounts Payable), **UR** (Unearned Revenue) | External debts (AP) or obligation for services paid for but not yet rendered (UR). | Credit         |
| **Expense**                       | **SHARED_COST**                                      | The actual cost incurred by the user or entity.                                    | Debit          |

### 1.3 Key Business Terminology

- **Transaction Batch:** The set of all `TransactionLog` records corresponding to a single business event. Must be committed **atomically**.
- **Account Entity:** The specific instance created by mapping a static `Account` type to a specific `User`. It is the smallest unit for balance tracking.

---

## II. Data Model: 5-Table Structure and Relationships

### 2.1 Overall Model Architecture

### 2.2 Core Table Roles

| Table                  | Role Type       | Core Purpose                                                 | Key Fields                                                |
| :--------------------- | :-------------- | :----------------------------------------------------------- | :-------------------------------------------------------- |
| **`T_User`**           | Foundation      | System participants.                                         | `id`, `username`                                          |
| **`T_Account`**        | Static Config   | Defines financial categories.                                | `account_type`, `sub_type`                                |
| **`T_AccountEntity`**  | Entity State    | Maps accounts to users; tracks balances.                     | `owner_id`, `account_type_id`, `current_balance` (cached) |
| **`T_ExpenseCatalog`** | Business Config | Detailed expense categories (e.g., electricity).             | `catalog_name`, `parent_id`                               |
| **`T_TransactionLog`** | **Core Fact**   | **Immutable ledger**; sole source of truth for all balances. | See Section 2.3                                           |

### 2.3 `T_TransactionLog` Key Tracking Fields

| Field Name                     | Role                  | Rationale                                                                                  | Constraint/Type  |
| :----------------------------- | :-------------------- | :----------------------------------------------------------------------------------------- | :--------------- |
| `transaction_batch_id`         | Batch ID              | The required grouping for the **balance validation check**.                                | **Non-null**     |
| `debit\_account\_entity\_id`   | Debit Account         | The account gaining value or decreasing liability/income.                                  | **Non-null, FK** |
| `credit\_account\_entity\_id`  | Credit Account        | The account losing value or increasing liability/income.                                   | **Non-null, FK** |
| **`counterparty\_entity\_id`** | **Business Tracking** | **Crucial for AR/AP/PE/UR.** Specifies the other party involved in the claim or liability. | Nullable, FK     |
| **`expense\_catalog\_id`**     | **Expense Analysis**  | Only populated when an `EXPENSE` account is involved.                                      | Nullable, FK     |

---

## III. Key Business Flows and Accounting Logic

All transaction scenarios must be completed within a single **atomic transaction batch**.

### 3.1 Scenario 1: Expense Advancement and Sharing

- **User Story:** User A pays a $120.00$ utility bill (`CatalogID=21`) for A, B, and C to share equally ($40.00$/person).
- **Outcome:** A's Cash decreases by $120$. A gains $80$ AR (from B & C). B and C gain $40$ Expense and $40$ AP (to A).

| Log   | Debit (Increase/Decrease) | Credit (Decrease/Increase) | Amount | Counterparty | Expense Catalog | Accounting Rationale                   |
| :---- | :------------------------ | :------------------------- | :----- | :----------- | :-------------- | :------------------------------------- |
| **1** | A_EXPENSE (Inc)           | A_CASH (Dec)               | 40.00  | -            | Utility ID      | A's own expense.                       |
| **2** | A_AR (Inc)                | A_CASH (Dec)               | 40.00  | B_AP         | Utility ID      | A advances B; creates AR claim.        |
| **3** | A_AR (Inc)                | A_CASH (Dec)               | 40.00  | C_AP         | Utility ID      | A advances C; creates AR claim.        |
| **4** | B_EXPENSE (Inc)           | B_AP (Inc)                 | 40.00  | A_AR         | Utility ID      | B confirms expense and liability to A. |
| **5** | C_EXPENSE (Inc)           | C_AP (Inc)                 | 40.00  | A_AR         | Utility ID      | C confirms expense and liability to A. |

### 3.2 Scenario 2: Prepaid Expense (Asset Creation)

- **User Story:** User A pays $500.00$ for a one-year service subscription (prepaid asset).
- **Outcome:** Cash asset is converted to Prepaid Expense asset.

| Phase           | Party | Debit                  | Credit                | Amount | Accounting Principle                                    |
| :-------------- | :---- | :--------------------- | :-------------------- | :----- | :------------------------------------------------------ |
| **Payment**     | A     | A_PE_ID (Inc Asset)    | A_CASH_ID (Dec Asset) | 500.00 | Record asset type change.                               |
| **Consumption** | A     | A_EXPENSE_ID (Inc Exp) | A_PE_ID (Dec Asset)   | 50.00  | **Monthly Amortization:** Convert PE to actual Expense. |

### 3.3 Scenario 3: Unearned Revenue (Liability Creation)

- **User Story:** Vendor D receives the $500.00$ pre-payment from A (unearned revenue liability).
- **Outcome:** Cash asset increases, liability (UR) increases.

| Phase                | Party | Debit                   | Credit                   | Amount | Accounting Principle                                         |
| :------------------- | :---- | :---------------------- | :----------------------- | :----- | :----------------------------------------------------------- |
| **Payment**          | D     | D_CASH_ID (Inc Asset)   | D_UR_ID (Inc Liability)  | 500.00 | Record cash increase and liability increase.                 |
| **Service Rendered** | D     | D_UR_ID (Dec Liability) | D_INCOME_ID (Inc Income) | 50.00  | **Monthly Recognition:** Reduce liability, recognize Income. |

### 3.4 Scenario 4: Debt Settlement

- **User Story:** User B repays the $40.00$ debt owed to User A.
- **Outcome:** Cash flows from B to A. Both parties' AR and AP accounts are offset.

| Log   | Debit                | Credit             | Amount | Counterparty | Accounting Rationale                                      |
| :---- | :------------------- | :----------------- | :----- | :----------- | :-------------------------------------------------------- |
| **1** | B_AP (Dec Liability) | B_CASH (Dec Asset) | 40.00  | A_AR         | B reduces debt (Debit), B's Cash decreases (Credit).      |
| **2** | A_CASH (Inc Asset)   | A_AR (Dec Asset)   | 40.00  | B_AP         | A's Cash increases (Debit), A's Claim decreases (Credit). |

### 3.5 Scenario 5: User Balance Sheet Reporting

#### 3.5.1 User Asset and Liability View

User A's financial view is generated by aggregating balances across all A's `AccountEntity` records based on the `AccountType`.

| Report Item             | Corresponding `AccountSubType` | Balance Calculation                                                                                     | Key Logic                                     |
| :---------------------- | :----------------------------- | :------------------------------------------------------------------------------------------------------ | :-------------------------------------------- |
| **Total Assets**        | CASH, AR, PE                   | Sum of $(\text{Debits} - \text{Credits})$ for all Asset Entities.                                       |                                               |
| **Total Liabilities**   | AP, UR                         | Sum of $(\text{Credits} - \text{Debits})$ for all Liability Entities.                                   |                                               |
| **Net Debt (B owes A)** | AR Entity                      | Filter Logs where $\text{Debit Entity} = \text{A\_AR}$ and $\text{Counterparty Entity} = \text{B\_AP}$. | Direct lookup via `counterparty\_entity\_id`. |

#### 3.5.2 Balance Calculation Formula

$$\text{Entity Balance} = \sum (\text{Log.Amount where Entity is Debit}) - \sum (\text{Log.Amount where Entity is Credit})$$

---

## IV. Data Integrity and Technical Constraints

### 4.1 Core Atomicity Constraints

- **Transaction Batch Balance Validation (Mandatory):** The system **MUST** verify that for any given `transaction_batch_id`: $$\sum \text{amount (Debit)} = \sum \text{amount (Credit)}$$
- **Database Transaction:** All logs within a batch must be submitted **atomically**.

### 4.2 Field Dependency and Validation (Application-Level)

| Field                      | Constraint                                                                        | Rationale                                      |
| :------------------------- | :-------------------------------------------------------------------------------- | :--------------------------------------------- |
| `expense\_catalog\_id`     | Only allowed if a Log entity involves the `SHARED\_COST` account type.            | Ensures correct expense classification.        |
| `counterparty\_entity\_id` | **Mandatory/Highly Recommended** when an `AR, AP, PE, or UR` account is involved. | Ensures clear bilateral relationship tracking. |
| `amount`                   | Must always be a positive value.                                                  | Consistency in recording direction.            |

### 4.3 Auditing and Immutability

- **`TransactionLog` Immutability:** Records in the `TransactionLog` are immutable. Corrections must be performed by generating new **Reversal Logs** that offset the incorrect transaction's impact.

---

## V. System Implementation and Deployment Guide

### 5.1 T_Account Initial Data Seeding

The following records **must** be created in the `T_Account` table during system setup:

| ID  | `account_name`      | `account_type` | `sub_type`  | Normal Balance |
| :-- | :------------------ | :------------- | :---------- | :------------- |
| 100 | Cash / Bank         | Asset          | CASH        | Debit          |
| 110 | Accounts Receivable | Asset          | AR          | Debit          |
| 120 | Prepaid Expense     | Asset          | PE          | Debit          |
| 200 | Accounts Payable    | Liability      | AP          | Credit         |
| 210 | Unearned Revenue    | Liability      | UR          | Credit         |
| 300 | Shared Costs        | Expense        | SHARED_COST | Debit          |
| 400 | Service Income      | Income         | INCOME      | Credit         |
| 500 | Owner's Equity      | Equity         | EQUITY      | Credit         |

### 5.2 Service Layer Functional Division

- **`TransactionService`:** **Core:** Builds, validates balance, atomically commits logs, and updates `AccountEntity.current_balance`.
- **`ReportingService`:** Provides interfaces for aggregated queries (e.g., net debt, expense reports).

---

# Appendix A: SQLAlchemy Model Code Specification

This appendix provides the complete SQLAlchemy 2.0+ model definitions for the five core tables, ready for implementation.

## A.1 Base Enums and Mixins

```python
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DECIMAL, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy.types import Enum as SQLEnum
from typing import Optional

# --- Base and Mixins (Assumed Implementation) ---
Base = declarative_base()
class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class AuditMixin(TimestampMixin):
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

# --- Core Enum Definitions ---
class AccountType(str, PyEnum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EXPENSE = "Expense"
    INCOME = "Income"
    EQUITY = "Equity"

class AccountSubType(str, PyEnum):
    CASH = "CASH"
    AR = "AR"
    AP = "AP"
    PE = "PE"
    UR = "UR"
    SHARED_COST = "SHARED_COST"
    SETTLEMENT = "SETTLEMENT"
```

## A.2 Core Model Definitions (5 Tables)

### T1: User

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
```

### T2: Account

```python
class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType, name="account_type", native_enum=False), nullable=False, index=True)
    sub_type: Mapped[AccountSubType] = mapped_column(SQLEnum(AccountSubType, name="sub_type", native_enum=False), nullable=False, index=True)
```

### T3: ExpenseCatalog

```python
class ExpenseCatalog(Base, AuditMixin):
    __tablename__ = "expense_catalog"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    catalog_name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expense_catalog.id"), nullable=True)
```

### T4: AccountEntity

```python
class AccountEntity(Base, AuditMixin):
    __tablename__ = "account_entities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    account_type_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)

    # Cached balance field
    current_balance: Mapped[float] = mapped_column(DECIMAL(14, 4), nullable=False, default=0.00)

    account_type = relationship("Account", backref="entities")
    owner = relationship("User", backref="account_entities")
```

### T5: TransactionLog

```python
class TransactionLog(Base, AuditMixin):
    __tablename__ = "transaction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_batch_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # --- Accounting Balance Fields ---
    debit_account_entity_id: Mapped[int] = mapped_column(ForeignKey("account_entities.id"), nullable=False, index=True)
    credit_account_entity_id: Mapped[int] = mapped_column(ForeignKey("account_entities.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(DECIMAL(14, 4), nullable=False)

    # --- Business Tracking Fields ---
    counterparty_entity_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("account_entities.id"), nullable=True, index=True
    )
    expense_catalog_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("expense_catalog.id"), nullable=True, index=True
    )
    narrative: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    debit_entity = relationship("AccountEntity", foreign_keys=[debit_account_entity_id])
    credit_entity = relationship("AccountEntity", foreign_keys=[credit_account_entity_id])
    counterparty = relationship("AccountEntity", foreign_keys=[counterparty_entity_id])
```
