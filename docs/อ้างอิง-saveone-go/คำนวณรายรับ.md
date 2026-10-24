# ระบบคำนวณสรุปยอดรายรับรายวันแยกสาขา (Daily Revenue Calculator)

> Google Apps Script + Google Sheets · ระบบคำนวณและสรุปยอดรายรับตลาดนัดรายวัน แยกตามสาขาและโซน พร้อมส่งข้อมูลเข้าฐานข้อมูลกลาง
>
> **สถานะ:** ใช้งานจริง (Production) · **ผู้รับผิดชอบ/ผู้พัฒนา:** Anansit Maneenoon

---

## 1. ภาพรวมระบบ (Overview)

ระบบนี้อ่านข้อมูลผู้ค้าในชีตประจำวัน แล้ว **คำนวณยอดรายรับสุทธิ** โดยแยกตาม 3 สาขา (บางนา / ประตูกรุงเทพ / ศรีสมาน) และแยกตามโซน (อาหาร / รถ Carboot) จากนั้นแสดงรายงานสรุปให้ยืนยัน ก่อนส่งข้อมูลไปบันทึกใน **ไฟล์ Report กลางของแต่ละสาขา** โดยอัตโนมัติ

**ปัญหาที่แก้:** การสรุปยอดรายวันต้องนับล็อก แยกโซน คำนวณค่าล็อกที่ราคาต่างกันตามวัน รวมค่าไฟค่าอุปกรณ์ แล้วกรอกลง Report กลางเอง — ซับซ้อน ใช้เวลา และคำนวณผิดง่าย ระบบนี้ทำทั้งหมดในคลิกเดียว

**จุดเชื่อมกับเว็บ (สำคัญ):** ไฟล์ Report กลางที่ระบบเขียนข้อมูลเข้าไป เป็นแหล่งข้อมูลที่เว็บไซต์/ฐานข้อมูลดึงไปใช้โดยตรง ระบบนี้จึงทำหน้าที่เป็น **data entry layer** ที่ป้อน **ข้อมูลดิบ** (จำนวนราย/ล็อก/ค่าไฟ/ค่าอุปกรณ์) เข้าสู่ระบบเว็บ — *ไม่ได้ป้อนราคาที่คำนวณ เว็บคำนวณราคาเองจากข้อมูลดิบ (ดูหมายเหตุข้อ 3.5)*

---

## 2. องค์ประกอบของระบบ (Components)

| ส่วน | หน้าที่ |
|------|---------|
| `onOpen` | สร้างเมนู "➕ คำนวณล็อก" 3 ปุ่มตามสาขา |
| `calculateDailyReport*` | ฟังก์ชันตัวกลาง 3 ตัว กำหนดพารามิเตอร์ของแต่ละสาขา |
| `processBranchData` | แกนหลัก: อ่านข้อมูล คำนวณ แสดงรายงาน |
| `saveDataByBranch` | ส่งข้อมูลไปบันทึกในไฟล์ Report กลาง |
| ไฟล์ Report กลาง 3 ไฟล์ | ฐานข้อมูลปลายทาง (แยกสาขา) ที่เว็บดึงไปใช้ |

---

## 3. ลอจิกการทำงานหลัก (Core Logic)

### 3.1 การกำหนดค่าแต่ละสาขา
แต่ละสาขามีกติกาแยกโซนตามตัวอักษรของรหัสล็อกต่างกัน:

| สาขา | โซนอาหาร | โซนรถ (Carboot) |
|------|----------|------------------|
| บางนา | ตัวแรก A–J | ตัวแรก U–Z |
| ประตูกรุงเทพ | 2 ตัวแรก GB–GT | 2 ตัวแรก GW–GZ |
| ศรีสมาน | A–Z (อาหารล้วน) | ยังไม่เปิดบริการ |

### 3.2 การเลือกวันที่
ก่อนคำนวณ ระบบถามวันที่ (รูปแบบ dd/mm/yyyy) หากปล่อยว่าง = ใช้วันปัจจุบัน วันที่นี้สำคัญเพราะใช้แยก **วันธรรมดา (จ–พฤ)** กับ **วันหยุด (ศ–อา)** ซึ่งมีราคาต่างกัน

