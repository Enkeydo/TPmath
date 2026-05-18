__version__ = "1.0.0"

import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

# Import the local package list
try:
    from packages import package_sizes
except ImportError:
    # Fallback to prevent crash if file is missing during build
    package_sizes = {"Error": ("packages.py not found", 0, 0)}

class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(55)
        self.font_size = '16sp'
        self.background_normal = ''
        self.background_color = (0.15, 0.15, 0.15, 1)

class TPMath(App):
    def build(self):
        # Local database for price tracking
        self.db_path = os.path.join(self.user_data_dir, "tpmath.db")
        self.init_db()

        self.package_lookup = {}
        sorted_keys = sorted(package_sizes.keys())
        spinner_values = []
        
        for k in sorted_keys:
            name, sheets, rolls = package_sizes[k]
            display_text = f"{k}: {name}"
            spinner_values.append(display_text)
            self.package_lookup[display_text] = (sheets, rolls)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # UI Header
        layout.add_widget(Label(text="TP Price Calculator", font_size='24sp', size_hint_y=None, height=dp(50)))

        # Package Selection
        self.spinner = Spinner(
            text="Select Package Type",
            values=spinner_values,
            option_cls=CustomSpinnerOption,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(self.spinner)

        # Quantity of Packs
        layout.add_widget(Label(text="Number of Packs:", size_hint_y=None, height=dp(30)))
        self.qty_input = TextInput(text="1", multiline=False, input_filter='int', size_hint_y=None, height=dp(45))
        layout.add_widget(self.qty_input)

        # Price Input
        layout.add_widget(Label(text="Total Price ($):", size_hint_y=None, height=dp(30)))
        self.price_input = TextInput(multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        layout.add_widget(self.price_input)

        # Calculate Button
        calc_btn = Button(text="Calculate & Save", size_hint_y=None, height=dp(60), background_color=(0.2, 0.6, 1, 1))
        calc_btn.bind(on_release=self.calculate)
        layout.add_widget(calc_btn)

        # Result Display
        self.result_label = Label(text="Result will appear here", markup=True, font_size='18sp')
        layout.add_widget(self.result_label)

        # History Button
        hist_btn = Button(text="View Price History", size_hint_y=None, height=dp(50))
        hist_btn.bind(on_release=self.show_history_popup)
        layout.add_widget(hist_btn)

        return layout

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history 
                     (label TEXT, price REAL, pp100 REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def calculate(self, instance):
        try:
            price = float(self.price_input.text)
            qty = int(self.qty_input.text)
            selection = self.spinner.text
            
            if selection == "Select Package Type":
                self.result_label.text = "[color=ff6666]Please select a brand[/color]"
                return

            sheets_per_roll, rolls_per_pack = self.package_lookup[selection]
            total_sheets = sheets_per_roll * rolls_per_pack * qty
            
            if total_sheets == 0:
                self.result_label.text = "[color=ff6666]Error: Total sheets is 0[/color]"
                return

            # Unit Math: (Price / Total Sheets) * 100
            pp100 = (price / total_sheets) * 100
            
            # Best Price Check
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT MIN(pp100) FROM history WHERE label = ?", (selection,))
            best_res = c.fetchone()[0]
            
            status_color = "ffffff" # White
            status_suffix = ""
            
            if best_res is not None:
                if pp100 <= (best_res + 0.001):
                    status_color = "00ff00" # Green
                    status_suffix = " [BEST PRICE!]"
                else:
                    diff = pp100 - best_res
                    status_suffix = f" (+${diff:.3f} vs best)"
            
            # Save the record
            c.execute("INSERT INTO history (label, price, pp100) VALUES (?, ?, ?)", (selection, price, pp100))
            conn.commit()
            conn.close()

            self.result_label.text = f"[color={status_color}]Price/100: ${pp100:.3f}{status_suffix}[/color]"
            
        except ValueError:
            self.result_label.text = "[color=ff6666]Invalid input[/color]"

    def show_history_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        history_label = Label(text="Loading...", size_hint_y=None, markup=True, halign='left')
        history_label.bind(texture_size=history_label.setter('size'))
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT label, pp100, timestamp FROM history ORDER BY timestamp DESC LIMIT 30")
        rows = c.fetchall()
        conn.close()

        history_text = ""
        for row in rows:
            # Shorten label for mobile display
            short_label = row[0].split(": ")[-1][:15]
            history_text += f"{row[2][5:16]} | {short_label}: [b]${row[1]:.3f}[/b]\n"
        
        history_label.text = history_text if history_text else "No history recorded yet."
        scroll.add_widget(history_label)
        content.add_widget(scroll)
        
        close_btn = Button(text="Close", size_hint_y=None, height=dp(50))
        popup = Popup(title="Price History", content=content, size_hint=(0.9, 0.8))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

if __name__ == '__main__':
    TPMath().run()
