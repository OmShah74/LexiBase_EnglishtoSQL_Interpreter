# LexiBase: The Intelligent Database Companion

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.x-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LexiBase is a sophisticated web application that transforms the way users interact with data. It provides an intuitive, modern interface where anyone can upload their own SQLite database and ask complex questions in plain English. The application leverages a locally-run, open-source Large Language Model (LLM) to accurately translate natural language into precise SQL queries, which are then safely executed to retrieve the requested information.

The entire backend is powered by Django, with a custom-built SQL interpreter for security and a state-of-the-art prompt engineering strategy to handle complex, nested queries using Common Table Expressions (CTEs).

![LexiBase Screenshot](https://i.imgur.com/your-image-url.png) <!-- Optional: Add a screenshot URL here -->

## ✨ Core Features

*   **Bring Your Own Database:** Securely upload any SQLite (`.db`, `.sqlite3`) database file.
*   **Natural Language to SQL:** Ask questions like *"Which 5 actors appeared in the most films?"* or *"What is the average film length for each category?"*
*   **Complex Query Handling:** Utilizes advanced prompt engineering with a "Chain-of-Thought" approach, instructing the model to generate efficient Common Table Expressions (CTEs) for nested or multi-step questions.
*   **Secure by Design:** Features a custom SQL interpreter that parses and validates every AI-generated query. Only `SELECT` statements are permitted, preventing any possibility of data modification or injection attacks.
*   **Modern, Immersive UI:** A professional, dark-themed interface built for a great user experience, complete with loading indicators and dynamic effects.
*   **Local & Private:** The entire application, including the AI model, runs on your local machine. No data ever leaves your computer, ensuring 100% privacy.
*   **Optimized for CPU:** The model is pre-loaded on server start to eliminate initial wait times, and inference is optimized to use all available CPU cores.

## 🛠️ Tech Stack

*   **Backend:** Django
*   **Database Interaction:** Python's built-in `sqlite3`
*   **LLM Runner:** `llama-cpp-python` for efficient CPU inference
*   **Language Model:** Configured for GGUF-formatted models (e.g., TinyLlama, Phi-3, Mistral, DeepSeek-Coder)
*   **SQL Parsing & Validation:** `sqlglot`
*   **Frontend:** HTML, CSS, Bootstrap, JavaScript

## 🚀 Getting Started

Follow these instructions to get LexiBase running on your local machine.

### Prerequisites

*   Python 3.11 or newer
*   Git

