# ระบบจัดการข้อมูลผู้ค้า Walk-in (Walk-in Data System)

> Google Apps Script + Google Sheets · ระบบจัดรูปแบบตารางอัตโนมัติและฟอร์มบันทึกผู้ค้ารายวันสำหรับตลาดนัด
>
> **สถานะ:** ใช้งานจริง (Production) · **ผู้รับผิดชอบ/ผู้พัฒนา:** Anansit Maneenoon

---

## 1. ภาพรวมระบบ (Overview)

ระบบนี้ช่วยแปลง "ข้อมูลดิบ" ที่ export ออกมาจากระบบจอง ให้กลายเป็นตารางเอกสารที่พร้อมใช้งานหน้างานทันที โดยอัตโนมัติ พร้อมทั้งมีฟอร์มสำหรับเพิ่มผู้ค้าที่มาลงหน้างาน (Walk-in) ให้แทรกเข้าตำแหน่งที่ถูกต้องตามรหัสล็อก (Lock ID)

**ปัญหาที่แก้:** เดิมต้องจัดตารางเอกสารเอง (ลบคอลัมน์เกิน ใส่เลขลำดับ ใส่กรอบ ระบายสี ดึงประวัติผู้ค้า) ทุกวัน ใช้เวลานานและผิดพลาดง่าย ระบบนี้ย่อทุกขั้นตอนเหลือกดปุ่มเดียว และเพิ่มผู้ค้า Walk-in ได้โดยไม่ต้องเรียงเอง

**คุณค่าเชิงธุรกิจ:** ลดเวลาจัดเอกสารรายวันจากหลายสิบนาทีเหลือไม่กี่วินาที · ลดข้อผิดพลาดในการเรียงลำดับ · ผู้ตรวจหน้างานอ่านตารางได้ง่ายเพราะเรียงตามรหัสล็อก

---

## 2. องค์ประกอบของระบบ (Components)

| ไฟล์ | ชนิด | หน้าที่ |
|------|------|---------|
| `Code.gs` | Apps Script | แกนหลักทั้งหมด: เมนู, จัดรูปแบบตาราง, ฟอร์ม, ตรรกะแทรกข้อมูล |
| `WalkInForm.html` | HTML Dialog | ฟอร์มบันทึกผู้ค้าทีละคน (สำหรับผู้ใช้ทั่วไป) |
| `WalkInBulk.html` | HTML Dialog | ฟอร์มวางข้อมูลหลายคนพร้อมกัน (จำกัดสิทธิ์เฉพาะเจ้าของ) |
| ไฟล์ประวัติกลาง | Google Sheet ภายนอก | แหล่งข้อมูลประวัติการกระทำผิดที่ดึงผ่าน IMPORTRANGE |

---

## 3. ลอจิกการทำงานหลัก (Core Logic)

### 3.1 เมนู (`onOpen`)
เมื่อเปิดไฟล์ Google Sheet จะสร้างเมนู **"⚙️ Walk-in Data"** ประกอบด้วย:
- 📝 เปิดฟอร์มบันทึกข้อมูล Walk-in (ทุกคน)
- 🛠️ รันการจัดรูปแบบทั้งหมด (setupSheetFull)
- ⚡ วางหลายคนพร้อมกัน (**โชว์เฉพาะเจ้าของ** — ถ้าไม่ใช่เจ้าของหรืออ่านอีเมลไม่ได้ เมนูนี้จะไม่แสดงเลย)

### 3.2 การจัดรูปแบบตารางอัตโนมัติ (`setupSheetFull`)
ทำงาน 13 ขั้นตอนต่อเนื่อง:

1. **ลบคอลัมน์ที่ไม่ต้องการ** — ลบตามตำแหน่งจากมากไปน้อย เพื่อไม่ให้ index เลื่อน
2. **แทรกคอลัมน์ No.** ด้านหน้าสุด
3. **เพิ่ม 3 คอลัมน์:** กระทำผิด / เซ็น / ประวัติ
4. **จัดรูปแบบหัวตาราง** (ตัวหนา, Calibri, กึ่งกลาง, กรอบ)
5. **ใส่เลขลำดับ** อัตโนมัติ (ใช้ `setValues` ยิงทีเดียว = เร็ว)
6. **ใส่กรอบทั้งตาราง**
7. **แทรกแถววันที่** ด้านบน (merge + จัดกึ่งกลาง)
8. **ระบายสีตามวันในสัปดาห์** — แต่ละวันมีชุดสีเฉพาะ (อา=แดง, จ=ขาว, อ=ชมพู, พ=เขียว, พฤ=ส้ม, ศ=ฟ้า, ส=ม่วง)
9. **ระบายสีคอลัมน์ค่าไฟ/ค่าอุปกรณ์** + ตั้งคอลัมน์ล็อกเป็น text ล้วน (กันรหัสถูกตัด)
10. **ใส่สูตร VLOOKUP + IMPORTRANGE** ดึงประวัติการกระทำผิดจากไฟล์กลาง
11. **Conditional Formatting** — ไฮไลต์แดงถ้าเจอคำว่า "เสี่ยง"
12. **เรียงข้อมูลตามรหัสล็อก** (คอลัมน์ F)
13. **แทรกหัวตารางซ้ำคั่นแต่ละกลุ่มตัวอักษร** — เพื่อให้อ่านง่ายเมื่อพิมพ์

