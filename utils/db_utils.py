import pymysql


def get_engine(host, username, password, database, port):
    return pymysql.connect(host=host,
                           user=username,
                           password=password,
                           database=database,
                           port=port
                           )
def get_table_ddl(cursor:pymysql.Connection.cursor, table_name:str):
    try:
        ddl_query = f"SHOW CREATE TABLE {table_name}"
        cursor.execute(ddl_query)
        ddl_result = cursor.fetchone()
        create_table_statement = ddl_result[1]
        return create_table_statement
    except Exception as e:
        raise e

def detect_database_schema(connecton:pymysql.Connection, database:str, tables_to_lookup:list=None):
    with connecton.cursor() as cursor:
        if tables_to_lookup:
            table_ddls = [get_table_ddl(cursor=cursor, table_name=table) for table in tables_to_lookup]
            return "\n\n".join(table_ddls)
        else:
            with connecton.cursor() as cursor:
                table_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
                cursor.execute(table_query, (database))
                tables = cursor.fetchall()
                table_ddls = [get_table_ddl(cursor=cursor, table_name=table[0]) for table in tables]
                return "\n\n".join(table_ddls)
