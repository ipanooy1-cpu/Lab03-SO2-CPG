import math
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# แต่ละเงื่อนไข: ชื่อ, alpha, phi
conditions = [
    ("A0", 1.1, 0.2),
    ("A1", 1.1, 0.4),
    ("A2", 1.3, 0.2),
]

# ค่าเริ่มต้นของ activation a1 และ a2
# เป็นตัวอย่างที่เลือกสำหรับการทดลองนี้
initial_states = [
    (0.1, 0.0),
    (0.0, 0.1),
    (0.1, 0.1),
]

steps = 1000
warmup = 200
output_dir = Path("results/lab_a")
output_dir.mkdir(parents=True, exist_ok=True)

for condition, alpha, phi in conditions:
    # คำนวณน้ำหนักทั้ง 4 ตัว
    w11 = alpha * math.cos(phi)
    w12 = alpha * math.sin(phi)
    w21 = -alpha * math.sin(phi)
    w22 = alpha * math.cos(phi)

    for run, (a1, a2) in enumerate(initial_states, start=1):
        rows = []

        # เก็บสถานะเริ่มต้น t=0 และอัปเดตอีก 1000 รอบ
        for t in range(steps + 1):
            o1 = math.tanh(a1)
            o2 = math.tanh(a2)

            rows.append([
                t, condition, a1, a2, o1, o2,
                alpha, phi, w11, w12, w21, w22
            ])

            if t < steps:
                # ทั้งสองสมการใช้ o1 และ o2 ชุดเดิม
                next_a1 = w11 * o1 + w12 * o2
                next_a2 = w21 * o1 + w22 * o2

                # เปลี่ยนสถานะหลังคำนวณครบทั้งคู่
                a1, a2 = next_a1, next_a2

        name = f"{condition}_IC{run}"

        # บันทึกข้อมูลทุกช่วง รวมช่วงเริ่มต้น
        with open(
            output_dir / f"{name}.csv",
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "t", "condition", "a1", "a2", "o1", "o2",
                "alpha", "phi", "w11", "w12", "w21", "w22"
            ])
            writer.writerows(rows)

        # วิเคราะห์และวาดกราฟตั้งแต่ t=200 เป็นต้นไป
        stable = rows[warmup:]
        times = [row[0] for row in stable]
        values1 = [row[4] for row in stable]
        values2 = [row[5] for row in stable]

        amp1 = (max(values1) - min(values1)) / 2
        amp2 = (max(values2) - min(values2)) / 2

        print(
            f"{name}: amplitude o1={amp1:.4f}, "
            f"amplitude o2={amp2:.4f}"
        )

        fig, axes = plt.subplots(2, 1, figsize=(10, 7))

        # กราฟสัญญาณตามเวลา
        axes[0].plot(times, values1, label="o1")
        axes[0].plot(times, values2, label="o2")
        axes[0].set_xlabel("Time step")
        axes[0].set_ylabel("Output")
        axes[0].set_title(
            f"{name}: alpha={alpha}, phi={phi} rad"
        )
        axes[0].legend()
        axes[0].grid(True)

        # กราฟ phase plane
        axes[1].plot(values1, values2)
        axes[1].set_xlabel("o1")
        axes[1].set_ylabel("o2")
        axes[1].set_title("Phase plane")
        axes[1].set_aspect("equal", adjustable="box")
        axes[1].grid(True)

        fig.tight_layout()
        fig.savefig(output_dir / f"{name}.png", dpi=180)
        plt.close(fig)

print(f"Finished! Results saved in: {output_dir.resolve()}")