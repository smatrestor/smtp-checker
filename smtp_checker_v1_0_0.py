"""
SMTP Checker v1.0.0
A desktop SMTP connection diagnostic tool.

This version intentionally tests one account supplied by the user at a time.
It does not process credential-combo lists, send test emails, export credentials,
or store passwords.
"""

import smtplib
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

APP_NAME = "SMTP Checker"
VERSION = "1.0.0"

BG = "#0b1020"
PANEL = "#121a2b"
PANEL_ALT = "#182338"
ACCENT = "#6c8cff"
TEXT = "#edf2ff"
MUTED = "#93a1bb"
GREEN = "#42d392"
RED = "#ff647c"
BORDER = "#263550"


class SMTPCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=BG)

        self.host_var = tk.StringVar(value="smtp.gmail.com")
        self.port_var = tk.StringVar(value="587")
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.security_var = tk.StringVar(value="STARTTLS")
        self.status_var = tk.StringVar(value="Ready")
        self.history = []

        self._style()
        self._show_splash()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=PANEL_ALT, background=PANEL_ALT,
                        foreground=TEXT, arrowcolor=TEXT)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_ALT)])
        style.configure("Horizontal.TProgressbar",
                        troughcolor=PANEL_ALT, background=ACCENT,
                        bordercolor=PANEL_ALT, lightcolor=ACCENT,
                        darkcolor=ACCENT)

    def _show_splash(self):
        self.splash = tk.Frame(self, bg=BG)
        self.splash.place(relx=0, rely=0, relwidth=1, relheight=1)

        center = tk.Frame(self.splash, bg=BG)
        center.place(relx=.5, rely=.46, anchor="center")

        tk.Label(center, text="SMTP", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 17, "bold")).pack()
        tk.Label(center, text="CHECKER", bg=BG, fg=TEXT,
                 font=("Segoe UI", 34, "bold")).pack(pady=(0, 5))
        tk.Label(center, text=f"DESKTOP DIAGNOSTICS  •  VERSION {VERSION}",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(pady=(0, 28))

        self.splash_progress = ttk.Progressbar(
            center, mode="indeterminate", length=250,
            style="Horizontal.TProgressbar")
        self.splash_progress.pack()
        self.splash_progress.start(12)
        tk.Label(center, text="Initializing workspace…", bg=BG,
                 fg=MUTED, font=("Segoe UI", 9)).pack(pady=12)
        self.after(1500, self._finish_splash)

    def _finish_splash(self):
        self.splash_progress.stop()
        self.splash.destroy()
        self._build_shell()
        self.show_page("Dashboard")

    def _build_shell(self):
        self.shell = tk.Frame(self, bg=BG)
        self.shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(self.shell, bg="#0e1728", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="SMTP CHECKER", bg="#0e1728",
                 fg=TEXT, font=("Segoe UI", 15, "bold")).pack(
                     anchor="w", padx=22, pady=(28, 2))
        tk.Label(sidebar, text=f"VERSION {VERSION}", bg="#0e1728",
                 fg=MUTED, font=("Segoe UI", 8)).pack(
                     anchor="w", padx=22, pady=(0, 28))

        self.nav_buttons = {}
        for label, icon in [
            ("Dashboard", "⌂"),
            ("SMTP Test", "◎"),
            ("Activity Logs", "≡"),
            ("Settings", "⚙"),
            ("About", "ⓘ"),
        ]:
            btn = tk.Button(
                sidebar, text=f"  {icon}   {label}", anchor="w",
                command=lambda p=label: self.show_page(p),
                bg="#0e1728", fg=MUTED, activebackground=PANEL_ALT,
                activeforeground=TEXT, relief="flat", bd=0,
                font=("Segoe UI", 10), padx=18, pady=13, cursor="hand2")
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[label] = btn

        tk.Label(sidebar, text="LOCAL DIAGNOSTICS", bg="#0e1728",
                 fg="#60718f", font=("Segoe UI", 8, "bold")).pack(
                     side="bottom", anchor="w", padx=22, pady=22)

        main = tk.Frame(self.shell, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(main, bg=BG, height=68)
        topbar.pack(fill="x", padx=32, pady=(16, 0))
        topbar.pack_propagate(False)
        self.page_title = tk.Label(topbar, text="Dashboard", bg=BG,
                                   fg=TEXT, font=("Segoe UI", 20, "bold"))
        self.page_title.pack(side="left", anchor="center")
        tk.Label(topbar, text="●  LOCAL SESSION", bg=BG, fg=GREEN,
                 font=("Segoe UI", 9, "bold")).pack(side="right", anchor="center")

        self.content = tk.Frame(main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=32, pady=20)

        footer = tk.Frame(main, bg=BG)
        footer.pack(fill="x", padx=32, pady=(0, 14))
        tk.Label(footer, textvariable=self.status_var, bg=BG,
                 fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(footer, text=f"{APP_NAME}  •  v{VERSION}",
                 bg=BG, fg="#60718f", font=("Segoe UI", 9)).pack(side="right")

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _card(self, parent, title, subtitle=None):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER,
                        highlightthickness=1)
        tk.Label(card, text=title, bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(
                     anchor="w", padx=20, pady=(18, 4))
        if subtitle:
            tk.Label(card, text=subtitle, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9), wraplength=650,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 14))
        return card

    def show_page(self, page):
        self._clear_content()
        self.page_title.config(text=page)
        for name, btn in self.nav_buttons.items():
            btn.config(bg=PANEL_ALT if name == page else "#0e1728",
                       fg=TEXT if name == page else MUTED)

        if page == "Dashboard":
            self._dashboard()
        elif page == "SMTP Test":
            self._test_page()
        elif page == "Activity Logs":
            self._logs_page()
        elif page == "Settings":
            self._settings_page()
        else:
            self._about_page()

    def _dashboard(self):
        tk.Label(self.content, text="Welcome back",
                 bg=BG, fg=TEXT, font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(self.content,
                 text="Check the connectivity of an SMTP account you own or are authorized to test.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(
                     anchor="w", pady=(5, 22))

        stats = tk.Frame(self.content, bg=BG)
        stats.pack(fill="x", pady=(0, 18))
        for title, value, detail in [
            ("APPLICATION", VERSION, "Current release"),
            ("TEST MODE", "Single account", "No combo-list processing"),
            ("SECURITY", "No storage", "Passwords are not saved"),
        ]:
            card = self._card(stats, title, detail)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(card, text=value, bg=PANEL, fg=ACCENT,
                     font=("Segoe UI", 17, "bold")).pack(
                         anchor="w", padx=20, pady=(0, 18))

        card = self._card(self.content, "Quick start",
                          "Configure your SMTP host and credentials, then run a connection test.")
        card.pack(fill="x")
        tk.Button(card, text="Open SMTP Test  →", command=lambda: self.show_page("SMTP Test"),
                  bg=ACCENT, fg="white", activebackground="#5577e8",
                  activeforeground="white", relief="flat", bd=0,
                  font=("Segoe UI", 10, "bold"), padx=18, pady=11,
                  cursor="hand2").pack(anchor="w", padx=20, pady=(0, 20))

        note = self._card(self.content, "Safety note",
                          "This release verifies a single SMTP login only. It does not send email, "
                          "bulk-check credential lists, or transmit credentials to a third party.")
        note.pack(fill="x", pady=16)

    def _field(self, parent, label, variable, show=None, width=42):
        wrap = tk.Frame(parent, bg=PANEL)
        tk.Label(wrap, text=label, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
        entry = tk.Entry(wrap, textvariable=variable, show=show, width=width,
                         bg=PANEL_ALT, fg=TEXT, insertbackground=TEXT,
                         relief="flat", font=("Segoe UI", 10),
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=ACCENT)
        entry.pack(fill="x", ipady=9)
        return wrap

    def _test_page(self):
        tk.Label(self.content, text="SMTP connection test",
                 bg=BG, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Use an account you own or have permission to administer.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(
                     anchor="w", pady=(4, 18))

        card = self._card(self.content, "Server configuration",
                          "Credentials are used only for this connection attempt and are not stored.")
        card.pack(fill="x")

        form = tk.Frame(card, bg=PANEL)
        form.pack(fill="x", padx=20, pady=(0, 20))
        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=1)

        self._field(form, "SMTP HOST", self.host_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 14), pady=8)
        self._field(form, "PORT", self.port_var).grid(
            row=0, column=1, sticky="ew", pady=8)
        self._field(form, "EMAIL / USERNAME", self.email_var).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=8)
        self._field(form, "PASSWORD / APP PASSWORD", self.password_var,
                    show="•").grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)

        tk.Label(form, text="ENCRYPTION", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=(10, 5))
        combo = ttk.Combobox(form, textvariable=self.security_var,
                             values=["STARTTLS", "SSL/TLS", "None"],
                             state="readonly", width=20)
        combo.grid(row=4, column=0, sticky="w", pady=(0, 14), ipady=5)

        actions = tk.Frame(form, bg=PANEL)
        actions.grid(row=5, column=0, columnspan=2, sticky="w", pady=(5, 0))
        self.test_button = tk.Button(
            actions, text="Run connection test", command=self.start_test,
            bg=ACCENT, fg="white", activebackground="#5577e8",
            activeforeground="white", relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"), padx=18, pady=11, cursor="hand2")
        self.test_button.pack(side="left")
        tk.Button(actions, text="Clear password", command=self.clear_password,
                  bg=PANEL_ALT, fg=TEXT, activebackground=BORDER,
                  relief="flat", bd=0, font=("Segoe UI", 9),
                  padx=14, pady=11, cursor="hand2").pack(side="left", padx=10)

        self.result_card = self._card(self.content, "Test result",
                                      "No test has been run in this session.")
        self.result_card.pack(fill="x", pady=16)
        self.result_label = tk.Label(self.result_card, text="Waiting for test…",
                                     bg=PANEL, fg=MUTED,
                                     font=("Segoe UI", 10))
        self.result_label.pack(anchor="w", padx=20, pady=(0, 18))

    def clear_password(self):
        self.password_var.set()
        self.status_var.set("Password cleared")

    def start_test(self):
        host = self.host_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        try:
            port = int(self.port_var.get().strip())
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid port", "Enter a valid port from 1 to 65535.")
            return
        if not host or not email or not password:
            messagebox.showwarning("Missing details", "Enter the host, username/email, and password.")
            return
        if self.security_var.get() == "SSL/TLS" and port == 587:
            messagebox.showwarning("Check configuration",
                                   "Port 587 normally uses STARTTLS. Choose STARTTLS or verify your provider's settings.")
        self.test_button.config(state="disabled", text="Testing…")
        self.result_label.config(text="Connecting to SMTP server…", fg=ACCENT)
        self.status_var.set("Test running")
        threading.Thread(target=self._test_worker,
                         args=(host, port, email, password, self.security_var.get()),
                         daemon=True).start()

    def _test_worker(self, host, port, email, password, security):
        server = None
        started = datetime.now()
        try:
            if security == "SSL/TLS":
                server = smtplib.SMTP_SSL(host, port, timeout=12)
            else:
                server = smtplib.SMTP(host, port, timeout=12)
                server.ehlo()
                if security == "STARTTLS":
                    server.starttls()
            server.ehlo()
            server.login(email, password)
            result = ("SUCCESS", f"SMTP authentication succeeded for {email} at {host}:{port}.")
        except smtplib.SMTPAuthenticationError:
            result = ("FAILED", "Authentication rejected. Check the username, password, and provider security requirements.")
        except socket.gaierror:
            result = ("FAILED", "The SMTP hostname could not be resolved. Check the host name and network.")
        except (socket.timeout, TimeoutError):
            result = ("FAILED", "The connection timed out. Check the host, port, firewall, and network.")
        except smtplib.SMTPConnectError as exc:
            result = ("FAILED", f"SMTP connection refused: {exc}")
        except smtplib.SMTPException as exc:
            result = ("FAILED", f"SMTP error: {exc}")
        except OSError as exc:
            result = ("FAILED", f"Network error: {exc}")
        except Exception as exc:
            result = ("FAILED", f"Unexpected error: {type(exc).__name__}")
        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    try:
                        server.close()
                    except Exception:
                        pass

        elapsed = (datetime.now() - started).total_seconds()
        self.after(0, self._finish_test, result, host, port, email, elapsed)

    def _finish_test(self, result, host, port, email, elapsed):
        status, detail = result
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, {
            "time": stamp, "status": status, "host": host,
            "port": port, "account": email, "detail": detail,
            "elapsed": elapsed
        })
        color = GREEN if status == "SUCCESS" else RED
        self.result_label.config(text=f"{status}  •  {detail}\nCompleted in {elapsed:.2f} seconds",
                                 fg=color)
        self.test_button.config(state="normal", text="Run connection test")
        self.status_var.set(f"Last test: {status.lower()}")

    def _logs_page(self):
        tk.Label(self.content, text="Session activity",
                 bg=BG, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Results are held in memory for this session only.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 18))
        card = self._card(self.content, "Recent tests")
        card.pack(fill="both", expand=True)
        table_wrap = tk.Frame(card, bg=PANEL)
        table_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        columns = ("time", "status", "account", "server", "elapsed")
        tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=14)
        headings = {"time": "TIME", "status": "RESULT", "account": "ACCOUNT",
                    "server": "SMTP SERVER", "elapsed": "DURATION"}
        widths = {"time": 150, "status": 90, "account": 190, "server": 190, "elapsed": 90}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")
        style = ttk.Style()
        style.configure("Treeview", background=PANEL_ALT, foreground=TEXT,
                        fieldbackground=PANEL_ALT, rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#22314a",
                        foreground=TEXT, relief="flat")
        for item in self.history:
            tree.insert("", "end", values=(
                item["time"], item["status"], item["account"],
                f'{item["host"]}:{item["port"]}', f'{item["elapsed"]:.2f}s'))
        tree.pack(fill="both", expand=True)
        if not self.history:
            tk.Label(card, text="No activity yet. Run a test to see results here.",
                     bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(pady=(0, 18))

    def _settings_page(self):
        tk.Label(self.content, text="Application settings",
                 bg=BG, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        card = self._card(self.content, "Privacy and behavior",
                          "These are the safety defaults for version 1.0.0.")
        card.pack(fill="x", pady=18)
        for heading, desc in [
            ("Password storage", "Disabled. Passwords remain only in the active form and memory."),
            ("Credential list imports", "Not supported. This release tests one account at a time."),
            ("Email sending", "Disabled. The connection test does not send messages."),
            ("Activity history", "Session-only. Results are cleared when the application closes."),
            ("Network security", "STARTTLS and SSL/TLS are supported."),
        ]:
            row = tk.Frame(card, bg=PANEL)
            row.pack(fill="x", padx=20, pady=9)
            tk.Label(row, text=heading, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(row, text=desc, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

    def _about_page(self):
        tk.Label(self.content, text="About SMTP Checker",
                 bg=BG, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        card = self._card(self.content, APP_NAME,
                          "A lightweight desktop utility for checking SMTP connectivity and authentication.")
        card.pack(fill="x", pady=18)
        tk.Label(card, text=f"Version {VERSION}", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(0, 8))
        tk.Label(card, text="Release channel: Stable • Interface: Desktop GUI • Runtime: Python",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(
                     anchor="w", padx=20, pady=(0, 18))
        tk.Label(card, text="This software is intended for accounts and SMTP servers you own "
                            "or are explicitly authorized to test.",
                 bg=PANEL, fg=TEXT, wraplength=650, justify="left",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(0, 20))


if __name__ == "__main__":
    app = SMTPCheckerApp()
    app.mainloop()