### 3.3 ตรรกะการหาตำแหน่งแทรก (`findInsertionRow`) — จุดเด่นทางเทคนิค
เมื่อเพิ่มผู้ค้า Walk-in ใหม่ ระบบต้องแทรกเข้าตำแหน่งที่ถูกต้อง โดย:
- **แยกรหัสล็อกเป็น (ตัวอักษร + ตัวเลข)** เช่น `C023,24` → กลุ่ม `C` เลข `23`
- **เทียบเป็นตัวเลขจริง** (ไม่ใช่เทียบข้อความ) จึงเรียง `C5 < C8 < C11 < C23` ได้ถูกต้อง
- **ต้องอยู่ในบล็อกตัวอักษรเดียวกัน** (C อยู่กับ C ไม่หลุดไป D)
- **ข้ามแถวหัวตารางที่คั่นกลุ่ม** ได้อย่างถูกต้อง

> **หมายเหตุประวัติการแก้ไข:** เวอร์ชันแรกใช้การเทียบข้อความ (`localeCompare`) ทำให้รหัสกลุ่ม C เรียงผิดและหลุดไปโผล่บล็อก D ได้ แก้เป็นการแยกตัวอักษร+ตัวเลขแล้วเทียบเลขจริง จึงเรียงถูกต้องทุกกรณี

### 3.4 การแยกข้อมูลดิบ (`parseRawData` — ฝั่ง HTML)
รับข้อความดิบที่ผู้ใช้วาง เช่น `นายชวกร A058-60 40 0 แพนเค้กจิ๋ว` แล้วแยกเป็น ชื่อ / รหัสล็อก / ค่าไฟ / ค่าอุปกรณ์ / สินค้า โดยอัตโนมัติ:
- ใช้ **รหัสล็อกเป็นหมุดตัด** (คำแรกที่เป็น ตัวอักษร+ตัวเลข)
- ทุกอย่างก่อนหมุด = ชื่อ (มีเว้นวรรคได้)
- สองตัวเลขถัดจากหมุด = ค่าไฟ/ค่าอุปกรณ์
- ที่เหลือ = สินค้า
- รองรับ 3 รูปแบบ: มีรหัสเต็ม / มีแต่ราคา / ข้อความล้วน

### 3.5 การควบคุมสิทธิ์ (Access Control)
ฟอร์ม "วางหลายคน" จำกัดเฉพาะเจ้าของ ด้วยการเทียบอีเมลผู้ใช้กับค่าที่กำหนดไว้ ป้องกัน 3 ชั้น:
1. **เมนู** (`onOpen`) — โชว์รายการ "วางหลายคน" เฉพาะเมื่ออีเมลตรงกับเจ้าของ คนอื่นไม่เห็นรายการนี้เลย
2. **ฟังก์ชันเปิดฟอร์ม** (`showWalkInBulkForm`) — เช็คอีเมลก่อนเปิด (กันคนเรียกฟังก์ชันตรง)
3. **ฟังก์ชันบันทึก** (`saveWalkInEntries`) — เช็คอีเมลอีกครั้งก่อนเขียนข้อมูล

> **บทเรียนทางเทคนิค (สำคัญ):** `Session.getActiveUser().getEmail()` มัก **คืนค่าว่าง `""`** สำหรับบัญชี @gmail.com ทั่วไป (โดยเฉพาะเมื่อถูกเรียกผ่าน `google.script.run` จาก dialog หรือบาง trigger) ทำให้เทียบอีเมลไม่ผ่าน → "สิทธิ์หลุด" ทั้งที่เป็นเจ้าของเอง
>
> **วิธีแก้:** สร้างฟังก์ชัน `getUserEmail()` ที่ fallback ไปใช้ `Session.getEffectiveUser().getEmail()` เมื่อ `getActiveUser` ว่าง แล้วใช้ตัวนี้ทุกจุดที่เช็คสิทธิ์ และย้ายการเช็คในเมนูมาซ่อนรายการแทนการโชว์แล้วบล็อก — ถ้าอ่านอีเมลไม่ได้ (ค่าว่าง) เมนูจะไม่โชว์ (fail-safe ปลอดภัยไว้ก่อน)

---

## 4. ทักษะที่ใช้ (Skills Demonstrated)

- **Google Apps Script** (JavaScript) — เขียน automation บน Google Workspace
- **การจัดการ Spreadsheet ระดับลึก** — batch operations, conditional formatting, borders, merge
- **Cross-file data** — IMPORTRANGE + VLOOKUP ดึงข้อมูลข้ามไฟล์
- **การออกแบบ Algorithm** — ตรรกะเรียงลำดับ/แทรกข้อมูลที่จัดการ edge case (แยกกลุ่ม, เทียบเลข, ข้ามหัวตาราง)
- **HTML/CSS/JavaScript** — ออกแบบ dialog form + parser ฝั่ง client
- **Access Control** — ระบบจำกัดสิทธิ์ตามผู้ใช้
- **UX สำหรับงานจริง** — ตารางพรีวิวก่อนบันทึก, การระบายสีเพื่อลดความผิดพลาดหน้างาน

---

## 5. โค้ดฉบับเต็ม (Full Source Code)

