"""
Loan Optimizer – อินโดนีเซีย
• คิดดอกเบี้ย P * r/100 * d/365
• แบ่ง segment  SCBT 1 W / 2 W  (คงอยู่ภายในเดือน)
  เหลือวันข้ามเดือนใช้ CIMB 1 M
• ไม่สลับ/จบ segment ในวันหยุด-เสาร์-อาทิตย์ (ใช้ lib ‘holidays’  ปฏิทิน ID)
• ถ้า segment SCBT ข้ามเดือน → ปรับ rate = 9.20 %
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import holidays

# --- อัตราดอกเบี้ย ---
SCBT_1W    = 6.20
SCBT_2W    = 6.60
SCBT_CROSS = 9.20
CIMB_1M    = 7.00
# -----------------------

ID_HOL = holidays.country_holidays("ID")  # ใช้วันหยุดอินโดนีเซีย


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

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    def interest(self, principal: float) -> float:
        return calc_interest(principal, self.rate, self.days)


# -------- กลยุทธ์หลัก ---------
def build_plan(start: date, total_days: int, principal: float) -> list[Segment]:
    segs: list[Segment] = []
    cur   = next_bday(start)
    remain = total_days

    # 1) SCBT 1W / 2W ภายในเดือน
    while remain > 0 and cur.month == start.month:
        if remain >= 14 and (cur + timedelta(days=13)).month == cur.month:
            seg_len, rate = 14, SCBT_2W
        elif remain >= 7 and (cur + timedelta(days=6)).month == cur.month:
            seg_len, rate = 7, SCBT_1W
        else:
            break

        end = next_bday(cur + timedelta(days=seg_len - 1))
        segs.append(Segment("SCBT", rate, cur, end))
        cur   = next_bday(end + timedelta(days=1))
        remain -= seg_len

    # 2) CIMB 1 M สำหรับวันที่ข้ามเดือน
    if remain > 0:
        end = next_bday(cur + timedelta(days=remain - 1))
        segs.append(Segment("CIMB", CIMB_1M, cur, end))

    # 3) ปรับ Cross-Month Penalty ของ SCBT
    for s in segs:
        if s.bank == "SCBT" and s.end.month != s.start.month:
            s.rate = SCBT_CROSS

    return segs


def total_interest(segs: list[Segment], principal: float) -> float:
    return sum(s.interest(principal) for s in segs)
