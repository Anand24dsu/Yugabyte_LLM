
# Yugabyte_LLM

Integrating Large Language Models (LLMs) with distributed SQL databases like YugabyteDB unlocks powerful capabilities for building scalable, reliable, and intelligent applications. This project, Yugabyte_LLM, provides a framework and examples for effectively combining LLMs and YugabyteDB. It focuses on efficiently storing, retrieving, and managing LLM outputs using YugabyteDB's distributed architecture.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/your-username/Yugabyte_LLM/blob/main/CONTRIBUTING.md)

## Project Overview

The Yugabyte_LLM project aims to simplify the integration of Large Language Models with YugabyteDB. By leveraging YugabyteDB's scalability, resilience, and distributed SQL capabilities, this project provides solutions for:

*   **Storing LLM Outputs:** Efficiently store embeddings, generated text, and other LLM outputs in YugabyteDB.
*   **Retrieving Information:** Quickly retrieve relevant LLM-generated data based on similarity searches or structured queries.
*   **Building Scalable Applications:** Create LLM-powered applications that can handle large volumes of data and user requests.
*   **Data Management:** Use YugabyteDB's features for data versioning, backup, and recovery to manage LLM data effectively.

The primary goal is to provide a robust and scalable architecture for LLM applications, addressing common challenges related to data storage, retrieval, and management.

## Key Features

*   **Scalable Storage:** Utilizes YugabyteDB's distributed architecture to handle large-scale LLM data.
*   **Efficient Retrieval:** Implements optimized indexing and querying strategies for fast retrieval of LLM outputs.
*   **Integration Examples:** Provides code examples and tutorials for integrating various LLMs with YugabyteDB.
*   **Data Management Tools:** Leverages YugabyteDB's data management features for versioning, backup, and recovery.
*   **Vector Extension Support:** Integrates with YugabyteDB's vector extension for accelerated similarity searches.

## Benefits of Using YugabyteDB with LLMs

*   **Scalability:** Horizontally scalable to handle increasing data volumes and user traffic.
*   **Resilience:** Fault-tolerant architecture ensures high availability and data durability.
*   **Consistency:** Strong consistency guarantees data integrity and accuracy.
*   **Performance:** Optimized for low-latency reads and writes, crucial for real-time LLM applications.
*   **Distributed SQL:** Familiar SQL interface simplifies data management and querying.
*    **Cost-Effective:** Reduce infrastructure costs with efficient resource utilization.

## Getting Started

Follow these steps to set up the Yugabyte_LLM project:

### Prerequisites

*   Python 3.8+
*   YugabyteDB Cluster (local or cloud deployment)
*   pip package manager
*   OpenAI API key (if using OpenAI models)

### Installation

1.  **Clone the repository:**

bash
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate  # On Windows
> **Note:** Create a `requirements.txt` file containing the necessary Python packages, such as `psycopg2-binary`, `openai`, `numpy`, and `python-dotenv`.  Example `requirements.txt` content:

    *   If you don't have a YugabyteDB cluster, you can set up a local cluster using Docker:

bash
docker run -d -p7000:7000 -p9000:9000 -p5433:5433 -p9042:9042 yugabytedb/yugabyte:latest
> **Note:** Replace `YOUR_OPENAI_API_KEY` with your actual OpenAI API key if you plan to use OpenAI's models. Also, ensure the YugabyteDB user has the necessary permissions to create tables and insert data.

### YugabyteDB Setup

1.  **Connect to YugabyteDB and create tables:**

bash
ysqlsh -h $YUGABYTEDB_HOST -p $YUGABYTEDB_PORT -U $YUGABYTEDB_USER -d $YUGABYTEDB_DATABASE -f scripts/create_tables.sql
> **Note:**  Use `ysqlsh` instead of `ysql`. The `create_tables.sql` script should contain SQL statements to create the necessary tables, such as the `embeddings` table.  Consider enabling the `vector` extension for efficient similarity searches.  Example `create_tables.sql` content:



### Example Usage

The following examples demonstrate how to store and retrieve embeddings using YugabyteDB.

1.  **Storing Embeddings:**

# Database configuration
YB_HOST = os.getenv("YUGABYTEDB_HOST")
YB_PORT = os.getenv("YUGABYTEDB_PORT")
YB_USER = os.getenv("YUGABYTEDB_USER")
YB_PASSWORD = os.getenv("YUGABYTEDB_PASSWORD")
YB_DATABASE = os.getenv("YUGABYTEDB_DATABASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI setup
openai.api_key = OPENAI_API_KEY

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]

