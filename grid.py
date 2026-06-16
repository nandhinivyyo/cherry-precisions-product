    def _build_filter_grid(self):
        # Glass card wrapper
        self.filter_card = ctk.CTkFrame(
            self,
            fg_color="#f8faff",
            corner_radius=20,
            border_width=1,
            border_color="#cbd5f0"
        )
        self.filter_card.pack(fill="x", padx=24, pady=(16, 8))

        # Card header row
        card_hdr = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        card_hdr.pack(fill="x", padx=20, pady=(16, 12))

        ctk.CTkLabel(
            card_hdr,
            text="🔍 Filter & Sort Parameters",
            font=("Segoe UI", 15, "bold"),
            text_color="#1e293b",
            anchor="w"
        ).pack(anchor="w")

        # Thin divider
        ctk.CTkFrame(self.filter_card, fg_color="#f3f4f6", height=1, corner_radius=0).pack(fill="x")

        # Grid container
        grid_frame = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(16, 0))

        for col in range(4):
            grid_frame.grid_columnconfigure(col, weight=1, uniform="filter_grid")

        def make_label(parent, text):
            """Uppercase small gray label matching reference image."""
            ctk.CTkLabel(
                parent,
                text=text.upper(),
                font=("Segoe UI", 10, "bold"),
                text_color="#64748b",
                anchor="w"
            ).pack(anchor="w", pady=(0, 4))

        def get_cell(row, col, padx=(0, 16)):
            cell = ctk.CTkFrame(grid_frame, fg_color="transparent")
            cell.grid(row=row, column=col, sticky="nsew", padx=padx, pady=(0, 16))
            return cell

        # ── ROW 1 ──────────────────────────────────────────────────
        c00 = get_cell(0, 0)
        make_label(c00, "From Date & Time")
        self.from_date_entry, self.from_time_spinner = self._add_date_time_widget(
            c00, self.from_date_var, self.from_time_var)

        c01 = get_cell(0, 1)
        make_label(c01, "To Date & Time")
        self.to_date_entry, self.to_time_spinner = self._add_date_time_widget(
            c01, self.to_date_var, self.to_time_var)

        c02 = get_cell(0, 2)
        make_label(c02, "Item ID / Name")
        self.item_combo = self._create_searchable_combobox_new(
            c02, self.item_var, ["Select item...", "Gear Shaft (ITEM-001)", "Piston Ring (ITEM-002)", "Valve Body (ITEM-003)", "Bearing Housing (ITEM-004)", "Cylinder Liner (ITEM-005)", "Camshaft (ITEM-006)", "Crankshaft Pin (ITEM-007)", "Rotor Disc (ITEM-008)"])

        c03 = get_cell(0, 3, padx=(0, 0))
        make_label(c03, "AirGauge ID / Channel")
        self.airgauge_combo = self._create_searchable_combobox_new(
            c03, self.airgauge_var, ["Select Airgauge...", "AG-01 (CH-01)", "AG-01 (CH-02)", "AG-02 (CH-01)", "AG-02 (CH-02)", "AG-03 (CH-01)", "AG-03 (CH-02)", "AG-04 (CH-01)"])
        self.airgauge_combo._base_values = list(self.airgauge_combo.cget("values"))

        # ── ROW 2 ──────────────────────────────────────────────────
        c10 = get_cell(1, 0)
        make_label(c10, "Drawing Number")
        self.drawing_combo = self._create_searchable_combobox_new(
            c10, self.drawing_var, ["Select drawing...", "DRW-REV1", "DRW-REV2", "DRW-REV3", "DRW-REV4", "DRW-REV5"])

        c11 = get_cell(1, 1)
        make_label(c11, "Operator Name")
        self.operator_combo = self._create_searchable_combobox_new(
            c11, self.operator_var, ["Select operator...", "Alex Mercer", "Ravi Kumar", "Sarah Jenkins", "Michael Chen", "Emma Watson", "David Smith"])

        c12 = get_cell(1, 2)
        make_label(c12, "Machine ID")
        self.machine_combo = self._create_searchable_combobox_new(
            c12, self.machine_var, ["Select machine...", "CNC-VERT-01", "CNC-VERT-02", "CNC-HORZ-01", "CNC-HORZ-02", "LATHE-01", "LATHE-02"])

        c13 = get_cell(1, 3, padx=(0, 0))
        make_label(c13, "Customer")
        self.customer_combo = self._create_searchable_combobox_new(
            c13, self.customer_var, ["Select customer...", "Aerospace Dynamics Inc.", "Precision Auto Parts Ltd.", "Global Heavy Machinery", "Defense Systems Corp.", "Marine Engineering Ltd."])

        # ── Action buttons ─────────────────────────────────────────
        actions_bar = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        actions_bar.pack(fill="x", padx=20, pady=(4, 20))

        buttons_wrapper = ctk.CTkFrame(actions_bar, fg_color="transparent")
        buttons_wrapper.pack(side="right")

        self.ref_btn = ctk.CTkButton(
            buttons_wrapper,
            text="🔄 Refresh Sort",
            text_color="#475569",
            fg_color="#f8fafc",
            hover_color="#f1f5f9",
            border_width=1,
            border_color="#cbd5e1",
            height=38,
            width=140,
            corner_radius=11,
            font=("Segoe UI", 13, "bold"),
            command=self.refresh_table_data
        )
        self.ref_btn.pack(side="left", padx=6)

        self.analyze_btn = ctk.CTkButton(
            buttons_wrapper,
            text="🔍 Analyze Data",
            text_color="#ffffff",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            height=38,
            width=150,
            corner_radius=11,
            font=("Segoe UI", 13, "bold"),
            command=self.open_analyze_page
        )
        self.analyze_btn.pack(side="left", padx=6)

    def _add_date_time_widget(self, parent, date_var, time_var):
        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.pack(fill="x", pady=(2, 4))
        body.grid_columnconfigure(0, weight=1)

        date_wrap = ctk.CTkFrame(
            body,
            fg_color="#ffffff",
            corner_radius=11,
            border_width=1,
            border_color="#cbd5f0",
            height=38
        )
        date_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        date_wrap.pack_propagate(False)

        combined_var = tk.StringVar(value=f"{date_var.get()} {time_var.get()[:5]}")
        
        def on_combined_change(*args):
            val = combined_var.get().strip()
            parts = val.split(" ")
            if len(parts) >= 1:
                date_var.set(parts[0])
            if len(parts) >= 2:
                time_var.set(parts[1] + ":00")
        combined_var.trace_add("write", on_combined_change)

        def on_date_change(*args):
            current_date = combined_var.get().split(" ")[0] if " " in combined_var.get() else combined_var.get()
            if current_date != date_var.get():
                parts = combined_var.get().split(" ")
                time_part = parts[1] if len(parts) > 1 else time_var.get()[:5]
                combined_var.set(f"{date_var.get()} {time_part}")
        date_var.trace_add("write", on_date_change)

        entry = tk.Entry(
            date_wrap,
            textvariable=combined_var,
            relief="flat",
            bd=0,
            bg="white",
            fg="#374151",
            font=("Segoe UI", 12),
            insertbackground="#374151",
            state="normal"
        )
        entry.pack(side="left", fill="both", expand=True, padx=(12, 4), pady=2)

        cal_btn = ctk.CTkLabel(
            date_wrap,
            text="📅",
            font=("Segoe UI", 12),
            text_color="#6b7280",
            cursor="hand2"
        )
        cal_btn.pack(side="right", padx=(0, 8))

        def on_entry_focus(e):
            date_wrap.configure(border_color="#8b5cf6")
        def on_entry_leave(e):
            date_wrap.configure(border_color="#cbd5f0")

        entry.bind("<FocusIn>", on_entry_focus)
        entry.bind("<FocusOut>", on_entry_leave)

        if Calendar is not None:
            cal_btn.bind("<Button-1>", lambda e: self.open_calendar_popup(date_wrap, date_var))

        # We must return an entry and a spinner, but the spinner is now removed.
        # Returning None to satisfy the unpacking in _build_filter_grid.
        return entry, None

    def _create_time_spinner_new(self, parent, time_var):
        outer = ctk.CTkFrame(
            parent,
            corner_radius=8,
            border_width=1,
            border_color="#e5e7eb",
            fg_color="white",
            height=38
        )
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=0)
        outer.pack_propagate(False)
        
        display = ctk.CTkFrame(outer, corner_radius=0, border_width=0, fg_color="white")
        display.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        
        display.grid_columnconfigure(0, weight=1, uniform="time_col")
        display.grid_columnconfigure(1, weight=0)
        display.grid_columnconfigure(2, weight=1, uniform="time_col")
        display.grid_columnconfigure(3, weight=0)
        display.grid_columnconfigure(4, weight=1, uniform="time_col")
        
        def parse_time(s):
            try:
                p = s.split(":")
                hh = int(p[0]) if p and p[0] else 0
                mm = int(p[1]) if len(p) > 1 and p[1] else 0
                ss = int(p[2]) if len(p) > 2 and p[2] else 0
            except Exception:
                hh, mm, ss = 0, 0, 0
            hh %= 24; mm %= 60; ss %= 60
            return hh, mm, ss
            
        hh_val, mm_val, ss_val = parse_time(time_var.get())
        NORMAL_BG = "white"; SELECT_BG = "#7c3aed"; NORMAL_TEXT = "#374151"; SELECT_TEXT = "white"
        LABEL_FONT = ("Segoe UI", 10, "bold"); COLON_FONT = ("Segoe UI", 10)
        
        hh_lbl = ctk.CTkLabel(display, text=f"{hh_val:02d}", font=LABEL_FONT, text_color=NORMAL_TEXT, fg_color=NORMAL_BG, corner_radius=6, anchor="center", width=32)
        hh_lbl.grid(row=0, column=0, sticky="nsew", padx=1, pady=3)
        
        colon1 = ctk.CTkLabel(display, text=":", font=COLON_FONT, text_color=NORMAL_TEXT)
        colon1.grid(row=0, column=1, sticky="nsew")
        
        mm_lbl = ctk.CTkLabel(display, text=f"{mm_val:02d}", font=LABEL_FONT, text_color=NORMAL_TEXT, fg_color=NORMAL_BG, corner_radius=6, anchor="center", width=32)
        mm_lbl.grid(row=0, column=2, sticky="nsew", padx=1, pady=3)
        
        colon2 = ctk.CTkLabel(display, text=":", font=COLON_FONT, text_color=NORMAL_TEXT)
        colon2.grid(row=0, column=3, sticky="nsew")
        
        ss_lbl = ctk.CTkLabel(display, text=f"{ss_val:02d}", font=LABEL_FONT, text_color=NORMAL_TEXT, fg_color=NORMAL_BG, corner_radius=6, anchor="center", width=32)
        ss_lbl.grid(row=0, column=4, sticky="nsew", padx=1, pady=3)
        
        arrow_frame = ctk.CTkFrame(outer, corner_radius=0, border_width=0, fg_color="white")
        arrow_frame.grid(row=0, column=1, sticky="ns")
        
        up_btn = ModernButton(
            arrow_frame,
            text="▲",
            width=20,
            height=12,
            fg_color="#ffffff",
            text_color="#8b5cf6",
            hover_color="#f5f7fb",
            hover=False,
            corner_radius=4,
            command=lambda: change_value(1),
            takefocus=False
        )
        up_btn.pack(side="top", padx=0, pady=(2, 2))
        
        down_btn = ModernButton(
            arrow_frame,
            text="▼",
            width=20,
            height=12,
            fg_color="#ffffff",
            text_color="#8b5cf6",
            hover_color="#f5f7fb",
            hover=False,
            corner_radius=4,
            command=lambda: change_value(-1),
            takefocus=False
        )
        down_btn.pack(side="top", padx=0, pady=(0, 2))
        
        selected = {"field": "hour"}
        typed_buffer = []
        
        def update_visual():
            hh_lbl.configure(fg_color=NORMAL_BG, text_color=NORMAL_TEXT)
            mm_lbl.configure(fg_color=NORMAL_BG, text_color=NORMAL_TEXT)
            ss_lbl.configure(fg_color=NORMAL_BG, text_color=NORMAL_TEXT)
            
            if selected["field"] == "hour":
                hh_lbl.configure(fg_color=SELECT_BG, text_color=SELECT_TEXT)
            elif selected["field"] == "minute":
                mm_lbl.configure(fg_color=SELECT_BG, text_color=SELECT_TEXT)
            else:
                ss_lbl.configure(fg_color=SELECT_BG, text_color=SELECT_TEXT)

        def select_field(f):
            selected["field"] = f
            typed_buffer.clear()
            update_visual()
            outer.configure(border_color="#7c3aed")
            try:
                root = outer.winfo_toplevel()
                root.focus_set()
            except:
                pass
            
        hh_lbl.bind("<Button-1>", lambda e: select_field("hour"))
        mm_lbl.bind("<Button-1>", lambda e: select_field("minute"))
        ss_lbl.bind("<Button-1>", lambda e: select_field("second"))
        
        def write_time(h, m, s):
            hh_lbl.configure(text=f"{h:02d}")
            mm_lbl.configure(text=f"{m:02d}")
            ss_lbl.configure(text=f"{s:02d}")
            time_var.set(f"{h:02d}:{m:02d}:{s:02d}")
            self._schedule_filter()

        def change_value(delta):
            nonlocal hh_val, mm_val, ss_val
            typed_buffer.clear()
            if selected["field"] == "hour":
                hh_val = (hh_val + delta) % 24
            elif selected["field"] == "minute":
                mm_val = (mm_val + delta) % 60
            else:
                ss_val = (ss_val + delta) % 60
            write_time(hh_val, mm_val, ss_val)

        def on_wheel(e):
            d = 1 if (e.delta > 0) else -1
            change_value(d)
        
        for w in [outer, hh_lbl, mm_lbl, ss_lbl, up_btn, down_btn, arrow_frame, colon1, colon2]:
            try:
                w.bind("<MouseWheel>", on_wheel)
            except:
                pass

        def is_typing_elsewhere():
            try:
                root = outer.winfo_toplevel()
                focused = root.focus_get()
                if focused:
                    cls = focused.winfo_class()
                    if cls in ("Entry", "Text", "TEntry", "TCombobox", "Listbox"):
                        return True
            except:
                pass
            return False

        def handle_digit(digit):
            if is_typing_elsewhere():
                return
            nonlocal hh_val, mm_val, ss_val
            val = int(digit)
            
            if len(typed_buffer) >= 2:
                typed_buffer.clear()
            typed_buffer.append(digit)
            
            if len(typed_buffer) == 1:
                limit = 3 if selected["field"] == "hour" else 6
                if val >= limit:
                    if selected["field"] == "hour":
                        hh_val = val
                        write_time(hh_val, mm_val, ss_val)
                        select_field("minute")
                    elif selected["field"] == "minute":
                        mm_val = val
                        write_time(hh_val, mm_val, ss_val)
                        select_field("second")
                    else:
                        ss_val = val
                        write_time(hh_val, mm_val, ss_val)
                    typed_buffer.clear()
                else:
                    if selected["field"] == "hour":
                        hh_val = val
                    elif selected["field"] == "minute":
                        mm_val = val
                    else:
                        ss_val = val
                    write_time(hh_val, mm_val, ss_val)
            else:
                first = typed_buffer[0]
                combined = int(first + digit)
                
                if selected["field"] == "hour":
                    if combined > 23:
                        combined = 23
                    hh_val = combined
                    write_time(hh_val, mm_val, ss_val)
                    select_field("minute")
                elif selected["field"] == "minute":
                    if combined > 59:
                        combined = 59
                    mm_val = combined
                    write_time(hh_val, mm_val, ss_val)
                    select_field("second")
                else:
                    if combined > 59:
                        combined = 59
                    ss_val = combined
                    write_time(hh_val, mm_val, ss_val)
                typed_buffer.clear()

        def handle_backspace():
            if is_typing_elsewhere():
                return
            nonlocal hh_val, mm_val, ss_val
            if selected["field"] == "hour":
                hh_val = 0
            elif selected["field"] == "minute":
                mm_val = 0
            else:
                ss_val = 0
            typed_buffer.clear()
            write_time(hh_val, mm_val, ss_val)

        def navigate_fields(direction):
            if is_typing_elsewhere():
                return
            if direction == -1:
                if selected["field"] == "second":
                    select_field("minute")
                elif selected["field"] == "minute":
                    select_field("hour")
            else:
                if selected["field"] == "hour":
                    select_field("minute")
                elif selected["field"] == "minute":
                    select_field("second")

        def change_value_key(direction):
            if is_typing_elsewhere():
                return
            change_value(direction)

        def on_enter(e):
            try:
                root = outer.winfo_toplevel()
                root.bind("<Up>", lambda ev: change_value_key(1))
                root.bind("<Down>", lambda ev: change_value_key(-1))
                root.bind("<Left>", lambda ev: navigate_fields(-1))
                root.bind("<Right>", lambda ev: navigate_fields(1))
                root.bind("<BackSpace>", lambda ev: handle_backspace())
                for digit in "0123456789":
                    root.bind(digit, lambda ev, d=digit: handle_digit(d))
            except:
                pass

        def on_leave(e):
            outer.configure(border_color="#e5e7eb")
            try:
                root = outer.winfo_toplevel()
                root.unbind("<Up>")
                root.unbind("<Down>")
                root.unbind("<Left>")
                root.unbind("<Right>")
                root.unbind("<BackSpace>")
                for digit in "0123456789":
                    root.unbind(digit)
            except:
                pass

        outer.bind("<Enter>", on_enter)
        outer.bind("<Leave>", on_leave)
        
        select_field("hour")
        write_time(hh_val, mm_val, ss_val)
        return outer

    def _create_searchable_combobox_new(self, parent_cell, tk_var, options_list, pack=True):
        combo = ctk.CTkComboBox(
            parent_cell,
            values=options_list,
            variable=tk_var,
            height=38,
            corner_radius=11,
            border_width=1,
            border_color="#cbd5f0",
            fg_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#f8fafc",
            dropdown_fg_color="#f8fafc",
            dropdown_hover_color="#f1f5f9",
            dropdown_text_color="#1e293b",
            text_color="#1e293b",
            font=("Segoe UI", 11),
            dropdown_font=("Segoe UI", 11)
        )
        if pack:
            combo.pack(fill="x", padx=0, pady=(0, 0))

        combo._base_values = list(options_list)

        def on_keyrelease(e):
            # Ignore navigation keys to not interfere with dropdown interaction
            if e.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab'):
                return
            
            typed = combo.get()
            typed_lower = typed.strip().lower()
            if typed_lower:
                filtered = [v for v in combo._base_values if typed_lower in v.lower()]
            else:
                filtered = combo._base_values
            if "All" not in filtered:
                filtered = ["All"] + filtered
            try:
                combo.configure(values=filtered)
                # Restore the typed text because configure(values=...) resets it
                combo.set(typed)
                
                # Keep cursor at the end
                if hasattr(combo, "_entry") and combo._entry:
                    combo._entry.icursor("end")
            except Exception:
                pass

        def on_select(event=None):
            val = combo.get().strip() or "All"
            tk_var.set(val)
            self._schedule_filter()

        combo.configure(command=lambda v: on_select())

        if hasattr(combo, "_entry") and combo._entry:
            combo._entry.bind("<KeyRelease>", on_keyrelease)
            combo._entry.bind("<FocusIn>", lambda e: combo.configure(border_color="#8b5cf6"))
            combo._entry.bind("<FocusOut>", lambda e: [combo.configure(border_color="#cbd5f0"), on_select()])

        return combo

    def _items_display_list(self):
        out = ["All"]
        for it in self.items_list:
            code = str(it.get("code", "")).strip()
            name = str(it.get("name", "")).strip()
            display = f"{code} - {name}" if code else name
            out.append(display)
        return out
    
    def _on_airgauge_changed(self, *_):
        ag = self.airgauge_var.get().strip()

        channels = self._load_channels_for_airgauge(ag)

        self.channel_combo._base_values = channels
        if hasattr(self.channel_combo, "configure"):
            self.channel_combo.configure(values=channels)
        else:
            self.channel_combo["values"] = channels

        if self.channel_var.get() not in channels:
            self.channel_var.set("All")

        self._schedule_filter()

    def _operators_display_list(self):
        out = ["All"]
        for op in self.operators_list:
            name = str(op.get("name", "")).strip()
            display = f"{op.get('id','')} - {name}" if op.get("id") else name
            out.append(display)
        return out

    def _machines_display_list(self):
        out = ["All"]
        for m in self.machines_list:
            code = str(m.get("code", "")).strip()
            name = str(m.get("name", "")).strip()
            display = f"{code} - {name}" if code else name
            out.append(display)
        return out

    def _update_all_dynamic_filters(self, data_list):
        """
        Dynamically repopulate all dropdowns (Item, Operator, Machine, AirGauge, Channel, etc.)
        based on what is actually present in the provided data_list.
        """
        try:
            items = set()
            operators = set()
            machines = set()
            airgauges = set()
            drawings = set()
            customers = set()

            for row, _, _ in data_list:
                if len(row) > 11 and row[11]: items.add(str(row[11]).strip())
                if len(row) > 9 and row[9]: operators.add(str(row[9]).strip())
                if len(row) > 12 and row[12]: machines.add(str(row[12]).strip())
                if len(row) > 6 and row[6]: 
                    ag = str(row[6]).strip()
                    if not ag.startswith("AG"): ag = f"AG{ag}"
                    airgauges.add(ag)
                if len(row) > 8 and row[8]: drawings.add(str(row[8]).strip())
                if len(row) > 13 and row[13]: customers.add(str(row[13]).strip())

            def update_combo(combo, var, new_vals):
                current = var.get()
                sorted_vals = ["All"] + sorted(list(new_vals))
                combo._base_values = sorted_vals
                if hasattr(combo, "configure"):
                    combo.configure(values=sorted_vals)
                else:
                    combo["values"] = sorted_vals
                if current not in sorted_vals:
                    var.set("All")

            update_combo(self.item_combo, self.item_var, items)
            update_combo(self.operator_combo, self.operator_var, operators)
            update_combo(self.machine_combo, self.machine_var, machines)
            update_combo(self.airgauge_combo, self.airgauge_var, airgauges)
            update_combo(self.drawing_combo, self.drawing_var, drawings)
            update_combo(self.customer_combo, self.customer_var, customers)

        except Exception as e:
            print(f"Filter update error: {e}")

    # ---------------------------
    # Time spinner (inline)
    # ---------------------------
    def _create_time_spinner(self, parent, time_var):
        outer = ctk.CTkFrame(parent, corner_radius=4, border_width=1, border_color="#D8E3DC", fg_color="white")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=0)
        display = ctk.CTkFrame(outer, corner_radius=0, border_width=0, fg_color="white")
        display.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        
        # Configure columns to be uniform and equal width
        display.grid_columnconfigure(0, weight=1, uniform="time_col")
        display.grid_columnconfigure(1, weight=0)
        display.grid_columnconfigure(2, weight=1, uniform="time_col")
        display.grid_columnconfigure(3, weight=0)
        display.grid_columnconfigure(4, weight=1, uniform="time_col")
        
        def parse_time(s):
            try:
                p = s.split(":")
                hh = int(p[0]) if p and p[0] else 0
                mm = int(p[1]) if len(p) > 1 and p[1] else 0
                ss = int(p[2]) if len(p) > 2 and p[2] else 0
            except Exception:
                hh, mm, ss = 0, 0, 0
            hh %= 24; mm %= 60; ss %= 60
            return hh, mm, ss
            
        hh_val, mm_val, ss_val = parse_time(time_var.get())
        NORMAL_BG = "white"; SELECT_BG = "#008A4D"; NORMAL_TEXT = "#222"; SELECT_TEXT = "white"
        LABEL_FONT = ("Segoe UI", 11, "bold"); COLON_FONT = ("Segoe UI", 11)
        
        # Perfectly uniform labels with width=35 and uniform padding
        hh_lbl = ctk.CTkLabel(display, text=f"{hh_val:02d}", font=LABEL_FONT, text_color=NORMAL_TEXT, fg_color=NORMAL_BG, corner_radius=4, anchor="center", width=35)
        hh_lbl.grid(row=0, column=0, sticky="nsew", padx=2, pady=3)
        
        colon1 = ctk.CTkLabel(display, text=":", font=COLON_FONT, text_color=NORMAL_TEXT)
        colon1.grid(row=0, column=1, sticky="nsew", padx=(1, 1))
        
        mm_lbl = ctk.CTkLabel(display, text=f"{mm_val:02d}", font=LABEL_FONT, text_color=NORMAL_TEXT, fg_color=NORMAL_BG, corner_radius=4, anchor="center", width=35)
        mm_lbl.grid(row=0, column=2, sticky="nsew", padx=2, pady=3)
        
        colon2 = ctk.CTkLabel(display, text=":", font=COLON_FONT, text_color=NORMAL_TEXT)
        colon2.grid(row=0, column=3, sticky="nsew", padx=(1, 1))
        
        ss_lbl = ctk.CTkLabel(display, text=f"{ss_val:02d}", font=LABEL_FONT, text_color=NORMAL_TEXT, fg_color=NORMAL_BG, corner_radius=4, anchor="center", width=35)
        ss_lbl.grid(row=0, column=4, sticky="nsew", padx=2, pady=3)
        
        arrow_frame = ctk.CTkFrame(outer, corner_radius=0, border_width=0, fg_color="white")
        arrow_frame.grid(row=0, column=1, sticky="ns")
        
        # Up and Down buttons configured with hover=False, border_width=0, and hover_color matching the normal background to prevent blue color
        up_btn = ModernButton(
            arrow_frame,
            text="▲",
            width=22,
            height=13,
            fg_color="#F5FBF8",
            text_color="#008A4D",
            hover_color="#F5FBF8",
            hover=False,
            corner_radius=4,
            command=lambda: change_value(1),
            takefocus=False
        )
        up_btn.pack(side="top", padx=0, pady=(2, 4))
        
        down_btn = ModernButton(
            arrow_frame,
            text="▼",
            width=22,
            height=13,
            fg_color="#F5FBF8",
            text_color="#008A4D",
            hover_color="#F5FBF8",
            hover=False,
            corner_radius=4,
            command=lambda: change_value(-1),
            takefocus=False
        )
        down_btn.pack(side="top", padx=0, pady=(0, 2))
        
        selected = {"field": "hour"}
        typed_buffer = []
        
        def update_visual():
            # Reset all label colors
            hh_lbl.configure(fg_color=NORMAL_BG, text_color=NORMAL_TEXT)
            mm_lbl.configure(fg_color=NORMAL_BG, text_color=NORMAL_TEXT)
            ss_lbl.configure(fg_color=NORMAL_BG, text_color=NORMAL_TEXT)
            
            if selected["field"] == "hour":
                hh_lbl.configure(fg_color=SELECT_BG, text_color=SELECT_TEXT)
            elif selected["field"] == "minute":
                mm_lbl.configure(fg_color=SELECT_BG, text_color=SELECT_TEXT)
            else:
                ss_lbl.configure(fg_color=SELECT_BG, text_color=SELECT_TEXT)

        def select_field(f):
            selected["field"] = f
            typed_buffer.clear()
            update_visual()
            try:
                root = outer.winfo_toplevel()
                root.focus_set()
            except:
                pass
            
        hh_lbl.bind("<Button-1>", lambda e: select_field("hour"))
        mm_lbl.bind("<Button-1>", lambda e: select_field("minute"))
        ss_lbl.bind("<Button-1>", lambda e: select_field("second"))
        
        def write_time(h, m, s):
            hh_lbl.configure(text=f"{h:02d}")
            mm_lbl.configure(text=f"{m:02d}")
            ss_lbl.configure(text=f"{s:02d}")
            time_var.set(f"{h:02d}:{m:02d}:{s:02d}")
            self._schedule_filter()

        def change_value(delta):
            nonlocal hh_val, mm_val, ss_val
            typed_buffer.clear()
            if selected["field"] == "hour":
                hh_val = (hh_val + delta) % 24
            elif selected["field"] == "minute":
                mm_val = (mm_val + delta) % 60
            else:
                ss_val = (ss_val + delta) % 60
            write_time(hh_val, mm_val, ss_val)

        def on_wheel(e):
            d = 1 if (e.delta > 0) else -1
            change_value(d)
        
        # Bind scroll to everything
        for w in [outer, hh_lbl, mm_lbl, ss_lbl, up_btn, down_btn, arrow_frame, colon1, colon2]:
            try:
                w.bind("<MouseWheel>", on_wheel)
            except:
                pass

        # Helper to check if user is typing inside standard entry fields elsewhere in the app
        def is_typing_elsewhere():
            try:
                root = outer.winfo_toplevel()
                focused = root.focus_get()
                if focused:
                    cls = focused.winfo_class()
                    if cls in ("Entry", "Text", "TEntry", "TCombobox", "Listbox"):
                        return True
            except:
                pass
            return False

        # Keypress Handlers for manual time entry
        def handle_digit(digit):
            if is_typing_elsewhere():
                return
            nonlocal hh_val, mm_val, ss_val
            val = int(digit)
            
            if len(typed_buffer) >= 2:
                typed_buffer.clear()
            typed_buffer.append(digit)
            
            if len(typed_buffer) == 1:
                # If first digit determines completion (e.g. >=3 for hour, >=6 for minute/second)
                limit = 3 if selected["field"] == "hour" else 6
                if val >= limit:
                    if selected["field"] == "hour":
                        hh_val = val
                        write_time(hh_val, mm_val, ss_val)
                        select_field("minute")
                    elif selected["field"] == "minute":
                        mm_val = val
                        write_time(hh_val, mm_val, ss_val)
                        select_field("second")
                    else:
                        ss_val = val
                        write_time(hh_val, mm_val, ss_val)
                    typed_buffer.clear()
                else:
                    if selected["field"] == "hour":
                        hh_val = val
                    elif selected["field"] == "minute":
                        mm_val = val
                    else:
                        ss_val = val
                    write_time(hh_val, mm_val, ss_val)
            else:
                first = typed_buffer[0]
                combined = int(first + digit)
                
                if selected["field"] == "hour":
                    if combined > 23:
                        combined = 23
                    hh_val = combined
                    write_time(hh_val, mm_val, ss_val)
                    select_field("minute")
                elif selected["field"] == "minute":
                    if combined > 59:
                        combined = 59
                    mm_val = combined
                    write_time(hh_val, mm_val, ss_val)
                    select_field("second")
                else:
                    if combined > 59:
                        combined = 59
                    ss_val = combined
                    write_time(hh_val, mm_val, ss_val)
                typed_buffer.clear()

        def handle_backspace():
            if is_typing_elsewhere():
                return
            nonlocal hh_val, mm_val, ss_val
            if selected["field"] == "hour":
                hh_val = 0
            elif selected["field"] == "minute":
                mm_val = 0
            else:
                ss_val = 0
            typed_buffer.clear()
            write_time(hh_val, mm_val, ss_val)

        def navigate_fields(direction):
            if is_typing_elsewhere():
                return
            if direction == -1: # Left
                if selected["field"] == "second":
                    select_field("minute")
                elif selected["field"] == "minute":
                    select_field("hour")
            else: # Right
                if selected["field"] == "hour":
                    select_field("minute")
                elif selected["field"] == "minute":
                    select_field("second")

        def change_value_key(direction):
            if is_typing_elsewhere():
                return
            change_value(direction)

        # Keyboard support (hover to enable)
        def on_enter(e):
            try:
                root = outer.winfo_toplevel()
                root.bind("<Up>", lambda ev: change_value_key(1))
                root.bind("<Down>", lambda ev: change_value_key(-1))
                root.bind("<Left>", lambda ev: navigate_fields(-1))
                root.bind("<Right>", lambda ev: navigate_fields(1))
                root.bind("<BackSpace>", lambda ev: handle_backspace())
                for digit in "0123456789":
                    root.bind(digit, lambda ev, d=digit: handle_digit(d))
            except Exception as ex:
                pass

        def on_leave(e):
            try:
                root = outer.winfo_toplevel()
                root.unbind("<Up>")
                root.unbind("<Down>")
                root.unbind("<Left>")
                root.unbind("<Right>")
                root.unbind("<BackSpace>")
                for digit in "0123456789":
                    root.unbind(digit)
            except Exception as ex:
                pass

        outer.bind("<Enter>", on_enter)
        outer.bind("<Leave>", on_leave)
        
        select_field("hour")
        write_time(hh_val, mm_val, ss_val)
        return outer

    # ---------------------------
    # Calendar popup (click outside to close)
    # ---------------------------
    def open_calendar_popup(self, entry_widget, target_var):
        if Calendar is None:
            return
        try:
            if hasattr(self, "_cal_popup") and self._cal_popup.winfo_exists():
                self._cal_popup.destroy()
            if hasattr(self, "_cal_overlay") and self._cal_overlay.winfo_exists():
                self._cal_overlay.destroy()
        except:
            pass
        root = self.winfo_toplevel()
        overlay = tk.Toplevel(root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        overlay.attributes("-alpha", 0.01)
        overlay.lift()
        self._cal_overlay = overlay
        def close_all(event=None):
            try: popup.destroy()
            except: pass
            try: overlay.destroy()
            except: pass
        overlay.bind("<Button-1>", close_all)
        popup = tk.Toplevel(root); self._cal_popup = popup
        popup.overrideredirect(True); popup.attributes("-topmost", True)
        x = entry_widget.winfo_rootx(); y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        popup.geometry(f"+{x}+{y}"); popup.lift(overlay)
        try:
            d, m, y = target_var.get().split("/"); d=int(d); m=int(m); y=int(y) if int(y)>50 else 2000+int(y)
        except:
            t = datetime.date.today(); d, m, y = t.day, t.month, t.year
        cal = Calendar(popup, selectmode="day", year=y, month=m, day=d, date_pattern="dd/mm/yyyy")
        cal.pack(padx=5, pady=5)
        def on_select(event=None):
            target_var.set(cal.get_date()); close_all()
        cal.bind("<<CalendarSelected>>", on_select)
        popup.bind("<Button-1>", lambda e: "break"); cal.bind("<Button-1>", lambda e: "break")
        popup.bind("<Escape>", lambda e: close_all())

    # ---------------------------
    # Table area build
    # ---------------------------
    def _build_table_area(self):
