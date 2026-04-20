# Hemlock: Zero-Trust Scraper Defense

Project Hemlock is a FastAPI middleware architecture and high-performance poisoning engine designed to actively push back against unauthorized AI data scraping. 

At its core, Hemlock intercepts traffic from Large Language Model (LLM) indexers and data scrapers. Instead of outright blocking them—which often prompts bots to rotate IPs or bypass blocks—Hemlock quietly serves them **"poisoned"** data.

## The "Poison" Concept

Hemlock uses **Homoglyph Substitution**. When the system determines that a requester is likely an automated bot, it passes outgoing JSON textual data through a high-speed C++ engine. This engine replaces standard Latin ASCII characters with visually identical Cyrillic characters (e.g., the Latin `a` becomes the Cyrillic `а`).

* **For Human Readers & Screen Readers**: The text appears visually identical and reads completely normally.
* **For AI Scrapers & Tokenizers**: The ingested data is fundamentally corrupted because Cyrillic characters map to entirely different vector space embeddings, rendering the scraped dataset useless for model training and context ingestion.

## Defense Layers

Hemlock utilizes a progressive, defense-in-depth protocol:

- **Layer 0 (First-Touch Zero-Trust)**: We assume all non-browser traffic is hostile. If a request lacks standard browser headers (like `Accept-Language` or `Sec-CH-UA`), it is immediately fed a 20% poisoned payload right from the very first request.
- **Layer 1 (Known Signatures)**: Immediate 100% poisoning for known AI bot user-agents (e.g., `gptbot`, `claudebot`, `bytespider`).
- **Layer 3 (Velocity Traps)**: If an IP exceeds 5 requests within a 10-second rolling window, it is flagged as an aggressive crawler and gets heavily poisoned (100%).
- **Layer 4 (Honeypots)**: Hemlock serves visually hidden `<a href="/api/hidden-data">` links on standard pages. Any bot that blindly crawls into these traps has its IP permanently placed in the penalty box for 100% poisoning on all future traffic.

## 🛠️ Tech Stack

* **Middleware API**: Python (FastAPI, Starlette)
* **High-Performance Substitution**: C++ (`pybind11` bridge for native execution speeds on the byte-substitution engine).
* **State Persistence**: PostgreSQL (via SQLAlchemy) logging detections and ban states.

## Getting Started

### Prerequisites
* Python 3.9+ (Tested on Anaconda 3.13)
* A C++ Compiler (e.g., `clang++` or `g++`)
* Docker (for the PostgreSQL database)

### Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy psycopg2-binary pybind11 requests
   ```

2. **Compile the Poison Engine**
   The homoglyph substitution relies on a high-performance C++ module. Compile it inplace:
   ```bash
   python setup.py build_ext --inplace
   ```

3. **Start the Database**
   Hemlock logs all IP bans and poisoned payloads to a Postgres database mapped on port 5434.
   ```bash
   docker-compose up -d
   ```

4. **Run the Middleware Server**
   Start the FastAPI instance:
   ```bash
   python -m uvicorn main:app
   ```

### Verifying the Defense

Hemlock comes with simulation scripts to verify the behavior of the Zero-Trust system:

* **Human Simulator:** Run `python test_scripts/human_sim.py` to see how legitimate requests equipped with real browser headers are parsed correctly.
* **Bot Simulator:** Run `python test_scripts/bot_sim.py` to watch Hemlock progressively increase the poison rates from Layer 0 (First-Touch) through Layer 4 (Honeypot) against an automated scraper. 
