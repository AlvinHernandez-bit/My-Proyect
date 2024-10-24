import abc
from datetime import datetime
import sqlite3
from typing import List, Optional

class Habitacion(abc.ABC):
    def __init__(self, numero: int, tipo: str, precio_por_noche: float):
        self.numero = numero
        self.tipo = tipo
        self.precio_por_noche = precio_por_noche
        self.disponible = True

    @abc.abstractmethod
    def aplicar_descuento(self):
        pass

class HabitacionEstandar(Habitacion):
    def __init__(self, numero: int, precio_por_noche: float):
        super().__init__(numero, "Estándar", precio_por_noche)

    def aplicar_descuento(self):
        self.precio_por_noche *= 0.95

class HabitacionSuite(Habitacion):
    def __init__(self, numero: int, precio_por_noche: float):
        super().__init__(numero, "Suite", precio_por_noche)

    def aplicar_descuento(self):
        self.precio_por_noche *= 0.9

class HabitacionDeluxe(Habitacion):
    def __init__(self, numero: int, precio_por_noche: float):
        super().__init__(numero, "Deluxe", precio_por_noche)

    def aplicar_descuento(self):
        self.precio_por_noche *= 0.85

class Cliente:
    def __init__(self, nombres: str, apellidos: str, dpi: str):
        self.nombres = nombres
        self.apellidos = apellidos
        self.dpi = dpi
        self.reservas: List[Reserva] = []

class Reserva:
    def __init__(self, cliente: Cliente, habitacion: Habitacion, fecha_entrada: datetime, fecha_salida: datetime):
        self.cliente = cliente
        self.habitacion = habitacion
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.estado = "Activa"

class GestorHotel:
    def __init__(self):
        self.habitaciones: List[Habitacion] = []
        self.clientes: List[Cliente] = []
        self.reservas: List[Reserva] = []

    def agregar_habitacion(self, habitacion: Habitacion):
        self.habitaciones.append(habitacion)

    def modificar_habitacion(self, numero: int, nuevo_precio: float):
        for habitacion in self.habitaciones:
            if habitacion.numero == numero:
                habitacion.precio_por_noche = nuevo_precio
                return True
        return False

    def eliminar_habitacion(self, numero: int):
        self.habitaciones = [h for h in self.habitaciones if h.numero != numero]

    def registrar_cliente(self, cliente: Cliente):
        self.clientes.append(cliente)

    def actualizar_cliente(self, dpi: str, nuevos_nombres: str, nuevos_apellidos: str):
        for cliente in self.clientes:
            if cliente.dpi == dpi:
                cliente.nombres = nuevos_nombres
                cliente.apellidos = nuevos_apellidos
                return True
        return False

    def crear_reserva(self, reserva: Reserva):
        if reserva.habitacion.disponible:
            reserva.habitacion.disponible = False
            self.reservas.append(reserva)
            reserva.cliente.reservas.append(reserva)
            return True
        return False

    def modificar_reserva(self, cliente_dpi: str, numero_habitacion: int, nueva_fecha_entrada: datetime, nueva_fecha_salida: datetime):
        for reserva in self.reservas:
            if reserva.cliente.dpi == cliente_dpi and reserva.habitacion.numero == numero_habitacion:
                reserva.fecha_entrada = nueva_fecha_entrada
                reserva.fecha_salida = nueva_fecha_salida
                return True
        return False

    def cancelar_reserva(self, cliente_dpi: str, numero_habitacion: int):
        for reserva in self.reservas:
            if reserva.cliente.dpi == cliente_dpi and reserva.habitacion.numero == numero_habitacion:
                reserva.estado = "Cancelada"
                reserva.habitacion.disponible = True
                return True
        return False

    def consultar_disponibilidad(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Habitacion]:
        return [h for h in self.habitaciones if h.disponible]

    def obtener_cliente(self, dpi: str) -> Optional[Cliente]:
        for cliente in self.clientes:
            if cliente.dpi == dpi:
                return cliente
        return None

    def obtener_habitacion(self, numero: int) -> Optional[Habitacion]:
        for habitacion in self.habitaciones:
            if habitacion.numero == numero:
                return habitacion
        return None

