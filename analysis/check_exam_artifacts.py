from pathlib import Path
import ast
import hashlib
import json
import re
import zipfile
from pypdf import PdfReader

ROOT = Path(r"D:\DemoExam")
PROJECT = ROOT / "exam_project"
STAGES = ROOT / "analysis/exam_stages"
guide = (ROOT / "EXAM_PROJECT_GUIDE.md").read_text(encoding="utf-8")
checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


check("No analytics section, dependencies or examples", not any(term in guide for term in ["analytics.py", "5.1 Для", "Sessions_analytics", "python -m pip install pandas"]))
for path in PROJECT.rglob("*.py"):
    code = path.read_text(encoding="utf-8")
    ast.parse(code, filename=str(path))
    check("Full current code in guide: " + path.name, code.rstrip() in guide)
    check("No training switch in current code: " + path.name, "MODULE" not in code and "self.module" not in code)
for path in STAGES.rglob("*.py"):
    code = path.read_text(encoding="utf-8")
    ast.parse(code, filename=str(path))
    check("Full stage code in guide: " + str(path.relative_to(STAGES)), code.rstrip() in guide)
    check("No training switch in stage code: " + str(path.relative_to(STAGES)), "MODULE" not in code and "self.module" not in code)
check("No lessons or analytics files in exam project", not (PROJECT / "lessons").exists() and not (PROJECT / "analytics.py").exists())
check("Exactly three app dependencies", (PROJECT / "requirements.txt").read_text(encoding="utf-8").splitlines() == ["psycopg[binary]", "openpyxl", "Pillow"])
check("Simple constructor", "def __init__(self):" in (PROJECT / "app/ui.py").read_text(encoding="utf-8"))
check("No manual refresh feature", "Обновить каталог" not in (PROJECT / "app/ui.py").read_text(encoding="utf-8"))

hashes = json.loads((ROOT / "analysis/exam_learning_hashes.json").read_text(encoding="utf-8"))
check("Learning guide, project and pack untouched", all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items()))
for stage, name in [(2, "Module_2_Catalog.zip"), (3, "Module_3_Interface.zip"), (4, "Module_4_Orders.zip")]:
    with zipfile.ZipFile(ROOT / "exam_versions" / name) as archive:
        check(f"Stage {stage} archive integrity", archive.testzip() is None)
        names = archive.namelist()
        check(f"Stage {stage} has SQL with data and PDF", "chudo_obuv/database/database_with_data.sql" in names and "chudo_obuv/ERD_module_1.pdf" in names)
        check(f"Stage {stage} has five XLSX and 31 photos", sum(n.endswith(".xlsx") for n in names) == 5 and sum(n.startswith("chudo_obuv/assets/products/") for n in names) == 31)
        check(f"Stage {stage} has no venv, caches or analytics", not any(".venv" in n or "__pycache__" in n or "analytics" in n for n in names))
        for name in ["app/ui.py", "app/service.py", "app/common.py"]:
            expected = STAGES / str(stage) / name
            if not expected.exists():
                expected = PROJECT / name
            check(f"Stage {stage}: correct standalone {name}", archive.read("chudo_obuv/" + name) == expected.read_bytes())
with zipfile.ZipFile(ROOT / "Exam_Project_Pack.zip") as archive:
    check("Pack integrity", archive.testzip() is None)
    check("Pack contains correct guide", archive.read("EXAM_PROJECT_GUIDE.md").decode("utf-8") == guide)
reader = PdfReader(PROJECT / "ERD_module_1.pdf")
check("PDF one page and seven table names", len(reader.pages) == 1 and all(name in reader.pages[0].extract_text() for name in ["roles", "users", "products", "sizes", "stock_items", "orders", "order_items"]))
integration = json.loads((ROOT / "analysis/exam_project_checks.json").read_text(encoding="utf-8"))
check("Real DB and GUI checks passed", integration["checks_passed"] >= 70)
report = {"checks_passed": len(checks), "checks": checks, "postgresql_and_tk_checks": integration["checks_passed"]}
(ROOT / "analysis/exam_artifact_checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"artifact_checks_passed": len(checks), "postgresql_and_tk_checks": integration["checks_passed"], "learning_files_unchanged": True}))
