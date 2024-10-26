import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal
import socket

fecha_actual = datetime.now().strftime('%Y%m%d')
global _entry_referencia
global _entry_cuota
global _entry_monto

def send_trama(trama):
    try:
        host = "127.0.0.1"
        port = 5555
        client_socket = socket.socket()
        client_socket.connect((host, port))
        client_socket.send(trama.encode())
        data = client_socket.recv(1024).decode()
        client_socket.close()
        return data
    except Exception as e:
        messagebox.showerror("Error de conexión", str(e))
        return None

def on_select(event):
    # Obtiene el elemento seleccionado
    selected_item = tabla.selection()
    if selected_item:
        # Obtiene los valores de la fila seleccionada
        item_values = tabla.item(selected_item, 'values')
        print("Fila seleccionada:", item_values)
        _entry_referencia.delete(0, "end")
        _entry_referencia.insert(0,item_values[6])
        _entry_cuota.delete(0, "end")
        _entry_cuota.insert(0,item_values[1].zfill(2))
        _entry_monto.delete(0, "end")
        _entry_monto.insert(0,item_values[2].zfill(2))



def consultar_cuotas():
    cliente_id = entry_cliente.get().zfill(8)

    if len(cliente_id) != 8:
        messagebox.showwarning("Advertencia", "El ID de cliente no es valido")
        return
    trama = f"01{cliente_id}"
    respuesta = send_trama(trama)
    if respuesta:
        respuesta = respuesta[:-1]
        for item in tabla.get_children():
            tabla.delete(item)

        filas = respuesta.split("+")
        print("fila: ", filas)
        data = []
        print(respuesta)
        for t in filas:
            if t:
                campos = t.split("$")
                if len(campos) >= 6:
                    cliente_id = int(campos[1])
                    cuota = int(campos[2])
                    monto = float(campos[3]) / 100.0
                    dia = campos[4][0:2]
                    mes = campos[4][2:4]
                    anio = campos[4][4:8]
                    fecha_cuota_pago = f"{dia}/{mes}/{anio}"## campos[4]
                    dia2 = campos[6][0:2]
                    mes2 = campos[6][2:4]
                    anio2 = campos[6][4:8]
                    fecha_pago = f"{dia2}/{mes2}/{anio2}"
                    estado = campos[5]
                    referencia = campos[7]

                    data.append(
                        (cliente_id, cuota, monto, fecha_cuota_pago, fecha_pago, estado, referencia)
                    )

        
        for item in data:
            print(item)
            tabla.insert("", "end", values=item)

    else:
        for item in tabla.get_children():
            tabla.delete(item)


def pagar_cuota():
    cliente_id = entry_cliente.get().zfill(8)
    cuota = _entry_cuota.get()
    fecha = entry_fecha_pago.get()
    monto = str(int(Decimal(_entry_monto.get())*100)).zfill(9)
    referencia = _entry_referencia.get()
    print("monto", monto)
    if len(cliente_id) != 8 or len(cuota) != 2 or len(fecha) != 8 or len(monto) != 9 or len(referencia) > 0:
        messagebox.showwarning("Advertencia", "Revisa los campos ingresados")
        return

    trama = f"02{cliente_id}{cuota}{fecha}{monto}"
    respuesta = send_trama(trama)
    list_result = respuesta.split("$")
    mensaje_resp = f"Pago realizado: {list_result[1]}" if list_result[0] == "00" else "Error, no se pudo realizar el pago" 
    print("respuesta trama pago: ", respuesta)
    consultar_cuotas()
    messagebox.showinfo("Respuesta del servidor", mensaje_resp)



def revertir_pago():
    cliente_id = entry_cliente.get().zfill(8)
    referencia = _entry_referencia.get()

    if len(cliente_id) != 8 or not referencia:
        messagebox.showwarning("Advertencia", "Revisa los campos ingresados")
        return
    trama = f"03{cliente_id}{referencia}"
    respuesta = send_trama(trama)
    consultar_cuotas()
    if respuesta:
        messagebox.showinfo("Respuesta del servidor", f"{respuesta}")




ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Sistema de Pagos por Cuotas Grupo #2")
root.geometry("1000x600")

title_label = ctk.CTkLabel(
    root,
    text="Sistema de Pagos por Cuotas Grupo #2",
    font=ctk.CTkFont(size=24, weight="bold"),
)
title_label.pack(pady=20)

form_frame = ctk.CTkFrame(root)
form_frame.pack(pady=10, padx=20, fill="x")

entry_cliente_label = ctk.CTkLabel(form_frame, text="ID Cliente:")
entry_cliente_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_cliente = ctk.CTkEntry(form_frame, width=200)
entry_cliente.grid(row=0, column=1, padx=10, pady=10)

entry_referencia_label = ctk.CTkLabel(form_frame, text="Referencia:")
entry_referencia_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
_entry_referencia = ctk.CTkEntry(form_frame, width=200)
_entry_referencia.grid(row=1, column=1, padx=10, pady=10)

entry_monto_label = ctk.CTkLabel(form_frame, text="Monto a Pagar:")
entry_monto_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
_entry_monto = ctk.CTkEntry(form_frame, width=200)
_entry_monto.grid(row=2, column=1, padx=10, pady=10)

entry_cuota_label = ctk.CTkLabel(form_frame, text="# Cuota:")
entry_cuota_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
_entry_cuota = ctk.CTkEntry(form_frame, width=200)
_entry_cuota.grid(row=3, column=1, padx=10, pady=10)

entry_fecha_pago_label = ctk.CTkLabel(form_frame, text="Fecha de Pago:")
entry_fecha_pago_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
entry_fecha_pago = ctk.CTkEntry(form_frame, width=200)
entry_fecha_pago.insert(0, fecha_actual)
entry_fecha_pago.grid(row=4, column=1, padx=10, pady=10)


button_frame = ctk.CTkFrame(form_frame)
button_frame.grid(row=0, column=2, rowspan=4, padx=85, pady=50, sticky="n")

consultar_button = ctk.CTkButton(
    button_frame, text="Consultar Cuotas", command=consultar_cuotas, width=150
)
consultar_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

pagar_button = ctk.CTkButton(
    button_frame, text="Pagar Cuota", command=pagar_cuota, width=150
)
pagar_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

revertir_button = ctk.CTkButton(
    button_frame, text="Revertir Pago", command=revertir_pago, width=150
)
revertir_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")


table_frame = ctk.CTkFrame(root)
table_frame.pack(pady=20, padx=20, fill="both", expand=True)

columnas = ("ID Cliente", "Cuota", "Monto", "FechaCuotaPago", "FechaPago", "Estado", "Referencia")
tabla = ttk.Treeview(table_frame, columns=columnas, show="headings", height=8)

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, anchor="center")
    
tabla.bind("<<TreeviewSelect>>", on_select)
tabla.pack(fill="both", expand=True)

root.mainloop()
