import re
import logging

logger = logging.getLogger("CheckCodeTTAA")


class CheckCodeTTAA:
    def decodeTTAA(self, textTTAA):
        # สร้าง dictionary เก็บข้อมูล
        data = {
            "temp": {
                "1050": [],
                "1000": [],
                "925": [],
                "850": [],
                "700": [],
                "500": [],
                "400": [],
                "300": [],
                "250": [],
                "200": [],
                "150": [],
                "100": [],
                "TP": [],
            },
            "wnd": {
                "1050": [],
                "1000": [],
                "925": [],
                "850": [],
                "700": [],
                "500": [],
                "400": [],
                "300": [],
                "250": [],
                "200": [],
                "150": [],
                "100": [],
                "TP": [],
                "MX": [],
            },
        }

        text = textTTAA
        text = text[16:]
        text = text.lstrip()  # ลบช่องว่างด้านหน้า

        # ตรวจสอบข่าว TTBB NIL
        if re.search(r"\bNIL\b", text) == True:
            return data

        # แบ่งชุดข้อมูล temp
        parts = text.split()

        # วนลูปทีละ 3 ตัว
        for i in range(0, len(parts) - 1, 3):  # หยุดก่อนตัวสุดท้ายเพื่อป้องกัน IndexError
            if re.search(r"\b99\d{3}\b", parts[i]):
                data["temp"]["1050"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["1050"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b00\d{3}\b", parts[i]):
                data["temp"]["1000"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["1000"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b92\d{3}\b", parts[i]):
                data["temp"]["925"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["925"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b85\d{3}\b", parts[i]):
                data["temp"]["850"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["850"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b70\d{3}\b", parts[i]):
                data["temp"]["700"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["700"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b50\d{3}\b", parts[i]):
                data["temp"]["500"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["500"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b40\d{3}\b", parts[i]):
                data["temp"]["400"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["400"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b30\d{3}\b", parts[i]):
                data["temp"]["300"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["300"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b25\d{3}\b", parts[i]):
                data["temp"]["250"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["250"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b20\d{3}\b", parts[i]):
                data["temp"]["200"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["200"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b15\d{3}\b", parts[i]):
                data["temp"]["150"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["150"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b10\d{3}\b", parts[i]):
                data["temp"]["100"].append(f"{parts[i]}:{parts[i + 1]}")
                data["wnd"]["100"].append(f"{parts[i]}:{parts[i + 2]}")
            elif re.search(r"\b88\d{3}\b", parts[i]):
                if parts[i] == "88999":
                    data["temp"]["TP"].append(f"{parts[i]}: /////")
                    data["wnd"]["TP"].append(f"{parts[i]}: /////")
                    if re.search(r"\b77\d{3}\b", parts[i + 1]):
                        if parts[i + 1] == "77999":
                            data["wnd"]["MX"].append(f"{parts[i+1]}: /////")
                        else:
                            data["wnd"]["MX"].append(f"{parts[i+1]}:{parts[i + 2]}")
                else:
                    data["temp"]["TP"].append(f"{parts[i]}:{parts[i + 1]}")
                    data["wnd"]["TP"].append(f"{parts[i]}:{parts[i + 2]}")

            elif re.search(r"\b77\d{3}\b", parts[i]):
                if parts[i] == "77999":
                    data["wnd"]["MX"].append(f"{parts[i]}: /////")

                else:
                    data["wnd"]["MX"].append(f"{parts[i]}:{parts[i + 1]}")
                break
            else:
                continue
        """----------------------------------------------------------------------------------------------"""
        # แสดงผลข้อมูล
        # print(data)

        ## Return ผลการตรวจสอบรหัส TTBB
        return data
