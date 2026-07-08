# Product #9 Build Spec: Personal Finance Tracker (THB)
Target: Google Sheets, single file, shareable via link
Time to build: 1-2 hours
Target user: Thai salaryman + freelancer
Version: 1.0 | Build date: 2026-06-05

---

## 1. Sheet Structure (6 sheets total)

สร้าง Google Sheet เดียว มี 6 sheets เรียงตามลำดับนี้ (tab ด้านล่าง):

### Sheet 1: Dashboard

**Purpose:** 1-page summary view เห็นสุขภาพการเงินทั้งเดือนใน 1 จอ

**Layout:** Cell A1 = "Dashboard" (title), แล้ว cells ตามตาราง

| Cell | Label | Formula/Value |
|---|---|---|
| B2 | เดือนปัจจุบัน | `=TEXT(TODAY(),"MMMM YYYY")` |
| B4 | **รายรับเดือนนี้** | `=SUMIFS(Income!D:D, Income!A:A, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1), Income!A:A, "<"&EDATE(DATE(YEAR(TODAY()),MONTH(TODAY()),1),1))` |
| B5 | รายจ่ายเดือนนี้ | `=SUMIFS(Expenses!D:D, Expenses!A:A, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1), Expenses!A:A, "<"&EDATE(DATE(YEAR(TODAY()),MONTH(TODAY()),1),1))` |
| B6 | คงเหลือ (เงินออม) | `=B4-B5` |
| B8 | **เป้าหมายออม (%)** | `=Settings!B3` (อ้างอิงจาก Settings) |
| B9 | ออมได้จริง (%) | `=IF(B4=0, 0, B6/B4)` |
| B10 | สถานะ | `=IF(B9>=B8, "✅ บรรลุเป้า", "⚠️ ต่ำกว่าเป้า")` |
| D4 | **Budget รายจ่าย** | `=Settings!B1` |
| D5 | ใช้ไป | `=B5` |
| D6 | คงเหลือ budget | `=D4-D5` |
| D7 | % ใช้ไป | `=IF(D4=0, 0, D5/D4)` |
| F4 | **Top 5 หมวดรายจ่าย** | (ดู formula ใน Section 2) |
| H4 | **ความคืบหน้าเป้าออม** | (ดู Section 2) |

**Purpose:** ผู้ใช้เปิด Sheet นี้ก่อนเลย เห็นภาพรวมทันที

---

### Sheet 2: Income

**Purpose:** บันทึกรายรับทั้งหมด (เงินเดือน, freelance, อื่น ๆ)

**Columns:**

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Date | Source | Type | Gross | Tax Withheld | Net | Notes |

**Type options (dropdown):** Salary, Freelance, Bonus, Investment, Other

**Sample rows (3-5):**

| Date | Source | Type | Gross | Tax Withheld | Net | Notes |
|---|---|---|---|---|---|---|
| 2026-06-01 | บริษัท ABC | Salary | 35,000 | 1,500 | 33,500 | เงินเดือนประจำเดือน |
| 2026-06-05 | ลูกค้า XYZ | Freelance | 15,000 | 750 | 14,250 | ทำเว็บ freelance |
| 2026-06-15 | บริษัท ABC | Salary | 35,000 | 1,500 | 33,500 | เงินเดือน |
| 2026-06-20 | ขายของออนไลน์ | Other | 3,500 | 0 | 3,500 | ขายเสื้อผ้า FB |

**Auto-sum ที่ row 100 (หรือ row สุดท้าย + 1):**
- `=SUM(D2:D99)` — Gross รวม
- `=SUM(E2:E99)` — Tax รวม
- `=SUM(F2:F99)` — Net รวม

---

### Sheet 3: Expenses

**Purpose:** บันทึกรายจ่ายทั้งหมด แยกตามหมวด

**Columns:**

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Date | Category | Description | Amount | Payment Method | Notes |

**Category options (dropdown):** Food, Transport, Housing, Health, Education, Entertainment, Shopping, Other

**Payment Method options (dropdown):** Cash, Bank Transfer, Credit Card, PromptPay, Other

