import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
import datetime

# Función para agregar productos al inventario
def agregar_producto():
    producto = producto_entry.get()
    cantidad = cantidad_entry.get()
    precio = precio_entry.get()
    
    if producto and cantidad and precio:
        try:
            conn = psycopg2.connect(
               host="localhost",
               database="inventario",
               user="postgres",
               password="123456"
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)", (producto, cantidad, precio))
            conn.commit()
            conn.close()
            actualizar_inventario()
        except psycopg2.IntegrityError:
            messagebox.showerror("Error", "El nombre del producto ya existe en el inventario.")
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
    else:
        messagebox.showerror("Error", "Ingrese un nombre de producto, cantidad y precio válidos")

# Función para registrar la salida de productos
def registrar_salida():
    producto = producto_entry.get()
    cantidad = cantidad_entry.get()
    
    if producto and cantidad:
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="inventario",
                user="postgres",
                password="123456"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT cantidad FROM productos WHERE nombre = %s", (producto,))
            producto_cantidad = cursor.fetchone()
            
            if producto_cantidad and producto_cantidad[0] >= int(cantidad):
                # Actualiza la cantidad en el inventario
                nueva_cantidad = producto_cantidad[0] - int(cantidad)
                cursor.execute("UPDATE productos SET cantidad = %s WHERE nombre = %s", (nueva_cantidad, producto))
                
                # Registra la salida en la tabla de ventas
                cursor.execute("INSERT INTO ventas (producto, cantidad, fecha) VALUES (%s, %s, %s)",
                               (producto, cantidad, datetime.datetime.now()))
                
                conn.commit()
                conn.close()
                
                actualizar_inventario()  # Actualiza la tabla de inventario
                print(f"Registro de salida exitoso: Producto: {producto}, Cantidad: {cantidad}")
            else:
                messagebox.showerror("Error", "No hay suficiente stock de este producto.")
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Error al registrar salida: {str(e)}")
    else:
        messagebox.showerror("Error", "Ingrese un nombre de producto y una cantidad válidos")

# Función para actualizar la tabla de inventario
def actualizar_inventario():
    # Limpiar la tabla
    for row in tabla_inventario.get_children():
        tabla_inventario.delete(row)
    
    # Obtener los productos del inventario y agregarlos a la tabla
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="inventario",
            user="postgres",
            password="123456"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, cantidad, precio FROM productos")
        productos = cursor.fetchall()
        conn.close()
        
        for i, (producto, cantidad, precio) in enumerate(sorted(productos)):
            tabla_inventario.insert('', 'end', values=(i+1, producto, cantidad, precio))
    except psycopg2.Error as e:
        messagebox.showerror("Error", f"Error al obtener inventario: {str(e)}")

# Crear una ventana
ventana = tk.Tk()
ventana.title("Sistema de Inventario")

# Crear etiquetas y campos de entrada
producto_label = tk.Label(ventana, text="Nombre del producto:")
cantidad_label = tk.Label(ventana, text="Cantidad:")
precio_label = tk.Label(ventana, text="Precio:")
producto_entry = tk.Entry(ventana)
cantidad_entry = tk.Entry(ventana)
precio_entry = tk.Entry(ventana)

# Crear botones
agregar_button = tk.Button(ventana, text="Agregar", command=agregar_producto)
salida_button = tk.Button(ventana, text="Registrar Salida", command=registrar_salida)

# Crear tabla de inventario
tabla_inventario = ttk.Treeview(ventana, columns=('Número', 'Producto', 'Cantidad', 'Precio'), show='headings')
tabla_inventario.heading('Número', text='Número')
tabla_inventario.heading('Producto', text='Producto')
tabla_inventario.heading('Cantidad', text='Cantidad')
tabla_inventario.heading('Precio', text='Precio')

# Colocar widgets en la ventana
producto_label.pack()
producto_entry.pack()
cantidad_label.pack()
cantidad_entry.pack()
precio_label.pack()
precio_entry.pack()
agregar_button.pack()
salida_button.pack()
tabla_inventario.pack()

# Iniciar la aplicación
actualizar_inventario()
ventana.mainloop()
