from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# ─── default rates (แก้ใน UI ได้) ────────────────────────────
RATES = {
    "SCBT_1W": 6.20,
    "SCBT_2W": 6.60,
    "SCBT_CROSS": 9.20,   # ถ้าไม่มี Call-bridge เลย
    "CIMB_1M": 7.00,
    "CITI_CALL": 7.75,
}
# ─────────────────────────────────────────────────────────────

ID_HOL = holidays.country_holidays("ID")      # วันหยุดอินโดฯ


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def next_business(d: date) -> date:
    while is_holiday(d):
        d += timedelta(days=1)
    return d


def prev_business(d: date) -> date:
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


# ─── core planner ───────────────────────────────────────────
def build_plan(
    start: date,
    total_days: int,
    bridge_priority: list[str],           # เช่น ["CITI", "CIMB"]
    rates: dict[str, float] = RATES,
) -> List[Segment]:
    """
    • วน SCBT ≤14 วัน (7/14/หรือสั้นกว่านั้น) ตราบใดที่:
        – ไม่ชนวันหยุดล่วงหน้า
        – ไม่ข้ามสิ้นเดือน
    • ถ้าเหลือวันทำการ < 7 ก่อนวันหยุด/สิ้นเดือน
        → สลับไป Call-bridge (Bank แรกใน priority)
          ครอบวันหยุดทั้งหมด + วันสิ้นเดือน
    • วันทำการแรกของเดือนใหม่ → กลับเข้า SCBT ต่อ
    • ถ้าไม่เปิด Call-bridge เลย → ใช้ SCBT_CROSS ยาวจนจบ
    """
    segs: List[Segment] = []
    cur = start
    left = total_days

    while left > 0:
        # 1) วันทำการสุดท้ายของเดือนนี้
        month_end = date(cur.year, cur.month + 1, 1) - timedelta(days=1)
        last_bus = prev_business(month_end)

        # 2) วันหยุดถัดไป (รวม cur ถ้าเป็นหยุด)
        nxt = cur
        while not is_holiday(nxt):
            nxt += timedelta(days=1)
        first_hol = nxt

        border = min(last_bus, first_hol - timedelta(days=1))
        room = (border - cur).days + 1      # #วันทำการต่อเนื่องก่อนตัด

        # ---------- case A: room >= 7 ----------
        if room >= 7:
            seg_len = 14 if room >= 14 and left >= 14 else 7
            seg_len = min(seg_len, left, room)
            rate_key = "SCBT_2W" if seg_len == 14 else "SCBT_1W"
            segs.append(Segment("SCBT", rates[rate_key],
                                cur, cur + timedelta(days=seg_len - 1)))
            cur += timedelta(days=seg_len)
            left -= seg_len
            continue

        # ---------- case B: room < 7  → ต้อง bridge ----------
        if not bridge_priority:                     # ไม่มี Call-bank
            segs.append(Segment("SCBT", rates["SCBT_CROSS"],
                                cur, cur + timedelta(days=left - 1)))
            break

        bridge_bank = bridge_priority[0]
        bridge_rate = rates["CITI_CALL"] if bridge_bank == "CITI" else rates["CIMB_1M"]

        bridge_start = cur
        bridge_end = month_end                     # ครอบจนสิ้นเดือน

        # เพิ่มวันหยุดต้นเดือนถัดไป (ถ้ามี) ใน Bridge ด้วย
        nxt_month_day = bridge_end + timedelta(days=1)
        while is_holiday(nxt_month_day):
            bridge_end = nxt_month_day
            nxt_month_day += timedelta(days=1)

        seg_len = (bridge_end - bridge_start).days + 1
        seg_len = min(seg_len, left)

        segs.append(Segment(bridge_bank, bridge_rate,
                            bridge_start, bridge_start + timedelta(days=seg_len - 1)))
        cur += timedelta(days=seg_len)
        left -= seg_len

    return segs


def total_interest(segs: List[Segment], p: float) -> float:
    return sum(s.interest(p) for s in segs)
