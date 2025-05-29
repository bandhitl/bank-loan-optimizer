from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# ─── ค่าเรทเริ่มต้น (แก้ได้ใน UI) ──────────────────────────
DEFAULT_RATES = dict(
    SCBT_1W=6.20,
    SCBT_2W=6.60,
    SCBT_CROSS=9.20,    # ถ้าฝืนลาก SCBT ข้ามเดือน
    CIMB_1M=7.00,
    CITI_CALL=7.75,
)
# ────────────────────────────────────────────────────────────

ID_HOL = holidays.country_holidays("ID")


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def next_business(d: date) -> date:
    while is_holiday(d):
        d += timedelta(days=1)
    return d


def calc_interest(p: float, r: float, d: int) -> float:
    return p * r / 100 * d / 365


@dataclass
class Segment:
    bank: str
    rate: float
    start: date
    end: date

    def days(self) -> int:
        return (self.end - self.start).days + 1

    def interest(self, p: float) -> float:
        return calc_interest(p, self.rate, self.days())


# ─── Core planner ───────────────────────────────────────────
def build_plan(
    start: date,
    total_days: int,
    bridge_priority: list[str],      # เช่น ["CITI", "CIMB"]
    rates: dict[str, float],
) -> List[Segment]:
    """
    • วน SCBT 1W / 2W ให้จบเดือน (เลี่ยงวันหยุดปลาย segment)
    • ช่วงข้ามเดือนใช้ bank แรกใน bridge_priority (“Call bridge”)
    • หลังวันทำการแรกของเดือนใหม่กลับสู่ SCBT ต่อ
    • ไม่มีการสลับในวันหยุด  (วันหยุดอยู่กับ segment เดิม)
    """
    segs: List[Segment] = []
    cur = next_business(start)             # เริ่มวันทำการแรก
    left = total_days

    def push(bank: str, rate: float, length: int):
        nonlocal cur, left
        end = cur + timedelta(days=length - 1)
        segs.append(Segment(bank, rate, cur, end))
        cur = next_business(end + timedelta(days=1))
        left -= length

    while left > 0:
        # ---------- เติม SCBT ภายในเดือน ----------
        remain_this_month = (date(cur.year, cur.month + 1, 1) - cur).days
        placed = False
        for seg_len, r_key in ((14, "SCBT_2W"), (7, "SCBT_1W")):
            if seg_len <= left and seg_len <= remain_this_month:
                push("SCBT", rates[r_key], seg_len)
                placed = True
                break
        if placed:
            continue

        # ---------- ต้องข้ามเดือน → Bridge ----------
        if not bridge_priority:
            # ไม่มีแบงก์ Bridge – ใช้ SCBT_CROSS ยาวทีเดียว
            push("SCBT", rates["SCBT_CROSS"], left)
            break

        bridge_bank = bridge_priority[0]
        bridge_rate = rates["CITI_CALL"] if bridge_bank == "CITI" else rates["CIMB_1M"]

        # ยาวจนถึงวันทำการสุดท้ายของเดือนนี้
        next_month_first = date(cur.year, cur.month + 1, 1)
        bridge_len = (next_month_first - cur).days
        push(bridge_bank, bridge_rate, bridge_len)

    return segs


def total_interest(segs: List[Segment], p: float) -> float:
    return sum(s.interest(p) for s in segs)