### 3.3 การนับล็อกและอ่านค่า
- อ่านข้อมูลช่วง A2:S
- รหัสล็อกอยู่คอลัมน์ K โดยนับจำนวนล็อกจากตัวคั่น `:` (เช่น `A005:A006:A007` = 3 ล็อก)
- ค่าไฟอยู่คอลัมน์ M, ค่าอุปกรณ์อยู่คอลัมน์ N

### 3.4 สูตรคำนวณรายได้ (Pricing Logic)

**โซนอาหาร** (ต่อล็อก):
- วันธรรมดา (จ–พฤ): 100 บาท
- วันหยุด (ศ–อา): 130 บาท

**โซนรถ Carboot:**
- วันธรรมดา (จ–พฤ): 300 บาท/ล็อก
- วันหยุด (ศ–อา): 1 ล็อก = 350 บาท, มากกว่า 1 ล็อก = 800 บาท (เหมา)

**ยอดรวมสุทธิ** = ค่าล็อกอาหาร + ค่าล็อกรถ + ค่าไฟ + ค่าอุปกรณ์ (ทุกโซน)

### 3.5 การยืนยันและบันทึก
ระบบแสดงรายงานสรุปแบบละเอียด (จำนวนราย จำนวนล็อก รายได้แต่ละหมวด) ให้ตรวจก่อน เมื่อกดยืนยัน (YES) จึงส่งข้อมูลไปต่อท้าย (`appendRow`) ในไฟล์ Report กลางของสาขานั้น โดยแยกเป็น 2 แถว (แถวอาหาร + แถวรถ)

> **หมายเหตุการออกแบบ:** มีขั้นตอน "ยืนยันก่อนบันทึก" เพื่อกันการเขียนข้อมูลผิดลงฐานข้อมูลกลาง ซึ่งสำคัญมากเพราะข้อมูลนี้เชื่อมกับเว็บโดยตรง

> **⚠️ สำคัญ — ราคาที่คำนวณ ไม่ได้ถูกเขียนลง DB:** ยอดรายได้ที่ระบบคำนวณ (`foodIncome`, `carIncome`, `grandTotal`) ถูกใช้แค่ใน **รายงานยืนยันหน้าจอ** เพื่อให้คนกดตรวจก่อนบันทึกเท่านั้น — `saveDataByBranch` (`appendRow`) เขียนลง Report กลางเฉพาะ **จำนวนราย / จำนวนล็อก / ค่าไฟ / ค่าอุปกรณ์ / สาขา** (ช่องราคาอื่นเป็น 0) เว็บดึงเฉพาะข้อมูลดิบเหล่านี้ไป **คำนวณราคาเองอีกที** ด้วยลอจิกใน `2_SaveOne_Knowledge.md`
>
> ดังนั้น **ลอจิกราคาในไฟล์นี้ที่ต่างจากเว็บ** (โซนรถ: วันธรรมดา 300/ล็อก, วันหยุด 1 ล็อก=350 / >1 ล็อก=800 เหมา — ไม่มี season, ไม่บวก Walk-in +50) **ไม่กระทบเว็บ** เป็นแค่ตัวประเมินคร่าวๆ หน้างานให้คนตรวจ ถ้าจะแก้ให้ตรงเว็บก็ได้ แต่ไม่จำเป็น

---

## 4. ทักษะที่ใช้ (Skills Demonstrated)

- **Google Apps Script** — automation ข้ามหลาย Spreadsheet
- **Business Logic Implementation** — แปลงกติกาการคิดราคาจริงเป็นโค้ด (ราคาต่างตามวัน/โซน/จำนวน)
- **การเชื่อมต่อฐานข้อมูลกลาง** — เขียนข้อมูลข้ามไฟล์ด้วย `openById` + `appendRow`
- **Data pipeline** — ทำหน้าที่เป็นชั้นป้อนข้อมูลเข้าสู่ระบบเว็บ
- **UX ป้องกันความผิดพลาด** — ระบบยืนยันก่อนบันทึก, เลือกย้อนวันได้
- **การจัดการ input ผู้ใช้** — parse วันที่, จัดการกรณี cancel/รูปแบบผิด

