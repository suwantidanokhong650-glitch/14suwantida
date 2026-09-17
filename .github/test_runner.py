import os
import re
import subprocess
import sys


def normalize_text(text):
    """ตัดสัญลักษณ์ ตัวพิมพ์เล็ก-ใหญ่ และเว้นวรรคส่วนเกิน"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[!.,:="\'\(\)]', " ", text)
    return " ".join(text.split())


def extract_numbers(text):
    """ดึงตัวเลขทั้งหมดจากผลลัพธ์ของนักเรียน"""
    if not text:
        return []
    return [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]


def run_student_code(filename, input_data):
    """สั่งรันโค้ดนักเรียน รองรับทั้งมีและไม่มี .py"""
    target_file = filename
    if not os.path.exists(target_file) and not target_file.endswith(".py"):
        target_file = filename + ".py"

    if not os.path.exists(target_file):
        return None, "File Not Found"

    try:
        process = subprocess.run(
            [sys.executable, target_file],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=5,
        )
        return process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return None, "Timeout (โปรแกรมวนลูปไม่จบ)"
    except Exception as e:
        return None, str(e)


# =========================================================
# เกณฑ์การตรวจยืดหยุ่นแยกรายข้อสำหรับ Set 7 (ข้อละ 4 คะแนน)
# =========================================================


def grade_exam_1(output, stderr, test_case):
    """ข้อ 1: คำนวณเงินทอน [pay - price]"""
    expected = test_case["expected"]
    pay = test_case["pay"]
    price = test_case["price"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณเงินทอนถูกต้อง
    elif any(abs(n - (price - pay)) < 0.1 for n in nums) or any(
        abs(n - pay) < 0.1 for n in nums
    ):
        return 0.5  # คำนวณสลับฝั่ง (price - pay) หรือแสดงเฉพาะยอดเงินที่จ่าย
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_2(output, stderr, test_case):
    """ข้อ 2: ตรวจสอบอุณหภูมิร่างกาย (Fever / Normal)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์ Fever หรือ Normal ถูกต้อง (ไม่ซีเรียสตัวพิมพ์เล็ก-ใหญ่)
    elif "fever" in norm_out or "normal" in norm_out:
        return 0.5  # พิมพ์สถานะออกมาแต่เงื่อนไขสลับกัน
    return 0.0


