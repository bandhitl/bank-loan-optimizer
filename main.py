"""
Loan Optimizer Core
- calc_interest           : P * r/100 * d/365
- build_plan / total_interest
  * ใช้ SCBT 1W / 2W ภายในเดือน
  * ส่วนที่ข้ามเดือนใช้ CIMB 1M
  * ไม่สลับ/จบ segment ในวันหยุดหรือเสาร์-อาทิตย์
  * ถ้า SCBT หลุดสิ้นเดือน → ใช้เรท SCBT_CROSS
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import holidays

# ---------- ชุดอัตราดอกเบี้ย ----------
SCBT_1W    = 6.20   # % ต่อปี
SCBT_2W    = 6.60
SCBT_CROSS = 9.20   # เรทปรับเมื่อ SCBT ข้ามเดือน
CIMB_1M    = 7.00   # 1 เดือน
# -------------------------------------

# ---------- วันหยุดอินโดนีเซีย ----------
ID_HOL = holidays.country_holidays("ID")   # ใช้ lib `holidays`
def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL

def next_bday(d: date) -> date:
    """เลื่อนไปวันทำการถัดไป"""
    while is_holiday(d):
        d += timedelta(days=1)
    return d
# ----------------------------------------


def calc_interest(principal: float, rate: float, days: int) -> float:
    return principal * rate / 100 * days / 365


@dataclass
class Segment:
    bank: str
    rate: float
    start: date
    end: date

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    def interest(self, principal: float) -> float:
        return calc_interest(principal, self.rate, self.days)


def build_plan(start: date, total_days: int, principal: float) -> list[Segment]:
    """
    1) เริ่มด้วย SCBT 1W/2W ให้อยู่ภายในเดือนเดียวกับ start
    2) เหลือวันข้ามเดือน → ใช้ CIMB 1M
    3) ไม่สลับ segment ในวันหยุด
    4) ถ้า SCBT segment ใดข้ามสิ้นเดือน → ปรับ rate = SCBT_CROSS
    """
    segs: list[Segment] = []
    cur = next_bday(start)
    remain = total_days

    # --- Phase 1 : SCBT ภายในเดือนปัจจุบัน ---
    while remain > 0 and cur.month == start.month:
        if remain >= 14 and (cur + timedelta(days=13)).month == cur.month:
            seg_len, rate = 14, SCBT_2W
        elif remain >= 7 and (cur + timedelta(days=6)).month == cur.month:
            seg_len, rate = 7, SCBT_1W
        else:
            break  # เหลือวันที่เกินเดือน
        end = next_bday(cur + timedelta(days=seg_len - 1))
        segs.append(Segment("SCBT", rate, cur, end))
        cur = next_bday(end + timedelta(days=1))
        remain -= seg_len

    # --- Phase 2 : CIMB สำหรับส่วนที่ข้ามเดือน ---
    if remain > 0:
        end = next_bday(cur + timedelta(days=remain - 1))
        segs.append(Segment("CIMB", CIMB_1M, cur, end))

    # --- ปรับ Cross-Month Penalty ให้ SCBT ---
    for s in segs:
        if s.bank == "SCBT" and s.end.month != s.start.month:
            s.rate = SCBT_CROSS

    return segs


def total_interest(segs: list[Segment], principal: float) -> float:
    return sum(s.interest(principal) for s in segs)
