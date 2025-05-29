from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# ── ค่าเรทเริ่มต้น ─────────────────────────────────────────
RATES = dict(
    SCBT_1W=6.20,
    SCBT_2W=6.60,
    SCBT_CROSS=9.20,
    CIMB_1M=7.00,
    CITI_CALL=7.75,
)
# ───────────────────────────────────────────────────────────

ID_HOL = holidays.country_holidays("ID")     # วันหยุดอินโดฯ


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


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


# ── planner ────────────────────────────────────────────────
def build_plan(
    start: date,
    total_days: int,
    bridge_priority: list[str],       # ex. ["CITI", "CIMB"]
    rates: dict[str, float] = RATES,
) -> List[Segment]:
    """
    • SCBT 1W/2W → สิ้นเดือน (รวมวันหยุด)
    • ถ้าข้ามเดือน  → Bank แรกใน bridge_priority (Call bridge) ครอบวันสิ้นเดือน+วันหยุด
    • วันทำการแรกของเดือนใหม่ → กลับเข้า SCBT ต่อตามปกติ
    • ถ้าไม่เปิด bridge เลย → ใช้ SCBT_CROSS ยาวจนจบ
    """
    segs: List[Segment] = []
    cur = start
    left = total_days

    def push(bank: str, rate_key: str, length: int):
        nonlocal cur, left
        segs.append(
            Segment(bank, rates[rate_key], cur, cur + timedelta(days=length - 1))
        )
        cur += timedelta(days=length)
        left -= length

    while left > 0:
        # --------- SCBT ภายในเดือน ----------
        placed = False
        for seg_len, rate_key in ((14, "SCBT_2W"), (7, "SCBT_1W")):
            end = cur + timedelta(days=seg_len - 1)
            if seg_len <= left and end.month == cur.month:
                push("SCBT", rate_key, seg_len)
                placed = True
                break
        if placed:
            continue

        # --------- ต้องข้ามเดือน ----------
        if not bridge_priority:
            push("SCBT", "SCBT_CROSS", left)
            break

        bank = bridge_priority[0]
        rate_key = "CITI_CALL" if bank == "CITI" else "CIMB_1M"

        # สร้างสะพานตั้งแต่วันนี้ถึงสิ้นเดือน
        next_month_1st = date(cur.year, cur.month + 1, 1)
        bridge_len = (next_month_1st - cur).days
        bridge_len = min(bridge_len, left)
        push(bank, rate_key, bridge_len)

    return segs


def total_interest(segs: List[Segment], principal: float) -> float:
    return sum(s.interest(principal) for s in segs)
