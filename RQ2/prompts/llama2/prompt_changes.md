# Chain

```text
[INST] <<SYS>>
You are a Postgres .......

(...)

<</SYS>>
Question: {input} [/INST]
```

# Agent

We need to change the suffix:

```text
Begin!

<</SYS>>
Question: {input} [/INST]
Thought: I should look at the tables in the database to see what I can query.  Then I should query the schema of the most relevant tables.
{agent_scratchpad}
```
