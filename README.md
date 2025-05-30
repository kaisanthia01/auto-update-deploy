Auto Update System

# 🛠️ Auto Update System for Windows App

ระบบอัปเดตอัตโนมัติสำหรับแอปพลิเคชัน Windows โดยใช้ Python และ GitHub Pages  
รองรับการเช็กเวอร์ชัน ดาวน์โหลด update.zip แตกไฟล์ และเปิดแอปใหม่อัตโนมัติ

## 📁 โครงสร้างโปรเจกต์

auto-update-deploy/<br>
├── version.txt # ไฟล์บอกเวอร์ชันล่าสุด<br>
├── update.zip # แพ็กเกจของโปรแกรมเวอร์ชันใหม่ (.exe + อื่น ๆ)

## 🧠 หลักการทำงาน

1.  รัน `auto_updater.exe`
2.  โหลด `version.txt` จาก GitHub Pages
3.  เทียบเวอร์ชันกับในเครื่อง
4.  หากเวอร์ชันใหม่กว่า:
    - ปิด `app.exe`
    - ดาวน์โหลดและแตก `update.zip`
    - เขียนเวอร์ชันใหม่
    - เปิดแอปอีกครั้ง

## 🐍 ตัวอย่างการตั้งค่า

1. UPDATE_URL = "https://kaisanthia01.github.io/auto-update-deploy/version.txt"
2. ZIP_URL = "https://kaisanthia01.github.io/auto-update-deploy/update.zip"
3. APP_NAME = "app.exe"

## 🏗️ วิธี Build โปรแกรม

pyinstaller auto_updater.py --onefile --name auto_updater
pyinstaller app.py --onefile --name app

## 🚀 วิธี Deploy ผ่าน GitHub Pages

- สร้าง GitHub Repo เช่น `auto-update-deploy`
- วางไฟล์ `version.txt` และ `update.zip` ใน root
- ไปที่ **Settings > Pages** แล้วเลือก Source: `main` branch
- เปิด URL: `https://kaisanthia01.github.io/auto-update-deploy/`

## 🔐 ความปลอดภัยเบื้องต้น

- ตรวจสอบว่า `update.zip` มาจากแหล่งที่ไว้ใจได้
- สามารถเพิ่มระบบ hash verification หรือ digital signature ได้ในอนาคต

## ✅ ตัวอย่าง version.txt

1.0.1

## 📬 ติดต่อ

ผู้พัฒนา: [kaisanthia01](https://github.com/kaisanthia01)  
เปิดรับคำแนะนำและ Pull Requests 👍