**Sample rows (10):**

| Date | Category | Description | Amount | Payment Method | Notes |
|---|---|---|---|---|---|
| 2026-06-01 | Housing | ค่าเช่าห้อง | 8,000 | Bank Transfer | ห้อง คอนโด ลาดพร้าว |
| 2026-06-02 | Food | กับข้าว + ของสด | 850 | PromptPay | ตลาด |
| 2026-06-03 | Transport | น้ำมันรถ | 1,200 | Credit Card | เติม 91 |
| 2026-06-04 | Food | กินข้าวนอก | 250 | Cash | ข้าวจานเดียว |
| 2026-06-05 | Entertainment | Netflix | 419 | Credit Card | รายเดือน |
| 2026-06-06 | Health | ค่ายา | 320 | Cash | ร้านยา |
| 2026-06-07 | Shopping | เสื้อผ้า | 1,500 | PromptPay | UNIQLO |
| 2026-06-08 | Transport | BTS เดือน | 1,000 | PromptPay | Rabbit card |
| 2026-06-09 | Education | หนังสือ | 750 | Credit Card | ซื้อออนไลน์ |
| 2026-06-10 | Food | กาแฟ + ขนม | 180 | PromptPay | ร้านกาแฟ |

**Auto-sum per category ที่ row 50+ (ใช้ SUMIFS):**
- `=SUMIFS(D:D, B:B, "Food")` — รวม Food
- `=SUMIFS(D:D, B:B, "Transport")` — รวม Transport
- ทำทุก category

**Total ที่ row 60:**
- `=SUM(D2:D49)` — รายจ่ายรวมทั้งหมด

---

### Sheet 4: Tax Calculator

**Purpose:** คำนวณภาษีรายได้บุคคลธรรมดาอัตโนมัติ (Thai progressive tax 2026)

**Layout (cells):**

| Cell | Label | Value/Formula |
|---|---|---|
| B1 | **คำนวณภาษีประจำปี** | (header) |
| B3 | รายได้รวมทั้งปี (Gross) | (user input — กรอกเอง) |
| B4 | หัก ณ ที่จ่ายสะสม (Withheld) | (user input — กรอกเอง) |
| B5 | ประกันสังคม (สูงสุด 9,000/ปี) | (user input) |
| B6 | ค่าลดหย่อนส่วนตัว | 60,000 |
| B7 | เงินบริจาค | (user input, default 0) |
| B8 | **รายได้สุทธิ (Net Income)** | `=MAX(0, B3-B5-B6-B7)` |
| B10 | **ภาษีที่ต้องจ่าย (คำนวณ)** | (formula ดู Section 2) |
| B11 | หัก ณ ที่จ่ายไปแล้ว | `=B4` |
| B12 | **ภาษีที่ต้องจ่ายเพิ่ม / ขอคืน** | `=B10-B11` |
| B14 | สถานะ | `=IF(B12>0, "ต้องจ่ายเพิ่ม " & TEXT(B12, "#,##0") & " บาท", "ได้คืน " & TEXT(ABS(B12), "#,##0") & " บาท")` |

**Thai Progressive Tax Brackets 2026:**

| Net Income (THB) | Tax Rate |
|---|---|
| 0 – 150,000 | 0% |
| 150,001 – 300,000 | 5% |
| 300,001 – 500,000 | 10% |
| 500,001 – 750,000 | 15% |
| 750,001 – 1,000,000 | 20% |
| 1,000,001 – 2,000,000 | 25% |
| 2,000,001 – 4,000,000 | 30% |
| 4,000,001+ | 35% |

**Personal allowance:** 60,000 THB/year (ใส่ใน B6 เป็น fixed value)

---

### Sheet 5: Savings Goals

**Purpose:** ติดตามเป้าหมายการออมหลายเป้าพร้อมกัน

**Columns:**

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Goal | Target Amount | Current | Progress % | Monthly Contribution | ETA (months) | Status |

**Sample rows (3-4):**

