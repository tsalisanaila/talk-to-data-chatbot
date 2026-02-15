# 🛍️ Talk-to-Data: Retail AI Analyst

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![LangChain](https://img.shields.io/badge/LangChain-0.1-green)
![Groq](https://img.shields.io/badge/AI-Llama3-orange)

**Transform Retail Transaction Data into Instant Business Insights using Generative AI.**

This application is an **AI-Powered Analytics Chatbot** designed to bridge the gap between raw data and business decision-making. It allows users to query sales data using natural language (English or Indonesian) and automatically generates accurate SQL queries, data tables, and interactive visualizations in real-time.

---

## 📸 Demo Preview

![Chatbot Screenshot (1)](assets\screenshot_retail-chatbot(1).png)

![Chatbot Screenshot (2)](assets\screenshot_retail-chatbot(2).png)

> *Example: The user asks "Show the sales trend per month," and the AI generates the SQL query and renders a Line Chart automatically.*

---

## ✨ Key Features

* **🗣️ Natural Language to SQL:** Translates human questions into valid MySQL queries using the **Llama 3** model (via Groq Cloud).
* **📊 Intelligent Auto-Visualization:** Automatically detects the nature of the data and selects the most appropriate visualization type (e.g., Line Charts for time-series, Bar Charts for categorical comparisons).

---

## 📂 Data Source

The dataset used in this project is sourced from Kaggle:
* **Retail Transactions Dataset** by Prasad22: [Link to Dataset](https://www.kaggle.com/datasets/prasad22/retail-transactions-dataset)

---

## 🛠️ Tech Stack

* **Language:** Python
* **LLM Engine:** Groq API (Model: `llama-3.3-70b-versatile`)
* **Orchestration:** LangChain
* **Database:** MySQL (Localhost via XAMPP)
* **Frontend:** Streamlit
* **Visualization:** Plotly Express & Pandas

---

## 🚀 Installation & Setup (Local)

Follow these steps to run the application on your local machine.

### 1. Prerequisites
Ensure you have the following installed:
* Python (version 3.9 or higher)
* XAMPP (or any MySQL Server)
* Git

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/talk-to-data-retail.git](https://github.com/YOUR_USERNAME/talk-to-data-retail.git)
cd talk-to-data-retail
```

### 3. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1.  Start **Apache** and **MySQL** in your XAMPP Control Panel.
2.  Open **phpMyAdmin** in your browser (`http://localhost/phpmyadmin`).
3.  Create a new database named `db_retail`.
4.  Click the **Import** tab.
5.  Select the `retail_data.sql` file provided in this repository.
6.  Click **Go** to execute the migration.

### 5. API Key Configuration
This project uses the Groq API.
1.  Get your API Key at [console.groq.com](https://console.groq.com/).
2.  Inside the project root folder, create a new folder named `.streamlit`.
3.  Inside that folder, create a file named `secrets.toml`.
4.  Add your key in the following format:

```toml
GROQ_API_KEY = "gsk_YOUR_ACTUAL_API_KEY_HERE"
```

### 6. Run the Application
Execute the following command in your terminal:
```bash
streamlit run app.py
```

---

## 💡 Example Queries
Try asking these questions to test the AI's capabilities:
1. "Show total sales per city." (Generates a Bar Chart)
2. "What is the transaction trend per month?" (Generates a Line Chart)
4. "Calculate the average basket size (average sales) per transaction."

---

**Created by Tsalisa Naila Ghaniyya - 2026**