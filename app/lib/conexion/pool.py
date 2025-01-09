# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.pool import SimpleConnectionPool

class DatabaseManager:
    def __init__(self):
        # Cargar las variables de entorno
        load_dotenv()

        # Configuración desde las variables de entorno
        self.database_config = {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        }

        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Inicializa el pool de conexiones."""
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,  # Ajusta según las necesidades de tu aplicación
                **self.database_config
            )
            if self.connection_pool:
                print("¡Pool de conexiones creado exitosamente!")
        except Exception as e:
            print("Error al crear el pool de conexiones:", e)
            raise

    def _reset_pool(self):
        """Reinicia el pool de conexiones en caso de fallo."""
        print("Reiniciando el pool de conexiones...")
        self.close_pool()
        self._initialize_pool()

    def get_connection(self) -> psycopg2.extensions.connection:
        """Obtiene una conexión del pool, reintenta si es necesario."""
        try:
            connection = self.connection_pool.getconn()
            # Verificar si la conexión está activa
            if connection.closed != 0:  # Conexión cerrada
                print("Conexión perdida, reiniciando pool...")
                self._reset_pool()
                connection = self.connection_pool.getconn()
            return connection
        except Exception as e:
            print("Error al obtener una conexión:", e)
            self._reset_pool()
            connection = self.connection_pool.getconn()
            return connection

    def release_connection(self, connection):
        """Libera una conexión de vuelta al pool."""
        try:
            if connection:
                self.connection_pool.putconn(connection)
        except Exception as e:
            print("Error al liberar la conexión:", e)
            raise

    def close_pool(self):
        """Cierra el pool de conexiones."""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                print("¡Pool de conexiones cerrado exitosamente!")
        except Exception as e:
            print("Error al cerrar el pool de conexiones:", e)
            raise

# Instancia global de DatabaseManager
db_manager_instance = DatabaseManager()
