from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import holidays

# --- ดอกเบี้ยเริ่มต้น (ปรับใน UI ได้ในอนาคต) ---
RATES = {
    "SCBT_1W": 6.20,
    "SCBT_2W": 6.60,
    "SCBT_CROSS": 9.20,
    "CIMB_1M": 7.00,
    "CITI_CALL": 7.75,
}
# ---------------------------------------------------

ID_HOL = holidays.country_holidays("ID")


def is_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in ID_HOL


def next_bday(d: date) -> date:
    """คืนวันทำการถัดไปจาก d (ถ้า d เป็นวันทำการอยู่แล้วจะคืน d เดิม)"""
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


# ---------- Helper ----------
def add_seg(segs: List[Seg], bank: str, rate: float,
            start: date, length: int) -> date:
    """เพิ่ม segment ยาว length วันต่อเนื่อง (รวมวันหยุด) แล้วคืนวันถัดไป"""
    end = start + timedelta(days=length - 1)
    segs.append(Seg(bank, rate, start, end))
    return end + timedelta(days=1)        # วันถัดไป (อาจเป็นวันหยุด)


# ---------- Core Planner ----------
def build_plan(start: date,
               total_days: int,
               active_banks: list[str]) -> List[Seg]:
    """
    • วน SCBT 1W / 2W ภายในเดือน
    • ถ้าข้ามเดือนให้ Bridge ไปยัง Bank ที่เปิดใช้ลำดับแรก (CITI → CIMB)
        – Bridge ช่วงวันหยุด/วันข้ามทั้งหมด (ดึงอัตราวันหยุดด้วย)
    • กลับเข้า SCBT ทันทีเมื่อพ้นวันทำการแรกของเดือนใหม่
    """
    segs: List[Seg] = []
    cur = start
    remain = total_days

    # เรียง priority ของ bank ปลายทาง
    dst_sequence = [b for b in ["CITI", "CIMB"] if b in active_banks]

    while remain > 0:
        # ---------- SCBT ภายในเดือน ----------
        placed = False
        for seg_len, rate in ((14, RATES["SCBT_2W"]), (7, RATES["SCBT_1W"])):
            last = cur + timedelta(days=seg_len - 1)
            if seg_len <= remain and last.month == cur.month:
                cur = add_seg(segs, "SCBT", rate, cur, seg_len)
                remain -= seg_len
                placed = True
                break
        if placed:
            continue  # กลับขึ้นต้น loop

        # ---------- Bridge ข้ามเดือน ----------
        if not dst_sequence:
            # ถ้าไม่มี bank ปลายทาง -> โดน penalty SCBT_CROSS
            seg_len = remain
            cur = add_seg(segs, "SCBT", RATES["SCBT_CROSS"], cur, seg_len)
            break

        bridge_bank = dst_sequence[0]
        bridge_rate = RATES["CITI_CALL"] if bridge_bank == "CITI" else RATES["CIMB_1M"]

        # วันสุดท้ายของเดือนปัจจุบัน
        month_end = date(cur.year, cur.month + 1, 1) - timedelta(days=1)
        seg_len = (month_end - cur).days + 1
        seg_len = min(seg_len, remain)

        cur = add_seg(segs, bridge_bank, bridge_rate, cur, seg_len)
        remain -= seg_len

        # กระโดดไปวันทำการแรกของเดือนใหม่
        cur = next_bday(cur)

    return segs


def total_interest(segs: List[Seg], p: float) -> float:
    return sum(s.interest(p) for s in segs)