class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None

    def conectar(self):
        self.conn = sqlite3.connect(self.db_name)

    def desconectar(self):
        if self.conn:
            self.conn.close()

    def crear_tablas(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habitaciones (
                numero INTEGER PRIMARY KEY,
                tipo TEXT,
                precio_por_noche REAL,
                disponible INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                dpi TEXT PRIMARY KEY,
                nombres TEXT,
                apellidos TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_dpi TEXT,
                habitacion_numero INTEGER,
                fecha_entrada TEXT,
                fecha_salida TEXT,
                estado TEXT,
                FOREIGN KEY (cliente_dpi) REFERENCES clientes (dpi),
                FOREIGN KEY (habitacion_numero) REFERENCES habitaciones (numero)
            )
        ''')
        self.conn.commit()

    def insertar_habitacion(self, habitacion: Habitacion):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO habitaciones (numero, tipo, precio_por_noche, disponible)
            VALUES (?, ?, ?, ?)
        ''', (habitacion.numero, habitacion.tipo, habitacion.precio_por_noche, int(habitacion.disponible)))
        self.conn.commit()

    def actualizar_habitacion(self, habitacion: Habitacion):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE habitaciones
            SET tipo = ?, precio_por_noche = ?, disponible = ?
            WHERE numero = ?
        ''', (habitacion.tipo, habitacion.precio_por_noche, int(habitacion.disponible), habitacion.numero))
        self.conn.commit()

    def eliminar_habitacion(self, numero: int):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM habitaciones WHERE numero = ?', (numero,))
        self.conn.commit()

    def insertar_cliente(self, cliente: Cliente):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (dpi, nombres, apellidos)
            VALUES (?, ?, ?)
        ''', (cliente.dpi, cliente.nombres, cliente.apellidos))
        self.conn.commit()

    def actualizar_cliente(self, cliente: Cliente):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE clientes
            SET nombres = ?, apellidos = ?
            WHERE dpi = ?
        ''', (cliente.nombres, cliente.apellidos, cliente.dpi))
        self.conn.commit()

    def insertar_reserva(self, reserva: Reserva):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO reservas (cliente_dpi, habitacion_numero, fecha_entrada, fecha_salida, estado)
            VALUES (?, ?, ?, ?, ?)
        ''', (reserva.cliente.dpi, reserva.habitacion.numero, reserva.fecha_entrada.isoformat(),
              reserva.fecha_salida.isoformat(), reserva.estado))
        self.conn.commit()

    def actualizar_reserva(self, reserva: Reserva):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE reservas
            SET fecha_entrada = ?, fecha_salida = ?, estado = ?
            WHERE cliente_dpi = ? AND habitacion_numero = ?
        ''', (reserva.fecha_entrada.isoformat(), reserva.fecha_salida.isoformat(), reserva.estado,
              reserva.cliente.dpi, reserva.habitacion.numero))
        self.conn.commit()

def mostrar_menu_principal():
    print("\n--- Menú Principal del Hotel ---")
    print("1. Registro de habitaciones")
    print("2. Registro de clientes")
    print("3. Registro de reservas")
    print("4. Consultar disponibilidad de habitaciones")
    print("5. Ver información de cliente y sus reservas")
    print("6. Salir")
    return input("Seleccione una opción: ")

def mostrar_submenu_habitaciones():
    print("\n--- Submenu de Habitaciones ---")
    print("1. Registrar nueva habitación")
    print("2. Modificar habitación")
    print("3. Eliminar habitación")
    print("4. Volver al menú principal")
    return input("Seleccione una opción: ")

def mostrar_submenu_clientes():
    print("\n--- Submenu de Clientes ---")
    print("1. Registrar nuevo cliente")
    print("2. Actualizar información de cliente")
    print("3. Volver al menú principal")
    return input("Seleccione una opción: ")

def mostrar_submenu_reservas():
    print("\n--- Submenu de Reservas ---")
    print("1. Realizar reserva")
    print("2. Modificar reserva")
    print("3. Cancelar reserva")
    print("4. Volver al menú principal")
    return input("Seleccione una opción: ")

def main():
    gestor = GestorHotel()
    db_manager = DatabaseManager("hotel.db")

    try:
        db_manager.conectar()
        db_manager.crear_tablas()

        while True:
            opcion_principal = mostrar_menu_principal()

            if opcion_principal == "1":  # Registro de habitaciones
                while True:
                    opcion_habitaciones = mostrar_submenu_habitaciones()
                    if opcion_habitaciones == "1":  # Registrar nueva habitación
                        numero = int(input("Número de habitación: "))
                        tipo = input("Tipo de habitación (1: Estándar, 2: Suite, 3: Deluxe): ")
                        precio = float(input("Precio por noche: "))
                        if tipo == "1":
                            habitacion = HabitacionEstandar(numero, precio)
                        elif tipo == "2":
                            habitacion = HabitacionSuite(numero, precio)
                        elif tipo == "3":
                            habitacion = HabitacionDeluxe(numero, precio)
                        else:
                            print("Tipo de habitación no válido.")
                            continue
                        gestor.agregar_habitacion(habitacion)
                        db_manager.insertar_habitacion(habitacion)
                        print("Habitación registrada con éxito.")
                    elif opcion_habitaciones == "2":  # Modificar habitación
                        numero = int(input("Número de habitación a modificar: "))
                        nuevo_precio = float(input("Nuevo precio por noche: "))
                        if gestor.modificar_habitacion(numero, nuevo_precio):
                            habitacion = gestor.obtener_habitacion(numero)
                            if habitacion:
                                db_manager.actualizar_habitacion(habitacion)
                                print("Habitación modificada con éxito.")
                            else:
                                print("Error al actualizar la habitación en la base de datos.")
                        else:
                            print("No se encontró la habitación.")
                    elif opcion_habitaciones == "3":  # Eliminar habitación
                        numero = int(input("Número de habitación a eliminar: "))
                        gestor.eliminar_habitacion(numero)
                        db_manager.eliminar_habitacion(numero)
                        print("Habitación eliminada con éxito.")
                    elif opcion_habitaciones == "4":  # Volver al menú principal
                        break
                    else:
                        print("Opción no válida. Por favor, intente de nuevo.")

            elif opcion_principal == "2":  # Registro de clientes
                while True:
                    opcion_clientes = mostrar_submenu_clientes()
                    if opcion_clientes == "1":  # Registrar nuevo cliente
                        nombres = input("Nombres del cliente: ")
                        apellidos = input("Apellidos del cliente: ")
                        dpi = input("DPI del cliente: ")
                        cliente = Cliente(nombres, apellidos, dpi)
                        gestor.registrar_cliente(cliente)
                        db_manager.insertar_cliente(cliente)
                        print("Cliente registrado con éxito.")
                    elif opcion_clientes == "2":  # Actualizar información de cliente
                        dpi = input("DPI del cliente a actualizar: ")
                        nuevos_nombres = input("Nuevos nombres: ")
                        nuevos_apellidos = input("Nuevos apellidos: ")
                        if gestor.actualizar_cliente(dpi, nuevos_nombres, nuevos_apellidos):
                            cliente = gestor.obtener_cliente(dpi)
                            if cliente:
                                db_manager.actualizar_cliente(cliente)
                                print("Información del cliente actualizada con éxito.")
                            else:
                                print("Error al actualizar el cliente en la base de datos.")
                        else:
                            print("No se encontró el cliente.")
                    elif opcion_clientes == "3":  # Volver al menú principal
                        break
                    else:
                        print("Opción no válida. Por favor, intente de nuevo.")

            elif opcion_principal == "3":  # Registro de reservas
                while True:
                    opcion_reservas = mostrar_submenu_reservas()
                    if opcion_reservas == "1":  # Realizar reserva
                        dpi_cliente = input("DPI del cliente: ")
                        numero_habitacion = int(input("Número de habitación: "))
                        fecha_entrada = datetime.strptime(input("Fecha de entrada (YYYY-MM-DD): "), "%Y-%m-%d")
                        fecha_salida = datetime.strptime(input("Fecha de  salida (YYYY-MM-DD): "), "%Y-%m-%d")
                        
                        cliente = gestor.obtener_cliente(dpi_cliente)
                        habitacion = gestor.obtener_habitacion(numero_habitacion)
                        
                        if cliente and habitacion:
                            reserva = Reserva(cliente, habitacion, fecha_entrada, fecha_salida)
                            if gestor.crear_reserva(reserva):
                                db_manager.insertar_reserva(reserva)
                                print("Reserva creada con éxito.")
                            else:
                                print("No se pudo crear la reserva. La habitación no está disponible.")
                        else:
                            print("Cliente o habitación no encontrados.")
                    elif opcion_reservas == "2":  # Modificar reserva
                        dpi_cliente = input("DPI del cliente: ")
                        numero_habitacion = int(input("Número de habitación: "))
                        nueva_fecha_entrada = datetime.strptime(input("Nueva fecha de entrada (YYYY-MM-DD): "), "%Y-%m-%d")
                        nueva_fecha_salida = datetime.strptime(input("Nueva fecha de salida (YYYY-MM-DD): "), "%Y-%m-%d")
                        
                        if gestor.modificar_reserva(dpi_cliente, numero_habitacion, nueva_fecha_entrada, nueva_fecha_salida):
                            for reserva in gestor.reservas:
                                if reserva.cliente.dpi == dpi_cliente and reserva.habitacion.numero == numero_habitacion:
                                    db_manager.actualizar_reserva(reserva)
                                    break
                            print("Reserva modificada con éxito.")
                        else:
                            print("No se encontró la reserva.")
                    elif opcion_reservas == "3":  # Cancelar reserva
                        dpi_cliente = input("DPI del cliente: ")
                        numero_habitacion = int(input("Número de habitación: "))
                        if gestor.cancelar_reserva(dpi_cliente, numero_habitacion):
                            for reserva in gestor.reservas:
                                if reserva.cliente.dpi == dpi_cliente and reserva.habitacion.numero == numero_habitacion:
                                    db_manager.actualizar_reserva(reserva)
                                    break
                            print("Reserva cancelada con éxito.")
                        else:
                            print("No se encontró la reserva.")
                    elif opcion_reservas == "4":  # Volver al menú principal
                        break
                    else:
                        print("Opción no válida. Por favor, intente de nuevo.")

            elif opcion_principal == "4":  # Consultar disponibilidad de habitaciones
                fecha_inicio = datetime.strptime(input("Fecha de inicio (YYYY-MM-DD): "), "%Y-%m-%d")
                fecha_fin = datetime.strptime(input("Fecha de fin (YYYY-MM-DD): "), "%Y-%m-%d")
                
                habitaciones_disponibles = gestor.consultar_disponibilidad(fecha_inicio, fecha_fin)
                print("Habitaciones disponibles:")
                for habitacion in habitaciones_disponibles:
                    print(f"Número: {habitacion.numero}, Tipo: {habitacion.tipo}, Precio: ${habitacion.precio_por_noche}")

            elif opcion_principal == "5":  # Ver información de cliente y sus reservas
                dpi_cliente = input("DPI del cliente: ")
                cliente = gestor.obtener_cliente(dpi_cliente)
                if cliente:
                    print(f"Información del cliente:")
                    print(f"Nombres: {cliente.nombres}")
                    print(f"Apellidos: {cliente.apellidos}")
                    print(f"DPI: {cliente.dpi}")
                    print("Reservas:")
                    for reserva in cliente.reservas:
                        print(f"Habitación: {reserva.habitacion.numero}, Entrada: {reserva.fecha_entrada}, Salida: {reserva.fecha_salida}, Estado: {reserva.estado}")
                else:
                    print("Cliente no encontrado.")

            elif opcion_principal == "6":  # Salir
                print("Gracias por usar el sistema. ¡Hasta luego!")
                break

            else:
                print("Opción no válida. Por favor, intente de nuevo.")

    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
    finally:
        db_manager.desconectar()

if __name__ == "__main__":
    main()