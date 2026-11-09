# Auto X SCRIPT SETUP

> Automatically generates and publishes daily Thai-language posts about technology, AI, scams, cybersecurity, and digital law on X.

โปรเจกต์นี้ใช้ GitHub Actions สร้างข้อความภาษาไทยด้วย OpenRouter (โมเดลฟรีที่เลือกให้อัตโนมัติ) และโพสต์ลง X ตามหัวข้อประจำวันเมื่อสั่งรันด้วยตนเอง โดยทำงานบน GitHub-hosted runner จึงไม่ต้องเปิดคอมพิวเตอร์ทิ้งไว้

> **ระวัง:** Workflow จะเผยแพร่ข้อความจริงบนบัญชี X ของคุณทุกครั้งที่ทำงาน รวมถึงเมื่อกด **Run workflow** ด้วยตนเอง

## โครงสร้างโปรเจกต์

```text
auto-x-script-setup/
├── .github/workflows/       # GitHub Actions
├── tests/                   # Unit tests
├── .env                     # API keys (ห้าม commit)
├── content_cycle.py         # เลือกหัวข้อตามวัน
├── main.py                  # จุดเริ่มต้นที่ workflow ใช้โพสต์หัวข้อประจำวัน
├── README.md
└── requirements.txt
```

## หัวข้อประจำวัน

`main.py` เลือกหัวข้อตามวันในประเทศไทย (UTC+7) และโพสต์หนึ่งครั้งต่อการรัน:

| วัน | หัวข้อ |
|---|---|
| จันทร์ | Technology น่ารู้ |
| อังคาร | AI น่ารู้ |
| พุธ | ภัยทางไซเบอร์ |
| พฤหัสบดี | Scam รอบตัว |
| ศุกร์ | วิธีป้องกัน scammer |
| เสาร์ | Hacker 101 (พื้นฐาน cybersecurity เชิงป้องกัน เรียนรู้เฉพาะระบบที่ได้รับอนุญาต) |
| อาทิตย์ | กฎหมายไทย (พ.ร.บ.คอมพิวเตอร์, PDPA และด้านดิจิทัล) |

## สิ่งที่ต้องมี

