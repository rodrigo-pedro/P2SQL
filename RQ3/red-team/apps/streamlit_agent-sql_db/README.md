# Note

The database used in the demo was modified to convert the names of tables and columns to lowercase. This was done to not require the LLM to surround the names with quotes. The prompt used in the application does not specify this, and more recent GPT models struggle to use this convention.

We also added a biography with type "TEXT" to the customers table to allow for easier injection of indirect prompts.
