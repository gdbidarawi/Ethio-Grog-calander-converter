import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Set up modern UI themes
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class EthiopianCalendarConverter:
    # Ethiopian Month Names
    ETHIOPIAN_MONTHS = [
        "Meskerem", "Tikimt", "Hidar", "Tahsas", "Tir", "Yekatit",
        "Megabit", "Miyazya", "Ginbot", "Sene", "Hamle", "Nehase", "Pagume"
    ]
    
    # Days of the week translated to English phonetic representation of Ethiopian days
    DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @staticmethod
    def is_gregorian_leap(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @classmethod
    def gregorian_to_ethiopian(cls, date_obj):
        """Converts a standard Python datetime.date object to Ethiopian Date"""
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # Inputs for calculation anchor points
        if (month == 1 and day >= 1) or (month <= 8) or (month == 9 and day <= 10):
            eth_year = year - 8
        else:
            eth_year = year - 7

        # Determine the Gregorian starting point for Meskerem 1
        # If the NEXT Ethiopian year is a leap year (divided by 4 with remainder 3)
        if (eth_year + 1) % 4 == 3:
            meskerem1_day = 12
        else:
            meskerem1_day = 11

        # Calculate exact day difference using a fixed historical anchor
        # Gregorian date for 12 Sept 2023 (Meskerem 1, 2016)
        anchor_greg = datetime.date(2023, 9, 12)
        anchor_eth_year = 2016
        
        # Calculate days relative to anchor
        days_diff = (date_obj - anchor_greg).days
        
        # Total days since anchor year Meskerem 1
        # Convert total days into Ethiopian years, months, days
        # Exact conversion logic via fixed absolute days calculation
        greg_epoch = datetime.date(1, 1, 1).toordinal()
        input_ordinal = date_obj.toordinal()
        
        # Absolute JDN style math adjustment for Ethiopian Calendar
        r_days = input_ordinal - datetime.date(8, 8, 29).toordinal()
        
        calculated_eth_year = r_days // 1461 * 4 + 1
        r_days %= 1461
        
        if r_days >= 366:
            calculated_eth_year += (r_days - 1) // 365
            r_days = (r_days - 1) % 365
            if r_days == 0 and calculated_eth_year % 4 == 0:
                r_days = 365
                calculated_eth_year -= 1

        eth_month = (r_days // 30) + 1
        eth_day = (r_days % 30) + 1
        
        if eth_month > 13:
            eth_month = 13
            eth_day = r_days - 360 + 1

        weekday = cls.DAYS_OF_WEEK[date_obj.weekday()]
        return int(calculated_eth_year), int(eth_month), int(eth_day), weekday

    @classmethod
    def ethiopian_to_gregorian(cls, eth_year, eth_month, eth_day):
        """Converts Ethiopian date components back to a Python datetime.date object"""
        # Validate Ethiopian inputs
        if eth_month < 1 or eth_month > 13:
            raise ValueError("Month must be between 1 and 13.")
        if eth_month <= 12 and (eth_day < 1 or eth_day > 30):
            raise ValueError("Months 1-12 have exactly 30 days.")
        
        is_leap = (eth_year % 4 == 3)
        if eth_month == 13:
            max_p_days = 6 if is_leap else 5
            if eth_day < 1 or eth_day > max_p_days:
                raise ValueError(f"Pagume has {max_p_days} days for year {eth_year}.")

        # Reconstruct ordinal days matching Ethio-Gregorian cycle offset
        # Base offset calculation
        cycles = (eth_year - 1) // 4
        remainder_years = (eth_year - 1) % 4
        
        total_days = cycles * 1461 + remainder_years * 365
        total_days += (eth_month - 1) * 30 + (eth_day - 1)
        
        # Gregorian offset anchor
        greg_ordinal = total_days + datetime.date(8, 8, 29).toordinal()
        return datetime.date.fromordinal(greg_ordinal)

    @classmethod
    def get_ethiopian_holidays(cls, eth_year):
        """Returns static fixed-date Ethiopian public holidays"""
        return {
            (1, 1): "Enkutatash (Ethiopian New Year)",
            (1, 17): "Meskel (Finding of the True Cross)",
            (4, 29): "Genna (Ethiopian Christmas)",
            (5, 11): "Timkat (Ethiopian Epiphany)",
            (6, 23): "Adwa Victory Day",
            (8, 23): "Siklet (Good Friday - Varied approximation)",
            (8, 25): "Fasika (Ethiopian Easter - Varied approximation)",
            (9, 1): "International Labour Day",
            (9, 20): "Patriots' Victory Day",
            (11, 21): "Downfall of the Derg Regime"
        }


class ModernCalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ethio-Gregorian Dynamic Date Converter")
        self.geometry("600x650")
        self.resizable(True, True)

        # Initialize Conversion Direction state
        self.greg_to_eth_direction = True

        # --- UI LAYOUT DESIGN ---
        self.title_label = ctk.CTkLabel(self, text="Ethiopian Calendar Converter", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Quick Display Frame for Current Date
        self.current_date_frame = ctk.CTkFrame(self, corner_radius=10)
        self.current_date_frame.pack(fill="x", padx=30, pady=10)
        
        self.current_date_lbl = ctk.CTkLabel(self.current_date_frame, text="Current Ethiopian Date Loading...", font=ctk.CTkFont(size=14, weight="medium"))
        self.current_date_lbl.pack(pady=10)

        # Main Interaction Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Swap Direction Button
        self.swap_btn = ctk.CTkButton(self.main_frame, text=" Toggle Direction: Gregorian ➔ Ethiopian", command=self.toggle_direction)
        self.swap_btn.pack(pady=15)

        # Entry Grid Fields
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.pack(pady=10)

        self.lbl1 = ctk.CTkLabel(self.input_frame, text="Day:", font=ctk.CTkFont(size=14))
        self.lbl1.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ent_day = ctk.CTkEntry(self.input_frame, width=80, placeholder_text="DD")
        self.ent_day.grid(row=0, column=1, padx=10, pady=5)

        self.lbl2 = ctk.CTkLabel(self.input_frame, text="Month:", font=ctk.CTkFont(size=14))
        self.lbl2.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_month = ctk.CTkEntry(self.input_frame, width=80, placeholder_text="MM")
        self.ent_month.grid(row=1, column=1, padx=10, pady=5)

        self.lbl3 = ctk.CTkLabel(self.input_frame, text="Year:", font=ctk.CTkFont(size=14))
        self.lbl3.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.ent_year = ctk.CTkEntry(self.input_frame, width=80, placeholder_text="YYYY")
        self.ent_year.grid(row=2, column=1, padx=10, pady=5)

        # Action Convert Button
        self.convert_btn = ctk.CTkButton(self.main_frame, text="Convert Date", fg_color="#1f538d", command=self.perform_conversion)
        self.convert_btn.pack(pady=15)

        # Output Card Panel
        self.output_frame = ctk.CTkFrame(self.main_frame, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        self.output_frame.pack(fill="x", padx=20, pady=15)

        self.txt_result = ctk.CTkLabel(self.output_frame, text="Enter a valid date above to process.", font=ctk.CTkFont(size=15), justify="left")
        self.txt_result.pack(pady=15, padx=15)

        # Bottom Utilities (Theme Toggling)
        self.theme_toggle = ctk.CTkSwitch(self, text="Dark Mode Override", command=self.change_theme)
        self.theme_toggle.pack(side="bottom", pady=15)
        if ctk.get_appearance_mode() == "Dark":
            self.theme_toggle.select()

        # Fire initial processes
        self.show_current_date()

    def change_theme(self):
        if self.theme_toggle.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def toggle_direction(self):
        self.greg_to_eth_direction = not self.greg_to_eth_direction
        if self.greg_to_eth_direction:
            self.swap_btn.configure(text=" Toggle Direction: Gregorian ➔ Ethiopian")
            self.lbl2.configure(text="Month (1-12):")
            self.ent_month.configure(placeholder_text="MM")
        else:
            self.swap_btn.configure(text=" Toggle Direction: Ethiopian ➔ Gregorian")
            self.lbl2.configure(text="Month (1-13):")
            self.ent_month.configure(placeholder_text="1-13")
        self.clear_fields()

    def clear_fields(self):
        self.ent_day.delete(0, tk.END)
        self.ent_month.delete(0, tk.END)
        self.ent_year.delete(0, tk.END)
        self.txt_result.configure(text="Direction Swapped. Waiting for values...")

    def show_current_date(self):
        today = datetime.date.today()
        ey, em, ed, wd = EthiopianCalendarConverter.gregorian_to_ethiopian(today)
        month_name = EthiopianCalendarConverter.ETHIOPIAN_MONTHS[em - 1]
        self.current_date_lbl.configure(
            text=f"Today in Ethiopia: {month_name} {ed}, {ey} E.C. ({wd})"
        )

    def perform_conversion(self):
        try:
            d = int(self.ent_day.get().strip())
            m = int(self.ent_month.get().strip())
            y = int(self.ent_year.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "All date entries must be valid numeric digits.")
            return

        if self.greg_to_eth_direction:
            # Gregorian -> Ethiopian
            try:
                greg_date = datetime.date(y, m, d)
            except ValueError as e:
                messagebox.showerror("Invalid Gregorian Date", f"Error: {str(e).capitalize()}.")
                return

            ey, em, ed, wd = EthiopianCalendarConverter.gregorian_to_ethiopian(greg_date)
            month_str = EthiopianCalendarConverter.ETHIOPIAN_MONTHS[em - 1]
            
            # Holiday Detection
            holidays = EthiopianCalendarConverter.get_ethiopian_holidays(ey)
            holiday_txt = f"\n National Holiday: {holidays[(em, ed)]}" if (em, ed) in holidays else ""
            
            output = (
                f" **Ethiopian Destination Date:**\n"
                f"• Year: {ey} E.C.\n"
                f"• Month: {month_str} (Month {em})\n"
                f"• Day: {ed}\n"
                f"• Day of Week: {wd}"
                f"{holiday_txt}"
            )
            self.txt_result.configure(text=output)

        else:
            # Ethiopian -> Gregorian
            try:
                greg_date = EthiopianCalendarConverter.ethiopian_to_gregorian(y, m, d)
            except ValueError as e:
                messagebox.showerror("Invalid Ethiopian Date", f"Error: {str(e)}")
                return

            wd = EthiopianCalendarConverter.DAYS_OF_WEEK[greg_date.weekday()]
            
            # Holiday Check
            holidays = EthiopianCalendarConverter.get_ethiopian_holidays(y)
            holiday_txt = f"\n National Holiday: {holidays[(m, d)]}" if (m, d) in holidays else ""

            output = (
                f" **Gregorian Destination Date:**\n"
                f"• Year: {greg_date.year} G.C.\n"
                f"• Month: {greg_date.strftime('%B')} ({greg_date.month})\n"
                f"• Day: {greg_date.day}\n"
                f"• Day of Week: {wd}"
                f"{holiday_txt}"
            )
            self.txt_result.configure(text=output)


if __name__ == "__main__":
    app = ModernCalendarApp()
    app.mainloop()