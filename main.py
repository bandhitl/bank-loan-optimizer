from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# ── default rates (แก้ใน UI ได้) ────────────────────────────
RATES = dict(
    SCBT_1W=6.20,
    SCBT_2W=6.60,
    SCBT_CROSS=9.20,      # ถ้าฝืนใช้ SCBT ข้ามเดือน
    CIMB_1M=7.00,
    CITI_CALL=7.75,
)
# ─────────────────────────────────────────────────────────────

ID_HOL = holidays.country_holidays("ID")        # วันหยุดอินโดฯ


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def next_bday(d: date) -> date:
    while is_holiday(d):
        d += timedelta(days=1)
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


# ── planner ─────────────────────────────────────────────────
def build_plan(
    start: date,
    total_days: int,
    bridge_priority: list[str],    # ตัวอย่าง ["CITI", "CIMB"]
    rates: dict[str, float] = RATES,
) -> List[Segment]:
    """
    • ใช้ SCBT 1W / 2W ต่อเนื่องจนสิ้นเดือน (รวมวันหยุด)
    • ถ้าเหลือวันข้ามเดือน  → ใช้ bank แรกใน bridge_priority เป็น Call bridge
    • หลังวันทำการแรกของเดือนใหม่ กลับเข้า SCBT วนต่อ
    • ถ้า bridge_priority ว่าง  ⇒ ใช้ SCBT_CROSS ยาวจนจบ
    """
    segs: List[Segment] = []
    cur = next_bday(start)                    # เริ่มวันทำการ
    left = total_days

    def push(bank: str, rate: float, length: int):
        nonlocal cur, left
        end = cur + timedelta(days=length - 1)
        segs.append(Segment(bank, rate, cur, end))
        cur = next_bday(end + timedelta(days=1))
        left -= length

    while left > 0:
        # -------- เติม SCBT ภายในเดือน ----------
        placed = False
        for seg_len, rate_key in ((14, "SCBT_2W"), (7, "SCBT_1W")):
            last = cur + timedelta(days=seg_len - 1)
            if seg_len <= left and last.month == cur.month:
                push("SCBT", rates[rate_key], seg_len)
                placed = True
                break
        if placed:
            continue

        # -------- ต้องข้ามเดือน → Bridge ----------
        if not bridge_priority:
            push("SCBT", rates["SCBT_CROSS"], left)
            break

        bridge_bank = bridge_priority[0]
        bridge_rate = rates["CITI_CALL"] if bridge_bank == "CITI" else rates["CIMB_1M"]

        # ความยาวจนถึงวันทำการสุดท้ายของเดือน
        month_end = date(cur.year, cur.month + 1, 1) - timedelta(days=1)
        while is_holiday(month_end):
            month_end -= timedelta(days=1)
        bridge_len = (month_end - cur).days + 1
        bridge_len = min(bridge_len, left)
        push(bridge_bank, bridge_rate, bridge_len)

    return segs


def total_interest(segs: List[Segment], principal: float) -> float:
    return sum(s.interest(principal) for s in segs)
