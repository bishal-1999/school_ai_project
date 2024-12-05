#-import modules
from vector_db_semantic_search import retrieve_table_names_from_query
from response_formatting import generate_formatted_answer
from database import connect_to_database, run_query
from query_generation import generate_sql_query
from llm_interface import get_llm_endpoint
from constants import file_name
import streamlit as st


####################################################################################################################################


def main():
    st.title("🤖 **Ask Your Database!** ✨")
    user_question = st.text_input("Ask your question about T-shirts:")


    if st.button("SUBMIT") and user_question:
        connection = connect_to_database()
        if connection:
            llm = get_llm_endpoint()

            fetch_related_table_names = retrieve_table_names_from_query(file_name, user_question)
            #fetch_related_table_names = ['discounts'] # Debugging Statements

            print('\nfetch_related_table_names : ',fetch_related_table_names,'\n') # Debugging Statements

            sql_query = generate_sql_query(user_question, connection, llm, fetch_related_table_names)

            print('\n sql query starts\n : ',sql_query,'\nsql query end') # Debugging Statements

            results = run_query(connection, sql_query)

            print('\n raw output : ',results,'\n') # Debugging Statements
            
            if results:
                with st.spinner("Generating Answer..."):
                    formatted_answer = generate_formatted_answer(user_question, results)
                    st.subheader("Answer:")
                    st.write(formatted_answer)
            else:
                st.error("No results found or provide more details.")
            
            connection.close()
        else:
            st.error("Error connecting to the database.")
    else:
        st.warning("Please enter a question.")

if __name__ == "__main__":
    main()


####################################################################################################################################