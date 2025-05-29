"""
Loan Optimizer – ID holidays / selectable banks
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import holidays
from typing import List

# ---- ดอกเบี้ยปัจจุบัน (แก้ใน UI ได้) ----
DEFAULT_RATES = {
    "SCBT_1W": 6.20,
    "SCBT_2W": 6.60,
    "SCBT_CROSS": 9.20,   # ถ้าหลุดข้ามเดือน
    "CIMB_1M": 7.00,
    "CITI_CALL": 7.75,
    "CITI_3M": 8.69,
}
# -------------------------------------------

ID_HOL = holidays.country_holidays("ID")


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def next_bday(d: date) -> date:
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

    def interest(self, principal: float) -> float:
        return calc_interest(principal, self.rate, self.days())


# ----------- Strategy Builder ------------
def plan_scbt_only(start: date, total_days: int, p: float, rates: dict) -> List[Segment]:
    """ใช้ SCBT ต่อเนื่อง แม้โดน Cross-Month Penalty"""
    segs: List[Segment] = []
    cur = next_bday(start)
    remain = total_days

    while remain > 0:
        if remain >= 14:
            seg_len, rate = 14, rates["SCBT_2W"]
        elif remain >= 7:
            seg_len, rate = 7, rates["SCBT_1W"]
        else:
            seg_len, rate = remain, rates["SCBT_1W"]

        end = next_bday(cur + timedelta(days=seg_len - 1))
        seg = Segment("SCBT", rate, cur, end)
        # ปรับเรทถ้า cross-month
        if seg.start.month != seg.end.month:
            seg.rate = rates["SCBT_CROSS"]
        segs.append(seg)

        cur = next_bday(end + timedelta(days=1))
        remain -= seg_len
    return segs


def plan_scbt_to_bank(start: date, total_days: int, p: float,
                      rates: dict, dst_bank: str) -> List[Segment]:
    """
    ภายในเดือนใช้ SCBT 1W / 2W
    ข้ามเดือนโยกไป  dst_bank (CIMB หรือ CITI_CALL)
    """
    segs: List[Segment] = []
    cur = next_bday(start)
    remain = total_days

    # --- SCBT ภายในเดือนแรก ---
    while remain > 0 and cur.month == start.month:
        if remain >= 14 and (cur + timedelta(days=13)).month == cur.month:
            seg_len, rate = 14, rates["SCBT_2W"]
        elif remain >= 7 and (cur + timedelta(days=6)).month == cur.month:
            seg_len, rate = 7, rates["SCBT_1W"]
        else:
            break
        end = next_bday(cur + timedelta(days=seg_len - 1))
        segs.append(Segment("SCBT", rate, cur, end))
        cur = next_bday(end + timedelta(days=1))
        remain -= seg_len

    # --- bank ปลายทาง สำหรับส่วนที่เหลือ ---
    if remain > 0:
        end = next_bday(cur + timedelta(days=remain - 1))
        if dst_bank == "CIMB":
            rate = rates["CIMB_1M"]
        else:                        # CITI_CALL
            rate = rates["CITI_CALL"]
        segs.append(Segment(dst_bank, rate, cur, end))

    return segs


def total_interest(segs: List[Segment], p: float) -> float:
    return sum(s.interest(p) for s in segs)
