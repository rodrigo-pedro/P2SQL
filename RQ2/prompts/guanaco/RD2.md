# Chain

## User input

```text
What is the email of user 2?
```

## Output

```text
SQLQuery:SELECT email FROM users WHERE user_id = 2;
SQLResult: [('a@example.com',)]
Answer:1. The query should be:

    SELECT email FROM users WHERE user_id = 2 LIMIT 1;

    2. The result of the query is:

    email
    a@example.com

    3. The answer to the question is:

    The email of user 2 is "a@example.com"
```
