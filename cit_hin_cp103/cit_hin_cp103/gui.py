"""Tkinter user interface for CIT HUB."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sqlite3
from database import initialize_database
from services import CampusHubService
from models import Equipment, Borrower
from reports import export_equipment

NAVY = "#17365D"
NAVY_DARK = "#102844"
PALE = "#F2F5F9"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"

class CITHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CIT HUB | School Resource Management")
        self.root.geometry("1180x740")
        self.root.minsize(980, 640)
        initialize_database()
        self.service = CampusHubService()
        self.selected_asset_id = None
        self._style()
        self._build()
        self.refresh_all()

    def _style(self):
        self.root.configure(bg=PALE)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=PALE)
        style.configure("Card.TFrame", background=WHITE)
        style.configure("TLabel", background=PALE, foreground=TEXT)
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground=NAVY, background=PALE)
        style.configure("Sub.TLabel", foreground=MUTED, background=PALE)
        style.configure("TButton", padding=(11, 7))
        style.configure("Primary.TButton", background=NAVY, foreground=WHITE, padding=(12, 8))
        style.map("Primary.TButton", background=[("active", NAVY_DARK)])
        style.configure("Treeview", rowheight=29, background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", background="#E7EDF5", foreground=NAVY, font=("Segoe UI", 9, "bold"))
        style.configure("TNotebook", background=PALE, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9), background="#E3EAF2")
        style.map("TNotebook.Tab", background=[("selected", WHITE)], foreground=[("selected", NAVY)])

    def _build(self):
        header = tk.Frame(self.root, bg=NAVY, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="▣  CIT HUB", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 22, "bold")).pack(side="left", padx=24)
        tk.Label(header, text="School Resource Borrowing & Inventory Management System",
                 bg=NAVY, fg="#DCE6F2", font=("Segoe UI", 10)).pack(side="left", padx=12, pady=(10,0))
        tk.Label(header, text="PYTHON • TKINTER • SQLITE", bg=NAVY, fg="#B8C9DC",
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=22)

        main = ttk.Frame(self.root, padding=(20, 16))
        main.pack(fill="both", expand=True)
        ttk.Label(main, text="Resource Management", style="Title.TLabel").pack(anchor="w")
        ttk.Label(main, text="Manage equipment, borrowers, and lending transactions in one place.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, 14))

        self.tabs = ttk.Notebook(main)
        self.tabs.pack(fill="both", expand=True)
        self.dashboard_tab = ttk.Frame(self.tabs, padding=16)
        self.inventory_tab = ttk.Frame(self.tabs, padding=16)
        self.borrowers_tab = ttk.Frame(self.tabs, padding=16)
        self.checkout_tab = ttk.Frame(self.tabs, padding=16)
        self.loans_tab = ttk.Frame(self.tabs, padding=16)
        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.inventory_tab, text="Equipment")
        self.tabs.add(self.borrowers_tab, text="Borrowers")
        self.tabs.add(self.checkout_tab, text="Borrow Equipment")
        self.tabs.add(self.loans_tab, text="Loans & Returns")
        self._dashboard_ui()
        self._inventory_ui()
        self._borrowers_ui()
        self._checkout_ui()
        self._loans_ui()
        footer = tk.Label(self.root, text="CIT HUB  |  Local database storage  |  Use fictional/test borrower records",
                          bg=PALE, fg=MUTED, font=("Segoe UI", 9))
        footer.pack(side="bottom", pady=(0,8))

    def _dashboard_ui(self):
        f = self.dashboard_tab
        ttk.Label(f, text="Dashboard overview", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(f, text="A quick view of the current equipment and borrowing activity.",
                  style="Sub.TLabel").pack(anchor="w", pady=(2,14))
        self.count_area = ttk.Frame(f)
        self.count_area.pack(fill="x", pady=(0,18))
        self.count_labels = {}
        for label in ["Total equipment", "Available", "Active loans", "Overdue"]:
            card = tk.Frame(self.count_area, bg=WHITE, highlightbackground="#DCE4ED",
                            highlightthickness=1, padx=18, pady=16)
            card.pack(side="left", fill="both", expand=True, padx=(0,10))
            tk.Label(card, text=label.upper(), bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            value = tk.Label(card, text="0", bg=WHITE, fg=NAVY,
                             font=("Segoe UI", 25, "bold"))
            value.pack(anchor="w", pady=(7,0))
            self.count_labels[label] = value
        ttk.Label(f, text="Getting started", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(6,8))
        tips = [
            "1. Add equipment records in the Equipment tab.",
            "2. Register borrowers using unique borrower codes.",
            "3. Create a checkout for an available asset and eligible borrower.",
            "4. Process returns from Loans & Returns; returned transactions remain in history.",
            "5. Use Export CSV in the Equipment tab to save an inventory report."
        ]
        for tip in tips:
            ttk.Label(f, text=tip).pack(anchor="w", pady=4)

    def _section_title(self, parent, title, subtitle=None):
        ttk.Label(parent, text=title, font=("Segoe UI", 15, "bold")).pack(anchor="w")
        if subtitle:
            ttk.Label(parent, text=subtitle, style="Sub.TLabel").pack(anchor="w", pady=(2,10))

    def _tree(self, parent, columns, headings, height=11):
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True, pady=(10,0))
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=120, minwidth=75, anchor="w")
        yscroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1); wrap.columnconfigure(0, weight=1)
        return tree

    def _inventory_ui(self):
        f = self.inventory_tab
        self._section_title(f, "Equipment inventory", "Add, search, update, or deactivate school resources.")
        form = ttk.LabelFrame(f, text="Equipment details", padding=10)
        form.pack(fill="x")
        self.eq_vars = {k: tk.StringVar() for k in ["code","name","category","location","condition"]}
        fields = [("Asset code","code"),("Equipment name","name"),("Category","category"),
                  ("Location","location"),("Condition","condition")]
        for i,(label,key) in enumerate(fields):
            ttk.Label(form,text=label).grid(row=0,column=i,sticky="w",padx=5)
            entry = ttk.Entry(form,textvariable=self.eq_vars[key],width=19)
            entry.grid(row=1,column=i,sticky="ew",padx=5,pady=(3,4))
        self.eq_vars["condition"].set("Good")
        actions = ttk.Frame(f); actions.pack(fill="x", pady=8)
        ttk.Button(actions,text="Add equipment",style="Primary.TButton",command=self.add_equipment).pack(side="left",padx=(0,6))
        ttk.Button(actions,text="Update selected",command=self.update_equipment).pack(side="left",padx=4)
        ttk.Button(actions,text="Deactivate selected",command=self.deactivate_equipment).pack(side="left",padx=4)
        ttk.Button(actions,text="Clear form",command=self.clear_equipment).pack(side="left",padx=4)
        ttk.Button(actions,text="Export CSV",command=lambda:export_equipment(self.root)).pack(side="right")
        searchrow = ttk.Frame(f); searchrow.pack(fill="x", pady=(5,0))
        ttk.Label(searchrow,text="Search code or name:").pack(side="left")
        self.eq_search = tk.StringVar()
        ent=ttk.Entry(searchrow,textvariable=self.eq_search,width=30); ent.pack(side="left",padx=8)
        ent.bind("<KeyRelease>",lambda e:self.refresh_equipment())
        self.eq_tree = self._tree(f,("id","code","name","category","location","condition","status"),
                                  ("ID","Asset code","Name","Category","Location","Condition","Status"))
        self.eq_tree.bind("<<TreeviewSelect>>",self.select_equipment)

    def _borrowers_ui(self):
        f=self.borrowers_tab
        self._section_title(f,"Borrower records","Register authorized borrowers. Use fictional or instructor-approved test data.")
        form=ttk.LabelFrame(f,text="Borrower details",padding=10);form.pack(fill="x")
        self.br_vars={k:tk.StringVar() for k in ["code","name","department"]}
        for i,(label,key) in enumerate([("Borrower code","code"),("Full name","name"),("Department / Program","department")]):
            ttk.Label(form,text=label).grid(row=0,column=i,sticky="w",padx=5)
            ttk.Entry(form,textvariable=self.br_vars[key],width=30).grid(row=1,column=i,sticky="ew",padx=5,pady=4)
        ttk.Button(f,text="Add borrower",style="Primary.TButton",command=self.add_borrower).pack(anchor="w",pady=9)
        sr=ttk.Frame(f);sr.pack(fill="x")
        ttk.Label(sr,text="Search code or name:").pack(side="left")
        self.br_search=tk.StringVar();e=ttk.Entry(sr,textvariable=self.br_search,width=32);e.pack(side="left",padx=8)
        e.bind("<KeyRelease>",lambda ev:self.refresh_borrowers())
        self.br_tree=self._tree(f,("id","code","name","department","active"),
                                ("ID","Borrower code","Name","Department / Program","Active"))

    def _checkout_ui(self):
        f=self.checkout_tab
        self._section_title(f,"Borrow equipment","Only available equipment and active borrowers can be checked out.")
        form=ttk.LabelFrame(f,text="New checkout",padding=18);form.pack(fill="x",anchor="n")
        self.co_vars={k:tk.StringVar() for k in ["asset","borrower","borrowed","due"]}
        self.co_vars["borrowed"].set(date.today().isoformat())
        from datetime import timedelta
        self.co_vars["due"].set((date.today()+timedelta(days=7)).isoformat())
        fields=[("Asset code","asset"),("Borrower code","borrower"),("Borrowed on (YYYY-MM-DD)","borrowed"),("Due on (YYYY-MM-DD)","due")]
        for i,(label,key) in enumerate(fields):
            ttk.Label(form,text=label).grid(row=0,column=i,sticky="w",padx=7)
            ttk.Entry(form,textvariable=self.co_vars[key],width=25).grid(row=1,column=i,sticky="ew",padx=7,pady=(5,12))
        ttk.Button(form,text="Confirm checkout",style="Primary.TButton",command=self.checkout).grid(row=2,column=0,sticky="w",padx=7)
        ttk.Label(f,text="Tip: Asset code and borrower code must already exist in their respective tabs.",
                  style="Sub.TLabel").pack(anchor="w",pady=12)
        self.available_tree=self._tree(f,("code","name","category","location"),
            ("Available asset code","Equipment","Category","Location"),height=9)

    def _loans_ui(self):
        f=self.loans_tab
        self._section_title(f,"Loans and returns","Review active, overdue, and returned transactions.")
        bar=ttk.Frame(f);bar.pack(fill="x")
        ttk.Label(bar,text="View:").pack(side="left")
        self.loan_mode=tk.StringVar(value="all")
        combo=ttk.Combobox(bar,textvariable=self.loan_mode,state="readonly",
                           values=["all","active","overdue","returned"],width=14)
        combo.pack(side="left",padx=7);combo.bind("<<ComboboxSelected>>",lambda e:self.refresh_loans())
        ttk.Label(bar,text="Search:").pack(side="left",padx=(15,0))
        self.loan_search=tk.StringVar();search=ttk.Entry(bar,textvariable=self.loan_search,width=28)
        search.pack(side="left",padx=7);search.bind("<KeyRelease>",lambda e:self.refresh_loans())
        ttk.Button(bar,text="Refresh",command=self.refresh_loans).pack(side="left",padx=5)
        self.loan_tree=self._tree(f,("id","asset","item","borrower_code","borrower","borrowed","due","returned","status"),
            ("Loan ID","Asset code","Equipment","Borrower code","Borrower","Borrowed","Due","Returned","Status"),height=12)
        ret=ttk.LabelFrame(f,text="Process return",padding=10);ret.pack(fill="x",pady=10)
        self.return_id=tk.StringVar();self.return_date=tk.StringVar(value=date.today().isoformat())
        ttk.Label(ret,text="Selected loan ID:").pack(side="left")
        ttk.Entry(ret,textvariable=self.return_id,width=10,state="readonly").pack(side="left",padx=6)
        ttk.Label(ret,text="Return date (YYYY-MM-DD):").pack(side="left",padx=(12,0))
        ttk.Entry(ret,textvariable=self.return_date,width=15).pack(side="left",padx=6)
        ttk.Button(ret,text="Record return",style="Primary.TButton",command=self.return_loan).pack(side="left",padx=8)
        self.loan_tree.bind("<<TreeviewSelect>>",self.select_loan)

    def _error(self, title, exc):
        if isinstance(exc, sqlite3.IntegrityError):
            messagebox.showerror(title,"A duplicate code or database relationship was detected. Check the code and try again.",parent=self.root)
        else:
            messagebox.showerror(title,str(exc),parent=self.root)

    def add_equipment(self):
        try:
            v=self.eq_vars
            self.service.add_equipment(Equipment(v["code"].get(),v["name"].get(),v["category"].get(),
                                                 v["location"].get(),v["condition"].get() or "Good"))
            self.clear_equipment();self.refresh_all()
            messagebox.showinfo("Saved","Equipment record added successfully.",parent=self.root)
        except Exception as e:self._error("Could not add equipment",e)

    def update_equipment(self):
        if not self.selected_asset_id:
            messagebox.showwarning("Select a record","Select an equipment row first.",parent=self.root);return
        try:
            v=self.eq_vars
            self.service.update_equipment(self.selected_asset_id,Equipment(v["code"].get(),v["name"].get(),
                v["category"].get(),v["location"].get(),v["condition"].get() or "Good"))
            self.refresh_all();messagebox.showinfo("Updated","Equipment details updated.",parent=self.root)
        except Exception as e:self._error("Could not update equipment",e)

    def deactivate_equipment(self):
        if not self.selected_asset_id:
            messagebox.showwarning("Select a record","Select an equipment row first.",parent=self.root);return
        if messagebox.askyesno("Confirm deactivation","Mark this equipment as inactive? The record will be retained.",parent=self.root):
            try:self.service.deactivate_equipment(self.selected_asset_id);self.clear_equipment();self.refresh_all()
            except Exception as e:self._error("Could not deactivate equipment",e)

    def clear_equipment(self):
        self.selected_asset_id=None
        for v in self.eq_vars.values():v.set("")
        self.eq_vars["condition"].set("Good")
        self.eq_tree.selection_remove(self.eq_tree.selection())

    def select_equipment(self,event=None):
        sel=self.eq_tree.selection()
        if not sel:return
        vals=self.eq_tree.item(sel[0],"values");self.selected_asset_id=int(vals[0])
        for key,val in zip(["code","name","category","location","condition"],vals[1:6]):
            self.eq_vars[key].set(val)

    def add_borrower(self):
        try:
            v=self.br_vars
            self.service.add_borrower(Borrower(v["code"].get(),v["name"].get(),v["department"].get()))
            for x in v.values():x.set("")
            self.refresh_borrowers()
            messagebox.showinfo("Saved","Borrower registered successfully.",parent=self.root)
        except Exception as e:self._error("Could not add borrower",e)

    def checkout(self):
        try:
            v=self.co_vars
            self.service.checkout(v["asset"].get(),v["borrower"].get(),v["borrowed"].get(),v["due"].get())
            self.refresh_all()
            messagebox.showinfo("Checkout complete","Loan saved. Equipment status is now Borrowed.",parent=self.root)
        except Exception as e:self._error("Checkout blocked",e)

    def select_loan(self,event=None):
        sel=self.loan_tree.selection()
        if sel:self.return_id.set(self.loan_tree.item(sel[0],"values")[0])

    def return_loan(self):
        if not self.return_id.get():
            messagebox.showwarning("Select a loan","Select an active loan first.",parent=self.root);return
        try:
            self.service.return_loan(int(self.return_id.get()),self.return_date.get())
            self.refresh_all();self.return_id.set("")
            messagebox.showinfo("Return complete","Return saved. Equipment is now Available.",parent=self.root)
        except Exception as e:self._error("Could not process return",e)

    def _fill_tree(self,tree,rows):
        tree.delete(*tree.get_children())
        for row in rows:tree.insert("","end",values=tuple(row))

    def refresh_equipment(self):
        rows=self.service.equipment(self.eq_search.get())
        self._fill_tree(self.eq_tree,[(r["asset_id"],r["asset_code"],r["name"],r["category"],
            r["location"],r["condition"],r["status"]) for r in rows])

    def refresh_borrowers(self):
        rows=self.service.borrowers(self.br_search.get())
        self._fill_tree(self.br_tree,[(r["borrower_id"],r["borrower_code"],r["display_name"],
            r["department_or_program"],"Yes" if r["active"] else "No") for r in rows])

    def refresh_loans(self):
        rows=self.service.loans(self.loan_search.get(),self.loan_mode.get())
        self._fill_tree(self.loan_tree,[(r["loan_id"],r["asset_code"],r["asset_name"],
            r["borrower_code"],r["display_name"],r["borrowed_on"],r["due_on"],
            r["returned_on"] or "—",r["display_status"]) for r in rows])

    def refresh_dashboard(self):
        for label,value in self.service.dashboard_counts().items():
            self.count_labels[label].configure(text=str(value))

    def refresh_available(self):
        rows=[r for r in self.service.equipment() if r["status"]=="Available"]
        self._fill_tree(self.available_tree,[(r["asset_code"],r["name"],r["category"],r["location"]) for r in rows])

    def refresh_all(self):
        self.refresh_equipment();self.refresh_borrowers();self.refresh_loans()
        self.refresh_dashboard();self.refresh_available()
