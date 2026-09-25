import csv
from pathlib import Path
from statistics import mean, pstdev

# ใช้โฟลเดอร์เดียวกับที่ lab_a.py บันทึกผล
data_dir = Path(__file__).resolve().parent / "results" / "lab_a"
warmup = 200


def find_peaks(times, values):
    """หาตำแหน่งเวลาของยอดคลื่นจากข้อมูลแต่ละ step"""
    return [
        times[i]
        for i in range(1, len(values) - 1)
        if values[i] > values[i - 1]
        and values[i] >= values[i + 1]
    ]


def measure_period(peaks):
    # ต้องมีอย่างน้อย 3 ยอด เพื่อวัดได้อย่างน้อย 2 คาบ
    if len(peaks) < 3:
        return None

    intervals = [
        peaks[i + 1] - peaks[i]
        for i in range(len(peaks) - 1)
    ]

    period = mean(intervals)

    # เกณฑ์ตรวจเบื้องต้นที่เลือกใช้ในการวิเคราะห์นี้:
    # ถ้าคาบกระจายมากกว่า 10% ให้ตรวจกราฟเพิ่มเติม
    if pstdev(intervals) / period > 0.10:
        return None

    return period


def display(value, digits=4):
    return "N/A" if value is None else f"{value:.{digits}f}"


summary = []

for condition in ("A0", "A1", "A2"):
    for ic in (1, 2, 3):
        name = f"{condition}_IC{ic}"
        path = data_dir / f"{name}.csv"

        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

        with path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))

        # ใช้เฉพาะข้อมูลตั้งแต่ t=200
        stable = [row for row in rows if float(row["t"]) >= warmup]

        if len(stable) < 3:
            raise ValueError(f"{name}: insufficient data after warmup")

        times = [float(row["t"]) for row in stable]
        o1 = [float(row["o1"]) for row in stable]
        o2 = [float(row["o2"]) for row in stable]

        amp1 = (max(o1) - min(o1)) / 2
        amp2 = (max(o2) - min(o2)) / 2

        peaks1 = find_peaks(times, o1)
        peaks2 = find_peaks(times, o2)

        period1 = measure_period(peaks1)
        period2 = measure_period(peaks2)

        lag_steps = None
        phase_deg = None
        status = "check_period"

        if period1 is not None and period2 is not None:
            period = (period1 + period2) / 2

            # ตรวจว่าทั้งสองสัญญาณมีคาบใกล้เคียงกัน
            if abs(period1 - period2) / period <= 0.05:
                lags = []

                for peak1 in peaks1:
                    # ตัดยอดใกล้ขอบช่วงข้อมูล เพื่อลดการจับคู่ผิดรอบ
                    if not (
                        peaks2[0] + period / 2
                        <= peak1
                        <= peaks2[-1] - period / 2
                    ):
                        continue

                    peak2 = min(peaks2, key=lambda p: abs(p - peak1))
                    difference = peak2 - peak1

                    if abs(difference) <= period / 2:
                        lags.append(difference)

                if len(lags) >= 3:
                    lag_steps = mean(lags)
                    phase_deg = 360 * lag_steps / period
                    status = "ok"
                else:
                    status = "insufficient_peak_pairs"
            else:
                status = "period_mismatch"

        result = {
            "run": name,
            "alpha": float(stable[0]["alpha"]),
            "phi_rad": float(stable[0]["phi"]),
            "amplitude_o1": amp1,
            "amplitude_o2": amp2,
            "period_o1_steps": period1,
            "period_o2_steps": period2,
            "frequency_o1_cycles_per_step": (
                1 / period1 if period1 is not None else None
            ),
            "lag_o2_relative_to_o1_steps": lag_steps,
            "phase_lag_deg": phase_deg,
            "status": status,
        }
        summary.append(result)

        print(
            f"{name}: "
            f"Amp1={display(amp1)}, Amp2={display(amp2)}, "
            f"T1={display(period1)}, T2={display(period2)}, "
            f"Lag={display(lag_steps)} steps, "
            f"Phase={display(phase_deg, 2)} deg, "
            f"status={status}"
        )

output_path = data_dir / "summary_lab_a.csv"

with output_path.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

print(f"\nSaved: {output_path}")