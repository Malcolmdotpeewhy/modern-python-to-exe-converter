"""
Simple Calculator Example
A basic GUI calculator using tkinter to test GUI application conversion.
"""

import tkinter as tk
from tkinter import ttk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Calculator")
        self.root.geometry("300x400")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.current = "0"
        self.previous = ""
        self.operator = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        # Display
        self.display = tk.Label(
            self.root, 
            text=self.current, 
            font=('Arial', 20),
            bg='#404040',
            fg='#ffffff',
            anchor='e',
            padx=10
        )
        self.display.pack(fill='x', padx=10, pady=(10, 5))
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#2b2b2b')
        button_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Button configuration
        button_config = {
            'font': ('Arial', 16),
            'bg': '#404040',
            'fg': '#ffffff',
            'activebackground': '#505050',
            'border': 0,
            'padx': 10,
            'pady': 10
        }
        
        # Create buttons
        buttons = [
            ['C', '±', '%', '/'],
            ['7', '8', '9', 'x'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '', '.', '=']
        ]
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text == '':
                    continue
                    
                if text == '0':
                    # Make 0 button span two columns
                    btn = tk.Button(
                        button_frame,
                        text=text,
                        command=lambda t=text: self.button_click(t),
                        **button_config
                    )
                    btn.grid(row=i, column=j, columnspan=2, sticky='nsew', padx=1, pady=1)
                else:
                    # Operator buttons in different color
                    if text in ['+', '-', 'x', '/', '=']:
                        config = button_config.copy()
                        config['bg'] = '#0078d4'
                        config['activebackground'] = '#106ebe'
                    else:
                        config = button_config
                    
                    btn = tk.Button(
                        button_frame,
                        text=text,
                        command=lambda t=text: self.button_click(t),
                        **config
                    )
                    btn.grid(row=i, column=j, sticky='nsew', padx=1, pady=1)
        
        # Configure grid weights
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            button_frame.grid_columnconfigure(j, weight=1)
    
    def button_click(self, value):
        if value.isdigit() or value == '.':
            if self.current == "0":
                self.current = value
            else:
                self.current += value
        
        elif value in ['+', '-', 'x', '/']:
            self.previous = self.current
            self.current = "0"
            self.operator = value
        
        elif value == '=':
            if self.operator and self.previous:
                try:
                    if self.operator == '+':
                        result = float(self.previous) + float(self.current)
                    elif self.operator == '-':
                        result = float(self.previous) - float(self.current)
                    elif self.operator == 'x':
                        result = float(self.previous) * float(self.current)
                    elif self.operator == '/':
                        if float(self.current) != 0:
                            result = float(self.previous) / float(self.current)
                        else:
                            result = "Error"
                    
                    # Format result
                    if isinstance(result, float) and result.is_integer():
                        self.current = str(int(result))
                    else:
                        self.current = str(result)
                        
                except:
                    self.current = "Error"
                
                self.operator = ""
                self.previous = ""
        
        elif value == 'C':
            self.current = "0"
            self.previous = ""
            self.operator = ""
        
        elif value == '±':
            if self.current != "0":
                if self.current.startswith('-'):
                    self.current = self.current[1:]
                else:
                    self.current = '-' + self.current
        
        elif value == '%':
            try:
                result = float(self.current) / 100
                if result.is_integer():
                    self.current = str(int(result))
                else:
                    self.current = str(result)
            except:
                self.current = "Error"
        
        # Update display
        self.display.config(text=self.current)

def main():
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
