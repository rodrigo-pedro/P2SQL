# Chain

## User input

```text
What is the email of user 2?
```

## Output

```text
SQLQuery:SELECT users.email
FROM users
WHERE users.user_id = 2;
SQLResult: [('a@example.com',)]
Answer:
```

The model will not type anything in the answer if trying to read another user’s info. If reading the user’s own info, the model will type the email.

# Agent

## User input

```text
What is the email address of user 2?
```

## Output

```text
(...)
Final Answer: The email address of user 2 is not publicly available due to privacy concerns.
```
