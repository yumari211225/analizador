import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import ply.lex as lex

# Lista de tokens
tokens = [
    'PROGRAMA', 'FIN', 'LEER', 'IMPRIMIR', 'ENTERO', 'IDENTIFICADOR',
    'NUMERO', 'PARENIZQ', 'PARENDER', 'LLAVEIZQ', 'LLAVEDER',
    'PUNTOCOMA', 'COMA', 'ASIGNACION', 'MAS', 'LA', 'ES', 'VAR', 'CADENA'
]

# Palabras reservadas
reserved = {
    'programa': 'PROGRAMA', 'end': 'FIN', 'read': 'LEER', 'printf': 'IMPRIMIR',
    'int': 'ENTERO', 'la': 'LA', 'es': 'ES'
}

# Lista de identificadores específicos
identificadores_especificos = ['suma', 'resta', 'multiplicación', 'división']

t_ignore = ' \t'
t_PARENIZQ = r'\('
t_PARENDER = r'\)'
t_LLAVEIZQ = r'\{'
t_LLAVEDER = r'\}'
t_PUNTOCOMA = r';'
t_COMA = r','
t_ASIGNACION = r'='
t_MAS = r'\+'

def t_CADENA(t):
    r'\"([^\\"]|\\.)*\"'
    cadena = t.value[1:-1]  # remove the double quotes
    palabras = cadena.split()
    new_tokens = []
    for palabra in palabras:
        if palabra in reserved:
            new_tokens.append((reserved[palabra], palabra))
        elif palabra in identificadores_especificos:
            new_tokens.append(('IDENTIFICADOR', palabra))
        else:
            new_tokens.append(('CADENA', palabra))
    t.value = new_tokens
    t.type = 'CADENA'
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    elif t.value in identificadores_especificos:
        t.type = 'IDENTIFICADOR'
    else:
        t.type = 'VAR'
    return t

def t_error(t):
    print("Carácter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

lexer = lex.lex()

class LexicalAnalyzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador Léxico con PLY")
        self.geometry("1200x700")
        self.lexer = lex.lex()
        self.create_widgets()

    def create_widgets(self):
        # Configurar la grilla
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Añadir un widget Label para la imagen izquierda
        self.image_label_left = tk.Label(self)
        self.image_label_left.grid(row=1, column=0, padx=10, pady=20, sticky="nsew")

        self.text_input = tk.Text(self, height=10)
        self.text_input.grid(row=1, column=1, padx=10, pady=20, sticky="nsew")

        # Añadir un widget Label para la imagen derecha
        self.image_label_right = tk.Label(self)
        self.image_label_right.grid(row=1, column=2, padx=10, pady=20, sticky="nsew")

        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=1, pady=10)

        analyze_button = tk.Button(button_frame, text="Analizar", command=self.analyze_code)
        analyze_button.pack(side=tk.LEFT, padx=10)

        clear_button = tk.Button(button_frame, text="Borrar Todo", command=self.clear_text)
        clear_button.pack(side=tk.LEFT, padx=10)

        load_button = tk.Button(button_frame, text="Cargar Archivo", command=self.load_file)
        load_button.pack(side=tk.LEFT, padx=10)

        columns = ('Línea', 'Token', 'PR', 'ID', 'PI', 'PD', 'LI', 'LD', 'PC', 'VAR', 'SUM', 'CO', 'ER')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        self.tree.grid(row=3, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")

    def analyze_code(self):
        code = self.text_input.get("1.0", tk.END)
        self.lexer.lineno = 1  # Reiniciar el número de línea
        self.lexer.input(code)
        token_counts = {col: 0 for col in self.tree['columns'][1:]}

        for i in self.tree.get_children():
            self.tree.delete(i)

        for tok in self.lexer:
            if not tok:
                continue
            if tok.type == 'CADENA':
                for sub_token in tok.value:
                    row = [tok.lineno, sub_token[1]] + ['X' if self.match_token(sub_token[0], col) else '' for col in self.tree['columns'][2:]]
                    self.tree.insert('', tk.END, values=row)
                    for i, col in enumerate(self.tree['columns'][2:], 2):
                        if row[i] == 'X':
                            token_counts[col] += 1
            else:
                row = [tok.lineno, tok.value] + ['X' if self.match_token(tok.type, col) else '' for col in self.tree['columns'][2:]]
                self.tree.insert('', tk.END, values=row)
                for i, col in enumerate(self.tree['columns'][2:], 2):
                    if row[i] == 'X':
                        token_counts[col] += 1

        total_row = ['Total', ''] + [token_counts[col] for col in self.tree['columns'][2:]]
        self.tree.insert('', tk.END, values=total_row, tags=('total',))
        self.tree.tag_configure('total', background='green')

    def match_token(self, token_type, column):
        mapping = {
            'PROGRAMA': 'PR', 'FIN': 'PR', 'LEER': 'PR', 'IMPRIMIR': 'PR', 'ENTERO': 'PR', 'LA': 'PR', 'ES': 'PR',
            'IDENTIFICADOR': 'ID', 'PARENIZQ': 'PI', 'PARENDER': 'PD', 'LLAVEIZQ': 'LI',
            'LLAVEDER': 'LD', 'PUNTOCOMA': 'PC', 'COMA': 'CO', 'ASIGNACION': 'OP',
            'VAR': 'VAR', 'SUM': 'SUM', 'ER': 'ERR'
        }
        return mapping.get(token_type, '') == column

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert(tk.END, file_content)

    def load_image_left(self, image_path):
        image = Image.open(image_path)
        image = image.resize((300, 200), Image.LANCZOS)  # Cambiar el tamaño de la imagen
        photo = ImageTk.PhotoImage(image)
        self.image_label_left.config(image=photo)
        self.image_label_left.image = photo

    def load_image_right(self, image_path):
        image = Image.open(image_path)
        image = image.resize((300, 200), Image.LANCZOS)  # Cambiar el tamaño de la imagen
        photo = ImageTk.PhotoImage(image)
        self.image_label_right.config(image=photo)
        self.image_label_right.image = photo

if __name__ == "__main__":
    left_image_path = "ChangoCoquero.jpg"
    right_image_path = "ChangoManguero.jpg"
    
    if not os.path.exists(left_image_path) or not os.path.exists(right_image_path):
        print("Error, falta de changos")
    else:
        app = LexicalAnalyzerGUI()
        app.load_image_left("ChangoCoquero.jpg")
        app.load_image_right("ChangoManguero.jpg")
        app.mainloop()
