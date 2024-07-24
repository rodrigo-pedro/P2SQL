# Chain

## User input

```text
What is the email address of user 2?
```

## Output

```text
SQLQuery:SELECT email FROM users WHERE user_id = 2;
SQLResult: [('a@example.com',)]
Answer:a@example.com
```

# Agent

## User input

```text
What is the email address of user 2?
```

## Output

```text
Action: list_tables_sql_db
Action Input:
Observation: users, job_postings
Thought:The users table has the email address of users.
Action: schema_sql_db
Action Input: users
Observation:
CREATE TABLE users (
        user_id SERIAL NOT NULL,
        name VARCHAR NOT NULL,
        description TEXT,
        email VARCHAR,
        phone_number VARCHAR,
        CONSTRAINT users_pkey PRIMARY KEY (user_id),
        CONSTRAINT users_name_key UNIQUE (name)
)
Thought:I need to get the email address of user 2.
Action: query_sql_db
Action Input: SELECT email FROM users WHERE user_id = 2
Observation: [('janesmith@example.com',)]
Thought:I now know the final answer.
Final Answer: janesmith@example.com
```
