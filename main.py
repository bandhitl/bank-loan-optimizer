from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# ----- ดอกเบี้ย -----
R = {
    "SCBT_1W": 6.20,
    "SCBT_2W": 6.60,
    "CITI_CALL": 7.75,
}
# ---------------------

ID_HOL = holidays.country_holidays("ID")


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def next_bday(d: date) -> date:
    while is_holiday(d):
        d += timedelta(days=1)
    return d


def calc_i(p: float, r: float, d: int) -> float:
    return p * r / 100 * d / 365


@dataclass
class Seg:
    bank: str
    rate: float
    start: date
    end: date

    def days(self) -> int:
        return (self.end - self.start).days + 1

    def interest(self, p: float) -> float:
        return calc_i(p, self.rate, self.days())


# ---------- NEW: auto-cycle SCBT ↔ CITI ----------
def plan_scbt_citi_cycle(start: date, total_days: int) -> List[Seg]:
    segs: List[Seg] = []
    cur, left = next_bday(start), total_days

    while left > 0:
        # (1) พยายามใส่ 14d / 7d SCBT ให้ “ไม่ข้ามเดือน”
        placed = False
        for seg_len, rate in ((14, R["SCBT_2W"]), (7, R["SCBT_1W"])):
            last = cur + timedelta(days=seg_len - 1)
            if seg_len <= left and last.month == cur.month:
                end = next_bday(last)
                segs.append(Seg("SCBT", rate, cur, end))
                cur = next_bday(end + timedelta(days=1))
                left -= seg_len
                placed = True
                break

        if placed:
            continue  # วน loop เติม SCBT ต่อ

        # (2) ถ้าใส่ SCBT เพิ่มแล้วจะข้ามเดือน ⇒ ใช้ CITI Call bridge
        month_end = date(cur.year, cur.month, 28)
        # หา last business day ของเดือนนี้
        while month_end.month == cur.month:
            month_end += timedelta(days=1)
        month_end -= timedelta(days=1)
        while is_holiday(month_end):
            month_end -= timedelta(days=1)

        # ช่วง CITI เริ่มวันนี้ ถึงวันทำการแรกของเดือนถัดไป-1
        end = month_end
        days_citi = (end - cur).days + 1
        if days_citi > left:
            end = cur + timedelta(days=left - 1)
            days_citi = left
        segs.append(Seg("CITI", R["CITI_CALL"], cur, end))
        cur = next_bday(end + timedelta(days=1))
        left -= days_citi

    return segs


def total_interest(segs: List[Seg], p: float) -> float:
    return sum(s.interest(p) for s in segs)