> ⚠️ **หมายเหตุความปลอดภัย:** โค้ดด้านล่างมี Spreadsheet ID และอีเมลจริง หากนำไปเก็บในที่สาธารณะ (GitHub public / เว็บ) ควรแทนที่ค่าเหล่านี้ด้วย placeholder เช่น `YOUR_SPREADSHEET_ID` และ `YOUR_EMAIL` ก่อน

### 5.1 `Code.gs`

```javascript
const AUTHORIZED_EMAIL = "<อีเมล Google ของเจ้าของ>";

const EXTERNAL_SS_ID = "<SHEET_ID_WALKIN_EXTERNAL>";

// อีเมลที่เชื่อถือได้: เผื่อ getActiveUser คืนค่าว่างสำหรับบัญชี @gmail.com ทั่วไป
function getUserEmail() {
  return Session.getActiveUser().getEmail() || Session.getEffectiveUser().getEmail();
}

function onOpen() {
  const email = getUserEmail();
  const menu = SpreadsheetApp.getUi().createMenu('⚙️ Walk-in Data')
      .addItem('📝 เปิดฟอร์มบันทึกข้อมูล Walk-in', 'showWalkInForm')
      .addSeparator()
      .addItem('🛠️ รันการจัดรูปแบบทั้งหมด (setupSheetFull)', 'setupSheetFull');

  // เมนูนี้โชว์เฉพาะเจ้าของ ถ้าอีเมลว่าง (fail-safe) ก็ไม่โชว์
  if (email === AUTHORIZED_EMAIL) {
    menu.addSeparator()
        .addItem('⚡ วางหลายคนพร้อมกัน (เฉพาะเจ้าของ)', 'showWalkInBulkForm');
  }

  menu.addToUi();
}

function showWalkInForm() {
  const html = HtmlService.createHtmlOutputFromFile('WalkInForm').setWidth(400).setHeight(600);
  SpreadsheetApp.getUi().showModalDialog(html, '📝 บันทึกข้อมูลพ่อค้า Walk-in');
}

function showWalkInBulkForm() {
  if (getUserEmail() !== AUTHORIZED_EMAIL) {
    SpreadsheetApp.getUi().alert('ออปชันนี้ใช้ได้เฉพาะเจ้าของเท่านั้น');
    return;
  }
  const html = HtmlService.createHtmlOutputFromFile('WalkInBulk').setWidth(420).setHeight(640);
  SpreadsheetApp.getUi().showModalDialog(html, '⚡ วางหลายคนพร้อมกัน');
}

function setupSheetFull() {
  const start = new Date();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  let lastColumn = sheet.getLastColumn();
  let lastRow = sheet.getLastRow();

  const columnsToDelete = [19, 18, 17, 16, 13, 12, 10, 9, 8, 6, 2, 1];
  columnsToDelete.forEach(col => {
    if (col <= lastColumn) { sheet.deleteColumn(col); lastColumn--; }
  });

  sheet.insertColumnBefore(1);
  sheet.getRange(1, 1).setValue('No.');
  lastColumn++;

  sheet.insertColumnsAfter(lastColumn, 3);
  sheet.getRange(1, lastColumn + 1).setValue('กระทำผิด');
  sheet.getRange(1, lastColumn + 2).setValue('เซ็น');
  sheet.getRange(1, lastColumn + 3).setValue('ประวัติ');
  lastColumn += 3;

  const numDataColumns = 11;

  const headerRange = sheet.getRange(1, 1, 1, lastColumn);
  headerRange.setFontWeight("bold").setFontFamily("Calibri").setFontSize(11).setHorizontalAlignment("center");
  headerRange.setBorder(true, true, true, true, true, true);

  lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    const numRows = lastRow - 1;
    const data = Array.from({ length: numRows }, (_, i) => [i + 1]);
    sheet.getRange(2, 1, numRows, 1).setValues(data);
  }

  sheet.getRange(1, 1, lastRow, lastColumn).setBorder(true, true, true, true, true, true);

  sheet.insertRowBefore(1);
  lastRow++;
  const dataRows = lastRow - 2;
  sheet.getRange(1, 1, 1, numDataColumns).merge();
  const mergedRange = sheet.getRange('A1');
  const currentDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "dd/MM/yyyy");
  mergedRange.setValue('วันที่: ' + currentDate)
    .setFontWeight("bold").setFontFamily("Calibri").setFontSize(11)
    .setHorizontalAlignment("center").setVerticalAlignment("middle")
    .setBorder(true, true, true, true, true, true);

  const day = new Date().getDay();
  const dayColors = {
    0: ["#ffcccc", "#ff6666"], 1: ["#ffffff", "#f0f0f0"], 2: ["#ffb3d9", "#ff66b2"],
    3: ["#b3e6b3", "#66cc66"], 4: ["#ffcc99", "#ff9900"], 5: ["#cce0ff", "#3399ff"],
    6: ["#e6ccff", "#9933cc"]
  };
  sheet.getRange(1, 1, 1, numDataColumns).setBackground(dayColors[day][0]);
  sheet.getRange(2, 1, 1, numDataColumns).setBackground(dayColors[day][1]);

  if (dataRows > 0) {
    sheet.getRange(3, 7, dataRows).setBackground("#fff9c4");
    sheet.getRange(3, 8, dataRows).setBackground("#d0f0c0");
    sheet.getRange(3, 6, dataRows).setNumberFormat('@');
  }

  const formulas = [
    { range: 'L3:L' + lastRow, formula: `=IFERROR(VLOOKUP(B3,IMPORTRANGE("${EXTERNAL_SS_ID}","การกระทำผิด!B:E"),4,FALSE), 0)` },
    { range: 'M3:M' + lastRow, formula: `=IFERROR(VLOOKUP(C3,IMPORTRANGE("${EXTERNAL_SS_ID}","การกระทำผิด!C:E"),3,FALSE), 0)` },
    { range: 'N3:N' + lastRow, formula: `=IFERROR(VLOOKUP(B3,IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติ_สส.!B:E"),4,FALSE), 0)` },
    { range: 'O3:O' + lastRow, formula: `=IFERROR(VLOOKUP(C3,IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติ_สส.!C:E"),3,FALSE), 0)` },
    { range: 'P3:P' + lastRow, formula: `=IFERROR(VLOOKUP(B3,IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติกระทำผิด!A:D"),4,FALSE), 0)` },
    { range: 'Q3:Q' + lastRow, formula: `=IFERROR(VLOOKUP(C3,IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติกระทำผิด!B:D"),3,FALSE), 0)` }
  ];
  formulas.forEach(item => {
    const cell = sheet.getRange(item.range);
    cell.setFormula(item.formula);
    cell.setHorizontalAlignment("right");
  });

  if (dataRows > 0) {
    const rule = SpreadsheetApp.newConditionalFormatRule()
      .whenTextContains('เสี่ยง').setBackground("#ffcccc").setFontColor("black")
      .setRanges([sheet.getRange(3, 11, dataRows, 1)]).build();
    sheet.setConditionalFormatRules([rule]);
  }

  if (lastRow > 2) {
    sheet.getRange(3, 1, lastRow - 2, lastColumn).sort({ column: 6, ascending: true });
  }

  const headerRows = sheet.getRange(1, 1, 2, numDataColumns).getValues();
  lastRow = sheet.getLastRow();
  const colFValues = sheet.getRange(3, 6, lastRow - 2, 1).getValues();
  let insertAfterRows = [];
  for (let i = 0; i < colFValues.length; i++) {
    const current = colFValues[i][0];
    const next = colFValues[i + 1] ? colFValues[i + 1][0] : null;
    const currentChar = typeof current === 'string' && current.trim() !== '' ? current.trim()[0].toUpperCase() : null;
    const nextChar = typeof next === 'string' && next.trim() !== '' ? next.trim()[0].toUpperCase() : null;
    if (currentChar && currentChar !== 'O' && currentChar !== nextChar) {
      insertAfterRows.push(i + 3);
    }
  }
  insertAfterRows.reverse().forEach(row => {
    sheet.insertRowsAfter(row, 2);
    sheet.getRange(row + 1, 1, 2, numDataColumns).setValues(headerRows);
    const d = new Date().getDay();
    sheet.getRange(row + 1, 1, 1, numDataColumns).merge()
      .setBackground(dayColors[d][0]).setBorder(true, true, true, true, true, true)
      .setHorizontalAlignment("center").setVerticalAlignment("middle");
    sheet.getRange(row + 2, 1, 1, numDataColumns)
      .setBackground(dayColors[d][1]).setBorder(true, true, true, true, true, true)
      .setHorizontalAlignment("center");
  });

  const seconds = Math.round((new Date() - start) / 1000);
  ss.toast("✅ เสร็จใน " + seconds + " วินาที", "สถานะ");
  return "✅ เสร็จใน " + seconds + " วินาที";
}

