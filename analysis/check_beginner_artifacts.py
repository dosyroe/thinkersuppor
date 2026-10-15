from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import ast
import importlib.util
import tempfile
import zipfile
import pandas as pd

ROOT = Path(r"D:\DemoExam")
PROJECT = ROOT / "training_project"
GUIDE = ROOT / "EXAM_LINUX_GUIDE.md"

# Every Python source parses, and each app file is present verbatim in the book.
guide = GUIDE.read_text(encoding="utf-8")
python_files = sorted(PROJECT.rglob("*.py"))
for path in python_files:
    code = path.read_text(encoding="utf-8").rstrip()
    ast.parse(code, filename=str(path))
    assert code in guide, f"Missing full source in tutorial: {path.name}"
for name in ["database/schema.sql", "requirements.txt", "README.md", ".gitignore"]:
    assert (PROJECT / name).read_text(encoding="utf-8").rstrip() in guide
assert "requirements.in" not in guide
assert "check_environment.py" not in guide
assert "source .venv/bin/activate" in guide

for module, filename in [(2, "Module_2_Catalog.zip"), (3, "Module_3_Interface.zip"),
                         (4, "Module_4_Orders.zip")]:
    with zipfile.ZipFile(ROOT / filename) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert not any("__pycache__" in name or ".venv" in name for name in names)
        assert f"MODULE = {module}" in archive.read("chudo_obuv/settings.py").decode("utf-8")
        assert len([name for name in names if name.startswith("chudo_obuv/assets/products/")]) == 31
        assert len([name for name in names if name.endswith(".xlsx")]) == 5
        assert "ВПИШИ_ПАРОЛЬ_POSTGRESQL" in archive.read("chudo_obuv/settings.py").decode("utf-8")
with zipfile.ZipFile(ROOT / "Exam_Linux_Pack.zip") as archive:
    assert archive.testzip() is None
    assert archive.read("EXAM_LINUX_GUIDE.md").decode("utf-8") == guide

spec = importlib.util.spec_from_file_location("analytics_example", PROJECT / "analytics.py")
analytics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analytics)
original_dir = analytics.DATA_DIR
try:
    analytics.calculate()
except ValueError as error:
    assert "Нужны четыре CSV" in str(error)
else:
    raise AssertionError("Missing official CSV must stop rather than invent answers")

# Artificial data only. This is never included among official exam materials.
with tempfile.TemporaryDirectory(prefix="analytics_test_", dir=ROOT / "analysis") as directory:
    analytics.DATA_DIR = Path(directory)
    sessions = []
    for number in range(1, 7):
        sessions.append({"session_id": f"s{number}", "user_id": f"u{number}",
                         "started_at": "2026-01-01 00:00:00",
                         "device_type": "mobile" if number <= 3 else "desktop",
                         "traffic_source": "A" if number <= 2 else "B" if number <= 4 else "C"})
    for number in (1, 5):
        sessions.append({"session_id": f"return{number}", "user_id": f"u{number}",
                         "started_at": "2026-02-15 00:00:00",
                         "device_type": "mobile" if number == 1 else "desktop", "traffic_source": "X"})
    orders, items = [], []
    quantities = [1, 2, 3, 4, 10]
    delays = [1, 2, 3, 4, 10]
    prices = [100, 100, 100, 100, 500]
    for number, (quantity, delay, price) in enumerate(zip(quantities, delays, prices), start=1):
        orders.append({"order_id": str(number), "user_id": f"u{number}", "session_id": f"s{number}",
                       "ordered_at": (pd.Timestamp("2026-01-01") + pd.Timedelta(days=delay)).isoformat(),
                       "status": "completed", "discount_percent": (number - 1) * 5})
        items.append({"order_id": str(number), "model_id": "m1" if number <= 2 else "m2",
                      "quantity": quantity, "unit_price": price, "line_total": quantity * price,
                      "discount_percent": (number - 1) * 5})
    # Must exclude both a canceled order and an April order, including their lines.
    for number, status, when in [(6, "canceled", "2026-01-03"), (7, "completed", "2026-04-01")]:
        orders.append({"order_id": str(number), "user_id": "u6", "session_id": "s6", "ordered_at": when,
                       "status": status, "discount_percent": 0})
        items.append({"order_id": str(number), "model_id": "m1", "quantity": 1000,
                      "unit_price": 10, "line_total": 10000, "discount_percent": 0})
    pd.DataFrame(sessions).to_csv(analytics.DATA_DIR / "Sessions_analytics.csv", index=False)
    pd.DataFrame(orders).to_csv(analytics.DATA_DIR / "Orders_analytics.csv", index=False)
    pd.DataFrame(items).to_csv(analytics.DATA_DIR / "Order_items_analytics.csv", index=False)
    pd.DataFrame([{"model_id": "m1", "category": "Category A"}, {"model_id": "m2", "category": "Category B"}]).to_csv(
        analytics.DATA_DIR / "Shoe_models_analytics.csv", index=False)
    expected_correlation = f"{pd.Series([0, 5, 10, 15, 20]).corr(pd.Series(quantities)):.3f}"
    for level, amount in [("orders", "quantity_times_unit_price"), ("items", "quantity_times_unit_price"), ("orders", "line_total")]:
        analytics.DISCOUNT_LEVEL = level
        analytics.LINE_AMOUNT = amount
        with redirect_stdout(StringIO()):
            answers = analytics.calculate()
        assert answers == {"5.1": "mobile", "5.2": 3600.0, "5.3": "A, C", "5.4": 4,
                           "5.5": expected_correlation, "5.6": "Category B"}, answers
    # Real headers may differ: renaming through the explicit map must work.
    table = pd.read_csv(analytics.DATA_DIR / "Sessions_analytics.csv")
    table.rename(columns={"started_at": "real_session_start"}).to_csv(
        analytics.DATA_DIR / "Sessions_analytics.csv", index=False)
    analytics.COLUMN_MAPS["sessions"]["started_at"] = "real_session_start"
    with redirect_stdout(StringIO()):
        assert analytics.calculate()["5.2"] == 3600.0
analytics.DATA_DIR = original_dir
print(f"Full source embedded: {len(python_files)} Python files")
print("All four archives: valid, resource counts correct, no venv, credentials are placeholders")
print("Analytics: missing files stopped; three modes and actual-header mapping passed on artificial data")
