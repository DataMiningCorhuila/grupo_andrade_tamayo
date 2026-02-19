#!/usr/bin/env python3
import json
import os
import logging
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Límite de personajes a mostrar (cambiar según necesidad)
LIMIT_CHARACTERS = 20

class SimpsonsViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("The Simpsons Characters Viewer")
        self.root.geometry("800x600")
        
        # Directorio de datos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, '..', 'data')
        json_file = os.path.join(data_dir, 'simpsons_characters.json')
        
        # Cargar datos
        logger.info(f"Cargando datos desde {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            all_characters = json.load(f)
        
        # Aplicar límite
        self.total_characters = len(all_characters)
        self.characters = all_characters[:LIMIT_CHARACTERS]
        logger.info(f"✅ Cargados {self.total_characters} personajes (mostrando {len(self.characters)})")
        
        # Configurar interfaz
        self.setup_ui()
        
    def setup_ui(self):
        # Título
        title = tk.Label(self.root, text="🎬 The Simpsons Characters 🎬", 
                        font=("Arial", 20, "bold"), bg="#FFD90F", pady=10)
        title.pack(fill=tk.X)
        
        # Frame con scroll
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=1)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame, bg="#87CEEB")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Frame para contenido
        content_frame = tk.Frame(canvas, bg="#87CEEB")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Permitir scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Contador
        counter_text = f"Mostrando {len(self.characters)} de {self.total_characters} personajes"
        counter = tk.Label(content_frame, text=counter_text,
                          font=("Arial", 12, "bold"), bg="#87CEEB", pady=10)
        counter.pack()
        
        # Mostrar personajes
        for character in self.characters:
            self.create_character_card(content_frame, character)
    
    def create_character_card(self, parent, character):
        # Frame para cada personaje
        card = tk.Frame(parent, bg="white", relief=tk.RAISED, borderwidth=2, padx=15, pady=15)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        # Frame horizontal para imagen y datos
        content = tk.Frame(card, bg="white")
        content.pack(fill=tk.X)
        
        # Imagen (lado izquierdo)
        img_frame = tk.Frame(content, bg="white")
        img_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        try:
            # Descargar imagen
            img_url = f"https://cdn.thesimpsonsapi.com/500{character['portrait_path']}"
            response = requests.get(img_url, timeout=5)
            response.raise_for_status()
            
            # Procesar imagen
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_data)
            
            img_label = tk.Label(img_frame, image=photo, bg="white")
            img_label.image = photo  # Mantener referencia
            img_label.pack()
        except Exception as e:
            logger.warning(f"Error cargando imagen para {character['name']}: {e}")
            placeholder = tk.Label(img_frame, text="❌\nImagen no\ndisponible", 
                                  bg="#f0f0f0", width=20, height=8, 
                                  font=("Arial", 10))
            placeholder.pack()
        
        # Datos (lado derecho)
        data_frame = tk.Frame(content, bg="white")
        data_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # ID
        id_label = tk.Label(data_frame, text=f"ID: {character['id']}", 
                           font=("Arial", 10), bg="white", fg="#666", anchor="w")
        id_label.pack(fill=tk.X, pady=2)
        
        # Nombre
        name_label = tk.Label(data_frame, text=character['name'], 
                             font=("Arial", 16, "bold"), bg="white", anchor="w")
        name_label.pack(fill=tk.X, pady=5)
        
        # Ocupación
        occupation_label = tk.Label(data_frame, 
                                   text=f"Ocupación: {character['occupation']}", 
                                   font=("Arial", 11), bg="white", anchor="w", 
                                   wraplength=500, justify="left")
        occupation_label.pack(fill=tk.X, pady=2)
        
        # Fecha de nacimiento
        birthdate = character['birthdate'] if character['birthdate'] else "Desconocida"
        birthdate_label = tk.Label(data_frame, 
                                  text=f"Fecha de nacimiento: {birthdate}", 
                                  font=("Arial", 11), bg="white", anchor="w")
        birthdate_label.pack(fill=tk.X, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpsonsViewer(root)
    logger.info("🚀 Iniciando visualizador...")
    root.mainloop()