function lockKey(raw) {
  const s = String(raw || '').toUpperCase().trim();
  const m = s.match(/^([A-Z]+)\s*0*(\d+)/);
  if (!m) return null;
  return { letter: m[1], num: parseInt(m[2], 10) };
}
function cmpKey(a, b) {
  if (a.letter !== b.letter) return a.letter < b.letter ? -1 : 1;
  return a.num - b.num;
}

function findInsertionRow(sheet, logData) {
  const newKey = lockKey(logData);
  const lastRow = sheet.getLastRow();
  if (lastRow < 3) return 3;
  if (!newKey) return lastRow + 1;

  const n = lastRow - 2;
  const values = sheet.getRange(3, 1, n, 6).getValues();
  const isSep = (a) => { const s = String(a || ''); return s.indexOf('วันที่') > -1 || s.indexOf('No.') > -1; };

  let firstGreater = -1;
  for (let i = 0; i < n; i++) {
    if (isSep(values[i][0])) continue;
    const k = lockKey(values[i][5]);
    if (!k) continue;
    if (cmpKey(k, newKey) > 0) { firstGreater = 3 + i; break; }
  }

  if (firstGreater === -1) {
    for (let i = n - 1; i >= 0; i--) {
      if (isSep(values[i][0])) continue;
      if (lockKey(values[i][5])) return 3 + i + 1;
    }
    return lastRow + 1;
  }

  let prevLetter = null;
  for (let i = (firstGreater - 3) - 1; i >= 0; i--) {
    if (isSep(values[i][0])) continue;
    const k = lockKey(values[i][5]);
    if (k) { prevLetter = k.letter; break; }
  }

  if (prevLetter !== null && prevLetter === newKey.letter) {
    let insertRow = firstGreater;
    let i = (firstGreater - 3) - 1;
    while (i >= 0 && isSep(values[i][0])) { insertRow = 3 + i; i--; }
    return insertRow;
  }

  return firstGreater;
}

