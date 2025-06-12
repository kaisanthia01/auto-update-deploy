# ✅ auth_service.py - ระบบจัดการผู้ใช้และการเข้าสู่ระบบ

import sys
import bcrypt  # ใช้สำหรับเข้ารหัสรหัสผ่านแบบปลอดภัย
import json
import os
import logging

# ✅ ตั้งชื่อ logger สำหรับแยก log ของ AuthService โดยเฉพาะ
logger = logging.getLogger("AuthService")

# ✅ กำหนด path สำหรับไฟล์ฐานข้อมูลผู้ใช้

# 🔸 ดึง path ปัจจุบันของไฟล์นี้ (.py)
current_file = os.path.abspath(__file__)

# 🔸 ย้อนขึ้นไป 2 ระดับ (ไปยัง root directory ของโปรเจกต์)
base_dir = os.path.abspath(os.path.join(current_file, "..", ".."))

# 🔸 แสดงผล path ที่ใช้ (เพื่อ debug)
logger.info(f"📂 Base directory: {base_dir}")

# 🔸 กำหนด path ไปยังไฟล์ JSON ที่เก็บข้อมูลผู้ใช้
USER_DB_FILE = os.path.join(base_dir, "data/json/users.json")

# 🔸 แสดงผล path ของไฟล์ฐานข้อมูล
logger.info(f"🗃️ User database file: {USER_DB_FILE}")


# ✅ คลาสจัดการระบบผู้ใช้ (สมัคร, เข้าสู่ระบบ, บันทึกไฟล์)
class AuthService:
    def __init__(self):
        # 🔸 ตรวจสอบว่าไฟล์ฐานข้อมูลผู้ใช้มีอยู่หรือไม่ หากไม่มีก็สร้างใหม่
        if not os.path.exists(USER_DB_FILE):
            self._initialize_user_db()

        # 🔸 โหลดข้อมูลผู้ใช้ทั้งหมดเข้า memory
        self._load_users()

    def _initialize_user_db(self):
        """สร้างฐานข้อมูลผู้ใช้ใหม่แบบว่าง ๆ หากยังไม่มี"""
        os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)  # บันทึก dict ว่างเปล่า

    def _load_users(self):
        """โหลดข้อมูลผู้ใช้จากไฟล์ JSON"""
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                self.users = json.load(f)
        except FileNotFoundError:
            logger.warning("⚠️ ไม่พบไฟล์ฐานข้อมูลผู้ใช้ กำลังสร้างใหม่")
            self._initialize_user_db()
            self.users = {}
        except json.JSONDecodeError:
            logger.error("❌ ไม่สามารถอ่านไฟล์ฐานข้อมูลผู้ใช้ได้ (JSON ผิดรูปแบบ)")
            self.users = {}

    def _save_users(self):
        """บันทึกข้อมูลผู้ใช้ทั้งหมดกลับลงไฟล์ JSON"""
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)

    def hash_password(self, password: str) -> str:
        """เข้ารหัสรหัสผ่านด้วย bcrypt (แบบปลอดภัย)"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str, hashed: str) -> bool:
        """ตรวจสอบว่ารหัสผ่านที่ป้อนมาตรงกับรหัสที่ถูก hash หรือไม่"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def register_user(self, username: str, password: str) -> bool:
        """ลงทะเบียนผู้ใช้ใหม่ พร้อมบันทึกรหัสผ่านที่เข้ารหัสแล้ว"""
        if username in self.users:
            logger.info(f"🔁 มีผู้ใช้ชื่อ '{username}' อยู่แล้ว")
            return False

        hashed = self.hash_password(password)  # เข้ารหัสรหัสผ่านก่อนบันทึก
        self.users[username] = {"password": hashed}
        self._save_users()
        logger.info(f"✅ สมัครสมาชิกใหม่: {username}")
        return True

    def authenticate_user(self, username: str, password: str) -> bool:
        """ตรวจสอบว่าผู้ใช้สามารถเข้าสู่ระบบได้หรือไม่"""
        if username not in self.users:
            logger.warning(f"❌ ไม่พบบัญชีผู้ใช้: {username}")
            return False

        stored_hash = self.users[username]["password"]  # ดึงรหัสผ่านที่ถูก hash
        if self.check_password(password, stored_hash):
            logger.info(f"🔓 เข้าสู่ระบบสำเร็จ: {username}")
            return True
        else:
            logger.warning(f"❌ รหัสผ่านไม่ถูกต้องสำหรับผู้ใช้: {username}")
            return False


# === ตัวอย่างการใช้งาน (สามารถเปิดคอมเมนต์เพื่อลองใช้ได้) ===
# auth = AuthService()
# username = "weather"
# password = "weather"
# success = auth.register_user(username, password)
# if success:
#     print("✅ สมัครสมาชิกสำเร็จ")
# else:
#     print("❌ ชื่อนี้มีอยู่แล้วในระบบ")
#
