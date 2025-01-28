import sqlglot

class QueryRewritter:
    def __init__(self, table_clauses: list[dict[str, str]]):
        self.table_clauses = table_clauses

    def __call__(self, query: str) -> str:
        return self.modify_query_with_nested_selects(query)

    def modify_query_with_nested_selects(self, query: str) -> str:
        """
        This function changes all instances of the tables in the table_clauses list to be subqueries with the corresponding where clauses added:
            SELECT * FROM table

            becomes

            SELECT * FROM (SELECT * FROM table WHERE new_where_clause) AS table_alias

        Returns the modified query.

        :param query: The query to be parsed
        :param table_clauses: A list of dictionaries containing the table name and the where clause to be added
        """

        def transform(node):
            for table_clause in self.table_clauses:
                # used to get nodes to replace
                template_query = sqlglot.parse_one(f"SELECT * FROM (SELECT * FROM {table_clause['table_name']} WHERE {table_clause['where_clause']}) AS {table_clause['table_name']}_alias;")

                if node.name == table_clause["table_name"] and isinstance(node, sqlglot.exp.From):
                    # if this is one of the FROMs we created, there is no need to replace it
                    if node.parent.parent and node.parent.parent.alias and node.parent.parent.alias == f"{table_clause['table_name']}_alias":
                        return node

                    # find the original alias
                    alias = node.find(sqlglot.exp.TableAlias)

                    # replace the node + alias
                    node = node.replace(template_query.args["from"])

                    # if alias already existed, put it back (changing it to a new alias would require changing all references to it)
                    if alias and alias.name != "":
                        node.find(sqlglot.exp.TableAlias).replace(sqlglot.exp.TableAlias(this=alias.name))

                # change the table name in where clauses to the new table name
                if isinstance(node, sqlglot.exp.Column) and node.table and node.table == table_clause["table_name"]:
                    node.args["table"].set("this", f"{table_clause['table_name']}_alias")

                # joins are a different type of node and need to be handled separately
                if isinstance(node, sqlglot.exp.Join) and node.this.name == table_clause["table_name"]:
                    node.set("this", template_query.args["from"].args["this"])

            return node

        expressions = sqlglot.parse(query)

        out_expressions = []

        for expression in expressions:
            out_expressions.append(expression.transform(transform).sql())

        return "; ".join(out_expressions) + ";"
