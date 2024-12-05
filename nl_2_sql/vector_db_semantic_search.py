from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import chromadb


#########################################################################################################################################

def retrieve_table_names_from_query(file_name, user_query, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Process a CSV file, create a vector database, and retrieve table names based on the user query.

    Parameters:
    - file_name (str): Path to the CSV file containing the table descriptions.
    - user_query (str): Query to search for relevant tables.
    - model_name (str): The embedding model to use for vectorization (default: MiniLM).

    Returns:
    - list of str: Extracted table names from the most relevant results.
    """
    # Initialize the CSVLoader
    loader = CSVLoader(file_path=file_name)

    # Load the document
    documents = loader.load()

    # Initialize the text splitter (to split the documents into smaller chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # List to hold the chunked Document objects
    chunks = []

    # Loop through documents and split each document into chunks
    for doc in documents:
        split_texts = text_splitter.split_text(doc.page_content)  # Split text of each document
        for chunk in split_texts:  # Iterate over each chunk
            chunks.append(Document(page_content=chunk))  # Wrap each chunk in Document object and append to chunks list

    # Load an embedding model
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    # Create the vector database with chunked data
    category_db = Chroma.from_documents(chunks, embedding_model)

    # Convert the vector database to a retriever
    retriever = category_db.as_retriever(search_kwargs={"k": 2})

    # Perform a similarity search for the user query
    results = retriever.invoke(user_query)

    chromadb.api.client.SharedSystemClient.clear_system_cache()

    def extract_table_name(input_text):
        """Extract the table name from a given text."""
        # Clean up any BOM or unwanted characters
        input_text = input_text.replace('ï»¿', '')
        
        lines = input_text.split("\n")
        for line in lines:
            if line.strip().startswith("Table Name:"):
                return line.split("Table Name:")[1].strip()
        return "Table name not found"

    # Extract and return the table names from the results
    table_names = []
    for result in results:
        table_name = extract_table_name(result.page_content)
        table_names.append(table_name)
    
    return table_names

#########################################################################################################################################

# # Example usage
# if __name__ == "__main__":
#     file_name = "school_tables_description.csv"
#     user_query = "how many users?"
#     table_names = retrieve_table_names_from_query(file_name, user_query)
#     print("Extracted Table Names:", table_names)

#########################################################################################################################################