function saveWalkInEntry(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const insertionRow = findInsertionRow(sheet, data.logData);
  const electricityCost = parseFloat(data.electricityCost) || 0;
  const equipmentCost = parseFloat(data.equipmentCost) || 0;
  const fullLockData = String(data.logData);

  const entryValues = [[
    '', data.name, data.phone, data.shopName, data.productName,
    fullLockData, electricityCost, equipmentCost, '', '', ''
  ]];

  sheet.insertRowBefore(insertionRow);
  sheet.getRange(insertionRow, 1, 1, entryValues[0].length).setValues(entryValues);

  const color = data.color || '#f9e6a0';
  sheet.getRange(insertionRow, 1, 1, 11).setBackground(color).setBorder(true, true, true, true, true, true);
  sheet.getRange(insertionRow, 6).setNumberFormat('@');
  sheet.getRange(insertionRow, 7).setNumberFormat('0');
  sheet.getRange(insertionRow, 8).setNumberFormat('0');

  const r = insertionRow;
  const formulas = [
    { col: 12, formula: `=IFERROR(VLOOKUP(B${r},IMPORTRANGE("${EXTERNAL_SS_ID}","การกระทำผิด!B:E"),4,FALSE), 0)` },
    { col: 13, formula: `=IFERROR(VLOOKUP(C${r},IMPORTRANGE("${EXTERNAL_SS_ID}","การกระทำผิด!C:E"),3,FALSE), 0)` },
    { col: 14, formula: `=IFERROR(VLOOKUP(B${r},IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติ_สส.!B:E"),4,FALSE), 0)` },
    { col: 15, formula: `=IFERROR(VLOOKUP(C${r},IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติ_สส.!C:E"),3,FALSE), 0)` },
    { col: 16, formula: `=IFERROR(VLOOKUP(B${r},IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติกระทำผิด!A:D"),4,FALSE), 0)` },
    { col: 17, formula: `=IFERROR(VLOOKUP(C${r},IMPORTRANGE("${EXTERNAL_SS_ID}","ประวัติกระทำผิด!B:D"),3,FALSE), 0)` }
  ];
  formulas.forEach(item => {
    sheet.getRange(r, item.col).setFormula(item.formula).setHorizontalAlignment("right");
  });
  sheet.getRange(r, 12, 1, 6).setBorder(true, true, true, true, true, true);

  return `✅ บันทึก ${data.name} แถวที่ ${insertionRow}`;
}

function saveWalkInEntries(entriesData) {
  if (getUserEmail() !== AUTHORIZED_EMAIL) {
    throw new Error('ไม่มีสิทธิ์ใช้ออปชันนี้');
  }
  let success = 0;
  entriesData.forEach(function(data) {
    try { saveWalkInEntry(data); success++; } catch (e) {}
  });
  SpreadsheetApp.getActiveSpreadsheet().toast('บันทึก ' + success + '/' + entriesData.length + ' รายการ', 'เสร็จแล้ว');
  return '✅ บันทึก ' + success + '/' + entriesData.length + ' รายการ';
}

