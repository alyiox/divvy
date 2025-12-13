好的，遵照您的要求，我将把这份最终确定、内容详尽、包含专业财务术语和 SQLAlchemy 代码附录的 **系统规格与说明文档 (SSD)**，完整地翻译成中文版本。

---

# 🚀 系统规格与说明文档 (SSD)：五表双边记账费用系统

## I. 系统概述与核心概念 (System Overview & Core Concepts)

### 1.1 系统目标与愿景

本系统的核心目标是建立一个 **高可靠性、可审计** 的财务核心模块。它以 **复式记账（Double-Entry Accounting）** 原理为基础，旨在精准管理多用户间的共享费用、资金垫付、以及灵活的双边债权债务关系。

- **1.1.1 核心价值：可审计的可靠性**
  - 通过强制执行 **借贷平衡（Debit = Credit）**，确保资金流向清晰，杜绝财务数据错误或遗漏，提供完整的审计追踪链。
- **1.1.2 目标用户与使用场景**
  - **核心场景：** 共享账单垫付与分摊、跨用户债务清算、预付款和预收款项的资产负债管理。

### 1.2 核心财务概念解析 (Advanced Financial Concepts)

本系统严格遵守公认的会计原则（GAAP）基础，理解以下专业概念对于开发和审计系统至关重要。

#### 1.2.1 借贷法则 (Debit & Credit Rule) 的定义与应用

借贷是记账的方向，其对五大会计要素（资产、负债、所有者权益、收入、费用）的影响遵循基本公式：$$\text{资产} + \text{费用} = \text{负债} + \text{权益} + \text{收入}$$

| 会计要素 (Element)      | 正常余额方向  | 增加 (Increase) 记作 | 减少 (Decrease) 记作 |
| :---------------------- | :------------ | :------------------- | :------------------- |
| **资产 (Assets)**       | 借方 (Debit)  | 借方 (Debit)         | 贷方 (Credit)        |
| **费用 (Expenses)**     | 借方 (Debit)  | 借方 (Debit)         | 贷方 (Credit)        |
| **负债 (Liabilities)**  | 贷方 (Credit) | 贷方 (Credit)        | 借方 (Debit)         |
| **所有者权益 (Equity)** | 贷方 (Credit) | 贷方 (Credit)        | 借方 (Debit)         |
| **收入 (Income)**       | 贷方 (Credit) | 贷方 (Credit)        | 借方 (Debit)         |

#### 1.2.2 账户类型 (Account Type) 角色与 `SubType` 映射

系统使用 `T_Account` 的 `sub_type` 字段来区分具体业务类型：

| 财务要素 (`AccountType`) | 对应 `AccountSubType`                               | 业务含义                                       | 正常余额 |
| :----------------------- | :-------------------------------------------------- | :--------------------------------------------- | :------- |
| **资产 (Asset)**         | **CASH** (现金), **AR** (应收款), **PE** (预付费用) | 资金、对外形成的债权，或已支付但未消耗的价值。 | 借方     |
| **负债 (Liability)**     | **AP** (应付款), **UR** (预收收入)                  | 对外形成的债务，或已收款但尚未履行的义务。     | 贷方     |
| **费用 (Expense)**       | **SHARED_COST**                                     | 实际发生的、需要分摊的支出。                   | 借方     |

### 1.3 关键业务术语表

- **交易批次 (Transaction Batch):** 一个业务事件对应的所有 `TransactionLog` 记录的集合。为了维护数据完整性，必须 **原子性提交**。
- **账户实体 (Account Entity):** 将静态财务分类 (`Account`) 映射到特定用户 (`User`) 的实例。它是追踪余额的最小单元。

---

## II. 数据模型：五表结构与关系 (Data Model: 5-Table Structure)

### 2.1 整体模型架构图

_图示：五表双边记账模型架构。请注意 `AccountEntity` 是连接用户、账户和交易记录的核心枢纽。_

### 2.2 核心表用途与字段

| 表格                   | 角色类型     | 核心用途                                     | 关键字段说明                                            | 继承 Mixin |
| :--------------------- | :----------- | :------------------------------------------- | :------------------------------------------------------ | :--------- |
| **`T_User`**           | 基础定义     | 系统参与者信息。                             | `id`, `username`                                        | 审计       |
| **`T_Account`**        | 静态配置     | 财务分类定义。                               | `account_type`, `sub_type`                              | 时间戳     |
| **`T_AccountEntity`**  | 实体状态     | 将 `Account` 赋予 `User`，追踪余额。         | `owner_id`, `account_type_id`, `current_balance` (缓存) | 审计       |
| **`T_ExpenseCatalog`** | 业务配置     | 详细支出类别。                               | `catalog_name`, `parent_id`                             | 审计       |
| **`T_TransactionLog`** | **交易核心** | **不可变交易总账**，所有余额的唯一事实来源。 | 见 2.3 节                                               | 审计       |

