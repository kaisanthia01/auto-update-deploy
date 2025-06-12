import requests
import sys
import re
import datetime
import json
import os
from bs4 import BeautifulSoup

# ตั้งค่าให้รองรับ UTF-8 ใน Windows
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")


class CheckURLSkewT:
    def urlGetContent(self, station_num, time, date):
        # หาตำแหน่งของไฟล์ config.json โดยอิงจากตำแหน่งของสคริปต์
        script_dir = os.path.dirname(os.path.realpath(__file__))  # ตำแหน่งของสคริปต์ที่รัน
        config_file_path = os.path.join(
            script_dir, "..", "json", "config.json"
        )  # สร้างพาธไปยัง config.json

        try:
            # เปิดไฟล์ config.json ในโหมดอ่าน
            with open(config_file_path, "r") as file:
                # โหลดข้อมูลจากไฟล์ JSON ไปยังตัวแปร config_data
                config_data = json.load(file)
        except FileNotFoundError:
            # หากไม่พบไฟล์ config.json จะแสดงข้อความ
            # print("ไม่พบไฟล์ config.json")
            # คืนค่า None เพื่อแจ้งว่าไม่สามารถอ่านไฟล์ได้
            return None

        # ดึงค่า URL จากข้อมูลใน config_data ที่เก็บใน settings
        url = config_data["settings"]["url_skewt"]

        date = date.split("-")
        day = date[2]  # วัน
        try:
            month = int(date[1])  # แปลงเดือนเป็นจำนวนเต็ม
            month = datetime.date(1900, month, 1).strftime("%b")  # แปลงเดือนเป็นชื่อย่อ
        except ValueError:
            # print("เดือนไม่ถูกต้อง")
            return None

        year = date[0]
        year = year[2:4]  # เอาแค่ 2 หลักสุดท้ายของปี
        ythai = str(int(date[0]) + 543)
        time = time[:2]  # ตัดเวลาออกมาใช้แค่ 2 หลักแรก

        # สร้าง URL ของหน้าเว็บที่ต้องการอ่าน
        url = (
            url.replace("{ythai}", ythai)
            .replace("{day}", day)
            .replace("{month}", month)
            .replace("{year}", year)
            .replace("{time}", time)
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # จะเกิด exception หากสถานะไม่ใช่ 200
        except requests.exceptions.RequestException as e:
            # print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
            return None

        if response.status_code == 200:
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)

            lines = text.splitlines()
            filtered_lines = [
                line.strip() for line in lines if not line.strip().startswith("U")
            ]

            final_text = " ".join(filtered_lines)
            text = re.sub(r"\*-*-*", "", final_text)
            text = re.sub(r"\s+", " ", text).strip()
            text = re.sub(r"=", "=\n", text)

            lines = text.splitlines()
            filtered_lines = [
                line.strip()
                for line in lines
                if line.strip().startswith("TTAA") or line.strip().startswith("TTBB")
            ]

            stations = [station_num]
            data = {}

            for station in stations:
                if station not in data:
                    data[station] = {"TTAA": "", "TTBB": ""}

                for line in filtered_lines:
                    parts = line.split()
                    TYPE = parts[0]
                    YYGGId = parts[1]
                    IIiii = parts[2]

                    if f"{TYPE} {YYGGId} {station}" in line:
                        if TYPE == "TTAA":
                            ttaa_start = line.find("TTAA")
                            ttaa_end = line.find("=", ttaa_start)
                            ttaa_data = line[ttaa_start:ttaa_end].strip()
                            data[station]["TTAA"] = ttaa_data

                        elif TYPE == "TTBB":
                            ttbb_start = line.find("TTBB")
                            ttbb_end = line.find("=", ttbb_start)
                            ttbb_data = line[ttbb_start:ttbb_end].strip()
                            data[station]["TTBB"] = ttbb_data

            return data[f"{station_num}"]
        else:
            # print(f"ไม่สามารถดึงข้อมูลจากหน้าเว็บได้ รหัสสถานะ: {response.status_code}")
            return None
