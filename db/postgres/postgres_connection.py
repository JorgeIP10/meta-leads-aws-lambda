from repositories.db_connection import DBConnection

class PostgresConnection(DBConnection):
    def __init__(self, hostname, database, username, password, port, connect):
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.connection_tool = connect
        self.connection = None
        self.cursor = None

    def start_connection(self):
        self.connection = self.connection_tool(host=self.hostname,
                                               database=self.database,
                                               user=self.username,
                                               password=self.password,
                                               port=self.port)

    def create_cursor(self):
        self.cursor = self.connection.cursor()

    def create_connection_cursor(self):
        try:
            self.start_connection()
            self.create_cursor()
            print("Conexión a la base de datos exitosa.")
        except Exception as error:
            print(f"Error al conectar a la base de datos: {error}")
