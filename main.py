"""Interfaz gráfica para la aplicación de cálculo de distancias entre contenedores."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import os
from data_handler import DataHandler
from distance_calculator import DistanceCalculator


class DistanceMatrixApp:
    """Aplicación GUI para calcular y visualizar matriz de distancias."""
    
    def __init__(self, root):
        """Inicializa la aplicación."""
        self.root = root
        self.root.title("Calculadora de Distancias entre Contenedores")
        self.root.geometry("1200x700")
        
        # Variables
        self.data_handler = DataHandler()
        self.distance_calculator = DistanceCalculator()
        self.df_locations = None
        self.distance_matrix = None
        self.ids = None
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        
        # Frame superior: controles
        frame_controls = ttk.Frame(self.root)
        frame_controls.pack(fill=tk.X, padx=10, pady=10)
        
        # Botón cargar datos
        ttk.Button(
            frame_controls,
            text="1. Cargar datos (Excel)",
            command=self.load_data
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón calcular distancias
        ttk.Button(
            frame_controls,
            text="2. Calcular Distancias",
            command=self.calculate_distances
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón exportar
        ttk.Button(
            frame_controls,
            text="3. Exportar Datos",
            command=self.export_data
        ).pack(side=tk.LEFT, padx=5)
        
        # Label de estado
        self.status_label = ttk.Label(
            frame_controls,
            text="Estado: Esperando cargar datos...",
            foreground="blue"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Frame para información de datos
        frame_info = ttk.LabelFrame(self.root, text="Información de Datos")
        frame_info.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_text = tk.Text(frame_info, height=3, width=100)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.config(state=tk.DISABLED)
        
        # Frame para tabla de distancias
        frame_table = ttk.LabelFrame(self.root, text="Matriz de Distancias (en km)")
        frame_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear Treeview con scrollbars
        style = ttk.Style()
        style.configure('Treeview', rowheight=25)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_table, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(frame_table, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(
            frame_table,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=15
        )
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        frame_table.grid_rowconfigure(0, weight=1)
        frame_table.grid_columnconfigure(0, weight=1)
        
        # Frame inferior: opciones
        frame_options = ttk.LabelFrame(self.root, text="Opciones")
        frame_options.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_options, text="Método de cálculo:").pack(side=tk.LEFT, padx=5)
        self.use_osrm = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame_options,
            text="Usar OSRM (distancia en carretera)",
            variable=self.use_osrm
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            frame_options,
            text="(Desmarcar usa distancia en línea recta)",
            foreground="gray"
        ).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        """Carga los datos del archivo Excel."""
        try:
            # Buscar automáticamente destinos.xlsx en la carpeta actual
            excel_file = Path("destinos.xlsx")
            
            if not excel_file.exists():
                messagebox.showerror("Error", "archivo 'destinos.xlsx' no encontrado")
                return
            
            self.df_locations = self.data_handler.read_excel(str(excel_file))
            
            if self.df_locations is None or len(self.df_locations) == 0:
                messagebox.showerror("Error", "No se pudieron cargar los datos del Excel")
                return
            


            

            
            self.ids = self.df_locations['ID'].tolist()
            
            # Actualizar información
            info = f"Contenedores cargados: {len(self.df_locations)}\n"
            info += f"Latitud (min): {self.df_locations['Latitud'].min():.4f}, (max): {self.df_locations['Latitud'].max():.4f}\n"
            info += f"Longitud (min): {self.df_locations['Longitud'].min():.4f}, (max): {self.df_locations['Longitud'].max():.4f}"
            
            self.update_info(info)
            self.status_label.config(
                text=f"Estado: {len(self.df_locations)} contenedores cargados",
                foreground="green"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            self.status_label.config(text="Estado: Error al cargar datos", foreground="red")
    
    def calculate_distances(self):
        """Calcula la matriz de distancias en un hilo separado."""
        if self.df_locations is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar los datos")
            return
        
        # Deshabiitar botón durante cálculo
        self.update_info("CALCULANDO DISTANCIAS... Esto puede tomar unos minutos.\n(No cierre la aplicación)")
        self.status_label.config(text="Estado: Calculando...", foreground="orange")
        
        # Ejecutar cálculo en hilo separado
        thread = threading.Thread(target=self._calculate_distances_thread)
        thread.start()
    
    def _calculate_distances_thread(self):
        """Calcula las distancias en un hilo."""
        try:
            self.distance_matrix = self.distance_calculator.calculate_distance_matrix(
                self.df_locations,
                use_osrm=self.use_osrm.get(),
                verbose=True
            )
            
            # Actualizar tabla
            self.root.after(0, self.update_table)
            
            self.status_label.config(
                text="Estado: Distancias calculadas correctamente",
                foreground="green"
            )
            
        except Exception as e:
            self.status_label.config(
                text=f"Estado: Error al calcular: {str(e)}",
                foreground="red"
            )
            messagebox.showerror("Error", f"Error al calcular distancias: {str(e)}")
    
    def update_table(self):
        """Actualiza la tabla con la matriz de distancias."""
        # Limpiar tabla anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Definir columnas
        columns = ["ID"] + self.ids
        self.tree["columns"] = columns
        self.tree.column("#0", width=0, stretch=tk.NO)
        
        # Encabezados
        self.tree.column("ID", width=80, anchor=tk.CENTER)
        self.tree.heading("ID", text="ID")
        
        for col in self.ids:
            self.tree.column(col, width=80, anchor=tk.CENTER)
            self.tree.heading(col, text=str(col))
        
        # Datos
        for i, id_origen in enumerate(self.ids):
            values = [id_origen] + [
                f"{self.distance_matrix[i][j]:.1f}" 
                for j in range(len(self.ids))
            ]
            self.tree.insert("", tk.END, values=values)
        
        self.update_info(
            f"Matriz de distancias calculada para {len(self.ids)} contenedores.\n"
            f"Total de pares: {len(self.ids) * len(self.ids)}\n"
            f"Ahora puedes exportar los datos."
        )
    
    def update_info(self, text):
        """Actualiza el texto de información."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)
    
    def export_data(self):
        """Menu para exportar datos."""
        if self.distance_matrix is None:
            messagebox.showwarning("Advertencia", "Primero debes calcular las distancias")
            return
        
        # Crear ventana de exportación
        export_window = tk.Toplevel(self.root)
        export_window.title("Exportar Datos")
        export_window.geometry("400x200")
        
        ttk.Label(
            export_window,
            text="Selecciona el formato de exportación:",
            font=("Arial", 11, "bold")
        ).pack(pady=10)
        
        def export_excel():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")]
            )
            if file_path:
                self.data_handler.save_distance_matrix_excel(
                    self.distance_matrix,
                    self.ids,
                    file_path
                )
                messagebox.showinfo("Éxito", f"Archivo guardado en:\n{file_path}")
                export_window.close()
        
        def export_json():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON", "*.json"), ("Todos", "*.*")]
            )
            if file_path:
                self.data_handler.save_distance_matrix_json(
                    self.distance_matrix,
                    self.ids,
                    file_path
                )
                messagebox.showinfo("Éxito", f"Archivo guardado en:\n{file_path}")
                export_window.close()
        
        def export_csv():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
            )
            if file_path:
                self.data_handler.save_distance_matrix_csv(
                    self.distance_matrix,
                    self.ids,
                    file_path
                )
                messagebox.showinfo("Éxito", f"Archivo guardado en:\n{file_path}")
                export_window.close()
        
        ttk.Button(
            export_window,
            text="Exportar a Excel (.xlsx)",
            command=export_excel,
            width=30
        ).pack(pady=10)
        
        ttk.Button(
            export_window,
            text="Exportar a JSON (.json)",
            command=export_json,
            width=30
        ).pack(pady=10)
        
        ttk.Button(
            export_window,
            text="Exportar a CSV (.csv)",
            command=export_csv,
            width=30
        ).pack(pady=10)


def main():
    """Punto de entrada de la aplicación."""
    root = tk.Tk()
    app = DistanceMatrixApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