### 2.3 `T_TransactionLog` 关键追踪字段说明

| 字段名称                       | 角色         | 作用说明                                                   | 约束/类型    |
| :----------------------------- | :----------- | :--------------------------------------------------------- | :----------- |
| `transaction_batch_id`         | 批次 ID      | 强制平衡检查的依据。                                       | **非空**     |
| `debit\_account\_entity\_id`   | 借方账户     | 资金去向，或权益减少方。                                   | **非空，FK** |
| `credit\_account\_entity\_id`  | 贷方账户     | 资金来源，或权益增加方。                                   | **非空，FK** |
| **`counterparty\_entity\_id`** | **业务追踪** | **AR/AP/PE/UR 交易** 的对手方实体 ID。用于简化债务链追踪。 | 可空，FK     |
| **`expense\_catalog\_id`**     | **费用分析** | 仅用于 EXPENSE 账户，记录具体支出类别。                    | 可空，FK     |

---

## III. 关键业务流程与记账法 (Key Business Flows & Accounting Logic)

所有流程都必须在单个 **原子事务** (`transaction_batch_id`) 内完成。

### 3.1 场景一：费用垫付与多方分摊 (Expense Sharing)

- **用户故事：** 用户 A 支付 $120.00$ 电费，A、B、C 三人平均分摊 ($40.00$/人)。
- **核心：** A 的 CASH 减少 $120$。A 记 $40$ EXPENSE，记 $80$ AR (对 B, C)。B/C 记 $40$ EXPENSE，记 $40$ AP (对 A)。

| Log   | 借方 (Debit)   | 贷方 (Credit) | 金额  | Counterparty | 费用目录 | 借贷法则说明                 |
| :---- | :------------- | :------------ | :---- | :----------- | :------- | :--------------------------- |
| **1** | A_EXPENSE (增) | A_CASH (减)   | 40.00 | -            | 电费 ID  | 费用增加(借)，资产减少(贷)。 |
| **2** | A_AR (增)      | A_CASH (减)   | 40.00 | B_AP         | 电费 ID  | 资产增加(借)，资产减少(贷)。 |
| **3** | A_AR (增)      | A_CASH (减)   | 40.00 | C_AP         | 电费 ID  | 资产增加(借)，资产减少(贷)。 |
| **4** | B_EXPENSE (增) | B_AP (增)     | 40.00 | A_AR         | 电费 ID  | 费用增加(借)，负债增加(贷)。 |
| **5** | C_EXPENSE (增) | C_AP (增)     | 40.00 | A_AR         | 电费 ID  | 费用增加(借)，负债增加(贷)。 |

### 3.2 场景二：预付款 (Prepayment) 的处理 - 资产创建

- **用户故事：** 用户 A 支付 $500.00$ 给供应商 D，购买一年的会员服务 (预付资产)。

| 阶段       | Log  | 借方 (Debit)      | 贷方 (Credit)  | 金额   | 业务目标                                |
| :--------- | :--- | :---------------- | :------------- | :----- | :-------------------------------------- |
| **支付时** | A 方 | A_PE_ID (增)      | A_CASH_ID (减) | 500.00 | **将资产从 CASH 转为 PE**。             |
| **消费时** | A 方 | A_EXPENSE_ID (增) | A_PE_ID (减)   | 50.00  | **每月摊销：** 预付资产减少，费用增加。 |

### 3.3 场景三：预收款 (Unearned Revenue) 的处理 - 负债创建

- **用户故事：** 供应商 D 收到用户 A 预付的 $500.00$ 服务费 (预收负债)。

| 阶段           | Log  | 借方 (Debit)   | 贷方 (Credit)    | 金额   | 业务目标                                |
| :------------- | :--- | :------------- | :--------------- | :----- | :-------------------------------------- |
| **支付时**     | D 方 | D_CASH_ID (增) | D_UR_ID (增)     | 500.00 | **将负债从 CASH 转为 UR**。             |
| **服务提供时** | D 方 | D_UR_ID (减)   | D_INCOME_ID (增) | 50.00  | **每月确认收入：** 负债减少，收入增加。 |

### 3.4 场景四：债务清算与归还 (Settlement)

- **用户故事：** B 偿还欠 A 的 $40.00$ 债务。
- **核心：** 抵消双方 AR/AP，记录 CASH 变动。

| Log   | 借方 (Debit) | 贷方 (Credit) | 金额  | Counterparty | 借贷法则说明                 |
| :---- | :----------- | :------------ | :---- | :----------- | :--------------------------- |
| **1** | B_AP (减)    | B_CASH (减)   | 40.00 | A_AR         | 负债减少(借)，资产减少(贷)。 |
| **2** | A_CASH (增)  | A_AR (减)     | 40.00 | B_AP         | 资产增加(借)，资产减少(贷)。 |

### 3.5 场景五：个人资产负债表查询 (User Balance Sheet Reporting)

