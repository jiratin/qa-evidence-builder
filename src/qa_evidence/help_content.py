HELP_SECTIONS = [
    (
        "1. เริ่มต้นใช้งาน",
        """
QA Evidence Builder คือเครื่องมือสำหรับช่วย QA / Tester / Developer
นำ Log API จำนวนมากมาจัดให้อยู่ในรูปแบบที่อ่านง่าย ค้นหาได้ และเลือกเฉพาะ
Log ที่ต้องการไปใช้เป็นหลักฐานประกอบ Ticket / Defect ได้

สิ่งที่โปรแกรมทำได้:
• Import JSON Array จากระบบ Log เช่น Kibana / Elasticsearch
• Import HAR จาก Browser / Network tools
• ดู API ตามลำดับเวลา
• Filter หา API ที่สนใจ
• รวม API ตาม Transaction
• เลือกเฉพาะ Log ที่ต้องการ Export
• Mask ข้อมูลสำคัญ เช่น Token / Password / Email
• สร้าง Evidence สำหรับแปะ Ticket
• Export เป็น ZIP พร้อม summary และ log ที่เลือก
• วิเคราะห์ Error Fingerprint และหา Error ที่เกิดซ้ำ

ตัวอย่างการใช้งานแบบง่าย:
1) เปิดโปรแกรม
2) กด Import JSON / HAR
3) เลือกไฟล์ sample_logs.json
4) ไปที่ Timeline
5) เลือก API ที่ต้องการ
6) กด Include Selected
7) ไปที่ Evidence เพื่อดู Preview
8) กด Copy Included for Ticket หรือ Export Included Evidence
""",
    ),
    (
        "2. Source — Import JSON / HAR",
        """
ปุ่ม Import JSON / HAR ใช้สำหรับเปิดไฟล์ Log จากเครื่อง

รองรับ:
• JSON Array
• HAR

JSON Array ต้องมีรูปแบบประมาณนี้:

[
  {
    "fields": {
      "TIMESTAMP": ["2026-08-21 11:03:36.230"],
      "REQUEST_URI": ["/api/v1/payment"],
      "REQUEST_METHOD": ["POST"],
      "RESPONSE_STATUS": [500],
      "RESPONSE_TIME": [3211],
      "REQUEST_ID": ["REQ-1002"],
      "CLIENT_PAGE_NAME": ["Checkout"],
      "kafka_topic_name": ["payment-service"],
      "REQUEST_BODY": ["{\\"orderId\\":\\"O-9001\\"}"],
      "RESPONSE_BODY": ["{\\"resultCode\\":\\"50001\\"}"]
    }
  }
]

HAR เป็นไฟล์ที่ Browser หรือ Network tool export ออกมา
โปรแกรมจะอ่าน URL, Method, Status, Response Time, Headers,
Request Body และ Response Body ที่มีใน HAR

วิธีใช้:
1) กด Import JSON / HAR
2) เลือกไฟล์
3) ถ้าอ่านได้ โปรแกรมจะแสดง Log ใน Timeline
4) ด้านบนจะแสดงจำนวน Log ที่โหลดเข้ามา

ถ้าไฟล์ไม่ถูกต้อง โปรแกรมจะแจ้ง Import failed
และจะไม่แก้ไขไฟล์ต้นฉบับของคุณ
""",
    ),
    (
        "3. Source — Paste JSON",
        """
Paste JSON ใช้กรณีที่ไม่ได้มีไฟล์ แต่ Copy JSON จากระบบ Log มาแล้ว

วิธีใช้:
1) กด Paste JSON
2) จะมีหน้าต่างใหม่เปิดขึ้น
3) วาง JSON Array หรือ HAR JSON ลงในช่อง
4) กด Load Logs
5) ถ้ารูปแบบถูกต้อง Log จะเข้า Timeline

ตัวอย่าง:
สมมติ Copy Log จาก Kibana มา 3 รายการ
ให้วางโดยมี [ และ ] ครอบทั้งหมด

[
  { "fields": { ... } },
  { "fields": { ... } },
  { "fields": { ... } }
]

ถ้าวางเฉพาะ Object เดียวแบบนี้:

{
  "fields": { ... }
}

โปรแกรมจะไม่ถือว่าเป็น JSON Array
""",
    ),
    (
        "4. Clear",
        """
Clear ใช้ล้างข้อมูลที่โหลดเข้ามาและเริ่มใหม่

สิ่งที่จะถูกล้าง:
• Log ที่ Import
• Filter
• รายการ Included
• Expected Result
• Actual Result

ไฟล์ต้นฉบับบนเครื่องจะไม่ถูกลบ
""",
    ),
    (
        "5. Timeline",
        """
Timeline เป็นหน้าหลักสำหรับดู API ทั้งหมดตามลำดับเวลา

Column สำคัญ:

Export
• ☐ = ยังไม่ได้เลือกสำหรับ Export
• ☑ = ถูก Include แล้ว

Timestamp
• เวลาที่ API เกิดขึ้น

Flag
• OK = ไม่เข้าเงื่อนไข Error/Slow
• ERROR = HTTP Status >= 400
• SLOW = Response Time >= 3000 ms

Fingerprint
• รหัสสำหรับ Error Signature เช่น ERR-A14F93C2
• ใช้ช่วยดูว่า Error หลายรายการเป็นปัญหาแบบเดียวกันหรือไม่

Method
• GET / POST / PUT / PATCH / DELETE

API
• Endpoint เช่น /api/v1/payment

Status
• HTTP Status เช่น 200 / 400 / 404 / 500

ms
• Response Time หน่วย millisecond

Request ID
• ID ของ request ถ้ามี

Transaction
• Transaction ID ที่โปรแกรมตรวจพบจาก Log

Timeline มี Scrollbar แนวนอนและแนวตั้ง
ดังนั้นถ้าหน้าต่างเล็ก Column จะไม่หาย เพียงเลื่อนดูได้
""",
    ),
    (
        "6. การเลือก Log เพื่อ Export",
        """
V3 ขึ้นไปจะไม่ Export ทุก Log อัตโนมัติ
ผู้ใช้ต้องกำหนดเองว่า Log ไหนจะถูก Include

วิธีที่ 1 — Include Selected
1) ไป Timeline
2) คลิกเลือก Row
3) ถ้าจะเลือกหลาย Row:
   • macOS ใช้ Command หรือ Shift
   • Windows ใช้ Ctrl หรือ Shift
4) กด Include Selected
5) Column Export จะเปลี่ยนจาก ☐ เป็น ☑

วิธีที่ 2 — Double-click
• Double-click ที่ Row เพื่อสลับ Include / Exclude

Select All
• Include ทุก Log ที่ผ่าน Filter ปัจจุบัน
• ไม่ได้หมายถึงทุก Log ทั้งหมดเสมอไป

ตัวอย่าง:
Import มา 1,000 Logs
Filter Status = 5xx เหลือ 12 Logs
กด Select All
=> Include แค่ 12 Logs

Exclude Selected
• เอา Row ที่เลือกออกจาก Included

Deselect All
• ล้าง Included ทั้งหมด
• ไม่ได้ลบ Log จาก Timeline

ข้อความ Included: N
จะบอกว่าตอนนี้มีกี่ Log ที่พร้อมใช้ Copy / Export
""",
    ),
    (
        "7. Filters — Search",
        """
Search ใช้ค้นหาคำจากข้อมูลหลัก เช่น:
• API
• Request ID
• Transaction ID
• Page
• Kafka Topic

ตัวอย่าง:
พิมพ์ payment

อาจเหลือ:
POST /api/v1/payment
GET /api/v1/payment/status

Search ไม่แก้ไขข้อมูลต้นฉบับ
และสามารถใช้ร่วมกับ Filter อื่นได้
""",
    ),
    (
        "8. Filters — Minimum response ms",
        """
ใช้กรองเฉพาะ API ที่ใช้เวลามากกว่าหรือเท่ากับค่าที่กำหนด

ตัวอย่าง:
ใส่ 1000

จะแสดงเฉพาะ API ที่ Response Time >= 1000 ms

เหมาะสำหรับ:
• หา API ช้า
• Performance investigation
• ตรวจ request ที่เกิน SLA

ถ้าไม่ต้องการกรอง ให้เว้นว่าง
""",
    ),
    (
        "9. Filters — Page / Kafka Topic / Transaction",
        """
Page
ใช้ค้นจาก CLIENT_PAGE_NAME

ตัวอย่าง:
Checkout

จะเหลือ Log ที่ Page มีคำว่า Checkout

Kafka Topic
ใช้ค้นจาก kafka_topic_name

ตัวอย่าง:
payment-service

Transaction ID
ใช้ดูเฉพาะ API ใน Transaction เดียวกัน

ตัวอย่าง:
TX-CHECKOUT-001

Filter ทั้งหมดสามารถใช้พร้อมกันได้

ตัวอย่าง:
Page = Checkout
Method = POST
Status = 5xx
Minimum response ms = 1000

ผลคือ:
เฉพาะ POST API ในหน้า Checkout
ที่ Error 5xx และใช้เวลา >= 1000 ms
""",
    ),
    (
        "10. Filters — HTTP Method / HTTP Status",
        """
HTTP Method:
• ALL
• GET
• POST
• PUT
• PATCH
• DELETE

HTTP Status:
• ALL
• 2xx
• 3xx
• 4xx
• 5xx
• Other

ตัวอย่าง:
Status = 5xx
จะแสดง 500, 501, 502, 503 ฯลฯ

Status = 4xx
จะแสดง 400, 401, 403, 404 ฯลฯ
""",
    ),
    (
        "11. Errors only / Slow only",
        """
Errors only
แสดงเฉพาะ Log ที่ HTTP Status >= 400

Slow only
แสดงเฉพาะ Log ที่ Response Time >= 3000 ms

สามารถเปิดพร้อมกันได้

ถ้าเปิดทั้ง:
✓ Errors only
✓ Slow only

จะแสดงเฉพาะ API ที่เป็น Error และช้าพร้อมกัน
""",
    ),
    (
        "12. Transactions",
        """
Transaction Tab ใช้ดูการจัดกลุ่ม API ตาม Transaction ID

จะแสดง:
• Transaction ID
• จำนวน API
• จำนวน Error
• จำนวน Slow API

ตัวอย่าง:

TX-CHECKOUT-001
APIs: 5
Errors: 1
Slow: 1

Double-click Transaction
โปรแกรมจะเอา Transaction ID ไปใส่ Filter อัตโนมัติ
Timeline จึงเหลือเฉพาะ API ของ Transaction นั้น

เหมาะสำหรับดู Journey เช่น:

cart/validate
→ payment
→ payment/confirm
→ order/status
""",
    ),
    (
        "13. Evidence — Expected Result",
        """
Expected Result คือผลที่ Tester คาดหวัง

ตัวอย่าง:
Payment should complete successfully and the order
should be created with status CONFIRMED.

หรือภาษาไทย:
หลังจากกดชำระเงิน ระบบควรชำระเงินสำเร็จ
และสร้าง Order สถานะ CONFIRMED

ข้อมูลนี้จะถูกใส่ลงใน Ticket Evidence
""",
    ),
    (
        "14. Evidence — Actual Result",
        """
Actual Result คือสิ่งที่เกิดขึ้นจริง

ตัวอย่าง:
Payment API returned HTTP 500 and the order
was not created.

หรือ:
เมื่อกดชำระเงิน API /payment ตอบ HTTP 500
และไม่สามารถสร้าง Order ได้

Expected / Actual ไม่บังคับ
ถ้าไม่กรอก โปรแกรมยังสามารถสร้าง Evidence ได้
""",
    ),
    (
        "15. Included Evidence Preview",
        """
Preview แสดงเฉพาะ Log ที่ถูก Include

นี่เป็นจุดสำคัญ:
Timeline อาจมี 100 Logs
แต่ Include 3 Logs
Preview จะใช้เฉพาะ 3 Logs

ใน Preview จะมี:
• Summary
• Error / Slow count
• Transaction count
• Auto Summary
• Expected Result
• Actual Result
• Timeline
• API Detail
• Query
• Request
• Response
• Error Fingerprint

ควรตรวจ Preview ก่อน Copy หรือ Export
""",
    ),
    (
        "16. Mask sensitive data",
        """
Mask sensitive data เปิดไว้เป็น Default

โปรแกรมพยายามปิดบังข้อมูลประเภท:
• Authorization
• Bearer Token
• JWT
• Cookie
• Password
• PIN
• Access Token
• Refresh Token
• Session
• Mobile / Phone
• Email
• Device ID

ตัวอย่าง:

ก่อน:
{
  "password": "MySecret123",
  "authorization": "Bearer abcdef"
}

หลัง Mask:
{
  "password": "********",
  "authorization": "********"
}

แนะนำให้เปิด Mask ไว้
โดยเฉพาะก่อนนำ Evidence ไปใส่ Ticket
""",
    ),
    (
        "17. Extra mask keys",
        """
ใช้กรณีองค์กรมี Field Sensitive เพิ่มเติมที่โปรแกรมไม่รู้จัก

กรอกชื่อ Field คั่นด้วย comma

ตัวอย่าง:

employeeId,citizenId,accountNumber

ถ้า Log มี:

{
  "employeeId": "E00001",
  "accountNumber": "1234567890"
}

หลัง Mask:

{
  "employeeId": "********",
  "accountNumber": "********"
}

ไม่ต้องแก้ Source Code
""",
    ),
    (
        "18. Package Contents",
        """
เลือกได้ว่า ZIP ที่ Export จะมีอะไร

summary.txt
• Evidence แบบ Text
• เหมาะกับเปิดอ่านง่าย

summary.md
• Evidence แบบ Markdown
• เหมาะกับระบบ Ticket/Documentation ที่รองรับ Markdown

Raw log files
• Log ต้นฉบับที่ไม่ได้ Mask
• OFF เป็น Default
• ควรเปิดเฉพาะเมื่อจำเป็น

Sanitized log files
• Log ที่ผ่าน Mask แล้ว
• ON เป็น Default

ตัวอย่าง Package:

QA_Evidence_20260821_170000.zip
├── summary.txt
├── summary.md
└── sanitized/
    ├── 001_payment.json
    └── 002_order_status.json

ถ้าเปิด Raw จะเพิ่ม:

raw/
├── 001_payment.json
└── 002_order_status.json
""",
    ),
    (
        "19. Copy Included for Ticket",
        """
Copy เฉพาะ Included Logs ไป Clipboard

วิธีใช้:
1) Include Log ที่ต้องการ
2) ตรวจ Preview
3) กด Copy Included for Ticket
4) ไป Jira / Ticket / Email
5) Paste

ถ้าไม่มี Included Log
โปรแกรมจะแจ้งให้เลือก Log ก่อน
""",
    ),
    (
        "20. Copy Included as Markdown",
        """
เหมือน Copy for Ticket
แต่ห่อ Evidence ใน Markdown code block

เหมาะกับ:
• Jira ที่เปิด Markdown
• GitHub Issue
• GitLab
• Wiki
• Markdown Documentation

ถ้าระบบปลายทางไม่รองรับ Markdown
ใช้ Copy Included for Ticket แทน
""",
    ),
    (
        "21. Export Included Evidence",
        """
สร้าง Evidence ZIP จาก Included Logs เท่านั้น

ขั้นตอน:
1) Include Logs
2) เลือก Package Contents
3) กด Export Included Evidence
4) เลือก Folder ปลายทาง
5) โปรแกรมสร้าง ZIP

ชื่อประมาณ:
QA_Evidence_20260821_170000.zip

ถ้าไม่ Include Log
โปรแกรมจะไม่ Export

ถ้า Package Contents ไม่เลือกอะไรเลย
โปรแกรมจะแจ้ง Error
""",
    ),
    (
        "22. Analysis — Auto Defect Summary",
        """
Analysis Tab สรุป Log แบบ Rule-based
ไม่มีการส่งข้อมูลไป AI หรือ Internet

ตัวอย่าง:

Observed 15 API logs across 2 transaction(s).
Detected 3 HTTP error(s) and 2 slow API(s).
First error: POST /api/v1/payment returned 500...
Found 1 repeated error signature...

ใช้สำหรับช่วย QA มองภาพรวมเร็วขึ้น
แต่ไม่ควรใช้แทนการวิเคราะห์โดยคนทั้งหมด
""",
    ),
    (
        "23. Analysis — Error Fingerprint",
        """
Error Fingerprint เป็นรหัสของรูปแบบ Error

โปรแกรมสร้างจากข้อมูลเช่น:
• HTTP Method
• API URI
• HTTP Status
• resultCode
• Error Message

ตัวอย่าง:

POST /api/v1/payment
HTTP 500
resultCode = 50001
Internal Server Error

=> ERR-A14F93C2

ถ้า Log อีกตัวมีรูปแบบ Error เหมือนกัน
จะได้ Fingerprint เดียวกัน

ประโยชน์:
• หา Error เกิดซ้ำ
• ช่วยดูว่าอาจเป็น Defect เดิม
• ลดเวลานั่งเทียบ Error ทีละ Log
""",
    ),
    (
        "24. Analysis — Duplicate / Similar Errors",
        """
Analysis จะรวม Error ที่มี Fingerprint เดียวกัน

ตัวอย่าง:

ERR-A14F93C2: 3 occurrence(s)
  - 11:03:36 POST /payment HTTP 500
  - 11:04:02 POST /payment HTTP 500
  - 11:06:14 POST /payment HTTP 500

ความหมาย:
พบ Error Signature เดียวกัน 3 ครั้ง

หมายเหตุ:
เป็นการตรวจภายใน Log ที่โหลดอยู่ตอนนี้
ยังไม่ได้ค้น Ticket เก่าใน Jira
""",
    ),
    (
        "25. ตัวอย่าง Workflow — Payment Defect",
        """
สถานการณ์:
Tester กด Payment แล้วหน้าจอ Error

ขั้นตอน:

1) Export Log จากระบบ Log เป็น JSON Array
2) เปิด QA Evidence Builder
3) Import JSON
4) Search = payment
5) Status = 5xx
6) เห็น:
   POST /api/v1/payment
   HTTP 500
   3211 ms
7) เลือก Row แล้วกด Include Selected
8) ถ้าต้องการ API ก่อนหน้า:
   Reset Filter
   Transaction = TX-CHECKOUT-001
9) Include:
   cart/validate
   payment
   order/status
10) ไป Evidence
11) Expected:
    Payment should succeed and order should be confirmed.
12) Actual:
    Payment returned HTTP 500 and order was not created.
13) ตรวจ Mask sensitive data = ON
14) ตรวจ Preview
15) Copy Included for Ticket
16) Paste ลง Defect
17) ถ้าต้องแนบไฟล์ กด Export Included Evidence

ผลคือ QA ส่ง Ticket ที่มี Technical Evidence ครบขึ้น
โดยไม่ต้อง Copy Log ทีละไฟล์
""",
    ),
    (
        "26. ตัวอย่าง Workflow — หา API ช้า",
        """
สถานการณ์:
ลูกค้าบอกว่าหน้า Checkout โหลดช้า

1) Import Log
2) Page = Checkout
3) Minimum response ms = 2000
4) หรือเปิด Slow only
5) Timeline อาจพบ:

GET /cart             350 ms
POST /validate       2100 ms
POST /payment        4100 ms

6) Include /validate และ /payment
7) ไป Evidence
8) Actual Result:
   Checkout waits around 6 seconds before completion.
9) Export Evidence

QA สามารถส่งให้ Developer ดู API ที่ช้าได้ตรงจุด
""",
    ),
    (
        "27. ตัวอย่าง Workflow — Transaction",
        """
สถานการณ์:
ต้องการดู API ทั้ง Journey ของการ Checkout

1) Import Log
2) เปิด Transactions
3) พบ TX-CHECKOUT-001
4) APIs = 5, Errors = 1
5) Double-click Transaction
6) Timeline เหลือ 5 API:

POST /cart/validate
POST /promotion/check
POST /payment
POST /order/create
GET  /order/status

7) Select All
8) ไป Evidence
9) จะได้ Timeline ทั้ง Journey ใน Ticket
""",
    ),
    (
        "28. ปัญหาที่พบบ่อย",
        """
Import failed
• ตรวจว่า JSON เป็น JSON Array
• ตรวจ comma / quote / bracket
• ถ้าเป็น HAR ให้ใช้ไฟล์ HAR จริง

Timeline ว่าง
• ตรวจ Filter ว่าค้างอยู่หรือไม่
• กด Reset Filters

Export แล้วไม่มี Log ที่ต้องการ
• ตรวจ Column Export ว่าเป็น ☑ หรือไม่
• Export ใช้ Included Logs ไม่ใช่ทุก Row

Copy แล้วขึ้น Nothing included
• ต้อง Include Selected หรือ Select All ก่อน

ข้อมูล Sensitive ยังแสดง
• ตรวจ Mask sensitive data = ON
• เพิ่ม Field ใน Extra mask keys

ปุ่มบางปุ่มหาไม่เจอเมื่อหน้าต่างเล็ก
• Sidebar จะย่อเป็น icon-only อัตโนมัติ
• Timeline มี Horizontal Scrollbar
• Detail inspector สามารถย่อได้ด้วย Splitter

PySide6 import error:
ModuleNotFoundError: No module named 'PySide6'

ติดตั้ง dependency ด้วย:
python -m pip install -r requirements.txt
""",
    ),
    (
        "29. คำแนะนำด้าน Security",
        """
Log อาจมีข้อมูลสำคัญ เช่น:
• Token
• Authorization
• Session
• Customer information
• Internal endpoint
• Device ID
• Personal information

คำแนะนำ:
• เปิด Mask sensitive data
• ใช้ Sanitized logs เป็นหลัก
• Raw log files เปิดเฉพาะเมื่อจำเป็น
• ตรวจ Evidence ก่อนส่ง
• ปฏิบัติตาม Security Policy ขององค์กร

โปรแกรมทำงาน Local-only
ไม่มี Code สำหรับ Upload Log ไป Server ภายนอก
""",
    ),
    (
        "30. Quick Start สรุปสั้น",
        """
สำหรับคนที่ไม่เคยใช้เลย:

1) Import JSON / HAR
2) เปิด Timeline
3) ใช้ Filter หา API
4) เลือก Row
5) Include Selected
6) ดูว่า Export เป็น ☑
7) ไป Evidence
8) กรอก Expected / Actual ถ้าต้องการ
9) เปิด Mask sensitive data
10) ตรวจ Preview
11) Copy Included for Ticket
หรือ
12) Export Included Evidence

จำง่าย ๆ:

Import
→ Filter
→ Include
→ Review
→ Copy / Export
""",
    ),
]