- Python 3.11 หรือใหม่กว่า
- OpenRouter API key จาก [OpenRouter](https://openrouter.ai/settings/keys)
- บัญชีและสิทธิ์ใช้งาน X Developer API สำหรับแอปที่จะโพสต์
- ค่ารับรอง X แบบ OAuth 1.0a: API Key, API Key Secret, Access Token และ Access Token Secret

โมเดลฟรีและข้อจำกัดการใช้งานของ OpenRouter อาจเปลี่ยนแปลงได้ ตรวจสอบ [โมเดลฟรี](https://openrouter.ai/models?max_price=0) และ [ข้อจำกัดการใช้งาน](https://openrouter.ai/docs/faq#how-are-rate-limits-calculated) ก่อนเปิดใช้โพสต์อัตโนมัติ

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

คัดลอก `.env.example` เป็นไฟล์ `.env` ที่ root ของโปรเจกต์ แล้วแทนที่ placeholder ด้วยค่าจริงของคุณ:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_TOKEN_SECRET=your_x_access_token_secret
```

ตัวอย่างคำสั่งคัดลอกใน PowerShell:

```powershell
Copy-Item .env.example .env
```

ค่าหลังเครื่องหมาย `=` ใน `.env.example` เป็น placeholder ให้แทนที่ด้วยค่าจริงจาก OpenRouter/X ตามหัวข้อด้านล่าง โดยคงชื่อทางซ้ายของ `=` ไว้ให้ตรงทุกตัว

อย่าใส่เครื่องหมาย quote รอบค่า เว้นแต่จำเป็นสำหรับค่าที่มีช่องว่าง และอย่าแชร์หรือ commit ไฟล์ `.env` — ไฟล์นี้อยู่ใน `.gitignore` แล้ว

ทดสอบสร้างโพสต์โดยไม่เผยแพร่ลง X:

```powershell
python main.py --dry-run
```

โหมดนี้ต้องใช้ `OPENROUTER_API_KEY` เท่านั้น ไม่ต้องตั้ง X credentials และจะแสดงข้อความที่สร้างพร้อมจำนวนตัวอักษร

## ขอ OpenRouter API key

1. สมัครหรือลงชื่อเข้าใช้ [OpenRouter](https://openrouter.ai/)
2. เปิดหน้า [Keys](https://openrouter.ai/settings/keys) แล้วเลือกสร้าง API key
3. ตั้งชื่อ key เพื่อจำได้ว่าใช้กับโปรเจกต์นี้ (ชื่อเป็น label สำหรับคุณ ไม่ใช่ค่าที่ต้องใส่ในโค้ด) แล้วสร้าง key
4. คัดลอกค่า API key ที่ OpenRouter แสดง แล้วนำไปใส่เป็นค่าของ `OPENROUTER_API_KEY` ใน `.env` หรือ GitHub Secret ชื่อเดียวกัน ดูขั้นตอน GitHub ด้านล่าง
5. โปรเจกต์ใช้ `openrouter/free` เพื่อเลือกโมเดลฟรีที่พร้อมให้บริการโดยอัตโนมัติ รุ่นที่ถูกเลือกอาจเปลี่ยนไปตามความพร้อมใช้งาน และคุณภาพ/ข้อจำกัดอาจแตกต่างกัน ตรวจสอบข้อจำกัดและจำนวนคำขอฟรีล่าสุดจาก OpenRouter

API key เป็นรหัสลับ ไม่ใช่ชื่อบัญชีหรือ URL หากปิดหน้าที่แสดง key แล้วคัดลอกไม่ได้ ให้สร้าง key ใหม่แทนการพยายามเดาค่า ตรวจสอบเครดิต/ข้อจำกัดของบัญชีด้วย เพราะ key ที่ถูกต้องก็อาจเรียก API ไม่ได้หากเครดิตหรือโควตาหมด

อย่าเผยแพร่ API key ใน source code, screenshot, log หรือ repository สาธารณะ

## สมัครและตั้งค่า X API

หน้าตาและเงื่อนไขการเข้าถึง Developer Portal อาจเปลี่ยนได้ และการใช้งาน X API อาจมีแผนหรือค่าใช้จ่ายต่างกัน ให้ยึดข้อมูลล่าสุดใน [X Developer Platform](https://developer.x.com/) และ [X API documentation](https://docs.x.com/).

1. ลงชื่อเข้าใช้บัญชี X ที่ต้องการให้เป็นผู้โพสต์ แล้วเข้า Developer Portal จาก [developer.x.com](https://developer.x.com/) หรือ [console.x.com](https://console.x.com/).
2. สมัคร/เปิดใช้งาน Developer access ตามขั้นตอนที่พอร์ทัลแสดง ระบุวัตถุประสงค์การใช้งานให้ตรงจริง เช่น สคริปต์ส่วนตัวสำหรับสร้างและโพสต์ความรู้ด้านเทคโนโลยีเป็นภาษาไทย
3. สร้าง Project และ App (หรือเลือก App ที่มีอยู่) ใน Developer Portal
4. ในการตั้งค่า App เปิด **User authentication settings** และกำหนด **App permissions** เป็น **Read and write** เพื่อให้โพสต์ได้ เลือกประเภทแอปและกรอก Callback URL/Website URL ตามข้อกำหนดของพอร์ทัล หากไม่ทราบว่าจะใส่ค่าใด ให้ตรวจคู่มือ X ปัจจุบันแทนการใช้ URL ตัวอย่างที่ไม่ตรงกับแอป
5. บันทึกการตั้งค่า จากนั้นไปที่ **Keys and tokens** และสร้างหรือ regenerate **Access Token and Secret** หลังตั้งสิทธิ์ Read and write แล้ว
6. ใส่ credentials ทั้งสี่ค่าลง `.env` หรือ GitHub Secrets โดยจับคู่ตามตารางนี้:

| ชื่อตัวแปร/Secret | คัดลอกค่าจาก X Developer Portal |
|---|---|
| `X_API_KEY` | **API Key** หรือ **Consumer Key** ในหน้า Keys and tokens ของ App |
| `X_API_SECRET` | **API Key Secret** หรือ **Consumer Secret** ของ App เดียวกัน |
| `X_ACCESS_TOKEN` | **Access Token** สำหรับบัญชีผู้ใช้ที่จะโพสต์ |
| `X_ACCESS_TOKEN_SECRET` | **Access Token Secret** ที่จับคู่กับ Access Token ข้างต้น |

`X_API_KEY` และ `X_API_SECRET` เป็น credentials ของ App ส่วน `X_ACCESS_TOKEN` และ `X_ACCESS_TOKEN_SECRET` เป็น credentials ของผู้ใช้ที่อนุญาตให้ App โพสต์ ต้องใช้ค่าจาก Project/App และบัญชีเดียวกับที่ต้องการโพสต์ อย่านำ Bearer Token มาใส่แทน Access Token

โค้ดใช้ OAuth 1.0a user context ผ่าน Tweepy ตาม credentials เหล่านี้ ดูรายละเอียดได้ที่ [X OAuth 1.0a documentation](https://docs.x.com/fundamentals/authentication/oauth-1-0a/overview).

> เก็บ credentials ทั้งสี่เป็นความลับ หากเผลอเปิดเผย ให้ revoke/regenerate ใน Developer Portal แล้วอัปเดต `.env` และ GitHub Secrets ทันที

## ใช้งาน GitHub Actions

ไฟล์ `.github/workflows/daily_tweet.yml` ไม่มีการตั้งเวลารันอัตโนมัติ จะทำงานเมื่อเจ้าของ repository สั่ง **Run workflow** เองเท่านั้น โดยแต่ละครั้งจะสร้างและโพสต์หนึ่งข้อความจริงลง X

1. Push โปรเจกต์ขึ้น GitHub repository และตรวจว่า workflow อยู่บน default branch
2. เปิดหน้า repository บน GitHub แล้วไปที่ **Settings → Secrets and variables → Actions** (ต้องมีสิทธิ์ Admin หรือสิทธิ์จัดการ Secrets)
3. ในส่วน **Repository secrets** เลือก **New repository secret** แล้วเพิ่มค่าทีละรายการ:

   | ช่อง **Name** (ใส่ชื่อนี้ตรงตัว) | ช่อง **Secret** (วางค่าจริงจากผู้ให้บริการ) |
   |---|---|
   | `OPENROUTER_API_KEY` | API key ที่สร้างจาก OpenRouter |
   | `X_API_KEY` | API Key / Consumer Key ของ X App |
   | `X_API_SECRET` | API Key Secret / Consumer Secret ของ X App |
   | `X_ACCESS_TOKEN` | Access Token ของบัญชี X ที่จะโพสต์ |
   | `X_ACCESS_TOKEN_SECRET` | Access Token Secret ที่คู่กับ Access Token |

   กด **Add secret** หลังกรอกแต่ละรายการ แล้วทำซ้ำจนครบทั้งห้าชื่อ ข้อความในช่อง **Name** ต้องตรงตามตาราง รวมตัวพิมพ์ใหญ่และ `_` ส่วนช่อง **Secret** ให้วางเฉพาะค่าจริงที่คัดลอกจากผู้ให้บริการ ไม่ต้องใส่ `NAME=`, ไม่ต้องใส่ `$` และไม่ต้องใส่ quote

   ตัวอย่าง: ในช่อง **Name** พิมพ์ `OPENROUTER_API_KEY` และในช่อง **Secret** วาง API key จาก OpenRouter (อย่าใช้ค่าตัวอย่างหรือส่ง key จริงในแชต)

4. ไปที่แท็บ **Actions** แล้วเลือก workflow **Daily Auto Tweet**
5. เมื่อพร้อมโพสต์ ให้กด **Run workflow** และยืนยันการรัน การสั่งงานนี้จะโพสต์จริงหนึ่งโพสต์ลง X

Workflow นี้อ่านค่าในชื่อเหล่านี้จาก **Repository secrets** โดยตรง จึงไม่ต้องสร้าง Environment หรือเพิ่ม Secrets ในหน้า **Variables** หากเคยสร้างเป็น Environment secret ให้ย้ายมาเป็น Repository secret หรือแก้ workflow ให้ระบุ Environment ด้วย GitHub Actions ใช้ Secrets ที่ตั้งไว้แทนไฟล์ `.env` ซึ่งอยู่ในคอมพิวเตอร์ของคุณ และ workflow นี้ต้องการเพียงสิทธิ์ `contents: read` สำหรับ checkout โค้ด ผู้ที่ clone โปรเจกต์ไปใช้ต้อง push ไปยัง repository ของตน เปิดใช้งาน GitHub Actions และตั้ง Secrets ของตนเองก่อน จึงจะสั่ง Run workflow ได้

GitHub จะไม่แสดงค่าเดิมของ Secret หลังบันทึก หากต้องแก้หรือเปลี่ยน key ให้เปิดหน้า **Actions secrets and variables** แล้วเลือกแก้ไข/ลบ Secret เดิมและเพิ่มค่าใหม่ด้วยชื่อเดิม หาก key ถูกเปิดเผย ให้ revoke หรือ regenerate ที่ OpenRouter/X ก่อน แล้วอัปเดตค่าทั้งใน `.env` และ GitHub Secret ที่เกี่ยวข้อง

## ข้อผิดพลาดที่พบบ่อย

- **OpenRouter HTTP 401**: ตรวจว่า `OPENROUTER_API_KEY` ถูกต้องและยังใช้งานได้
- **OpenRouter HTTP 402/403**: ตรวจเครดิต ยอดใช้จ่าย และข้อจำกัดของบัญชีหรือ API key
- **OpenRouter HTTP 429**: คำขออาจชน rate limit ของ OpenRouter หรือโมเดลฟรีที่ถูกเลือก ลองใหม่ภายหลังหรือตรวจข้อจำกัดของโมเดล
- **OpenRouter returned no text, finish_reason=length**: โมเดลที่ถูกเลือกอาจใช้ token budget ไปกับ reasoning จนไม่มีข้อความโพสต์ ลองใหม่ภายหลัง เพราะ `openrouter/free` อาจเลือกโมเดลฟรีตัวอื่น
- **Generated post is too long**: โปรแกรมขอให้สร้างโพสต์ไม่เกิน 140 ตัวอักษร และจะลองสั่งย่อให้อีกหนึ่งครั้ง หากยังยาวเกินให้ลองรันใหม่หรือเปลี่ยนโมเดลที่ใช้สร้างข้อความ
- **ข้อมูลกฎหมายไม่เป็นปัจจุบัน**: รุ่นฟรีนี้ไม่ได้ค้นเว็บ; โพสต์กฎหมายเป็นข้อมูลทั่วไป ไม่ใช่คำปรึกษา ควรตรวจสอบรายละเอียดล่าสุดจากแหล่งทางการ
- **X HTTP 401/403**: ตรวจว่า credentials ถูกต้อง ยังใช้งานได้ และ Access Token ถูกสร้างหลังตั้งสิทธิ์ **Read and write**
- **Missing required environment variable**: ตรวจชื่อใน `.env` หรือ GitHub Secrets ให้ตรงตามตัวอย่างทุกตัว
- **โพสต์ผิดหัวข้อหรือโพสต์ซ้ำ**: ตรวจวัน/เขตเวลาและ workflow run history ก่อนกด **Run workflow** ซ้ำ เพราะแต่ละ run จะสร้างโพสต์จริง

## ทดสอบตารางหัวข้อ

```powershell
python -m unittest discover -s tests
```
