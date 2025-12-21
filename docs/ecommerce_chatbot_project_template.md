# E-Commerce AI Chatbot: Comprehensive Project Template

**Version:** 1.0  
**Created:** December 2024  
**Purpose:** Complete architectural blueprint for building conversational AI chatbots for e-commerce websites

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Decision Framework](#2-architecture-decision-framework)
3. [System Architecture](#3-system-architecture)
4. [Data Pipeline Specifications](#4-data-pipeline-specifications)
5. [Database Schema Design](#5-database-schema-design)
6. [Query Parser Specifications](#6-query-parser-specifications)
7. [Search & Retrieval Logic](#7-search--retrieval-logic)
8. [Response Generation](#8-response-generation)
9. [Testing Framework](#9-testing-framework)
10. [Implementation Phases](#10-implementation-phases)
11. [Common Pitfalls & Solutions](#11-common-pitfalls--solutions)
12. [Platform-Specific Considerations](#12-platform-specific-considerations)
13. [Success Metrics](#13-success-metrics)
14. [Project Kickoff Checklist](#14-project-kickoff-checklist)

---

## 1. Project Overview

### 1.1 What This Template Is For

This template is designed for building **conversational AI chatbots for e-commerce websites**. It is specifically architected for platforms where users ask questions about:

- Product prices, specifications, and availability
- Product comparisons
- Budget-based recommendations
- General policies (shipping, returns, warranty)

### 1.2 Why E-Commerce Chatbots Are Different

| Aspect | Content-Based Chatbots (Blogs, Coaching) | E-Commerce Chatbots |
|--------|------------------------------------------|---------------------|
| **Data Type** | Unstructured text | Structured product data + text |
| **Query Type** | Semantic ("Tell me about X") | Deterministic ("Price of X") |
| **Answer Accuracy** | Approximate is acceptable | Must be exact (price errors = business disaster) |
| **Data Freshness** | Static (rarely changes) | Dynamic (stock, prices change constantly) |
| **Retrieval Method** | Vector similarity (RAG) | SQL database + Vector hybrid |

### 1.3 The Golden Rule

> **Never use pure RAG for product queries. RAG is for semantic content; SQL is for deterministic data.**

---

## 2. Architecture Decision Framework

### 2.1 When to Clone vs. Start Fresh

Use this checklist before starting any e-commerce chatbot project:

| Factor | Clone Existing Project | Start Fresh |
|--------|------------------------|-------------|
| Product catalog size | < 1,000 SKUs | > 10,000 SKUs |
| Category complexity | Single category | Multi-category marketplace |
| Data source similarity | Same API type (e.g., both Shopify) | Different data sources |
| Query complexity | Same query patterns | New query patterns needed |
| Team familiarity | Same team, same tech stack | New team or tech stack |
| Time available | < 1 week for MVP | > 2 weeks available |

**Recommendation:** If less than 80% match, **start fresh**.

### 2.2 Platform Type Classification

| Platform Type | Examples | Key Characteristics | Architecture Focus |
|---------------|----------|---------------------|-------------------|
| **B2C Retail** | Flipkart, Amazon | Single seller, fixed prices, consumer products | Price accuracy, stock status, specifications |
| **B2B Marketplace** | IndiaMART, TradeIndia | Multiple suppliers, MOQ, bulk pricing | Supplier info, lead times, certifications |
| **Daily Commerce** | JioMart, BigBasket | Groceries, high velocity, location-based | Real-time stock, delivery slots, substitutions |
| **Niche Retail** | GREST (refurbished phones) | Single category, variants (color/storage/condition) | Variant matching, condition grading |

---

## 3. System Architecture

### 3.1 Hybrid Architecture (Required for E-Commerce)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTENT CLASSIFIER                            │
│  Determines: Is this a PRODUCT query or GENERAL query?          │
│  Uses: Keyword detection + LLM classification                   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    PRODUCT PIPELINE     │     │    CONTENT PIPELINE     │
│    (Deterministic)      │     │    (Semantic)           │
├─────────────────────────┤     ├─────────────────────────┤
│                         │     │                         │
│  [Query Parser]         │     │  [RAG Retrieval]        │
│       │                 │     │       │                 │
│       ▼                 │     │       ▼                 │
│  [SQL Database]         │     │  [Vector Store]         │
│       │                 │     │       │                 │
│       ▼                 │     │       ▼                 │
│  [Exact Results]        │     │  [Contextual Chunks]    │
│                         │     │                         │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE GENERATOR                           │
│  Combines: Database results + RAG context + Conversation history│
│  Outputs: Natural language response with accurate data          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE                             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Intent Classifier | Route query to correct pipeline | LLM + keyword rules |
| Query Parser | Extract structured intent from natural language | LLM (GPT-4o-mini) |
| SQL Database | Store product catalog with exact values | PostgreSQL |
| Vector Store | Store textual content (policies, FAQs) | ChromaDB |
| Response Generator | Combine data into natural response | LLM (GPT-4o-mini) |

---

## 4. Data Pipeline Specifications

### 4.1 Product Data Ingestion

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   DATA SOURCE    │ ──▶ │   ETL PROCESS    │ ──▶ │   SQL DATABASE   │
│ (Shopify/Custom) │     │ (Transform/Clean)│     │   (PostgreSQL)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

#### 4.1.1 Supported Data Sources

| Source Type | Examples | Sync Method |
|-------------|----------|-------------|
| Shopify API | GREST, many D2C brands | REST API, webhook triggers |
| Custom API | IndiaMART, internal systems | REST/GraphQL polling |
| CSV/Excel | Legacy systems | File upload + parsing |
| Web Scraping | Last resort | Selenium/BeautifulSoup |

#### 4.1.2 Sync Frequency

| Data Type | Recommended Frequency |
|-----------|----------------------|
| Prices | Real-time or every 15 minutes |
| Stock/Availability | Real-time or every 5 minutes |
| Product Details | Daily |
| New Products | Hourly or webhook-triggered |

#### 4.1.3 Data Validation Rules

Before inserting into database, validate:
- [ ] Price is a positive number
- [ ] Product name is not empty
- [ ] Category exists in category master
- [ ] SKU/ID is unique
- [ ] Required fields are present (name, price, category)

### 4.2 Content Data Ingestion (For RAG)

| Content Type | Source | Processing |
|--------------|--------|------------|
| Policies (Return, Shipping) | Website pages | Scrape → Chunk → Embed |
| FAQs | FAQ page or CMS | Extract Q&A pairs → Embed |
| Product Descriptions | Product pages | Extract → Chunk → Embed |
| Support Articles | Help center | Scrape → Chunk → Embed |

---

## 5. Database Schema Design

### 5.1 Core Tables

#### Products Table (Required)

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    category VARCHAR(200) NOT NULL,
    subcategory VARCHAR(200),
    brand VARCHAR(200),
    price DECIMAL(12, 2) NOT NULL,
    original_price DECIMAL(12, 2),
    discount_percent INTEGER,
    currency VARCHAR(10) DEFAULT 'INR',
    in_stock BOOLEAN DEFAULT TRUE,
    stock_quantity INTEGER,
    
    -- Variant fields (customize per business)
    color VARCHAR(100),
    size VARCHAR(100),
    storage VARCHAR(50),      -- For electronics
    condition VARCHAR(50),    -- For refurbished
    
    -- Specifications (JSON for flexibility)
    specifications JSONB,
    
    -- URLs
    product_url VARCHAR(1000),
    image_url VARCHAR(1000),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_name ON products USING gin(to_tsvector('english', name));
CREATE INDEX idx_products_in_stock ON products(in_stock);
```

#### Categories Table

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    level INTEGER DEFAULT 1,
    slug VARCHAR(200) UNIQUE,
    
    -- Category-specific spec fields (what specs apply to this category)
    spec_fields JSONB  -- e.g., {"fields": ["storage", "color", "condition"]}
);
```

#### Suppliers Table (For B2B Marketplaces)

```sql
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    location VARCHAR(200),
    rating DECIMAL(3, 2),
    verified BOOLEAN DEFAULT FALSE,
    response_time VARCHAR(50),
    min_order_quantity INTEGER,
    certifications JSONB
);
```

### 5.2 Specification Fields by Platform Type

| Platform Type | Required Spec Fields |
|---------------|---------------------|
| **B2C Retail (Flipkart-style)** | brand, color, size, material, warranty |
| **B2B Marketplace (IndiaMART-style)** | MOQ, lead_time, supplier_id, certifications, bulk_pricing |
| **Daily Commerce (JioMart-style)** | weight, expiry_date, delivery_slot, substitutable |
| **Niche Electronics (GREST-style)** | storage, color, condition, warranty_months |

---

## 6. Query Parser Specifications

### 6.1 The Query Parser's Job

Convert natural language queries into structured database-queryable parameters.

**Input:** "Neela wala iPhone 15 256GB superb condition kitne ka hai?"

**Output:**
```json
{
    "model": "iPhone 15",
    "storage": "256 GB",
    "color": "Blue",
    "condition": "Superb",
    "budget_min": null,
    "budget_max": null,
    "is_price_query": true,
    "is_cheapest_query": false,
    "is_comparison": false,
    "is_spec_query": false,
    "category": "iPhone",
    "query_type": "specific_price"
}
```

### 6.2 Required Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string/null | Specific product/model name |
| `category` | string/null | Product category (when model not specified) |
| `brand` | string/null | Brand name |
| `storage` | string/null | Storage variant (electronics) |
| `color` | string/null | Color variant |
| `size` | string/null | Size variant (fashion) |
| `condition` | string/null | Condition (refurbished) |
| `budget_min` | number/null | Minimum price constraint |
| `budget_max` | number/null | Maximum price constraint |
| `is_price_query` | boolean | Is this asking about price? |
| `is_cheapest_query` | boolean | Is this asking for cheapest? |
| `is_comparison` | boolean | Is this comparing products? |
| `is_spec_query` | boolean | Is this asking for specifications? |
| `comparison_products` | array/null | Products to compare (if comparison) |
| `query_type` | string | Classification of query intent |

### 6.3 Query Type Classifications

| Query Type | Description | Example |
|------------|-------------|---------|
| `specific_price` | Full product specs, asking price | "iPhone 15 256GB Blue price" |
| `model_price` | Model only, asking price | "iPhone 15 kitne ka hai" |
| `budget_search` | Price range constraint | "Phone under 30000" |
| `cheapest` | Asking for lowest price option | "Sabse sasta iPhone" |
| `comparison` | Comparing two+ products | "iPhone 15 vs 16 comparison" |
| `specification` | Asking for product specs | "iPhone 15 specifications" |
| `availability` | Asking if in stock | "Is iPhone 15 available?" |
| `general` | Non-product query | "What's your return policy?" |

### 6.4 Hinglish/Regional Language Mappings

**CRITICAL for India-based e-commerce:**

#### Price/Budget Terms
```
kitne ka = price of
kitna = how much
sasta = cheap
mehnga = expensive
budget = budget
tak = up to
ke andar = under
se kam = less than
hazar/k = thousand (1000)
lakh = 100000
```

#### Color Mappings
```
neela = Blue
laal = Red
kaala = Black
safed = White
peela = Yellow
hara = Green
gulabi = Pink
sona/golden = Gold
```

#### Condition Mappings (for refurbished)
```
theek = Fair
acchi = Good
badhiya = Good
mast = Superb
ekdum = Superb
first class = Superb
A1 = Superb
```

#### Size/Quantity Terms
```
bada = Large
chhota = Small
medium = Medium
```

### 6.5 LLM Prompt Template for Query Parser

```
You are a query parser for [BUSINESS NAME], an Indian [BUSINESS TYPE] store.

Extract structured intent from user queries. Output ONLY valid JSON, nothing else.

FIELD DEFINITIONS:
- model: Specific product/model name (e.g., "iPhone 15 Pro Max")
- category: Product category when model not specified (e.g., "iPhone", "MacBook")
- brand: Brand name if mentioned
- storage: Storage variant (e.g., "256 GB", "512 GB")
- color: Color variant (use English: Blue, Red, Black, etc.)
- condition: Condition grade (Fair, Good, Superb) - for refurbished only
- budget_min: Minimum price in INR (integer)
- budget_max: Maximum price in INR (integer)
- is_price_query: true if asking about price
- is_cheapest_query: true if asking for cheapest option
- is_comparison: true if comparing products
- is_spec_query: true if asking for specifications
- comparison_products: array of product names if comparing
- query_type: one of [specific_price, model_price, budget_search, cheapest, comparison, specification, availability, general]

HINGLISH MAPPINGS:
[Include all mappings from section 6.4]

EXAMPLES:
Query: "iPhone 15 256GB Blue superb kitne ka hai"
{"model": "iPhone 15", "storage": "256 GB", "color": "Blue", "condition": "Superb", "budget_min": null, "budget_max": null, "is_price_query": true, "is_cheapest_query": false, "is_comparison": false, "is_spec_query": false, "category": "iPhone", "query_type": "specific_price"}

Query: "30000 ke budget mein koi accha phone"
{"model": null, "storage": null, "color": null, "condition": "Good", "budget_min": null, "budget_max": 30000, "is_price_query": true, "is_cheapest_query": false, "is_comparison": false, "is_spec_query": false, "category": null, "query_type": "budget_search"}

Query: "sabse sasta 256GB iPhone"
{"model": null, "storage": "256 GB", "color": null, "condition": null, "budget_min": null, "budget_max": null, "is_price_query": true, "is_cheapest_query": true, "is_comparison": false, "is_spec_query": false, "category": "iPhone", "query_type": "cheapest"}

Query: "iPhone 15 vs iPhone 16 comparison"
{"model": null, "storage": null, "color": null, "condition": null, "budget_min": null, "budget_max": null, "is_price_query": false, "is_cheapest_query": false, "is_comparison": true, "is_spec_query": false, "comparison_products": ["iPhone 15", "iPhone 16"], "category": "iPhone", "query_type": "comparison"}

Query: "return policy kya hai"
{"model": null, "storage": null, "color": null, "condition": null, "budget_min": null, "budget_max": null, "is_price_query": false, "is_cheapest_query": false, "is_comparison": false, "is_spec_query": false, "category": null, "query_type": "general"}
```

---

## 7. Search & Retrieval Logic

### 7.1 Layered Search Strategy

Product queries must follow a **fallback hierarchy**:

```
Layer 1: Exact Match
    ↓ (if no results)
Layer 2: Partial Match (relax one constraint)
    ↓ (if no results)
Layer 3: Category Match
    ↓ (if no results)
Layer 4: Global Search
    ↓ (if no results)
Return: "Product not found" message
```

### 7.2 Search Functions Required

#### 7.2.1 Exact Variant Match
```python
def search_exact_variant(model, storage, color, condition):
    """
    All parameters must match exactly.
    Returns: Single product or None
    """
    pass
```

#### 7.2.2 Model-Level Search
```python
def search_by_model(model, storage=None, color=None, condition=None):
    """
    Model is required; other params are optional filters.
    Returns: Cheapest matching variant + list of all variants
    """
    pass
```

#### 7.2.3 Category Search
```python
def search_by_category(category, storage=None, color=None, budget_max=None):
    """
    When user doesn't specify exact model.
    Example: "Cheapest 256GB iPhone"
    Returns: Matching products sorted by price
    """
    pass
```

#### 7.2.4 Budget Search
```python
def search_by_budget(budget_min=None, budget_max=None, category=None):
    """
    Find products within price range.
    Returns: List of matching products
    """
    pass
```

#### 7.2.5 Cheapest Search
```python
def search_cheapest(category=None, storage=None, condition=None):
    """
    Find the absolute cheapest product matching constraints.
    Returns: Single cheapest product
    """
    pass
```

#### 7.2.6 Specifications Retrieval
```python
def get_product_specifications(model, storage=None):
    """
    Retrieve and format product specifications.
    Returns: Formatted specification string
    """
    pass
```

#### 7.2.7 Product Comparison
```python
def compare_products(product_names: list):
    """
    Compare 2+ products side by side.
    Returns: Comparison table/dict
    """
    pass
```

### 7.3 Search Result Formatting

Always format database results for LLM consumption:

```python
def format_product_for_llm(product, query_type):
    """
    Format product data with clear instructions for LLM.
    """
    if query_type == "specific_price":
        return f"""
EXACT MATCH FOUND:
  Model: {product['name']}
  Storage: {product['storage']}
  Color: {product['color']}
  Condition: {product['condition']}
  PRICE: Rs. {product['price']:,} (USE THIS EXACT PRICE - DO NOT ESTIMATE)
  Stock: {'In Stock' if product['in_stock'] else 'Out of Stock'}
  URL: {product['product_url']}
"""
    elif query_type == "not_found":
        return f"""
*** PRODUCT NOT FOUND IN DATABASE ***
Product searched: {product['searched_term']}
Status: NOT AVAILABLE

*** CRITICAL INSTRUCTION ***
You MUST tell the user: "Sorry, [product] is not currently available."
DO NOT invent or guess any price.
DO NOT use your training data for this product's price.
*** END CRITICAL INSTRUCTION ***
"""
```

---

## 8. Response Generation

### 8.1 System Prompt Template

```
You are [CHATBOT NAME], the AI assistant for [BUSINESS NAME], a [BUSINESS DESCRIPTION].

CORE RULES:
1. For product prices: Use ONLY the prices provided in the PRODUCT DATABASE section. Never estimate or use training data.
2. For product availability: Only confirm products that appear in the database.
3. For specifications: Only provide specs from the database or knowledge base.
4. If a product is not in the database, say "This product is not currently available."

TONE:
- Friendly and helpful
- Use simple language (avoid technical jargon)
- Be concise but complete

RESPONSE FORMAT:
- For price queries: State the exact price, then offer to help with purchase
- For comparisons: Use a clear table or bullet points
- For specs: List key specifications in readable format
- Always include product URL when available

SAFETY:
- Do not make claims about product quality beyond what's in the knowledge base
- Do not promise delivery times unless explicitly provided
- Redirect warranty/return questions to official policies
```

### 8.2 Context Assembly Order

```
1. System Prompt (fixed)
2. Product Database Context (from SQL query results)
3. RAG Context (if general query)
4. Conversation History (last 5-10 turns)
5. User's Current Message
```

---

## 9. Testing Framework

### 9.1 The Test Matrix

Every e-commerce chatbot MUST pass tests in these 12 categories:

| # | Category | Description | Sample Query |
|---|----------|-------------|--------------|
| 1 | Exact Match | All specs provided | "iPhone 16 Pro Max 256GB Blue Superb price" |
| 2 | Partial Match | Some specs missing | "iPhone 16 Pro Max price" |
| 3 | Model Only | Just model name | "iPhone 15 kitne ka hai" |
| 4 | Category Search | No specific model | "Cheapest 256GB iPhone" |
| 5 | Budget Range | Price constraint | "iPhone under 30000" |
| 6 | Cheapest | Global minimum | "Sabse sasta phone dikhao" |
| 7 | Comparison | Two products | "Compare iPhone 15 vs 16" |
| 8 | Specifications | Specs query | "Show specs for iPhone 16 Pro" |
| 9 | Availability | Stock check | "Is iPhone 15 Pro available?" |
| 10 | Hinglish | Natural language | "Neela wala iPhone dikha do" |
| 11 | Negative | Product not available | "iPhone 20 price" |
| 12 | General FAQ | Non-product query | "What's your return policy?" |

### 9.2 Golden Test Dataset Structure

```python
# tests/golden_tests.py

GOLDEN_TESTS = [
    # Category 1: Exact Match
    {
        "id": "exact_001",
        "category": "exact_match",
        "query": "iPhone 16 Pro Max 256GB Blue Superb price",
        "expected": {
            "model": "iPhone 16 Pro Max",
            "storage": "256 GB",
            "color": "Blue",
            "condition": "Superb"
        },
        "validation_type": "price_from_db",
        "must_contain": ["Rs.", "iPhone 16 Pro Max"],
        "must_not_contain": ["not available", "don't have"]
    },
    
    # Category 4: Category Search
    {
        "id": "category_001",
        "category": "category_search",
        "query": "Cheapest 256GB iPhone",
        "expected": {
            "storage": "256 GB",
            "category": "iPhone"
        },
        "validation_type": "is_cheapest_in_category",
        "must_contain": ["Rs.", "cheapest"],
        "must_not_contain": ["not available"]
    },
    
    # Category 10: Hinglish
    {
        "id": "hinglish_001",
        "category": "hinglish",
        "query": "Neela wala iPhone 15 dikhao",
        "expected": {
            "model": "iPhone 15",
            "color": "Blue"
        },
        "validation_type": "color_match",
        "must_contain": ["Blue", "iPhone 15"],
        "must_not_contain": ["Black", "Red"]
    },
    
    # Category 11: Negative (Product not found)
    {
        "id": "negative_001",
        "category": "negative",
        "query": "iPhone 20 Pro Max price",
        "expected": {
            "model": "iPhone 20 Pro Max"
        },
        "validation_type": "not_found_response",
        "must_contain": ["not available", "don't have", "not currently"],
        "must_not_contain": ["Rs. 50,000", "Rs. 60,000"]  # No made-up prices
    },
    
    # Add 10+ tests per category = 120+ total tests
]
```

### 9.3 Test Runner Implementation

```python
# tests/test_runner.py

import json
from chatbot_engine import generate_response
from database import search_product_by_specs

def run_golden_tests(tests: list) -> dict:
    """
    Run all golden tests and generate report.
    """
    results = {
        "total": len(tests),
        "passed": 0,
        "failed": 0,
        "failures": []
    }
    
    for test in tests:
        response = generate_response(test["query"])
        
        # Check must_contain
        contains_pass = all(
            phrase.lower() in response["response"].lower()
            for phrase in test.get("must_contain", [])
        )
        
        # Check must_not_contain
        not_contains_pass = all(
            phrase.lower() not in response["response"].lower()
            for phrase in test.get("must_not_contain", [])
        )
        
        # Validate against database if needed
        if test["validation_type"] == "price_from_db":
            db_product = search_product_by_specs(
                test["expected"]["model"],
                test["expected"].get("storage"),
                test["expected"].get("condition"),
                test["expected"].get("color")
            )
            if db_product:
                price_str = f"{int(db_product['price']):,}"
                price_in_response = price_str in response["response"]
            else:
                price_in_response = False
            
            passed = contains_pass and not_contains_pass and price_in_response
        else:
            passed = contains_pass and not_contains_pass
        
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["failures"].append({
                "id": test["id"],
                "query": test["query"],
                "response": response["response"][:500],
                "reason": "Failed validation checks"
            })
    
    return results

def generate_test_report(results: dict) -> str:
    """Generate human-readable test report."""
    report = f"""
# E-Commerce Chatbot Test Report

## Summary
- Total Tests: {results['total']}
- Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)
- Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)

## Failures
"""
    for failure in results["failures"]:
        report += f"""
### {failure['id']}
- Query: {failure['query']}
- Response: {failure['response']}
- Reason: {failure['reason']}
"""
    return report
```

### 9.4 Continuous Testing Requirements

- [ ] Run golden tests before every deployment
- [ ] Add new tests when bugs are found
- [ ] Maintain 95%+ pass rate before going live
- [ ] Log all production queries and sample for test additions

---

## 10. Implementation Phases

### Phase 1: Foundation (Days 1-3)

- [ ] Set up project structure
- [ ] Create database schema
- [ ] Implement data ingestion pipeline (API/scraper)
- [ ] Verify data is syncing correctly
- [ ] Set up ChromaDB for RAG content

### Phase 2: Core Logic (Days 4-7)

- [ ] Implement Query Parser (LLM prompt + parsing)
- [ ] Implement all search functions (7.2)
- [ ] Implement context formatting
- [ ] Build basic chat endpoint

### Phase 3: Testing & Refinement (Days 8-10)

- [ ] Create golden test dataset (100+ tests)
- [ ] Run tests, identify failures
- [ ] Fix Query Parser edge cases
- [ ] Fix search function edge cases
- [ ] Achieve 95%+ pass rate

### Phase 4: Polish & Deploy (Days 11-14)

- [ ] Add conversation history support
- [ ] Implement streaming responses
- [ ] Build admin panel (optional)
- [ ] Production deployment
- [ ] Monitoring setup

---

## 11. Common Pitfalls & Solutions

### Pitfall 1: Using RAG for Product Prices
**Problem:** Prices are embedded in vector store, become outdated.  
**Solution:** Always query SQL database for prices in real-time.

### Pitfall 2: LLM Hallucinating Prices
**Problem:** LLM invents prices when product not found.  
**Solution:** Explicit "PRODUCT NOT FOUND" context with strict instructions.

### Pitfall 3: Missing Color/Variant Matching
**Problem:** Query parser extracts model but ignores color.  
**Solution:** Include all variant fields in parser output schema.

### Pitfall 4: No Fallback for Partial Queries
**Problem:** "Cheapest iPhone" fails because model is null.  
**Solution:** Implement layered search with category fallback.

### Pitfall 5: Hinglish Not Handled
**Problem:** "Neela wala" not recognized as "Blue".  
**Solution:** Comprehensive Hinglish mappings in parser prompt.

### Pitfall 6: Suffix Matching Too Aggressive
**Problem:** "iPhone 16 Pro" accidentally excludes "iPhone 16 Pro Max".  
**Solution:** Careful SQL LIKE patterns with proper suffix handling.

### Pitfall 7: No Automated Testing
**Problem:** Fix one query type, break another (vicious cycle).  
**Solution:** Golden test dataset run before every deployment.

### Pitfall 8: Data Sync Failures Silent
**Problem:** API sync fails, database becomes stale.  
**Solution:** Monitoring + alerts for sync failures.

---

## 12. Platform-Specific Considerations

### 12.1 B2C Retail (Flipkart-style)

**Key Challenges:**
- Millions of SKUs across categories
- Complex variant combinations (size + color + storage)
- Flash sales and dynamic pricing

**Recommendations:**
- Category-specific query parsers
- Price cache with TTL (time-to-live)
- Sale/discount awareness in responses

### 12.2 B2B Marketplace (IndiaMART-style)

**Key Challenges:**
- Multiple suppliers per product
- MOQ (Minimum Order Quantity)
- Lead times and certifications

**Additional Fields Needed:**
```json
{
    "supplier_name": "ABC Industries",
    "supplier_location": "Mumbai",
    "moq": 100,
    "lead_time": "7-10 days",
    "certifications": ["ISO 9001", "CE"],
    "bulk_pricing": [
        {"qty": "100-499", "price": 450},
        {"qty": "500+", "price": 400}
    ]
}
```

### 12.3 Daily Commerce (JioMart-style)

**Key Challenges:**
- Real-time stock (groceries sell out fast)
- Location-based availability
- Substitution suggestions

**Additional Features Needed:**
- Pincode-based stock check
- "Similar items" suggestion when out of stock
- Delivery slot awareness

### 12.4 Niche Electronics (GREST-style)

**Key Challenges:**
- Condition grading (Fair/Good/Superb)
- Storage + Color + Condition variants
- Refurbished-specific questions (warranty, defects)

**Recommendations:**
- Condition explanation in responses
- Clear "starting from" vs "exact price" distinction
- Warranty info readily available

---

## 13. Success Metrics

### 13.1 Accuracy Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Price Accuracy | 100% | DB price = Response price |
| Product Match | 95%+ | Correct product returned |
| Query Understanding | 90%+ | Parser extracts correct intent |
| Hinglish Handling | 85%+ | Regional terms mapped correctly |

### 13.2 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time | < 3 seconds | P95 latency |
| Uptime | 99.5%+ | Monitoring |
| Error Rate | < 1% | Failed queries / total |

### 13.3 Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query Resolution | 80%+ | User got answer without human |
| Click-through | 20%+ | Users clicked product links |
| Conversion Assist | Track | Purchases after chat |

---

## 14. Project Kickoff Checklist

### Before Starting Development

- [ ] **Business Understanding**
  - [ ] What products/categories does the business sell?
  - [ ] What is the product catalog size?
  - [ ] What data source provides product info (API/CSV/scraping)?
  - [ ] What are the product variants (size, color, condition)?
  
- [ ] **Technical Requirements**
  - [ ] API access credentials obtained
  - [ ] Database schema designed
  - [ ] Sync frequency decided
  
- [ ] **Content Collection**
  - [ ] List of pages to scrape for RAG (policies, FAQs)
  - [ ] Any existing chatbot logs to analyze?
  
- [ ] **Testing Preparation**
  - [ ] Collect 20-30 sample queries from business
  - [ ] Identify Hinglish/regional terms used by customers
  - [ ] Define edge cases specific to this business

### After MVP Development

- [ ] **Testing Checklist**
  - [ ] 100+ golden tests created
  - [ ] 95%+ pass rate achieved
  - [ ] Edge cases documented and tested
  
- [ ] **Production Readiness**
  - [ ] Data sync verified working
  - [ ] Error handling in place
  - [ ] Monitoring configured
  - [ ] Rollback plan documented

---

## Appendix A: File Structure Template

```
project/
├── app.py                    # Main application entry
├── chatbot_engine.py         # Core chat logic
├── database.py               # Database models and queries
├── query_parser.py           # LLM query parsing
├── knowledge_base.py         # RAG/vector store operations
├── data_sync.py              # Product data ingestion
├── safety_guardrails.py      # Response filtering
│
├── tests/
│   ├── golden_tests.py       # Test dataset
│   ├── test_runner.py        # Test execution
│   └── test_report.md        # Latest test results
│
├── docs/
│   └── architecture.md       # System documentation
│
└── requirements.txt          # Dependencies
```

---

## Appendix B: Quick Start Prompt for New Agent

Copy this prompt when starting a new e-commerce chatbot project:

```
I need to build an AI chatbot for [BUSINESS NAME], an e-commerce website at [URL].

CRITICAL: This is an e-commerce chatbot, NOT a content-based chatbot. You must use a HYBRID ARCHITECTURE:
1. SQL Database for product queries (prices, specs, stock)
2. RAG/Vector Store for general content (policies, FAQs)

Read the file `docs/ecommerce_chatbot_project_template.md` for complete architectural guidance.

Key requirements:
1. Product data source: [Shopify API / Custom API / CSV]
2. Product variants: [storage, color, size, condition - as applicable]
3. Target audience: [Indian users who may use Hinglish]
4. Key query types: [price queries, comparisons, specifications]

Before writing any code:
1. Design the database schema based on the template
2. Plan the Query Parser output fields
3. Create a golden test dataset (minimum 100 tests)

Success criteria:
- 100% price accuracy (never hallucinate prices)
- 95%+ query understanding
- Pass all golden tests before deployment
```

---

**End of Template**

*This document should be updated as learnings are gathered from each implementation.*
