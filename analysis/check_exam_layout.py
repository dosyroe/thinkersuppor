from pathlib import Path
import sys
import json
import importlib.util
import zipfile
import tkinter as tk

ROOT = Path(r"D:\DemoExam")
sys.path.insert(0, str(ROOT / "analysis/exam_test_deps"))
sys.path.insert(0, str(ROOT / "exam_project"))
import settings
settings.DB_PORT = 55440
settings.DB_PASSWORD = ""
settings.DB_NAME = json.loads((ROOT / "analysis/exam_project_checks.json").read_text(encoding="utf-8"))["database"]
checks = []
for stage, name in [(2, "Module_2_Catalog.zip"), (3, "Module_3_Interface.zip"), (4, "Module_4_Orders.zip")]:
    target = ROOT / "analysis" / f"exam_layout_stage_{stage}"
    with zipfile.ZipFile(ROOT / "exam_versions" / name) as archive:
        assert all((target / item.filename).resolve().is_relative_to(target.resolve()) for item in archive.infolist())
        archive.extractall(target)
    spec = importlib.util.spec_from_file_location(f"layout_ui_{stage}", target / "chudo_obuv/app/ui.py")
    ui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ui)
    app = ui.ShoeApp()
    for size in ["900x580", "1200x800"]:
        app.geometry(size)
        app.update_idletasks()
        cards = app.catalog_scroll.inner.winfo_children()
        assert len(cards) == 31
        for card in cards:
            panel = next(child for child in card.winfo_children() if isinstance(child, tk.Frame))
            assert panel.winfo_width() >= 120
            assert all(int(label.cget("wraplength")) <= panel.winfo_width() for label in panel.winfo_children())
        checks.append(f"Stage {stage} at {size}: labels wrap within their frame")
    app.destroy()
(ROOT / "analysis/exam_layout_checks.json").write_text(json.dumps({"checks_passed": len(checks), "checks": checks}, ensure_ascii=False, indent=2), encoding="utf-8")
print("Responsive text checks passed:", len(checks))
