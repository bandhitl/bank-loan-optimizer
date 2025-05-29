from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# default rates – ปรับได้ใน UI ------------------------------
RATES = {
    "SCBT_1W": 6.20,
    "SCBT_2W": 6.60,
    "SCBT_CROSS": 9.20,
    "CIMB_1M": 7.00,
    "CITI_CALL": 7.75,
}
# -----------------------------------------------------------

ID_HOL = holidays.country_holidays("ID")


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def prev_bday(d: date) -> date:
    while is_holiday(d):
        d -= timedelta(days=1)
    return d


def calc_i(p: float, r: float, days: int) -> float:
    return p * r / 100 * days / 365


@dataclass
class Segment:
    bank: str
    rate: float
    start: date
    end: date

    def days(self) -> int:
        return (self.end - self.start).days + 1

    def interest(self, p: float) -> float:
        return calc_i(p, self.rate, self.days())


# ---------------- Core planner -----------------------------
def build_plan(
    start: date,
    total_days: int,
    bridge_priority: list[str],          # เช่น ["CITI", "CIMB"]
    rates: dict[str, float] = RATES,
) -> List[Segment]:
    segs: List[Segment] = []
    cur = start
    left = total_days

    while left > 0:
        # --- วันสุดท้ายของเดือน & วันทำการสุดท้าย ---
        month_end_cal = date(cur.year, cur.month + 1, 1) - timedelta(days=1)
        month_end_bus = prev_bday(month_end_cal)

        days_rem_month = (month_end_bus - cur).days + 1

        # (A) พอใส่ 14 วันได้?
        if left >= 14 and days_rem_month >= 14:
            seg_len, rate_key = 14, "SCBT_2W"
        # (B) ใส่ 7 วันได้?
        elif left >= 7 and days_rem_month >= 7:
            seg_len, rate_key = 7, "SCBT_1W"
        else:
            # (C) เหลือวันน้อยกว่า 7 ก่อนสิ้นเดือน → Call-bridge
            if not bridge_priority:
                # ไม่มี bank Bridge → ใช้ SCBT_CROSS ยาวรวด
                segs.append(
                    Segment("SCBT", rates["SCBT_CROSS"], cur, cur + timedelta(days=left - 1))
                )
                break

            bank = bridge_priority[0]
            rate_key = "CITI_CALL" if bank == "CITI" else "CIMB_1M"

            # ยาวจากวันนี้ถึงวันทำการสุดท้ายของเดือนนี้
            seg_len = days_rem_month

            segs.append(
                Segment(bank, rates[rate_key], cur, cur + timedelta(days=seg_len - 1))
            )
            cur += timedelta(days=seg_len)
            left -= seg_len
            continue  # ไปเริ่ม SCBT เดือนใหม่

        # ----- push SCBT -----
        segs.append(
            Segment("SCBT", rates[rate_key], cur, cur + timedelta(days=seg_len - 1))
        )
        cur += timedelta(days=seg_len)
        left -= seg_len

    return segs


def total_interest(segs: List[Segment], p: float) -> float:
    return sum(s.interest(p) for s in segs)
