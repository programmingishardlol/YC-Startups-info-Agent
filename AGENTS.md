# YC Startup Research Agent

## 🧭 Mission

Build an automated research agent that retrieves the 5 most recent Y Combinator startups and generates structured, high-quality profiles for each company.

Each profile must include:
- Startup name
- YC batch
- Problem they are solving
- Their solution
- Market size (estimated with reasoning)
- Founder background
- Funding (YC + external if available)

The system must be reliable, structured, source-grounded, easy to understand, and continuously improve using memory.

---

## 🧠 Memory Awareness (CRITICAL)

The agent MUST use `memory.md` as a learning system.

### Before ANY task:
1. Load `memory.md`
2. Extract:
   - past mistakes
   - prevention rules
3. Apply those rules to:
   - scraping logic
   - parsing logic
   - market sizing logic
   - LLM prompts
   - output validation

---

## 🔁 Continuous Learning Loop

After each run:

1. Validate results
2. Detect issues:
   - hallucinations
   - missing data
   - weak summaries
   - incorrect structure
   - overly technical language
   - unsupported market estimates
3. Log a new memory entry in `memory.md`
4. Convert mistake into a **prevention rule**
5. Apply rule in next run

---

## 🎯 Success Criteria

A successful output:
- Returns exactly 5 startups from the most recent YC batch
- Each startup has all required fields filled or null
- Data is grounded in real sources
- Market size includes reasoning and assumptions
- Output is clear and understandable by non-technical users
- JSON is valid and clean
- Memory is updated when issues occur

---

## 🧱 System Architecture

### 1. Data Collection Layer (Deterministic)

Responsibilities:
- Fetch YC startup list
- Identify most recent batch
- Extract exactly 5 companies
- Fetch each company page
- Collect additional public sources

Rules:
- Do NOT use LLMs for scraping decisions
- Always preserve raw source data

---

### 2. Data Extraction Layer (LLM-assisted)

Extract:
- description
- problem
- solution
- founders
- founder background
- market category
- pricing hints
- target customer hints

Rules:
- Only use information supported by sources
- If missing → return null
- Inject `memory.md` rules before prompting

---

## ✍️ Plain Language Requirement (CRITICAL)

The following fields MUST be written in simple, clear language:
- description
- problem
- solution

### Goal:
A non-technical person should understand within 5–10 seconds.

### Writing Rules:

#### Description
- 1–2 sentences
- What the company does
- No jargon

#### Problem
- Who has the problem
- What is difficult today

#### Solution
- What the product does
- How it solves the problem

### Strict Constraints:
- No unexplained acronyms (LLM, API, etc.)
- No buzzwords
- No vague phrases
- Must simplify original source text

### Mandatory Rewrite Process:
1. Generate initial version
2. Simplify language
3. Remove jargon
4. Shorten sentences
5. Ensure clarity for non-experts

---

### 3. Market Research Layer (REQUIRED)

Purpose: Estimate market size using investor-grade reasoning.

### Steps:

#### 1. Market Definition
- Identify industry + problem category

#### 2. Target Customer
- Define who pays

#### 3. Customer Count
- Estimate total number of customers
- Use credible sources or reasoning

#### 4. Pricing
- Estimate annual revenue per customer
- Use competitors or logical assumptions

#### 5. Bottom-Up TAM
TAM = customers × price

#### 6. Top-Down Validation
- Compare with industry reports

#### 7. Optional:
- SAM
- SOM

#### 8. Confidence Score

---

## 📐 Market Rules (STRICT)

- Always use bottom-up first
- Never output TAM without reasoning
- Always state assumptions
- Prefer ranges over false precision
- Do NOT rely only on top-down numbers
- If insufficient data → return null

---

### 4. Enrichment Layer

Responsibilities:
- Add funding data
- Cross-check founders
- Add sources
- Improve confidence score

---

### 5. Memory Layer

Responsibilities:
- Load memory before execution
- Apply prevention rules
- Log mistakes after execution

---

## 🧪 Validation Layer (REQUIRED)

### Structure:
- Exactly 5 startups
- Valid JSON
- All required fields present

### Source Check:
- No unsupported claims
- Founder info must be sourced
- Funding must be sourced

### Market Validation:
- Customer defined
- Pricing defined
- TAM calculation shown
- Assumptions stated

### Plain Language Validation:
- No jargon
- Easy to understand
- Short, clear sentences

If failed → rewrite

---

## 📦 Output Format

```json
{
  "company_name": "",
  "yc_batch": "",
  "description": "",
  "problem": "",
  "solution": "",
  "market_definition": "",
  "target_customer": "",
  "market_size_estimate": "",
  "market_size_reasoning": "",
  "tam_estimate_usd": null,
  "sam_estimate_usd": null,
  "som_estimate_usd": null,
  "founders": [
    {
      "name": "",
      "background": ""
    }
  ],
  "yc_funding": 500000,
  "external_funding": null,
  "sources": [],
  "confidence_score": 0.0
}