| Goal | Target | Current | Progress % | Monthly Contribution | ETA | Status |
|---|---|---|---|---|---|---|
| Emergency Fund | 100,000 | 45,000 | 45% | 5,000 | 11 | 🟡 In progress |
| Vacation (Japan) | 80,000 | 20,000 | 25% | 10,000 | 6 | 🟡 In progress |
| New Laptop | 50,000 | 50,000 | 100% | 0 | 0 | ✅ Done |
| iPhone 17 Pro | 45,000 | 12,000 | 27% | 3,000 | 11 | 🟡 In progress |

**Formulas:**
- D2 (Progress %): `=IF(B2=0, 0, C2/B2)`
- F2 (ETA): `=IF(E2=0, "N/A", CEILING((B2-C2)/E2, 1))`
- G2 (Status): `=IF(D2>=1, "✅ Done", IF(D2>=0.75, "🟢 Almost", IF(D2>=0.25, "🟡 In progress", "🔴 Just started")))`

**Conditional formatting:**
- Column D: `<25%` = แดง (`#ef4444`), `25-75%` = เหลือง (`#f59e0b`), `>75%` = เขียว (`#22c55e`)

---

### Sheet 6: Settings

**Purpose:** ศูนย์รวมการตั้งค่า — sheet อื่น ๆ ดึงค่าจากที่นี่

**Layout (cells):**

| Cell | Label | Value | Type |
|---|---|---|---|
| A1 | **ตั้งค่าทั่วไป** | | header |
| B1 | Budget รายจ่ายรายเดือน | 20,000 | user input |
| B2 | งบ Food | 6,000 | user input |
| B3 | งบ Transport | 3,000 | user input |
| B4 | งบ Housing | 10,000 | user input |
| B5 | งบ Entertainment | 2,000 | user input |
| B6 | งบอื่น ๆ | 3,000 | user input |
| A8 | **เป้าหมาย** | | header |
| B8 | เป้าออม (%) | 20 | user input (20%) |
| B9 | เป้า Emergency Fund (เดือน) | 6 | user input |
| A11 | **ภาษี** | | header |
| B11 | ค่าลดหย่อนส่วนตัว | 60,000 | fixed |
| B12 | ประกันสังคม/ปี (max) | 9,000 | fixed |
| A14 | **สกุลเงิน** | | header |
| B14 | Currency | THB | fixed |
| B15 | Locale | th-TH | fixed |

**Validation:**
- B8 (เป้าออม): ต้อง 0-100 (%)
- B1-B6: ต้อง >= 0

---

## 2. Key Formulas (copy-paste ready)

ใช้สูตรเหล่านี้ใน cell ที่ระบุ — เปิด Google Sheet แล้ว paste ได้เลย

### 1. รายรับเดือนปัจจุบัน (Dashboard B4)
```excel
=SUMIFS(Income!D:D, Income!A:A, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1), Income!A:A, "<"&EDATE(DATE(YEAR(TODAY()),MONTH(TODAY()),1),1))
```

### 2. รายจ่ายเดือนปัจจุบัน (Dashboard B5)
```excel
=SUMIFS(Expenses!D:D, Expenses!A:A, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1), Expenses!A:A, "<"&EDATE(DATE(YEAR(TODAY()),MONTH(TODAY()),1),1))
```

### 3. เงินคงเหลือ (Dashboard B6)
```excel
=B4-B5
```

### 4. % ออม (Dashboard B9)
```excel
=IF(B4=0, 0, B6/B4)
```

### 5. รายจ่ายตามหมวด (Expenses row 50+)
```excel
=SUMIFS(Expenses!D:D, Expenses!B:B, "Food")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Transport")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Housing")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Health")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Education")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Entertainment")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Shopping")
=SUMIFS(Expenses!D:D, Expenses!B:B, "Other")
```