---

## 5. โค้ดฉบับเต็ม (Full Source Code)

> ⚠️ **หมายเหตุความปลอดภัย:** โค้ดนี้มี **Spreadsheet ID ของไฟล์ Report กลางทั้ง 3 สาขา** ซึ่งเป็นฐานข้อมูลที่เชื่อมกับเว็บ **ไม่ควรเผยแพร่สาธารณะ** (GitHub public หรือฝังในหน้าเว็บที่คนนอกเข้าถึง) หากต้องนำไปแสดงในพอร์ต/เว็บ ให้แทน ID ด้วย placeholder เช่น `REPORT_SS_ID_BANGNA` ก่อนเสมอ

```javascript
/**
 * 1. ระบบเมนูช็อตคัต
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('➕ คำนวณล็อก')
      .addItem('สรุปยอดวันนี้ (บางนา)', 'calculateDailyReportBangna')
      .addItem('สรุปยอดวันนี้ (ประตูกรุงเทพ)', 'calculateDailyReportBangkokGate')
      .addItem('สรุปยอดวันนี้ (ศรีสมาน)', 'calculateDailyReportSrisaman')
      .addToUi();
}

function calculateDailyReportBangna() { processBranchData("บางนา", "A-J", "U-Z"); }
function calculateDailyReportBangkokGate() { processBranchData("ประตูกรุงเทพ", "GB-GT", "GW-GZ"); }
function calculateDailyReportSrisaman() { processBranchData("ศรีสมาน", "A-Z", "NONE"); }

/**
 * 2. ฟังก์ชันหลักในการประมวลผล (เพิ่มระบบเลือกวันที่)
 */
function processBranchData(branch, foodRange, carRange) {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const lastRow = sheet.getLastRow();

  if (lastRow < 2) {
    ui.alert("❌ ไม่พบข้อมูลในตาราง");
    return;
  }

  // --- ส่วนที่เพิ่มใหม่: ถามวันที่ ---
  let selectedDate = new Date(); // ค่าเริ่มต้นคือวันนี้
  const datePrompt = ui.prompt('📅 เลือกวันที่', 'ระบุวันที่ต้องการ (เช่น 19/04/2026)\n*หากต้องการใช้วันที่วันนี้ ให้ปล่อยว่างแล้วกด OK*', ui.ButtonSet.OK_CANCEL);

  if (datePrompt.getSelectedButton() == ui.Button.OK) {
    let inputDate = datePrompt.getResponseText().trim();
    if (inputDate !== "") {
      // แปลงข้อความจาก dd/mm/yyyy เป็น Date Object
      let parts = inputDate.split('/');
      if (parts.length === 3) {
        selectedDate = new Date(parts[2], parts[1] - 1, parts[0]);
      } else {
        ui.alert("❌ รูปแบบวันที่ไม่ถูกต้อง (กรุณาใช้ วัน/เดือน/ปีค.ศ.)");
        return;
      }
    }
  } else {
    return; // กด Cancel ให้หยุดทำงาน
  }

  const data = sheet.getRange("A2:S" + lastRow).getValues();
  const isWeekday = (selectedDate.getDay() >= 1 && selectedDate.getDay() <= 4);

  let foodCount = 0, foodLocks = 0, foodLight = 0, foodTools = 0;
  let carCount = 0, carLocks = 0, carIncome = 0, carLight = 0, carTools = 0;

  data.forEach(row => {
    let lockStr = String(row[10]); // คอลัมน์ K
    if (!lockStr || lockStr.trim() === "") return;

    let locksArray = lockStr.split(':').filter(item => item.trim() !== "");
    let numLocks = locksArray.length;
    let lockID = locksArray[0].toUpperCase();

    let currentLight = Number(row[13]) || 0; // คอลัมน์ M
    let currentTools = Number(row[14]) || 0; // คอลัมน์ N

    let isFood = false, isCar = false;
    if (branch === "บางนา") {
      let prefix = lockID.charAt(0);
      if (prefix >= 'A' && prefix <= 'J') isFood = true;
      else if (prefix >= 'U' && prefix <= 'Z') isCar = true;
    }
    else if (branch === "ประตูกรุงเทพ") {
      let prefix2 = lockID.substring(0, 2);
      if (prefix2 >= 'GB' && prefix2 <= 'GT') isFood = true;
      else if (prefix2 >= 'GW' && prefix2 <= 'GZ') isCar = true;
    }
    else if (branch === "ศรีสมาน") {
      let prefix = lockID.charAt(0);
      if (prefix >= 'A' && prefix <= 'Z') isFood = true;
    }

    if (isFood) {
      foodCount++; foodLocks += numLocks; foodLight += currentLight; foodTools += currentTools;
    }
    else if (isCar) {
      carCount++; carLocks += numLocks; carLight += currentLight; carTools += currentTools;
      if (isWeekday) carIncome += (numLocks * 300);
      else carIncome += (numLocks === 1 ? 350 : 800);
    }
  });

  let foodIncome = foodLocks * (isWeekday ? 100 : 130);
  let grandTotal = foodIncome + carIncome + foodLight + foodTools + carLight + carTools;

  let dateStr = Utilities.formatDate(selectedDate, Session.getScriptTimeZone(), "dd/MM/yyyy");
  let dayLabel = isWeekday ? "จันทร์-พฤหัสบดี" : "ศุกร์-อาทิตย์";

  let report = `🏢 รายงานสรุปสาขา: ${branch}\n` +
               `📅 วันที่: ${dateStr} (${dayLabel})\n` +
               `--------------------------------------\n` +
               `🍴 [โซนอาหาร ${foodRange}]\n` +
               `   • มาทั้งหมด: ${foodCount} ราย (${foodLocks} ล็อก)\n` +
               `   • รายได้ค่าล็อก: ${foodIncome.toLocaleString()} บาท\n` +
               `   • ค่าไฟฟ้า (M): ${foodLight.toLocaleString()} บาท\n` +
               `   • ค่าอุปกรณ์ (N): ${foodTools.toLocaleString()} บาท\n\n`;

  if (carRange !== "NONE") {
    report += `🚗 [โซน Carboot ${carRange}]\n` +
               `   • มาทั้งหมด: ${carCount} ราย (${carLocks} ล็อก)\n` +
               `   • รายได้ค่าล็อก: ${carIncome.toLocaleString()} บาท\n` +
               `   • ค่าไฟฟ้า (M): ${carLight.toLocaleString()} บาท\n` +
               `   • ค่าอุปกรณ์ (N): ${carTools.toLocaleString()} บาท\n` +
               `--------------------------------------\n`;
  } else {
    report += `🚗 [โซน Carboot]\n   • ยังไม่เปิดให้บริการ\n--------------------------------------\n`;
  }
  report += `💰 ยอดรวมรายรับสุทธิ: ${grandTotal.toLocaleString()} บาท`;

  const response = ui.alert('📊 ยืนยันการบันทึกข้อมูล', report + '\n\nบันทึกข้อมูลลงไฟล์ Report กลางหรือไม่?', ui.ButtonSet.YES_NO);

  if (response == ui.Button.YES) {
    saveDataByBranch(branch, dateStr, foodCount, foodLocks, foodLight, foodTools, carCount, carLocks, carLight, carTools);
  }
}

/**
 * 3. ฟังก์ชันบันทึกข้อมูล
 */
function saveDataByBranch(branch, dateStr, fCount, fLocks, fLight, fTools, cCount, cLocks, cLight, cTools) {
  let targetId = "";
  let foodSheetName = "";
  let carSheetName = "";

  if (branch === "ศรีสมาน") {
    targetId = "<SHEET_ID_SS>";
    foodSheetName = "Report Srisaman";
    carSheetName = "Report-Boot Seller";
  }
  else if (branch === "ประตูกรุงเทพ") {
    targetId = "<SHEET_ID_BG>";
    foodSheetName = "Report SaveOne Go";
    carSheetName = "Report-Car Boot";
  }
  else if (branch === "บางนา") {
    targetId = "<SHEET_ID_BN>";
    foodSheetName = "Report Bangna";
    carSheetName = "Bangna - Car Boot";
  }

  try {
    const targetSs = SpreadsheetApp.openById(targetId);
    const fSheet = targetSs.getSheetByName(foodSheetName);
    if (fSheet) {
      fSheet.appendRow([dateStr, fCount, fLocks, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, fLight, fTools, branch]);
    }
    const cSheet = targetSs.getSheetByName(carSheetName);
    if (cSheet) {
      cSheet.appendRow([dateStr, cCount, cLocks, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, cLight, cTools, branch]);
    }
    SpreadsheetApp.getUi().alert("✅ บันทึกข้อมูลสาขา " + branch + " (วันที่ " + dateStr + ") สำเร็จ!");
  } catch (e) {
    SpreadsheetApp.getUi().alert("❌ ข้อผิดพลาด: " + e.message);
  }
}
```

