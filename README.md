# Auto X Script Setup

โปรเจกต์ Python นี้สร้างข้อความภาษาไทยด้วย Gemini แล้วโพสต์ลง X ผ่าน X API ได้ มีทั้งการทดสอบสร้างข้อความในเครื่อง, การโพสต์ครั้งเดียว และ GitHub Actions สำหรับโพสต์ตามหัวข้อประจำวัน

> **ระวัง:** สคริปต์ที่โพสต์จะเผยแพร่ข้อความจริงบนบัญชี X ของคุณ ตรวจเนื้อหาและบัญชีให้ถูกต้องก่อนรัน โดยเฉพาะ `scripts/post_cyber_once.py`, `scripts/post_today_once.py`, `main.py` และการกด Run workflow ด้วยตนเอง

## โครงสร้างโปรเจกต์

```text
auto-x-script-setup/
├── .github/workflows/       # GitHub Actions
├── scripts/                 # สคริปต์สำหรับรันด้วยตนเอง
├── tests/                   # Unit tests
├── .env                     # API keys (ห้าม commit)
├── content_cycle.py         # เลือกหัวข้อตามวัน
├── main.py                  # สร้างและโพสต์หัวข้อประจำวัน
├── README.md
└── requirements.txt
```

## หัวข้อประจำวัน

`main.py` เลือกหัวข้อตามวันในประเทศไทย (UTC+7) และโพสต์หนึ่งครั้งต่อการรัน:

| วัน | หัวข้อ |
|---|---|
| จันทร์ | AI และเทคโนโลยี |
| อังคาร | กฎหมายและสิทธิใกล้ตัว |
| พุธ | คำถามชวนแสดงความคิดเห็น |
| พฤหัสบดี | ความรู้ทั่วไป |
| ศุกร์ | เครื่องมือและแอป |
| เสาร์ | วิธีรับมือปัญหา |
| อาทิตย์ | ข่าวเทคโนโลยีประจำสัปดาห์ |

หัวข้อ `cybersecurity` ใช้ในสคริปต์ทดสอบโพสต์ไซเบอร์แบบครั้งเดียว ไม่ได้อยู่ในตารางหัวข้อประจำสัปดาห์

## สิ่งที่ต้องมี