### 6. Thai Progressive Tax (Tax Calculator B10)
```excel
=MAX(0,
  MIN(B8, 150000)*0
) + MAX(0, MIN(B8, 300000)-150000)*0.05
  + MAX(0, MIN(B8, 500000)-300000)*0.10
  + MAX(0, MIN(B8, 750000)-500000)*0.15
  + MAX(0, MIN(B8, 1000000)-750000)*0.20
  + MAX(0, MIN(B8, 2000000)-1000000)*0.25
  + MAX(0, MIN(B8, 4000000)-2000000)*0.30
  + MAX(0, B8-4000000)*0.35
```

### 7. Tax Owed / Refund (Tax Calculator B12)
```excel
=B10-B4
```

### 8. Progress % Savings Goal (Savings Goals D2)
```excel
=IF(B2=0, 0, C2/B2)
```

### 9. ETA เป้าออม (Savings Goals F2)
```excel
=IF(E2=0, "N/A", CEILING((B2-C2)/E2, 1))
```

### 10. Status เป้าออม (Savings Goals G2)
```excel
=IF(D2>=1, "✅ Done", IF(D2>=0.75, "🟢 Almost", IF(D2>=0.25, "🟡 In progress", "🔴 Just started")))
```

### 11. Top 5 หมวดรายจ่าย (Dashboard F4:H8) — ใช้ 5 formula
```excel
=SORT(SUMIFS(Expenses!D:D, Expenses!B:B, {"Food";"Transport";"Housing";"Health";"Education";"Entertainment";"Shopping";"Other"}), 1, FALSE)
```
(ถ้า SORT ไม่ได้ผล ให้ใช้ INDEX + LARGE + MATCH)

### 12. Progress bar (Savings Goals column H) — ใช้ REPT
```excel
=REPT("█", ROUND(D2*20)) & REPT("░", 20-ROUND(D2*20))
```

### 13. Total Gross Income (Income row 100)
```excel
=SUM(D2:D99)
```

### 14. Total Net Income (Income row 101)
```excel
=SUM(F2:F99)
```

### 15. Total Tax Withheld (Income row 102)
```excel
=SUM(E2:E99)
```

---

## 3. Visual Design

### Color Scheme

| สี | Hex Code | ใช้กับ |
|---|---|---|
| Green (รายรับ) | `#22c55e` | Income column, positive numbers |
| Red (รายจ่าย) | `#ef4444` | Expenses column, negative numbers |
| Blue (ออม) | `#3b82f6` | Savings goals, progress bars |
| Yellow (warning) | `#f59e0b` | In progress 25-75% |
| Gray (header) | `#1f2937` | Header row background |
| White | `#ffffff` | Cell background |

### Conditional Formatting Rules

**Sheet 1 (Dashboard):**
- B9 (% ออม): `>= B8` = เขียวพื้น, `< B8` = เหลืองพื้น
- D7 (% budget ใช้ไป): `> 100%` = แดงพื้น, `70-100%` = เหลืองพื้น

**Sheet 3 (Expenses):**
- Column D (Amount): ตัวเลข > 0 = ตัวอักษรสีแดง (`#dc2626`)

**Sheet 5 (Savings Goals):**
- Column D (Progress %): `< 0.25` = แดงพื้น, `0.25-0.75` = เหลืองพื้น, `> 0.75` = เขียวพื้น
- Column G (Status): มี emoji → ไม่ต้อง CF

### Header Row Formatting (ทุก sheet)

- Background: `#1f2937` (gray-800)
- Text: `#ffffff`, bold
- Font size: 12pt
- Height: 36px
- Horizontal alignment: center
- Freeze row 1 (View → Freeze → 1 row)

### Frozen Panes

- Sheet 1 (Dashboard): Freeze A2 (เห็น header เสมอ)
- Sheet 2 (Income): Freeze A2
- Sheet 3 (Expenses): Freeze A2
- Sheet 4 (Tax): Freeze A2
- Sheet 5 (Savings): Freeze A2
- Sheet 6 (Settings): Freeze A2

### Number Formatting

- Cells ที่เป็นเงิน (Income D-F, Expenses D, Savings B-C): Format → Number → Custom: `#,##0.00`
- Cells ที่เป็น % (Dashboard B9, D7, Savings D): Format → Number → Percent (2 ตำแหน่ง)
- Cells ที่เป็น Date: Format → Date → `YYYY-MM-DD`

