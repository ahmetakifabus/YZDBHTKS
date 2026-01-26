import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("=" * 60)
    print("      YAPAY ZEKA DESTEKLİ BİTKİ HASTALIĞI TESPİTİ")
    print("=" * 60)

def main():
    while True:
        clear_screen()
        print_banner()
        print("\n[1] Web Dashboard'u Başlat (Flask Browser UI)")
        print("[2] CLI Analiz Sistemini Başlat (Real-time Camera/File)")
        print("[q] Çıkış")
        print("\n" + "-" * 60)
        
        choice = input("\nSeçiminiz: ").strip().lower()

        if choice == '1':
            print("\nWeb Dashboard başlatılıyor...")
            os.system('python app.py')
            break
        elif choice == '2':
            print("\nCLI Analiz Sistemi başlatılıyor...")
            os.system('python YZDBHTS.py')
            break
        elif choice == 'q':
            print("\nÇıkış yapılıyor. İyi günler!")
            break
        else:
            input("\nGecersiz secim! Devam etmek için Enter'a basın.")

if __name__ == "__main__":
    main()