- Python 3.11 หรือใหม่กว่า
- Gemini API key จาก [Google AI Studio](https://aistudio.google.com/apikey)
- บัญชีและสิทธิ์ใช้งาน X Developer API สำหรับแอปที่จะโพสต์
- ค่ารับรอง X แบบ OAuth 1.0a: API Key, API Key Secret, Access Token และ Access Token Secret

โควตาและค่าใช้จ่ายของ Gemini/X ขึ้นอยู่กับโปรเจกต์ บัญชี และแผนที่ใช้งาน ตรวจสอบข้อมูลล่าสุดจากผู้ให้บริการก่อนเปิดใช้งานแบบอัตโนมัติ

## ติดตั้งและตั้งค่าในเครื่อง

เปิด PowerShell ที่โฟลเดอร์โปรเจกต์ แล้วสร้าง virtual environment และติดตั้ง dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

ถ้า PowerShell แจ้งว่าไม่อนุญาตให้รันสคริปต์ ให้ใช้ Command Prompt แล้วเปิด environment ด้วย:

```bat
.venv\Scripts\activate.bat
```

สร้างไฟล์ชื่อ `.env` ที่ root ของโปรเจกต์ แล้วใส่ค่าของคุณเอง:

```dotenv
GEMINI_API_KEY=ใส่_Gemini_API_key
X_API_KEY=ใส่_X_API_Key
X_API_SECRET=ใส่_X_API_Key_Secret
X_ACCESS_TOKEN=ใส่_X_Access_Token
X_ACCESS_TOKEN_SECRET=ใส่_X_Access_Token_Secret
```

อย่าใส่เครื่องหมาย quote รอบค่า เว้นแต่จำเป็นสำหรับค่าที่มีช่องว่าง และอย่าแชร์หรือ commit ไฟล์ `.env` — ไฟล์นี้อยู่ใน `.gitignore` แล้ว

## ขอ Gemini API key

1. เปิด [Google AI Studio – API keys](https://aistudio.google.com/apikey) และลงชื่อเข้าใช้บัญชี Google
2. เลือกหรือสร้าง Google Cloud project ตามที่ AI Studio แสดง
3. สร้าง API key และนำไปใส่ใน `GEMINI_API_KEY` ใน `.env`
4. ตรวจสอบโควตา สถานะ billing และข้อจำกัดของโมเดลใน AI Studio ก่อนใช้งาน

อย่าเผยแพร่ API key ใน source code, screenshot, log หรือ repository สาธารณะ รายละเอียดเพิ่มเติมอยู่ใน [Gemini API key documentation](https://ai.google.dev/gemini-api/docs/api-key).

## สมัครและตั้งค่า X API

หน้าตาและเงื่อนไขการเข้าถึง Developer Portal อาจเปลี่ยนได้ และการใช้งาน X API อาจมีแผนหรือค่าใช้จ่ายต่างกัน ให้ยึดข้อมูลล่าสุดใน [X Developer Platform](https://developer.x.com/) และ [X API documentation](https://docs.x.com/).

1. ลงชื่อเข้าใช้บัญชี X ที่ต้องการให้เป็นผู้โพสต์ แล้วเข้า Developer Portal จาก [developer.x.com](https://developer.x.com/) หรือ [console.x.com](https://console.x.com/).
2. สมัคร/เปิดใช้งาน Developer access ตามขั้นตอนที่พอร์ทัลแสดง ระบุวัตถุประสงค์การใช้งานให้ตรงจริง เช่น สคริปต์ส่วนตัวสำหรับสร้างและโพสต์ความรู้ด้านเทคโนโลยีเป็นภาษาไทย
3. สร้าง Project และ App (หรือเลือก App ที่มีอยู่) ใน Developer Portal
4. ในการตั้งค่า App เปิด **User authentication settings** และกำหนด **App permissions** เป็น **Read and write** เพื่อให้โพสต์ได้ เลือกประเภทแอปและกรอก Callback URL/Website URL ตามข้อกำหนดของพอร์ทัล หากไม่ทราบว่าจะใส่ค่าใด ให้ตรวจคู่มือ X ปัจจุบันแทนการใช้ URL ตัวอย่างที่ไม่ตรงกับแอป
5. บันทึกการตั้งค่า จากนั้นไปที่ **Keys and tokens** และสร้างหรือ regenerate **Access Token and Secret** หลังตั้งสิทธิ์ Read and write แล้ว
6. ใส่ credentials ทั้งสี่ค่าลง `.env` ให้ตรงกับตารางด้านล่าง

| ชื่อตัวแปรใน `.env` | ชื่อ credential ใน X |
|---|---|
| `X_API_KEY` | API Key (Consumer Key) |
| `X_API_SECRET` | API Key Secret (Consumer Secret) |
| `X_ACCESS_TOKEN` | Access Token |
| `X_ACCESS_TOKEN_SECRET` | Access Token Secret |

โค้ดใช้ OAuth 1.0a user context ผ่าน Tweepy ตาม credentials เหล่านี้ ดูรายละเอียดได้ที่ [X OAuth 1.0a documentation](https://docs.x.com/fundamentals/authentication/oauth-1-0a/overview).

> เก็บ credentials ทั้งสี่เป็นความลับ หากเผลอเปิดเผย ให้ revoke/regenerate ใน Developer Portal แล้วอัปเดต `.env` และ GitHub Secrets ทันที

## วิธีทดสอบและโพสต์

### สร้างข้อความในเครื่องโดยไม่โพสต์

```powershell
python -m scripts.generate_local
```

สคริปต์นี้เรียก Gemini เพื่อสร้างข้อความของหัวข้อประจำวัน แต่ **ไม่ส่งโพสต์ไป X** และจะวนสร้างซ้ำทุก 5 นาทีจนกด `Ctrl+C` ใช้ทดสอบสั้น ๆ เท่านั้น เพราะทุกครั้งที่วนจะเรียก Gemini และใช้โควตา

### โพสต์ความรู้ไซเบอร์หนึ่งครั้ง

```powershell
python -m scripts.post_cyber_once
```

เรียก Gemini เพื่อสร้างโพสต์ความรู้ทั่วไปด้านการป้องกันไซเบอร์ แล้วส่งไป X **หนึ่งโพสต์** หาก Gemini ตอบข้อผิดพลาด โค้ดจะหยุดก่อนส่งโพสต์

### โพสต์หัวข้อประจำวันหนึ่งครั้ง

```powershell
python -m scripts.post_today_once
```

สร้างข้อความตามหัวข้อของวันในประเทศไทย แล้วส่งไป X **หนึ่งโพสต์** เช่นเดียวกับการรัน:

```powershell
python main.py
```

ทุกครั้งที่เรียก `main.py` จะสร้างและโพสต์หนึ่งครั้ง ไม่ใช่โหมด dry-run

## โพสต์ตามรอบสัปดาห์ด้วย GitHub Actions

ไฟล์ `.github/workflows/daily_tweet.yml` ตั้งเวลาให้รัน `python main.py` ทุกวัน เวลา **09:00 น. ประเทศไทย** (02:00 UTC) จึงวนครบทั้งเจ็ดหัวข้อเมื่อรันต่อเนื่องครบสัปดาห์ ทั้งนี้ GitHub อาจเริ่มงานช้ากว่าเวลา cron ที่กำหนดได้

1. Push โปรเจกต์ขึ้น GitHub repository และตรวจว่า workflow อยู่บน default branch
2. เปิด repository บน GitHub แล้วไปที่ **Settings → Secrets and variables → Actions**
3. เลือก **New repository secret** และเพิ่ม secret เหล่านี้ทีละรายการ:

   | ชื่อ Secret | ค่าที่ต้องใส่ |
   |---|---|
   | `GEMINI_API_KEY` | Gemini API key |
   | `X_API_KEY` | X API Key |
   | `X_API_SECRET` | X API Key Secret |
   | `X_ACCESS_TOKEN` | X Access Token |
   | `X_ACCESS_TOKEN_SECRET` | X Access Token Secret |

4. ไปที่แท็บ **Actions** แล้วเลือก workflow **Daily Auto Tweet** เพื่อตรวจสอบสถานะ
5. ต้องการทดสอบด้วยตนเอง ให้กด **Run workflow** — การทำเช่นนี้จะโพสต์จริงหนึ่งโพสต์ทันที

GitHub Actions ใช้ Secrets ที่ตั้งไว้แทนไฟล์ `.env` และ workflow นี้ต้องการเพียงสิทธิ์ `contents: read` สำหรับ checkout โค้ด

## ข้อผิดพลาดที่พบบ่อย

- **Gemini HTTP 429**: อาจชนขีดจำกัดคำขอ, token, โควตารายวัน, billing หรือข้อจำกัดของเครื่องมือค้นหา ตรวจหน้า [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) และ Usage ของโปรเจกต์ อย่าปล่อย `scripts.generate_local` วนทิ้งไว้
- **Gemini HTTP 503**: โมเดลอาจมีผู้ใช้งานหนาแน่นชั่วคราว ลองใหม่ภายหลัง ข้อผิดพลาดนี้เกิดก่อนขั้นตอนโพสต์ X
- **X HTTP 401/403**: ตรวจว่า credentials ถูกต้อง ยังใช้งานได้ และ Access Token ถูกสร้างหลังตั้งสิทธิ์ **Read and write**
- **Missing required environment variable**: ตรวจชื่อใน `.env` หรือ GitHub Secrets ให้ตรงตามตัวอย่างทุกตัว
- **โพสต์ผิดหัวข้อหรือโพสต์ซ้ำ**: ตรวจวัน/เขตเวลาและ workflow run history ก่อนรันซ้ำ เพราะการรันด้วยตนเองก็สร้างโพสต์จริงได้

## ทดสอบตารางหัวข้อ

```powershell
python -m unittest discover -s tests
```
