import sys
with open("d:/cherry-precisions-product/CHERRY_SPC.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# find ReportPage methods
start_str = '    def _build_filter_grid(self):'
end_str = '    def _build_table_area(self):'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx == -1 or end_idx == -1:
    print("Could not find methods")
    sys.exit(1)

methods_code = content[start_idx:end_idx]

# Remove 'self.refresh_table_data' etc binding if they cause issue, or just define them
dummy_methods = """
    def refresh_table_data(self, *args):
        pass

    def open_analyze_page(self, *args):
        pass

    def _schedule_filter(self, *args):
        pass

    def _set_loading_state(self, state):
        pass
"""

methods_code += dummy_methods

# Find RunChatPage init
runchat_init = '        self.comp_map = self.load_component_specs()\n        self._is_active = False   # becomes True when the page is shown'
runchat_replace = '''        self.comp_map = self.load_component_specs()
        self._is_active = False   # becomes True when the page is shown

        import datetime
        self.from_date_var = tk.StringVar(value="01/01/2020")
        self.to_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%d/%m/%Y"))
        self.from_time_var = tk.StringVar(value="00:00:00")
        self.to_time_var = tk.StringVar(value="23:59:59")
        self.item_var = tk.StringVar(value="All")
        self.operator_var = tk.StringVar(value="All")
        self.machine_var = tk.StringVar(value="All")
        self.airgauge_var = tk.StringVar(value="All")
        self.drawing_var = tk.StringVar(value="All")
        self.customer_var = tk.StringVar(value="All")
        self._build_filter_grid()
'''

if runchat_init in content:
    content = content.replace(runchat_init, runchat_replace)
else:
    print("RunChat init not found!")
    sys.exit(1)

# inject methods at the end of RunChatPage
# look for 'class RunChatPage' and then the next class
class_start = content.find("class RunChatPage")
next_class = content.find("class ", class_start + 20)

# insert before next_class
if next_class != -1:
    content = content[:next_class] + "\n" + methods_code + "\n" + content[next_class:]
else:
    content += "\n" + methods_code + "\n"

with open("d:/cherry-precisions-product/CHERRY_SPC.py", "w", encoding="utf-8") as f:
    f.write(content)
print("SUCCESS")