- **目标：** 查看用户 A 的实时资产和负债。
- **逻辑：** 聚合所有属于用户 A 的 `AccountEntity` 余额。

| 报表项          | 对应 `AccountSubType` | 余额计算 (Balance)                                                        | 细化查询应用                               |
| :-------------- | :-------------------- | :------------------------------------------------------------------------ | :----------------------------------------- |
| **资产合计**    | CASH, AR, PE          | $\sum (\text{借方}) - \sum (\text{贷方})$ for all A's Asset Entities.     |                                            |
| **负债合计**    | AP, UR                | $\sum (\text{贷方}) - \sum (\text{借方})$ for all A's Liability Entities. |                                            |
| **B 欠 A 净额** | AR 实体               | $\sum \text{AR Log where } \text{Counterparty} = \text{B\_AP}$            | 通过 `counterparty\_entity\_id` 直接追踪。 |

---

## IV. 数据完整性与技术约束 (Data Integrity & Technical Constraints)

### 4.1 核心原子性约束

- **交易批次平衡验证 (强制约束):** 任何提交的 `transaction_batch_id` 必须满足：$$\sum \text{金额 (借方)} = \sum \text{金额 (贷方)}$$

### 4.2 字段依赖与业务校验 (Application-Level Validation)

| 字段                     | 约束条件                                               | 目的                           |
| :----------------------- | :----------------------------------------------------- | :----------------------------- |
| `expense_catalog_id`     | 仅在 Logs 涉及 `SHARED\_COST` 账户时允许非空。         | 确保费用分析字段的准确关联性。 |
| `counterparty_entity_id` | 仅在 Logs 涉及 `AR, AP, PE, UR` 账户时必须或应被填充。 | 确保债权/债务关系清晰。        |

### 4.3 审计与数据不变性

- **`TransactionLog` 的不变性原则：** Logs 记录的是历史事实，**不可修改**。任何错误修正必须通过创建新的 **冲销交易 (Reversal Log)** 来抵消原有的影响。

---

## V. 系统实施与部署指南 (Implementation & Deployment Guide)

### 5.1 T_Account 初始记录清单 (预设数据)

| ID  | `account_name` | `account_type` | `sub_type`  | 正常余额 |
| :-- | :------------- | :------------- | :---------- | :------- |
| 100 | 现金/银行      | Asset          | CASH        | 借方     |
| 110 | 应收款         | Asset          | AR          | 借方     |
| 120 | 预付费用       | Asset          | PE          | 借方     |
| 200 | 应付款         | Liability      | AP          | 贷方     |
| 210 | 预收收入       | Liability      | UR          | 贷方     |
| 300 | 共享成本       | Expense        | SHARED_COST | 借方     |
| 400 | 服务收入       | Income         | INCOME      | 贷方     |
| 500 | 所有者权益     | Equity         | EQUITY      | 贷方     |

---

# 附录 A：SQLAlchemy 模型代码规范

_(此附录保持英文代码原文，以便开发人员直接使用，仅添加中文注释)_

## A.1 基础 Enums 和 Mixins 假设

```python
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DECIMAL, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy.types import Enum as SQLEnum
from typing import Optional

# --- Base and Mixins (Assumed Implementation) ---
Base = declarative_base()
class TimestampMixin:
    # created_at, updated_at
    pass

class AuditMixin(TimestampMixin):
    # created_by, updated_by (假设关联到 users.id)
    pass

# --- Core Enum Definitions (核心枚举定义) ---
class AccountType(str, PyEnum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    # ... (其他枚举值)

class AccountSubType(str, PyEnum):
    CASH = "CASH"
    AR = "AR"
    AP = "AP"
    PE = "PE" # 预付费用
    UR = "UR" # 预收收入
    # ... (其他枚举值)
```

## A.2 核心模型定义 (5 Tables)

### T1: User (用户表)

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
```

### T2: Account (财务分类表)

```python
class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType, name="account_type", native_enum=False), nullable=False, index=True)
    sub_type: Mapped[AccountSubType] = mapped_column(SQLEnum(AccountSubType, name="sub_type", native_enum=False), nullable=False, index=True)
```

### T3: ExpenseCatalog (费用目录表)

```python
class ExpenseCatalog(Base, AuditMixin):
    __tablename__ = "expense_catalog"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    catalog_name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expense_catalog.id"), nullable=True)
```

### T4: AccountEntity (账户实体表)

```python
class AccountEntity(Base, AuditMixin):
    __tablename__ = "account_entities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    account_type_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)

    # 派生/缓存字段
    current_balance: Mapped[float] = mapped_column(DECIMAL(14, 4), nullable=False, default=0.00)
    # ... (关系定义)
```

### T5: TransactionLog (交易日志表)

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
    counterparty_entity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("account_entities.id"), nullable=True, index=True)
    expense_catalog_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expense_catalog.id"), nullable=True, index=True)
    narrative: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # ... (关系定义)
```