def grade_exam_3(output, stderr, test_case):
    """ข้อ 3: คำนวณราคาสินค้าตามสถานะสมาชิก (สมาชิก ลด 10%)"""
    expected = test_case["expected"]
    price = test_case["price"]
    discount_amount = price * 0.10
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณราคาสุทธิถูกต้อง
    elif any(abs(n - price) < 0.1 for n in nums) or any(
        abs(n - discount_amount) < 0.1 for n in nums
    ):
        return 0.5  # แสดงราคาเดิมเต็มจำนวน หรือแสดงเฉพาะยอดส่วนลด 10%
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_4(output, stderr, test_case):
    """ข้อ 4: คำนวณค่าจอดรถ (0, 20 หรือ 50)"""
    expected = test_case["expected"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณค่าจอดรถตรงตามช่วงเวลา
    elif any(n in [0, 20, 50] for n in nums):
        return 0.5  # พิมพ์ตัวเลขกลุ่มราคาค่าจอดรถออกมาแต่เงื่อนไขผิด
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_5(output, stderr, test_case):
    """ข้อ 5: ประเมินค่าดัชนีมวลกาย BMI (Underweight / Normal / Overweight)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์ Underweight / Normal / Overweight ถูกต้อง
    elif any(k in norm_out for k in ["underweight", "normal", "overweight"]):
        return 0.5  # พิมพ์เกณฑ์ BMI ตัวใดตัวหนึ่งออกมาได้
    return 0.0


# =========================================================
# ชุดข้อมูลทดสอบ (Test Cases สำหรับ Set 7)
# =========================================================
EXAMS = {
    "Examination_1.py": {
        "grader": grade_exam_1,
        "cases": [
            {"input": "100\n70\n", "expected": 30, "pay": 100, "price": 70},
            {"input": "500\n120\n", "expected": 380, "pay": 500, "price": 120},
            {"input": "50\n50\n", "expected": 0, "pay": 50, "price": 50},
            {"input": "1000\n450\n", "expected": 550, "pay": 1000, "price": 450},
        ],
    },
    "Examination_2.py": {
        "grader": grade_exam_2,
        "cases": [
            {"input": "36.5\n", "expected": "Normal"},
            {"input": "37.4\n", "expected": "Normal"},
            {"input": "37.5\n", "expected": "Fever"},
            {"input": "39.0\n", "expected": "Fever"},
        ],
    },
    "Examination_3.py": {
        "grader": grade_exam_3,
        "cases": [
            {"input": "100\n1\n", "expected": 90.0, "price": 100},
            {"input": "100\n0\n", "expected": 100.0, "price": 100},
            {"input": "500\n1\n", "expected": 450.0, "price": 500},
            {"input": "250\n0\n", "expected": 250.0, "price": 250},
        ],
    },
    "Examination_4.py": {
        "grader": grade_exam_4,
        "cases": [
            {"input": "1\n", "expected": 0},
            {"input": "3\n", "expected": 20},
            {"input": "4\n", "expected": 20},
            {"input": "5\n", "expected": 50},
        ],
    },
    "Examination_5.py": {
        "grader": grade_exam_5,
        "cases": [
            {"input": "16.5\n", "expected": "Underweight"},
            {"input": "18.5\n", "expected": "Normal"},
            {"input": "22.0\n", "expected": "Normal"},
            {"input": "25.0\n", "expected": "Overweight"},
        ],
    },
}

# =========================================================
# ประมวลผลและสร้าง Markdown สรุปคะแนน
# =========================================================
total_score = 0.0
summary_rows = []

for exam_name, exam_data in EXAMS.items():
    grader = exam_data["grader"]
    cases = exam_data["cases"]

    exam_score = 0.0
    passed_cases = 0.0

    for case in cases:
        stdout, stderr = run_student_code(exam_name, case["input"])
        if stdout is not None:
            score = grader(stdout, stderr, case)
            exam_score += score
            if score >= 1.0:
                passed_cases += 1.0
            elif score > 0:
                passed_cases += 0.5

    final_exam_score = min(4.0, round(exam_score, 1))
    total_score += final_exam_score

    if final_exam_score >= 4.0:
        status = "🟢 ผ่าน"
    elif final_exam_score > 0:
        status = "🟡 ผ่านบางส่วน"
    else:
        status = "❌ ไม่ผ่าน"

    score_display = (
        f"{int(final_exam_score)}"
        if final_exam_score.is_integer()
        else f"{final_exam_score}"
    )
    passed_display = (
        f"{int(passed_cases)}"
        if passed_cases.is_integer()
        else f"{passed_cases}"
    )

    summary_rows.append(
        f"| `{exam_name}` | {status} | {passed_display}/4 เคส | {score_display} / 4 |"
    )

final_total_display = (
    f"{int(total_score)}" if total_score.is_integer() else f"{total_score}"
)

markdown_summary = f"""
## 📊 สรุปผลการสอบวิชาเขียนโปรแกรม (Set 7)

| ข้อสอบ | สถานะการตรวจ | ผ่าน Test Cases | คะแนนที่ได้ |
| :--- | :--- | :--- | :--- |
""" + "\n".join(summary_rows) + f"""

### 🎯 คะแนนรวมทั้งหมด: {final_total_display} / 20 คะแนน
"""

print(markdown_summary)

github_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if github_summary_path:
    with open(github_summary_path, "a", encoding="utf-8") as f:
        f.write(markdown_summary)