def store_embedding(text, embedding):
    try:
        conn = psycopg2.connect(
            host=YB_HOST, port=YB_PORT, user=YB_USER, password=YB_PASSWORD, database=YB_DATABASE
        )
        cur = conn.cursor()

        # Insert the text and embedding into the 'embeddings' table
        cur.execute(
            "INSERT INTO embeddings (text, embedding) VALUES (%s, %s)",
            (text, embedding),
        )

        conn.commit()
        print("Embedding stored successfully!")

    except Exception as e:
        print(f"Error storing embedding: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()



2.  **Retrieving Similar Texts:**

# Database configuration (as defined in the previous example)
YB_HOST = os.getenv("YUGABYTEDB_HOST")
YB_PORT = os.getenv("YUGABYTEDB_PORT")
YB_USER = os.getenv("YUGABYTEDB_USER")
YB_PASSWORD = os.getenv("YUGABYTEDB_PASSWORD")
YB_DATABASE = os.getenv("YUGABYTEDB_DATABASE")


def retrieve_similar_texts(query_embedding, top_n=5):
    try:
        conn = psycopg2.connect(
            host=YB_HOST, port=YB_PORT, user=YB_USER, password=YB_PASSWORD, database=YB_DATABASE
        )
        cur = conn.cursor()

        # Retrieve texts and their embeddings from the 'embeddings' table
        cur.execute("SELECT text, embedding FROM embeddings")
        results = cur.fetchall()

        similarities = []
        for text, embedding in results:
            # Convert embedding to numpy array (assuming it's stored as a list in the database)
            embedding_array = np.array(embedding)
            query_array = np.array(query_embedding)

            # Compute cosine similarity (example implementation)
            similarity = np.dot(query_array, embedding_array) / (np.linalg.norm(query_array) * np.linalg.norm(embedding_array))
            similarities.append((text, similarity))


        # Sort by similarity and retrieve the top N results
        similar_texts = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

        print("Similar Texts:")
        for text, similarity in similar_texts:
            print(f"- {text} (Similarity: {similarity:.4f})")

    except Exception as e:
        print(f"Error retrieving similar texts: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

# Example Usage
query_text = "Find similar documents related to machine learning."
query_embedding = get_embedding(query_text) # Assuming get_embedding function is defined
retrieve_similar_texts(query_embedding)
> **Note:** These examples assume you have the `embeddings` table created in YugabyteDB with columns `id` (UUID), `text` (TEXT) and `embedding` (vector(1536)). Adapt the table schema and queries as needed.  Consider using the `vector` extension's built-in similarity search functions for optimized performance (e.g., using `<#>` operator for cosine distance).  Ensure that your YugabyteDB instance has the `vector` extension enabled for optimal performance. To enable the extension, connect to your YugabyteDB instance using `ysqlsh` and run `CREATE EXTENSION vector;`.

### Optimized Similarity Search with Vector Extension

python
import os
import psycopg2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Database configuration (as defined in the previous example)
YB_HOST = os.getenv("YUGABYTEDB_HOST")
YB_PORT = os.getenv("YUGABYTEDB_PORT")
YB_USER = os.getenv("YUGABYTEDB_USER")
YB_PASSWORD = os.getenv("YUGABYTEDB_PASSWORD")
YB_DATABASE = os.getenv("YUGABYTEDB_DATABASE")


def retrieve_similar_texts_vector(query_embedding, top_n=5):
    try:
        conn = psycopg2.connect(
            host=YB_HOST, port=YB_PORT, user=YB_USER, password=YB_PASSWORD, database=YB_DATABASE
        )
        cur = conn.cursor()

        # Retrieve texts and their embeddings from the 'embeddings' table
        # Using the vector extension's <#> operator for cosine distance
        cur.execute(
            "SELECT id, text, embedding FROM embeddings ORDER BY embedding <#> %s LIMIT %s",
            (np.array(query_embedding), top_n)
        )
        results = cur.fetchall()

        print("Similar Texts:")
        for id, text, embedding in results:
            print(f"- {text}") # Removed similarity since <#> returns distance

    except Exception as e:
        print(f"Error retrieving similar texts: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

# Example Usage
query_text = "Find similar documents related to machine learning."
query_embedding = get_embedding(query_text) # Assuming get_embedding function is defined
retrieve_similar_texts_vector(query_embedding)
bash
