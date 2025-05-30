---

## 🧠 หลักการทำงาน

1. `auto_updater.exe` ทำงาน
2. ไปโหลด `version.txt` จาก GitHub Pages
3. เปรียบเทียบกับ `version.txt` ในเครื่อง
4. ถ้าเวอร์ชันใหม่กว่า:
   - Kill โปรแกรมเก่า (`app.exe`)
   - ดาวน์โหลด `update.zip`
   - แตกไฟล์ทับ
   - เปิด `app.exe` ใหม่

---

## 🐍 ตัวอย่างโค้ด `auto_updater.py`

```python
UPDATE_URL = "https://kaisanthia01.github.io/auto-update-deploy/version.txt"
ZIP_URL = "https://kaisanthia01.github.io/auto-update-deploy/update.zip"
APP_NAME = "app.exe"
```