---

## 6. บทสรุปสำหรับเรซูเม่ / รายงาน (Résumé Bullet)

> พัฒนาระบบคำนวณสรุปยอดรายรับรายวันของตลาดนัด 3 สาขาด้วย Google Apps Script โดยแปลงกติกาการคิดราคาจริง (แยกตามโซนอาหาร/รถ, วันธรรมดา/วันหยุด, จำนวนล็อก) เป็นตรรกะอัตโนมัติ พร้อมระบบยืนยันก่อนบันทึก และเชื่อมต่อส่งข้อมูลเข้าฐานข้อมูลกลางที่เว็บไซต์ดึงไปใช้โดยตรง — เปลี่ยนงานสรุปยอดที่ซับซ้อนและเสี่ยงผิดพลาดให้เหลือเพียงคลิกเดียว

---

## 7. คำแนะนำการเก็บไฟล์ในโปรเจกต์เว็บ (Notes on Storage)

| สิ่งที่เก็บ | เก็บในเว็บ (สาธารณะ) ได้ไหม | เหตุผล |
|-------------|------------------------------|--------|
| เอกสารสรุป (ส่วนที่ 1–4) | ✅ ได้ | เป็นคำอธิบาย ไม่มีข้อมูลลับ |
| โค้ดที่ปิด ID ด้วย placeholder | ✅ ได้ | ปลอดภัย ใช้โชว์พอร์ตได้ |
| โค้ดที่มี Spreadsheet ID จริง | ❌ ไม่ควร | ID คือกุญแจเข้าถึงฐานข้อมูลกลางที่เชื่อมกับเว็บ |

**สรุป:** ถ้าจะเก็บไฟล์นี้ในโปรเจกต์เว็บที่ push ขึ้น repo สาธารณะ ให้แทน Spreadsheet ID จริงด้วย placeholder ก่อน แล้วเก็บเวอร์ชันที่มี ID จริงไว้ในที่ส่วนตัว (เช่น Google Drive ส่วนตัว หรือ .env ที่ไม่ commit) — เอกสารและโครงสร้างโค้ดเปิดเผยได้ แต่ตัว ID ควรเป็นความลับ

---

## Changelog
- **v1.1 (14 ก.ค. 2569):** จดเพิ่ม — ราคาที่คำนวณในไฟล์นี้ใช้แค่รายงานยืนยันหน้าจอ ไม่ได้เขียนลง DB (append เฉพาะข้อมูลดิบ) เว็บคำนวณราคาเองจากข้อมูลดิบ → ลอจิกราคาที่ต่างจากเว็บไม่กระทบ
- **v1.0:** เอกสารตั้งต้น + โค้ดฉบับเต็ม