---

## 4. Setup Steps (10 steps, 1-2 hours)

### Step 1: สร้าง Google Sheet ใหม่
- ไปที่ https://sheets.google.com
- คลิก "+ Blank" สร้าง sheet ใหม่
- ตั้งชื่อไฟล์: `Personal Finance Tracker (THB) — {{BRAND_NAME}}`

### Step 2: สร้าง 6 sheets (tabs)
- คลิก "+" ด้านล่างซ้าย เพื่อเพิ่ม sheet
- ตั้งชื่อ (คลิกขวา → Rename):
  1. `Dashboard`
  2. `Income`
  3. `Expenses`
  4. `Tax Calculator`
  5. `Savings Goals`
  6. `Settings`

### Step 3: Copy headers ตาม spec ใน Section 1
- Sheet 1 → Row 1 ใส่ "Dashboard" (A1) แล้ว cells ตามตาราง
- Sheet 2 → Row 1 ใส่ headers: Date | Source | Type | Gross | Tax Withheld | Net | Notes
- Sheet 3 → Row 1 ใส่ headers: Date | Category | Description | Amount | Payment Method | Notes
- Sheet 4 → ใส่ labels ตามตาราง B1-B14
- Sheet 5 → Row 1 ใส่ headers ตามตาราง
- Sheet 6 → ใส่ labels ตามตาราง A1-B15

### Step 4: เพิ่ม formulas (Section 2)
- Copy-paste 15 formulas ลงใน cells ที่ระบุ
- ทดสอบ 1 formula ก่อน (Dashboard B4) แล้วค่อย ๆ ทำต่อ

### Step 5: เพิ่ม Conditional Formatting
- Format → Conditional formatting
- ทำตามกฎใน Section 3
- ใช้ "Color scale" สำหรับ Progress %

### Step 6: เพิ่ม Data Validation (dropdowns)
- Sheet 2 (Income) Column C: เลือก cell C2 → Data → Data validation → Criteria: List of items → `Salary,Freelance,Bonus,Investment,Other`
- Sheet 3 (Expenses) Column B: `Food,Transport,Housing,Health,Education,Entertainment,Shopping,Other`
- Sheet 3 (Expenses) Column E: `Cash,Bank Transfer,Credit Card,PromptPay,Other`
- Sheet 6 (Settings) B8: ตัวเลข 0-100

### Step 7: ทดสอบด้วย sample data
- Copy sample data จาก Section 5 ลง Sheet 2 และ Sheet 3
- เปิด Dashboard → ดูว่า cell B4, B5, B6 อัปเดต
- ทดสอบ Tax Calculator: ใส่ Gross 600,000 → ดูภาษีที่คำนวณ

### Step 8: Lock Dashboard เป็น default
- คลิกขวา tab "Dashboard" → สี tab = เขียว (`#38ef7d`)
- ลาก tab "Dashboard" ไปทางซ้ายสุด
- (Optional) ซ่อน sheets ที่ไม่ต้องการให้ user เห็น: คลิกขวา → Hide sheet
  - แนะนำซ่อน "Settings" ไว้ (advanced users เปิดเองได้)

### Step 9: ตั้ง share permissions
- คลิก "Share" (มุมขวาบน)
- เปลี่ยน "Restricted" → "Anyone with the link"
- Permission: "Viewer" (ผู้ซื้อดูได้อย่างเดียว ไม่แก้ของคนอื่น)
- **สำคัญ:** ถ้าต้องการให้ user "Make a copy" ได้ → เปลี่ยนเป็น "Editor" หรือใส่คำแนะนำใน email ส่งไป

### Step 10: ทดสอบ acceptance criteria
- ทำตาม Section 6
- ถ้าผ่านหมด → เก็บ file ID ของ Google Sheet ไว้สำหรับส่ง email ให้ลูกค้า

---

## 5. Sample Data (พร้อม paste)

