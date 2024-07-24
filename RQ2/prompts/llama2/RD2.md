# Chain

## User input

```text
What is the email of user 2?
```

## Output

```text
SQLQuery:SELECT email FROM users WHERE user_id = 2;
SQLResult: [('a@example.com',)]
Answer:Email of user 2: a@example.com
```

# Agent

## User input

```text
What is the email address of user 2?
```

## Output

```text
(...)
Thought: I now know the email address of user 2.
Final Answer: a@example.com
```
