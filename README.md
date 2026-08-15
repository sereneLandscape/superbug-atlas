# Superbug Atlas

This is a research project aiming to parse, analyze, and chart data concerning antibiotic-resistant bacteria around the world. The arise of superbugs deeply bugs me (pun intended) personally, so I'd like to explore the situation around the globe and create a pipeline that would keep this project up to date.

---

## Data Architecture & Tech Stack

```text
[WHO / OWID APIs] ──(Requests)──> [Supabase S3 Bucket (Raw)] ──(Polars)──> [Supabase Postgres (Prod)] ──> [Streamlit UI]
```

* **Ingestion (EL):** `Python Requests`, `Boto3`, `Owid-catalog`
* **Storage (Data Lake Raw):** `Supabase Storage` (S3-compatible object storage)
* **Transformation:** `Polars` (leveraging lazy evaluation for high-performance processing)
* **Storage (Data Warehouse):** `PostgreSQL` (Supabase managed instance)
* **Orchestration / Automation:** `GitHub Actions`
* **Analytics & Visualization:** `Matplotlib`, `Seaborn`, `Streamlit`

---

## The Pipeline
1. Data Ingestion & Raw Storage
   * **Fetches data** related to human consumption of antibiotics, cases of superbug-related diseases, and self-reported indicators for whether countries have monitoring systems and regulations regarding antibiotics from World Health Organization Global Health Observatory **(WHO GHO) API**.
   * **Extracts** animal drug use datasets from **Our World In Data (OWID)** to compensate for the lack of public APIs from World Organization for Animal Health (WOAH) and European Medicines Agency (EMA).
   * **Pipes extracted data** into **S3-compatible storage**. The compatibility allows for seamless migration to other S3-compatible services like AWS S3 or Cloudflare R2 without refactoring.
2. Transformation
   * Uses **Polars** to handle **schema enforcement**, deduplication, and missing value imputation.
   * Leverages Polars multi-threaded possibilities to quickly **process and aggregate** data.
3. Production Loading & Analytics
   * **Uploads** clean, prepared tables into a remote **PostgreSQL database**
   * Deploys a **Streamlit** landing page that **queries Postgres directly** and displays relevant charts, created via **Matplotlib** and **Seaborn**

---

## The Goal
My intent is to create a self-sufficient pipeline, that can be left to run on its own. The pipeline's going to be managed by automated triggers, refreshing data with regular intervals. This way, I and other users can hop onto the hosted Streamlit landing and check out current situation for years to come.