// ยูทิลิตี้ตรวจอีเมลที่ระบบมองเห็น (ใช้ debug ปัญหาสิทธิ์)
function เช็คอีเมลฉัน() {
  const email = getUserEmail();
  SpreadsheetApp.getUi().alert('ระบบเห็นอีเมล: [' + email + ']');
}
```

### 5.2 `WalkInForm.html` (ฟอร์มทีละคน — ผู้ใช้ทั่วไป)

```html
<head>
  <base target="_top">
  <style>
    body { font-family: Arial, sans-serif; padding: 10px; max-width: 350px; margin: 0 auto; }
    input[type="number"], input[type="text"], select, textarea {
      width: 100%; padding: 8px; margin: 5px 0 15px 0; display: inline-block;
      border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;
    }
    textarea { resize: none; }
    label { font-weight: bold; margin-bottom: 5px; display: block; }
    .btn { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; float: right; margin-left: 10px; margin-top: 20px; }
    .btn-close { background-color: #f44336; }
    .item-type-grid { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; }
    .item-type-label {
      flex: 1; text-align: center; padding: 10px 5px; border-radius: 6px; cursor: pointer;
      border: 2px solid #ccc; transition: all 0.2s; font-weight: 600; font-size: 14px; color: #444;
    }
    .item-type-label input { display: none; }
    input[id="walkIn"]:checked + .item-type-label { background-color: #b3e6ff; border-color: #3399ff; color: #000; }
    input[id="nonFood"]:checked + .item-type-label { background-color: #e6ccff; border-color: #9933cc; color: #000; }
    input[id="leave"]:checked + .item-type-label { background-color: #f9e6a0; border-color: #ff9900; color: #000; }
  </style>
</head>
<body>
  <h3>📝 บันทึกรายการด่วน / Quick Paste</h3>
  <form id="walkinForm">
    <label for="rawDataInput">ช่องวางข้อมูลดิบ (Quick Paste):</label>
    <textarea id="rawDataInput" name="rawDataInput" rows="3" placeholder="ตัวอย่าง: นายชวกร A058-60 40  0 แพนเค้กจิ๋ว"></textarea>
    <p style="font-size: 10px; color: gray; margin-top: -10px;">* ระบบจะพยายามแยกข้อมูลดิบออกเป็น ชื่อ, Lock ID, ค่าไฟ, ค่าอุปกรณ์ และ สินค้า</p>

    <div id="parsingFeedback" style="font-size: 12px; color: #333; margin-top: -10px; margin-bottom: 10px;"></div>

    <label for="lockIdInput">Lock ID (สำหรับกำหนดตำแหน่งแทรก):</label>
    <input type="text" id="lockIdInput" name="lockIdInput" value="" placeholder="เช่น A058-60" required>

    <label for="itemType">ประเภทรายการ (เลือกเพื่อกำหนดสี):</label>
    <div class="item-type-grid" id="itemType">
      <input type="radio" id="walkIn" name="itemType" value="Walk In" required>
      <label for="walkIn" class="item-type-label">Walk In</label>
      <input type="radio" id="nonFood" name="itemType" value="Nonfood" required>
      <label for="nonFood" class="item-type-label">Non Food</label>
      <input type="radio" id="leave" name="itemType" value="ลา" required>
      <label for="leave" class="item-type-label">ลา</label>
    </div>

    <label for="electricityCost">ค่าไฟ:</label>
    <input type="number" id="electricityCost" name="electricityCost" value="0" min="0" required>

    <label for="equipmentCost">ค่าอุปกรณ์:</label>
    <input type="number" id="equipmentCost" name="equipmentCost" value="0" min="0" required>

    <button type="button" class="btn btn-close" onclick="google.script.host.close()">ยกเลิก</button>
    <button type="submit" class="btn">บันทึก</button>
  </form>

  <script>
    function getColorByItemType(itemType) {
      switch(itemType) {
        case 'Walk In': return '#b3e6ff';
        case 'Nonfood': return '#e6ccff';
        case 'ลา': return '#f9e6a0';
        default: return '#f9e6a0';
      }
    }

    function parseRawData(rawData) {
      const result = { name: '', logData: '', productName: '', extractedElectricity: 0, extractedEquipment: 0 };
      const cleanData = rawData.trim().replace(/"/g, '').replace(/(\t|\s+)/g, ' ');
      const parts = cleanData.split(' ').filter(p => p.trim() !== '');
      const lockIdRegex = /^([A-Z]\d+[\w-]*)/i;
      let lockIdIndex = -1;
      for (let i = 0; i < parts.length; i++) {
          if (parts[i].match(lockIdRegex)) { lockIdIndex = i; break; }
      }

      if (lockIdIndex > -1 && parts.length >= 4) {
          const lockIdFull = parts[lockIdIndex].trim().toUpperCase();
          result.logData = lockIdFull;
          result.name = parts.slice(0, lockIdIndex).join(' ').trim() || 'N/A';
          let costStart = lockIdIndex + 1;
          if (parts.length > costStart && !isNaN(parseFloat(parts[costStart]))) {
              result.extractedElectricity = parseFloat(parts[costStart]) || 0;
              if (parts.length > costStart + 1 && !isNaN(parseFloat(parts[costStart + 1]))) {
                  result.extractedEquipment = parseFloat(parts[costStart + 1]) || 0;
                  result.productName = parts.slice(costStart + 2).join(' ').trim() || '';
              } else {
                  result.productName = parts.slice(costStart + 1).join(' ').trim() || '';
              }
          } else {
              result.productName = parts.slice(lockIdIndex + 1).join(' ').trim() || '';
          }
      } else if (parts.length >= 3 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1]))) {
          result.extractedElectricity = parseFloat(parts[0]) || 0;
          result.extractedEquipment = parseFloat(parts[1]) || 0;
          result.productName = parts.slice(2).join(' ').trim() || '';
          result.name = 'N/A';
          result.logData = '';
      } else {
          result.name = cleanData.substring(0, 50).trim() || 'N/A';
          result.productName = 'Raw Paste / Lock ID Not Found';
          result.logData = '';
      }
      return result;
    }

    document.getElementById('walkinForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(e.target);
      const itemType = formData.get('itemType');
      const electricityCost = formData.get('electricityCost');
      const equipmentCost = formData.get('equipmentCost');
      const rawDataInput = formData.get('rawDataInput').trim();
      const lockIdInput = formData.get('lockIdInput').trim();
      const color = getColorByItemType(itemType);

      let dataToSend = {
        shopName: itemType,
        electricityCost: electricityCost,
        equipmentCost: equipmentCost,
        color: color,
        name: itemType,
        productName: '',
        logData: lockIdInput,
        phone: '',
      };

      if (rawDataInput) {
        const parsedData = parseRawData(rawDataInput);
        dataToSend.name = (parsedData.name === 'N/A' && dataToSend.name === itemType) ? itemType : parsedData.name;
        dataToSend.productName = parsedData.productName;
        dataToSend.electricityCost = parsedData.extractedElectricity;
        dataToSend.equipmentCost = parsedData.extractedEquipment;
        if (!lockIdInput && parsedData.logData) {
            dataToSend.logData = parsedData.logData;
        }
      }

      document.getElementById('walkinForm').innerHTML = 'กำลังบันทึกข้อมูล...';

      google.script.run
        .withSuccessHandler(function(result) {
          google.script.host.close();
          setTimeout(function() { console.log(result); }, 500);
        })
        .withFailureHandler(function(error) {
          document.getElementById('walkinForm').innerHTML = `<p style="color: red;">❌ เกิดข้อผิดพลาด: ${error.message}</p><button onclick="google.script.host.close()">ปิด</button>`;
        })
        .saveWalkInEntry(dataToSend);
    });

    document.getElementById('rawDataInput').addEventListener('input', function() {
      const rawData = this.value.trim();
      const feedbackDiv = document.getElementById('parsingFeedback');
      const lockIdInput = document.getElementById('lockIdInput');
      feedbackDiv.innerHTML = '';

      if (rawData) {
        const parsedData = parseRawData(rawData);
        document.getElementById('electricityCost').value = parsedData.extractedElectricity;
        document.getElementById('equipmentCost').value = parsedData.extractedEquipment;
        if (parsedData.logData) {
            lockIdInput.value = parsedData.logData;
        } else if (parsedData.logData === '') {
             lockIdInput.value = '';
        }
        if (parsedData.name !== 'N/A' || parsedData.logData) {
             feedbackDiv.innerHTML = `
                <p style="margin: 0; color: #1e88e5;">✔ แยกข้อมูลสำเร็จ:</p>
                <ul style="list-style: none; padding-left: 10px; margin: 5px 0 0 0;">
                    <li>ชื่อ: <strong>${parsedData.name}</strong></li>
                    <li>สินค้า: <strong>${parsedData.productName || '-'}</strong></li>
                </ul>`;
        } else {
             feedbackDiv.innerHTML = `<p style="margin: 0; color: #ff9900;">⚠ ไม่สามารถแยก Lock ID ได้</p>`;
        }
      } else {
          document.getElementById('electricityCost').value = 0;
          document.getElementById('equipmentCost').value = 0;
          lockIdInput.value = '';
          feedbackDiv.innerHTML = '';
      }
    });
  </script>
</body>
```

### 5.3 `WalkInBulk.html` (ฟอร์มวางหลายคน — เฉพาะเจ้าของ)

```html
<head>
  <base target="_top">
  <style>
    body { font-family: Arial, sans-serif; padding: 10px; max-width: 400px; margin: 0 auto; }
    textarea { width: 100%; padding: 8px; margin: 5px 0 8px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-family: monospace; font-size: 13px; resize: vertical; }
    label { font-weight: bold; display: block; margin-bottom: 5px; }
    .btn { background:#4CAF50; color:#fff; padding:10px 15px; border:none; border-radius:4px; cursor:pointer; float:right; margin-left:10px; margin-top:10px; }
    .btn-close { background:#f44336; }
    .hint { font-size:11px; color:gray; margin-top:-4px; }
    .grid { display:flex; gap:8px; margin:8px 0 16px 0; }
    .lbl { flex:1; text-align:center; padding:10px 5px; border-radius:6px; cursor:pointer; border:2px solid #ccc; font-weight:600; font-size:14px; color:#444; }
    .lbl input { display:none; }
    input[id="w"]:checked + .lbl { background:#b3e6ff; border-color:#3399ff; color:#000; }
    input[id="n"]:checked + .lbl { background:#e6ccff; border-color:#9933cc; color:#000; }
    input[id="l"]:checked + .lbl { background:#f9e6a0; border-color:#ff9900; color:#000; }
    #preview { font-size:12px; margin:4px 0 12px 0; max-height:220px; overflow-y:auto; }
    #preview table { width:100%; border-collapse:collapse; }
    #preview td { padding:2px 4px; border-bottom:1px solid #eee; }
    .ok{color:#1e88e5;} .warn{color:#e53935;} .count{font-weight:bold;margin-bottom:4px;}
  </style>
</head>
<body>
  <h3>⚡ วางหลายคนพร้อมกัน</h3>
  <label for="raw">วางข้อมูล (1 คนต่อ 1 บรรทัด):</label>
  <textarea id="raw" rows="10" placeholder="นางสาว สุจิตรา ปานกลาง C023,24 50 0 ขนมปังปิ้ง&#10;นาย กฤตนัย นามวงศ์ C025,26 60 0 ไก่ย่าง"></textarea>
  <p class="hint">* แต่ละบรรทัด: ชื่อ  LockID  ค่าไฟ  ค่าอุปกรณ์  สินค้า</p>
  <div id="preview"></div>
  <label>ประเภท (สีของทั้งชุด):</label>
  <div class="grid">
    <input type="radio" id="w" name="t" value="Walk In" checked><label for="w" class="lbl">Walk In</label>
    <input type="radio" id="n" name="t" value="Nonfood"><label for="n" class="lbl">Non Food</label>
    <input type="radio" id="l" name="t" value="ลา"><label for="l" class="lbl">ลา</label>
  </div>
  <button type="button" class="btn btn-close" onclick="google.script.host.close()">ยกเลิก</button>
  <button type="button" class="btn" id="save">บันทึกทั้งหมด</button>

  <script>
    function colorOf(t){return t==='Walk In'?'#b3e6ff':t==='Nonfood'?'#e6ccff':'#f9e6a0';}
    function parse(raw){
      const r={name:'',logData:'',productName:'',e:0,q:0};
      const parts=raw.trim().replace(/"/g,'').replace(/(\t|\s+)/g,' ').split(' ').filter(p=>p!=='');
      const rx=/^([A-Z]\d+[\w,-]*)/i; let idx=-1;
      for(let i=0;i<parts.length;i++){if(parts[i].match(rx)){idx=i;break;}}
      if(idx>-1&&parts.length>=4){
        r.logData=parts[idx].toUpperCase(); r.name=parts.slice(0,idx).join(' ')||'N/A';
        let c=idx+1;
        if(parts.length>c&&!isNaN(parseFloat(parts[c]))){
          r.e=parseFloat(parts[c])||0;
          if(parts.length>c+1&&!isNaN(parseFloat(parts[c+1]))){r.q=parseFloat(parts[c+1])||0;r.productName=parts.slice(c+2).join(' ');}
          else r.productName=parts.slice(c+1).join(' ');
        } else r.productName=parts.slice(idx+1).join(' ');
      } else {r.name=raw.trim().substring(0,50)||'N/A';r.productName='แยก LockID ไม่ได้';r.logData='';}
      return r;
    }
    function lines(){return document.getElementById('raw').value.split('\n').map(l=>l.trim()).filter(l=>l!=='');}
    function render(){
      const L=lines(),box=document.getElementById('preview'); if(!L.length){box.innerHTML='';return;}
      let rows='',ok=0;
      L.forEach(line=>{const p=parse(line);
        if(p.logData){ok++;rows+=`<tr><td class="ok">✓</td><td>${p.name}</td><td>${p.logData}</td><td>${p.e}/${p.q}</td><td>${p.productName||'-'}</td></tr>`;}
        else rows+=`<tr><td class="warn">⚠</td><td colspan="4" class="warn">${line}</td></tr>`;});
      box.innerHTML=`<div class="count">พบ ${L.length} บรรทัด (แยกได้ ${ok})</div><table>${rows}</table>`;
    }
    document.getElementById('raw').addEventListener('input',render);
    document.getElementById('save').addEventListener('click',function(){
      const L=lines(); if(!L.length){alert('กรุณาวางข้อมูล');return;}
      const t=document.querySelector('input[name="t"]:checked').value, color=colorOf(t);
      const entries=L.map(line=>{const p=parse(line);return {shopName:t,name:(p.name&&p.name!=='N/A')?p.name:t,productName:p.productName,logData:p.logData,electricityCost:p.e,equipmentCost:p.q,color:color,phone:''};});
      const b=this; b.disabled=true; b.textContent='กำลังบันทึก...';
      google.script.run.withSuccessHandler(()=>google.script.host.close())
        .withFailureHandler(e=>{b.disabled=false;b.textContent='บันทึกทั้งหมด';alert('❌ '+e.message);})
        .saveWalkInEntries(entries);
    });
  </script>
</body>
```

---

## 6. บทสรุปสำหรับเรซูเม่ / รายงาน (Résumé Bullet)

> ออกแบบและพัฒนาระบบจัดการข้อมูลผู้ค้าตลาดนัดด้วย Google Apps Script ที่ทำงานอัตโนมัติแบบครบวงจร ตั้งแต่จัดรูปแบบเอกสารรายวัน (ลบคอลัมน์ ใส่กรอบ ระบายสีตามวัน เรียงลำดับ) ดึงประวัติผู้ค้าข้ามไฟล์ด้วย IMPORTRANGE/VLOOKUP ไปจนถึงฟอร์มบันทึกผู้ค้า Walk-in ที่แยกข้อมูลดิบอัตโนมัติและแทรกเข้าตำแหน่งตามรหัสล็อกด้วยอัลกอริทึมเรียงลำดับเชิงตัวเลข พร้อมระบบควบคุมสิทธิ์การใช้งานตามผู้ใช้ — ลดเวลาจัดเอกสารรายวันจากหลายสิบนาทีเหลือไม่กี่วินาที

---

## 7. ประวัติการแก้ไข (Fix Log)

### v1.1 (ก.ค. 2569) — 🔒 แก้ "สิทธิ์หลุด" + ซ่อนเมนูเฉพาะเจ้าของ
| Fix | ปัญหา | แก้อะไร |
|---|---|---|
| PERM-01 🐛 | `Session.getActiveUser().getEmail()` คืนค่าว่างสำหรับบัญชี @gmail.com ทั่วไป → เทียบอีเมลไม่ผ่าน "สิทธิ์หลุด" ทั้งที่เป็นเจ้าของ | เพิ่มฟังก์ชัน `getUserEmail()` fallback ไป `getEffectiveUser().getEmail()` เมื่อ `getActiveUser` ว่าง แล้วใช้แทนทุกจุดที่เช็คสิทธิ์ (`showWalkInBulkForm`, `saveWalkInEntries`) |
| PERM-02 🔒 | เมนู "วางหลายคน" โชว์กับทุกคนแล้วค่อยบล็อกตอนกด | `onOpen` เช็คอีเมลก่อน — เพิ่มรายการเมนูนี้เฉพาะเมื่อเป็นเจ้าของ คนอื่น (หรืออ่านอีเมลไม่ได้ = ค่าว่าง) จะไม่เห็นเลย (fail-safe) |