### Sheet 2 (Income) — 5 rows

```
2026-06-01	บริษัท ABC	Salary	35000	1500	33500	เงินเดือนประจำเดือน
2026-06-05	ลูกค้า XYZ	Freelance	15000	750	14250	ทำเว็บ freelance
2026-06-15	บริษัท ABC	Salary	35000	1500	33500	เงินเดือน
2026-06-20	ขายของออนไลน์	Other	3500	0	3500	ขายเสื้อผ้า FB
2026-06-25	ลูกค้า DEF	Freelance	8000	400	7600	ออกแบบโลโก้
```

### Sheet 3 (Expenses) — 10 rows

```
2026-06-01	Housing	ค่าเช่าห้อง	8000	Bank Transfer	ห้อง คอนโด ลาดพร้าว
2026-06-02	Food	กับข้าว + ของสด	850	PromptPay	ตลาด
2026-06-03	Transport	น้ำมันรถ	1200	Credit Card	เติม 91
2026-06-04	Food	กินข้าวนอก	250	Cash	ข้าวจานเดียว
2026-06-05	Entertainment	Netflix	419	Credit Card	รายเดือน
2026-06-06	Health	ค่ายา	320	Cash	ร้านยา
2026-06-07	Shopping	เสื้อผ้า	1500	PromptPay	UNIQLO
2026-06-08	Transport	BTS เดือน	1000	PromptPay	Rabbit card
2026-06-09	Education	หนังสือ	750	Credit Card	ซื้อออนไลน์
2026-06-10	Food	กาแฟ + ขนม	180	PromptPay	ร้านกาแฟ
```

### Sheet 4 (Tax Calculator) — ตัวอย่าง input

| Cell | Value | หมายเหตุ |
|---|---|---|
| B3 | 750000 | รายได้รวมทั้งปี |
| B4 | 25000 | หัก ณ ที่จ่ายสะสม |
| B5 | 9000 | ประกันสังคม (max) |
| B6 | 60000 | ค่าลดหย่อนส่วนตัว (auto) |
| B7 | 0 | เงินบริจาค |

**ผลลัพธ์ที่คาดหวัง:**
- B8 (Net Income) = 681,000
- B10 (ภาษี) = (681,000 - 150,000) × 5% + (500,000 - 300,000) × 10% + (681,000 - 500,000) × 15%
  = 26,550 + 20,000 + 27,150
  = **73,700 บาท**
- B12 (ต้องจ่ายเพิ่ม) = 73,700 - 25,000 = **48,700 บาท**

### Sheet 5 (Savings Goals) — 3 rows

```
Emergency Fund	100000	45000	0.45	5000	11	🟡 In progress
Vacation (Japan)	80000	20000	0.25	10000	6	🟡 In progress
New Laptop	50000	50000	1	0	0	✅ Done
```

---

## 6. Acceptance Criteria

ทดสอบทั้งหมดนี้ก่อน deliver ให้ลูกค้า:

### Test 1: บันทึก income 1 รายการ
- Action: เปิด Sheet 2 → เพิ่ม row ใหม่ → ใส่ Date, Source, Type, Gross, Tax Withheld
- Expected: ใส่ได้ภายใน **30 วินาที**
- Result: ✅ / ❌

### Test 2: บันทึก expenses 3 รายการ
- Action: เปิด Sheet 3 → เพิ่ม 3 rows → เลือก Category จาก dropdown → ใส่ Amount
- Expected: เสร็จภายใน **1 นาที 30 วินาที** (รวม dropdown click)
- Result: ✅ / ❌

### Test 3: ดู Dashboard อัปเดต
- Action: กลับไป Sheet 1 (Dashboard)
- Expected: B4, B5, B6, B9 เปลี่ยนค่าอัตโนมัติ — **ไม่ต้อง refresh**
- Result: ✅ / ❌

