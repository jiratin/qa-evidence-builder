HELP_SECTIONS = [
    (
        "1. ภาพรวมและ Flow ปัจจุบัน",
        """
QA Evidence Builder v1.0 เป็นเครื่องมือ Local-only สำหรับ QA / Tester / Developer
เพื่ออ่าน Log จำนวนมาก คัดเฉพาะรายการที่เกี่ยวข้องกับ Defect และสร้าง Evidence
สำหรับ Ticket โดยไม่ต้อง Copy Request/Response ทีละรายการ

Flow หลักของเวอร์ชันปัจจุบัน:

Import / Paste
→ Filter
→ Include Logs
→ Review Transaction / Analysis
→ กรอก Expected / Actual
→ ตรวจ Mask และ Preview
→ Copy หรือ Export Evidence

ข้อมูลที่ Import เข้ามาจะใช้เพื่อวิเคราะห์ภายในโปรแกรมเท่านั้น โปรแกรมไม่ได้แก้ไข
ไฟล์ต้นฉบับ และจาก source ปัจจุบันไม่มีขั้นตอน Upload Log ไป Server ภายนอก

หน้าหลักแบ่งเป็น:
• Sidebar ซ้าย — Source, Filters, Export Selection, Evidence Options,
  Package Contents และ Actions
• Timeline — รายการ API ตามลำดับเวลา
• Transactions — รวม API ตาม Transaction ID
• Evidence — Expected / Actual และ Evidence Preview
• Analysis — Auto Summary และ Duplicate Error Fingerprint
""",
    ),
    (
        "2. Quick Start — ใช้งานครั้งแรก",
        """
วิธีใช้งานที่สั้นที่สุด:

1) เปิด QA Evidence Builder
2) กด Import JSON / HAR หรือ Paste JSON
3) ดูรายการที่ Tab Timeline
4) ใช้ Filters ด้านซ้ายเพื่อหา Log ที่เกี่ยวข้อง
5) เลือก Row ที่ต้องการ
6) กด Include Selected
7) ตรวจว่า Column Export เปลี่ยนเป็น ☑
8) ถ้าต้องการ ให้ดู Transactions และ Analysis เพิ่มเติม
9) ไป Tab Evidence
10) กรอก Expected Result และ Actual Result
11) เปิด Mask sensitive data ไว้
12) ตรวจ Included Evidence Preview
13) เลือก Copy Included for Ticket, Copy Included as Markdown
    หรือ Export Included Evidence

จำง่าย ๆ:
Import → Filter → Include → Review → Copy / Export
""",
    ),
    (
        "3. Source — Import JSON / HAR",
        """
กด Import JSON / HAR เพื่อเลือกไฟล์จากเครื่อง

File dialog รองรับ:
• *.json
• *.har
• All files

JSON ที่เหมาะกับโปรแกรมเป็น JSON Array จากระบบ Log เช่น Kibana /
Elasticsearch โดยแต่ละรายการอาจมี fields เช่น TIMESTAMP, REQUEST_URI,
REQUEST_METHOD, RESPONSE_STATUS, RESPONSE_TIME, REQUEST_ID,
CLIENT_PAGE_NAME, kafka_topic_name, REQUEST_BODY และ RESPONSE_BODY

ตัวอย่างแบบย่อ:

[
  {
    "fields": {
      "TIMESTAMP": ["2026-08-21 11:03:36.230"],
      "REQUEST_URI": ["/api/v1/payment"],
      "REQUEST_METHOD": ["POST"],
      "RESPONSE_STATUS": [500],
      "RESPONSE_TIME": [3211],
      "REQUEST_ID": ["REQ-1002"]
    }
  }
]

HAR ใช้ข้อมูล Network เช่น URL, Method, Status, Timing, Headers,
Request Body และ Response Body ตามข้อมูลที่มีอยู่ในไฟล์

เมื่อ Import สำเร็จ:
• Timeline จะถูกเติมข้อมูล
• Filter/Analysis จะคำนวณใหม่
• Status ด้านบนจะแสดงจำนวน Log

ถ้า Parse ไม่สำเร็จ โปรแกรมจะแสดง Import failed
""",
    ),
    (
        "4. Source — Paste JSON",
        """
ใช้เมื่อ Copy JSON มาแล้วและไม่ต้องการสร้างไฟล์ก่อน

1) กด Paste JSON
2) หน้าต่าง Paste JSON Array / HAR JSON จะเปิด
3) วาง JSON
4) กด Load Logs
5) ถ้า Parse สำเร็จ ข้อมูลจะเข้าสู่ Timeline

สามารถวาง JSON Array หรือ HAR JSON ที่ parser รองรับได้

สำหรับ Log หลายรายการ แนะนำให้ Copy เป็น Array ที่มี [ ... ] ครอบรายการทั้งหมด
เพื่อให้โครงสร้างชัดเจนและลดความผิดพลาดจาก JSON ไม่สมบูรณ์
""",
    ),
    (
        "5. Source — Clear",
        """
Clear ใช้เริ่มงานใหม่โดยล้าง state ของงานปัจจุบัน

สิ่งที่ถูกล้าง:
• Imported Logs
• Included Logs
• Expected Result
• Actual Result
• Filters

ไฟล์ JSON/HAR ต้นฉบับบนเครื่องไม่ถูกลบหรือแก้ไข
""",
    ),
    (
        "6. Timeline — อ่านรายการ API",
        """
Timeline คือหน้าหลักสำหรับตรวจ Log

Column ปัจจุบัน:
• Export — ☐ ยังไม่ Include / ☑ Include แล้ว
• Timestamp — เวลาของ Log
• Flag — Severity ที่ parser/analyzer กำหนด
• Fingerprint — Error Fingerprint ถ้ามี
• Method — GET / POST / PUT / PATCH / DELETE
• API — Request URI
• Status — HTTP Status
• ms — Response Time
• Request ID — Request identifier
• Transaction — Transaction ID ที่ตรวจพบ

Timeline รองรับ Multi-select และมี Scrollbar แนวตั้ง/แนวนอน

Double-click Row:
สลับสถานะ Include / Exclude ของ Log นั้นทันที
""",
    ),
    (
        "7. Filters — วิธีกรอง Log",
        """
Filters ด้านซ้ายทำงานร่วมกันได้ และ Timeline จะ Refresh เมื่อค่าเปลี่ยน

มี Filter:
• Search API / ID
• Minimum response ms
• Page
• Kafka Topic
• Transaction ID
• HTTP Method
• HTTP Status
• Errors only
• Slow only

Search API / ID ใช้ค้นจากข้อมูลที่ filtering layer รองรับ เช่น API/ID
และข้อมูลสำคัญที่เกี่ยวข้องกับ Log

Minimum response ms:
ใส่ 1000 เพื่อดูรายการที่ Response Time >= 1000 ms

HTTP Method:
ALL, GET, POST, PUT, PATCH, DELETE

HTTP Status:
ALL, 2xx, 3xx, 4xx, 5xx, Other

Errors only:
ใช้ดู Error ตาม rule ของโปรแกรม

Slow only:
ใช้ดู Slow API ตาม rule ของโปรแกรม

Reset Filters:
คืน Filter ทุกตัวกลับค่าเริ่มต้น โดยไม่ลบ Imported Logs หรือ Included Logs
""",
    ),
    (
        "8. ตัวอย่าง Filter หลายเงื่อนไข",
        """
ตัวอย่างหา Payment API ที่มีปัญหา:

Search API / ID = payment
HTTP Method = POST
HTTP Status = 5xx

ตัวอย่างหา API ช้าในหน้า Checkout:

Page = Checkout
Minimum response ms = 2000

ตัวอย่างดู Journey เดียว:

Transaction ID = TX-CHECKOUT-001

Filter สามารถใช้พร้อมกันได้ ดังนั้นถ้าเงื่อนไขเข้มเกินไปจน Timeline ว่าง
ให้กด Reset Filters แล้วค่อยเพิ่มเงื่อนไขทีละตัว
""",
    ),
    (
        "9. Export Selection — Include / Exclude",
        """
โปรแกรมไม่ Export ทุก Log ที่ Import มาโดยอัตโนมัติ
เฉพาะ Log ที่อยู่ใน Included set เท่านั้นที่จะถูก Copy/Export

Include Selected:
1) เลือก Row ใน Timeline
2) เลือกหลาย Row ได้ด้วย Shift และปุ่ม modifier ของระบบ
3) กด Include Selected
4) Column Export จะเป็น ☑

Exclude Selected:
เอา Row ที่เลือกออกจาก Included set

Double-click Row:
สลับ Include / Exclude ได้โดยตรง

Included: N:
บอกจำนวน Log ทั้งหมดที่ Include อยู่ ไม่ใช่จำนวน Row ที่กำลังแสดงหลัง Filter
""",
    ),
    (
        "10. Select All / Deselect All",
        """
Select All ใน UI ปัจจุบันหมายถึง:
Include ทุก Log ที่ผ่าน Filter ปัจจุบัน

ตัวอย่าง:
Import 1,000 Logs
→ Filter HTTP Status = 5xx
→ เหลือ 12 Logs
→ กด Select All
ผลคือ Include 12 Logs ที่กำลังผ่าน Filter

Deselect All:
ล้าง Included set ทั้งหมด ไม่ว่าจะกำลัง Filter อะไรอยู่

Deselect All ไม่ได้ลบ Imported Logs
""",
    ),
    (
        "11. Transactions Tab",
        """
Transactions รวม Log ตาม Transaction ID ของรายการที่ผ่าน Filter ปัจจุบัน

Column:
• Transaction ID
• APIs
• Errors
• Slow

Double-click Transaction:
โปรแกรมนำ Transaction ID ไปใส่ช่อง Transaction ID Filter
เพื่อให้ Timeline แสดงเฉพาะ Journey นั้น

ถ้าเป็นกลุ่ม (no transaction) โปรแกรมจะล้าง Transaction ID Filter

ตัวอย่าง Journey:
POST /cart/validate
→ POST /promotion/check
→ POST /payment
→ POST /order/create
→ GET /order/status
""",
    ),
    (
        "12. Evidence — Expected / Actual",
        """
Tab Evidence มีช่อง Expected Result และ Actual Result

Expected Result:
ผลที่ควรเกิดขึ้นตาม requirement

ตัวอย่าง:
Payment should complete successfully and the order should be CONFIRMED.

Actual Result:
สิ่งที่เกิดขึ้นจริง

ตัวอย่าง:
POST /api/v1/payment returned HTTP 500 and the order was not created.

สองช่องนี้ไม่บังคับ แต่เมื่อกรอกแล้วจะถูกนำไปใส่ Evidence Preview,
Copy for Ticket, Markdown และ summary ที่ Export
""",
    ),
    (
        "13. Included Evidence Preview",
        """
Preview สร้างจาก Included Logs เท่านั้น ไม่ได้สร้างจากทุก Row ใน Timeline

ตัวอย่าง:
Import 500 Logs
Filter เหลือ 20
Include 4
→ Preview ใช้ 4 Logs

Preview ปัจจุบันประกอบด้วยข้อมูล เช่น:
• Selected log count
• Error / Slow count
• Transaction count
• Auto Summary
• Expected / Actual
• Timeline
• API details
• Request ID / Transaction ID
• Error Fingerprint
• Page / Kafka Topic
• Query / Request / Response

ควรตรวจ Preview ก่อน Copy หรือ Export ทุกครั้ง
""",
    ),
    (
        "14. Evidence Options — Mask sensitive data",
        """
Mask sensitive data เปิดเป็นค่าเริ่มต้น

เมื่อเปิด โปรแกรมจะส่งข้อมูลผ่าน sanitizer ก่อนนำไปสร้าง Evidence
และก่อนสร้าง Sanitized log files

ข้อมูลที่ควรระวัง เช่น:
• Authorization / Bearer Token / JWT
• Cookie
• Password / PIN
• Access / Refresh Token
• Session
• Email / Phone
• Device identifiers
• Field ภายในองค์กรที่ถือเป็นข้อมูลสำคัญ

แม้เปิด Mask แล้ว ควรตรวจ Preview ก่อนส่ง Ticket โดยเฉพาะ Log Production
หรือ Log ที่มีข้อมูลลูกค้า
""",
    ),
    (
        "15. Evidence Options — Extra mask keys",
        """
Extra mask keys ใช้เพิ่มชื่อ Field ที่องค์กรต้องการ Mask เอง
โดยไม่ต้องแก้ source code

กรอกแบบ comma separated:

employeeId,citizenId,accountNumber

โปรแกรมจะแยกด้วย comma และนำชื่อ Field ที่ไม่ว่างไปเพิ่มใน sanitizer

เหมาะกับ Field เฉพาะระบบภายในที่ default sanitizer อาจไม่รู้จัก
""",
    ),
    (
        "16. Package Contents",
        """
ก่อน Export สามารถเลือกเนื้อหาใน Package ได้ 4 แบบ:

summary.txt
• เปิดเป็นค่าเริ่มต้น
• Evidence แบบ plain text

summary.md
• เปิดเป็นค่าเริ่มต้น
• Evidence ที่ห่อใน Markdown code block

Raw log files
• ปิดเป็นค่าเริ่มต้น
• เขียน e.raw โดยตรง
• ไม่มีการ Mask
• เปิดเฉพาะเมื่อมีเหตุผลและได้รับอนุญาตให้แชร์ข้อมูลต้นฉบับ

Sanitized log files
• เปิดเป็นค่าเริ่มต้น
• Log JSON ที่ผ่าน sanitizer

ต้องเลือกอย่างน้อย 1 ประเภท มิฉะนั้น Export จะถูกปฏิเสธ
""",
    ),
    (
        "17. Actions — Copy Included for Ticket",
        """
Copy Included for Ticket สร้าง plain-text Evidence จาก Included Logs
แล้ว Copy เข้า Clipboard

Flow:
1) Include Logs
2) กรอก Expected / Actual ถ้าต้องการ
3) ตรวจ Mask
4) ตรวจ Preview
5) กด Copy Included for Ticket
6) Paste ลง Ticket / Email / Chat ที่ได้รับอนุญาต

ถ้าไม่มี Included Log โปรแกรมจะแจ้ง Nothing included
""",
    ),
    (
        "18. Actions — Copy Included as Markdown",
        """
สร้าง Evidence ชุดเดียวกันในรูปแบบ Markdown code block แล้ว Copy เข้า Clipboard

เหมาะกับปลายทางที่รองรับ Markdown เช่น GitHub/GitLab/Wiki
หรือ Ticket system บางระบบ

ถ้าปลายทางไม่ render Markdown ให้ใช้ Copy Included for Ticket
""",
    ),
    (
        "19. Actions — Export Included Evidence",
        """
Export Included Evidence ใช้ Included Logs เท่านั้น

ขั้นตอน:
1) Include Logs
2) ตั้ง Expected / Actual
3) ตั้ง Mask / Extra mask keys
4) เลือก Package Contents
5) กด Export Included Evidence
6) เลือก Parent Folder
7) โปรแกรมสร้าง Folder ชื่อประมาณ:
   QA_Evidence_20260824_120000
8) โปรแกรมสร้าง ZIP ชื่อเดียวกัน:
   QA_Evidence_20260824_120000.zip

ภายใน Folder/ZIP จะมีเฉพาะประเภทที่เลือก

ตัวอย่าง:
QA_Evidence_20260824_120000/
├── summary.txt
├── summary.md
└── sanitized/
    ├── 001_payment.json
    └── 002_order_status.json

ถ้าเปิด Raw log files จะมี raw/ เพิ่มด้วย
""",
    ),
    (
        "20. ชื่อไฟล์ Log ภายใน Evidence Package",
        """
ไฟล์ JSON ภายใน raw/ และ sanitized/ ใช้รูปแบบ:

ลำดับ 3 หลัก + ชื่อส่วนท้ายของ API

ตัวอย่าง:
/api/v1/payment
→ 001_payment.json

/api/v1/order/status
→ 002_status.json

ลำดับนี้อิงลำดับของ Included Entries ที่ถูกส่งเข้า Export Package

หมายเหตุ:
Flow Evidence Package ปัจจุบันไม่ได้ใช้ชื่อ timestamp_api แบบ ExportLogsToFiles
รุ่นเก่า ดังนั้นควรอิงชื่อไฟล์ตามรูปแบบ 001_api.json ของ source ปัจจุบัน
""",
    ),
    (
        "21. Analysis — Auto Defect Analysis",
        """
Tab Analysis วิเคราะห์รายการที่ผ่าน Filter ปัจจุบัน ไม่ใช่เฉพาะ Included Logs

จะแสดง:
• Auto Summary
• Duplicate / Similar Error Signatures
• Error Fingerprint ที่เกิดซ้ำ
• Timestamp / Method / API / HTTP Status ของรายการในกลุ่มซ้ำ

จุดสำคัญ:
Analysis เป็น Rule-based จากข้อมูลในโปรแกรม
ไม่ได้ส่ง Log ไป AI หรือ Internet

ใช้เป็นตัวช่วยหา pattern แต่ควรให้ QA/Developer ตรวจบริบทจริงก่อนสรุป Root Cause
""",
    ),
    (
        "22. Error Fingerprint / Duplicate Errors",
        """
Error Fingerprint ใช้สร้าง Signature ของ Error เพื่อช่วยจัดกลุ่ม Error ที่คล้ายกัน

ถ้า Analysis พบ Fingerprint เดิมหลายครั้ง จะแสดงประมาณ:

ERR-A14F93C2: 3 occurrence(s)
  - 11:03:36 POST /payment HTTP 500
  - 11:04:02 POST /payment HTTP 500
  - 11:06:14 POST /payment HTTP 500

ประโยชน์:
• มองเห็น Error ที่เกิดซ้ำในชุด Log
• ลดเวลานั่งเทียบ Error ทีละรายการ
• ช่วยเลือก Evidence ที่เป็นตัวแทนของปัญหา

ไม่ได้หมายความว่า Fingerprint เดียวกันยืนยันว่าเป็น Jira Defect เดียวกันเสมอ
""",
    ),
    (
        "23. Flow ตัวอย่าง — Payment Defect",
        """
สถานการณ์:
Tester กด Payment แล้วเกิด Error

1) Import JSON / HAR
2) Search API / ID = payment
3) HTTP Status = 5xx
4) ตรวจ Timeline
5) Include POST /api/v1/payment ที่ผิดปกติ
6) เปิด Transactions เพื่อหา Transaction เดียวกัน
7) Double-click Transaction
8) Include API ก่อน/หลัง Payment ที่จำเป็นต่อการอธิบาย Journey
9) เปิด Analysis ดูว่ามี Error Signature ซ้ำหรือไม่
10) ไป Evidence
11) Expected: Payment should succeed and order should be confirmed.
12) Actual: Payment returned HTTP 500 and order was not created.
13) เปิด Mask sensitive data
14) ตรวจ Preview
15) Copy Included for Ticket
16) ถ้าต้องแนบไฟล์ ให้ Export Included Evidence
""",
    ),
    (
        "24. Flow ตัวอย่าง — Performance Issue",
        """
สถานการณ์:
หน้า Checkout ช้า

1) Import Log
2) Page = Checkout
3) Minimum response ms = 2000
   หรือเปิด Slow only
4) ตรวจ Timeline
5) Include API ที่ช้าและ API ที่ช่วยอธิบาย Journey
6) ดู Transactions เพื่อเข้าใจลำดับการเรียก
7) ไป Evidence
8) กรอก Actual Result เช่น:
   Checkout waits several seconds before completion.
9) ตรวจ Preview
10) Copy หรือ Export Evidence

ถ้าต้องการวิเคราะห์ทุก Slow Log ในชุดข้อมูล ให้ใช้ Analysis ร่วมด้วย
""",
    ),
    (
        "25. Flow ตัวอย่าง — Transaction Journey",
        """
สถานการณ์:
ต้องการแนบ API ทั้ง Journey ของ Checkout

1) Import Log
2) เปิด Transactions
3) หา Transaction ที่ต้องการ
4) Double-click Transaction
5) Timeline จะถูกกรองด้วย Transaction ID
6) ตรวจว่ารายการที่เหลือถูกต้อง
7) กด Select All
8) ไป Evidence
9) ตรวจ Timeline ใน Preview
10) Copy / Export

Select All ณ จุดนี้จะ Include เฉพาะรายการที่ผ่าน Transaction Filter
""",
    ),
    (
        "26. Help / User Guide และ About",
        """
เปิดคู่มือได้ 2 ทาง:

• ปุ่ม Help / User Guide ด้านล่างสุดของ Sidebar
• Menu bar → Help → User Guide

หน้าคู่มือมี:
• รายการหัวข้อด้านซ้าย
• เนื้อหาด้านขวา
• Search ด้านบน

Search สามารถใช้คำ เช่น:
Export, Mask, Transaction, Error, HAR, Raw

Menu bar → Help → About
จะแสดงชื่อโปรแกรมและ Version 1.0.0
""",
    ),
    (
        "27. ปัญหาที่พบบ่อย",
        """
Import failed
• ตรวจ JSON/HAR ว่าสมบูรณ์
• ลองเปิดไฟล์ด้วย text editor เพื่อตรวจ syntax
• ถ้า Copy JSON มา ให้ลอง Paste JSON

Timeline ว่างหลัง Import
• กด Reset Filters
• ตรวจ Status/Method/Minimum response ms

Nothing included
• เลือก Row แล้วกด Include Selected
• หรือใช้ Select All หลังตั้ง Filter

Export ไม่มี Log ที่ต้องการ
• ตรวจ Column Export ว่าเป็น ☑
• Preview ควรมีรายการเดียวกับที่จะ Export

Export failed เพราะไม่ได้เลือก Package Contents
• เปิดอย่างน้อย summary.txt, summary.md, Raw หรือ Sanitized

Sensitive data ยังปรากฏ
• เปิด Mask sensitive data
• เพิ่มชื่อ Field ใน Extra mask keys
• ตรวจ Preview ก่อนส่ง

หน้าต่างเล็ก
• Sidebar เลื่อนแนวตั้งได้
• Timeline มี Scrollbar
• เนื้อหาหลักแยกเป็น Tabs
""",
    ),
    (
        "28. macOS / Windows — การเปิดโปรแกรม",
        """
ถ้าใช้ Source Code:
ต้องมี Python environment และ Tkinter ที่ทำงานได้

ถ้า macOS แจ้ง:
ModuleNotFoundError: No module named '_tkinter'
ให้ตรวจ Python/Tk installation ที่ใช้อยู่ก่อน

ถ้าใช้ไฟล์ .app หรือ .exe จาก Release:
ไม่จำเป็นต้องเปิดผ่าน VS Code

macOS อาจแสดง Gatekeeper warning ถ้า build ยังไม่ได้ Developer ID sign/notarize
Windows อาจแสดง SmartScreen/Unknown Publisher ถ้า build ยังไม่ได้ code-sign
ด้วย certificate ที่ระบบเชื่อถือ

Security warning ของระบบปฏิบัติการเป็นคนละส่วนกับ Log masking ภายในโปรแกรม
""",
    ),
    (
        "29. Security / Privacy ก่อนส่ง Evidence",
        """
Log สามารถมีข้อมูลสำคัญมากกว่าที่เห็นบนหน้าจอ เช่น Header หรือ Raw Payload

แนวทางใช้งาน:
• เปิด Mask sensitive data เป็นค่าเริ่มต้น
• ใช้ Sanitized log files เป็นหลัก
• Raw log files เปิดเฉพาะเมื่อจำเป็น
• เพิ่ม Extra mask keys สำหรับ Field ภายในองค์กร
• ตรวจ Included Evidence Preview
• ถ้าเปิด Raw ให้ตรวจไฟล์ raw/ ก่อนแนบ Ticket
• ปฏิบัติตาม Security / Data Classification Policy ขององค์กร

โปรแกรมปัจจุบันประมวลผล Log แบบ Local-only ตาม source ที่ตรวจ
แต่ผู้ใช้ยังต้องรับผิดชอบว่าปลายทางที่นำ Evidence ไปวางได้รับอนุญาตให้เห็นข้อมูลนั้น
""",
    ),
    (
        "30. Checklist ก่อนสร้าง Ticket",
        """
ก่อน Copy / Export แนะนำตรวจตามนี้:

□ Import ชุด Log ถูกไฟล์
□ Reset/ตั้ง Filter ถูกต้อง
□ Include เฉพาะ Log ที่จำเป็น
□ ตรวจ Transaction/Journey
□ ตรวจ Analysis ถ้าต้องการหา Error ซ้ำ
□ Expected Result ถูกต้อง
□ Actual Result ถูกต้อง
□ Mask sensitive data เปิดอยู่
□ Extra mask keys ครบ
□ Preview ไม่มีข้อมูลที่ไม่ควรส่ง
□ Raw log files ปิดอยู่ถ้าไม่จำเป็น
□ Package Contents ถูกต้อง
□ Copy/Export แล้วตรวจผลลัพธ์อีกครั้ง
""",
    ),
    (
        "31. Quick Reference — ปุ่มสำคัญ",
        """
Import JSON / HAR
→ โหลดไฟล์ Log

Paste JSON
→ วาง JSON โดยตรง

Clear
→ ล้างงานปัจจุบัน

Reset Filters
→ ล้าง Filter แต่เก็บ Log/Included

Include Selected
→ Include Row ที่เลือก

Exclude Selected
→ เอา Row ที่เลือกออกจาก Included

Select All
→ Include ทุก Row ที่ผ่าน Filter

Deselect All
→ ล้าง Included ทั้งหมด

Copy Included for Ticket
→ Copy Evidence แบบ Text

Copy Included as Markdown
→ Copy Evidence แบบ Markdown

Export Included Evidence
→ สร้าง Folder + ZIP ตาม Package Contents

Help / User Guide
→ เปิดคู่มือฉบับนี้
""",
    ),
]
