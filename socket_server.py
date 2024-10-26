import random
import string
import socket
import mysql.connector
from mysql.connector import Error


def ConexionDB():
    try:
        connection = mysql.connector.connect(
            host="", database="socket", user="admin", password="Admin.123"
        )
        return connection
    except Error as ex:
        print(f"Error al conectarse a DB: {ex}")
        return None


def ConsultarPago(num_cliente):
    connDB = ConexionDB()
    if connDB:
        cursor = connDB.cursor()
        sql = f"SELECT ClienteId, Couta, Monto, FechaCuotaPago, Estado, FechaPago, Referencia  FROM Pagos WHERE ClienteId = {num_cliente}"
        cursor.execute(sql)
        listaCuotasResult = cursor.fetchall()
        connDB.close()
        return listaCuotasResult

    return []


def PagarCuota(num_cliente, cuota, fecha_afectacion, monto, referencia):
    connDB = ConexionDB()
    if connDB:
        cursor = connDB.cursor()
        sql = f"UPDATE Pagos SET Estado = 'C', FechaPago = '{fecha_afectacion}', Referencia = '{referencia}' WHERE ClienteId = {num_cliente} AND Couta = {cuota}"
        cursor.execute(sql)
        connDB.commit()
        connDB.close()
        return True
    return False


def RevertirPago(referencia):
    connDB = ConexionDB()
    if connDB:
        cursor = connDB.cursor()
        sql = "UPDATE Pagos SET Estado='A', Referencia='', FechaPago=NULL WHERE Referencia=%s"
        cursor.execute(sql, (referencia,))
        connDB.commit()
        connDB.close()
        return True

    return False


def ConsultarReferencia(referencia):
    connDB = ConexionDB()
    if connDB:
        cursor = connDB.cursor()
        sql = "SELECT Referencia FROM Pagos WHERE Referencia=%s"
        cursor.execute(sql, (referencia,))
        result = cursor.fetchone()
        connDB.close()
        return result

    return None


def generar_referencia(longitud):
    caracteres = string.ascii_letters + string.digits
    num_referencia = "".join(random.choice(caracteres) for _ in range(longitud))
    return num_referencia


def server_run():
    host = "127.0.0.1"
    port = 5555
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(5)

    while True:
        conn, address = server_socket.accept()
        print(f"Conexion desde {address}")

        data = conn.recv(1024).decode()
        print(f"Datos recebidos: {data}")

        metodo = data[:2]
        cliente_num = int(data[2:10])
        print(f"metodo: {metodo}, clienteId: {cliente_num}")

        if metodo == "01":
            cuotas_pendientes = ConsultarPago(cliente_num)
            trama_salida = ""

            for cuota in cuotas_pendientes:
                print("fecha: ", cuota[5])
                clienteNum = cuota[0]
                cuotaNum = cuota[1]
                monto_str = str(int(cuota[2] * 100)).zfill(9)
                fecha_str = cuota[3].strftime("%d%m%Y")
                estado = cuota[4]
                fecha_pagostr = (
                    "--------" if cuota[5] == None else cuota[5].strftime("%d%m%Y")
                )
                referencia = "" if cuota[6] == None else cuota[6]
                trama_salida += f"${clienteNum}${cuotaNum}${monto_str}${fecha_str}${estado}${fecha_pagostr}${referencia}+"

            conn.send(trama_salida.encode())

        if metodo == "02":
            print("metodo de pago: ", metodo)
            cuota = int(data[10:12])
            fecha_afectacion = data[12:20]
            monto = int(data[20:29])
            referencia = generar_referencia(8)
            response_result = PagarCuota(
                cliente_num, cuota, fecha_afectacion, monto, referencia
            )

            print("pago: ", response_result)
            resp_status = f"00${referencia}" if response_result else "01"
            conn.send(f"{resp_status}".encode())

        if metodo == "03":
            referencia = data[10:18]

            existeReferencia = ConsultarReferencia(referencia)
            print(existeReferencia)
            if existeReferencia != None:
                respuesta = RevertirPago(referencia)
                if respuesta == True:
                    trama_salida = "¡Pago revertido con Exito!"
                else:
                    trama_salida = "¡Oh no, ha ocurrido un error, porfavor contacta al administrador!"
            else:
                trama_salida = "¡ERROR: No existe ningun pago con esa referencia!"

            conn.send(trama_salida.encode())

        conn.close()


if __name__ == "__main__":
    server_run()