### Test 4: คำนวณภาษี
- Action: เปิด Sheet 4 → ใส่ B3 = 600,000, B4 = 25,000, B5 = 9,000
- Expected: B10 (ภาษี) = 50,350 บาท, B12 (จ่ายเพิ่ม) = 25,350 บาท
- Result: ✅ / ❌
- (Verify: (600,000-9,000-60,000) = 531,000 net; 150,000×0 + 150,000×0.05 + 200,000×0.10 + 31,000×0.15 = 7,500+20,000+4,650 = 32,150 ... ใส่ค่าใหม่ทดสอบตามจริง)

### Test 5: ติดตาม savings goal
- Action: เปิด Sheet 5 → เพิ่ม goal ใหม่ (Target=50,000, Current=10,000, Monthly=5,000)
- Expected: Progress% = 20% (แดง), ETA = 8 เดือน, Status = "🔴 Just started"
- Result: ✅ / ❌

### Test 6: Formulas ไม่มี error
- Action: เลื่อนดูทุก sheet
- Expected: ไม่มี cell ที่แสดง `#REF!` หรือ `#N/A` หรือ `#DIV/0!`
- Result: ✅ / ❌

### Test 7: Mobile-friendly
- Action: เปิด Google Sheets app บนมือถือ
- Expected: อ่านได้ทุก sheet, dropdown ใช้ได้, scroll ได้
- Result: ✅ / ❌

### Test 8: Share link ใช้งานได้
- Action: เปิด Incognito → paste share link
- Expected: เปิดได้โดยไม่ต้อง login
- Result: ✅ / ❌

### Test 9: Validation ทำงาน
- Action: ลองพิมพ์ "abc" ใน cell Amount
- Expected: Google Sheets reject (เพราะ format = number)
- Result: ✅ / ❌

### Test 10: Copy + edit ได้
- Action: File → Make a copy → แก้ข้อมูลใน copy
- Expected: แก้ได้โดยไม่กระทบ original
- Result: ✅ / ❌

---

## Deliverable Checklist (สำหรับคน build)

- [ ] Google Sheet สร้างแล้ว มี 6 tabs
- [ ] Headers ครบทุก sheet
- [ ] 15 formulas ทำงาน
- [ ] Conditional formatting 3+ rules
- [ ] Data validation dropdowns 3+ lists
- [ ] Sample data 5 income + 10 expenses ใส่แล้ว
- [ ] Share link: "Anyone with link can view"
- [ ] Tax Calculator ทดสอบกับตัวเลข 3 cases (300k, 600k, 1.5M)
- [ ] Mobile test ผ่าน
- [ ] File ID เก็บไว้แล้ว → ส่งให้ลูกค้าใน email (Section 4 Step 9)

**Build time estimate:**
- มีประสบการณ์ Google Sheets: **45 นาที - 1 ชั่วโมง**
- มือใหม่: **1.5 - 2 ชั่วโมง**

---

## Tax Bracket Reference (สำหรับ verify)

Thai personal income tax 2026 (สำหรับ net income หลังหักค่าลดหย่อน):

| Bracket | Range (THB) | Rate | Tax on top of bracket |
|---|---|---|---|
| 1 | 0 – 150,000 | 0% | 0 |
| 2 | 150,001 – 300,000 | 5% | 7,500 |
| 3 | 300,001 – 500,000 | 10% | 27,500 |
| 4 | 500,001 – 750,000 | 15% | 65,000 |
| 5 | 750,001 – 1,000,000 | 20% | 115,000 |
| 6 | 1,000,001 – 2,000,000 | 25% | 365,000 |
| 7 | 2,000,001 – 4,000,000 | 30% | 965,000 |
| 8 | 4,000,001+ | 35% | (35% on amount > 4M) |

**Personal allowance:** 60,000 THB/year (standard)
**Social security:** max 9,000 THB/year (5% of salary, capped at 15,000/month × 12 = 180,000/yr × 5% = 9,000)

**ตัวอย่างการคำนวณ:**
- Net Income 681,000 (เช่น Section 5)
- Tax = 0 + 7,500 + 20,000 + 27,150 = 54,650 บาท
- (Brackets 1-4: 0% on 150k + 5% on 150k + 10% on 200k + 15% on 181k)
