import os
import platform
import psutil
import wmi
import socket
import time
from fpdf import FPDF

def system_info():
    """Sistem bilgilerini gösterir."""
    info = []
    info.append("Sistem Bilgileri:")
    info.append(f"İşletim Sistemi: {platform.system()}")
    info.append(f"Sürüm: {platform.version()}")
    info.append(f"Mimari: {platform.machine()}")
    info.append(f"İşlemci: {platform.processor()}")
    info.append(f"RAM: {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB")
    info.append(f"Sabit Disk Kullanımı: {psutil.disk_usage('/').percent}%")
    return "\n".join(info)

def check_windows_updates():
    """Windows güncellemelerini kontrol eder."""
    c = wmi.WMI()
    updates = c.Win32_QuickFixEngineering()
    update_info = []
    if updates:
        update_info.append("\nYüklü Güncellemeler:")
        for update in updates:
            update_info.append(f"Hotfix ID: {update.HotFixID}, Description: {update.Description}, Install Date: {update.InstalledOn}")
    else:
        update_info.append("\nYüklü güncelleme bulunamadı.")
    return "\n".join(update_info)

def cpu_usage():
    """CPU kullanımını gösterir."""
    return f"\nAnlık CPU Kullanımı: {psutil.cpu_percent(interval=1)}%"

def memory_usage():
    """Bellek kullanımını gösterir."""
    memory = psutil.virtual_memory()
    return (f"\nToplam RAM: {round(memory.total / (1024.0 ** 3), 2)} GB\n"
            f"Kullanılan RAM: {round(memory.used / (1024.0 ** 3), 2)} GB\n"
            f"Boş RAM: {round(memory.available / (1024.0 ** 3), 2)} GB\n"
            f"RAM Kullanımı: {memory.percent}%")

def disk_usage_details():
    """Disk kullanım detaylarını gösterir."""
    details = ["\nDisk Kullanım Detayları:"]
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            details.append(f"Disk Bölümü: {partition.device}")
            details.append(f"Toplam Boyut: {round(usage.total / (1024.0 ** 3), 2)} GB")
            details.append(f"Kullanılan: {round(usage.used / (1024.0 ** 3), 2)} GB")
            details.append(f"Boş: {round(usage.free / (1024.0 ** 3), 2)} GB")
            details.append(f"Kullanım Yüzdesi: {usage.percent}%\n")
        except PermissionError:
            continue
    return "\n".join(details)

def network_info():
    """Ağ bilgilerini ve bağlantı durumunu gösterir."""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    net_io = psutil.net_io_counters()
    return (f"\nAğ Bilgileri:\nHostname: {hostname}\nIP Adresi: {ip_address}\n"
            f"Toplam Gönderilen: {round(net_io.bytes_sent / (1024 ** 2), 2)} MB\n"
            f"Toplam Alınan: {round(net_io.bytes_recv / (1024 ** 2), 2)} MB")

def process_list():
    """Çalışan süreçlerin listesi ve CPU/RAM kullanımını gösterir."""
    processes = ["\nÇalışan Süreçler:"]
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(f"PID: {proc.info['pid']}, İsim: {proc.info['name']}, "
                         f"CPU Kullanımı: {proc.info['cpu_percent']}%, "
                         f"RAM Kullanımı: {proc.info['memory_percent']}%")
    return "\n".join(processes)

def battery_status():
    """Pil durumunu gösterir (dizüstü bilgisayarlar için)."""
    battery = psutil.sensors_battery()
    if battery:
        return (f"\nPil Durumu: {battery.percent}%\n"
                f"Şarj Durumu: {'Şarj Ediliyor' if battery.power_plugged else 'Şarj Edilmiyor'}\n"
                f"Kalan Süre: {round(battery.secsleft / 60)} dakika")
    else:
        return "\nPil bilgisi bulunamadı (Masaüstü bilgisayar)."

def system_uptime():
    """Sistem çalışma süresini gösterir."""
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    return f"\nSistem Çalışma Süresi: {int(uptime_hours)} saat {int(uptime_minutes)} dakika"

def save_to_pdf(content):
    """Verileri PDF olarak kaydeder."""
    pdf = FPDF()
    pdf.add_page()

    # Başlık ekleme
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Sistem Raporu", ln=True, align="C")
    
    # Tarih ekleme
    pdf.set_font('Arial', '', 12)
    current_date = time.strftime("%d/%m/%Y %H:%M:%S")
    pdf.cell(200, 10, txt=f"Tarih: {current_date}", ln=True, align="C")
    
    # Bir boşluk bırakmak
    pdf.ln(10)

    # Unicode karakterleri destekleyen DejaVuSans fontunu ekleyin
    # Fontu doğru şekilde eklemek için .ttf dosyasına ulaşmanız gerekebilir.
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 10)

    for line in content.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output("system_report.pdf")


if __name__ == "__main__":
    # Verilerin toplanması
    report_content = ""
    report_content += system_info()
    report_content += cpu_usage()
    report_content += memory_usage()
    report_content += disk_usage_details()
    report_content += network_info()
    report_content += process_list()
    report_content += battery_status()
    report_content += system_uptime()
    report_content += check_windows_updates()
    
    # Verilerin PDF'e kaydedilmesi
    save_to_pdf(report_content)
    
    print("Sistem raporu 'system_report.pdf' dosyasına kaydedildi.")
