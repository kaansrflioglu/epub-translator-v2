# HTML Metin Ayıklayıcı ve Birleştirici (HTML Text Extractor & Merger)

Bu proje, bir klasör içerisindeki çoklu HTML/XHTML/HTM dosyalarının içindeki metinleri HTML etiketlerinden arındırarak, düzgün paragraflarla ve sıralı biçimde tek bir `.txt` dosyasında birleştiren yardımcı bir Python aracıdır. Katmanlı mimariye uygun şekilde tasarlanmıştır.

## Özellikler

1. **Akıllı Satır Birleştirme (Smart Sentence Merging):** 
   E-kitap veya PDF dönüştürme işlemlerinden kaynaklanan ve cümleleri ortasından bölen hatalı satır sonlarını (line-breaks) otomatik olarak algılar ve birleştirir.
2. **Çıktı Sürümleme (Outputs Naming):**
   Birleştirilen dosyalar `outputs/` klasörüne kaydedilir. Eğer klasörde halihazırda bir dosya varsa, üzerine yazmak yerine sırasıyla `combined_text_2.txt`, `combined_text_3.txt` şeklinde devam eder.
3. **Katmanlı Mimari:**
   Proje; veri erişimi, iş mantığı, ayrıştırma ve sunum (arayüz) katmanlarına bölünmüştür. Bu sayede genişletilebilir ve bakımı kolaydır.
4. **UTF-8 Desteği:**
   Türkçe ve diğer özel karakterlerin bozulmasını önlemek için tüm okuma ve yazma işlemlerinde UTF-8 kodlaması kullanır.

---

## Proje Klasör Yapısı

Katmanlı mimariye uygun geliştirilmiş proje yapısı şu şekildedir:

```text
OEBPS/
│
├── html_source/          <-- [Veri Katmanı Giriş] HTML/XHTML kaynak dosyaları buraya konur
│   ├── text00000.html
│   └── ...
│
├── outputs/              <-- [Veri Katmanı Çıkış] Birleştirilen .txt dosyaları buraya kaydedilir
│   ├── combined_text.txt
│   ├── combined_text_2.txt
│   └── ...
│
├── src/                  <-- [Uygulama Mantığı Klasörü]
│   ├── __init__.py
│   ├── parser.py         <-- [Ayrıştırma Katmanı] HTML etiketlerini ve özel boşlukları temizler
│   ├── file_handler.py   <-- [Veri Erişim Katmanı] Dosya okuma/yazma ve isimlendirme işlemlerini yürütür
│   └── processor.py      <-- [İş Mantığı Katmanı] Cümle birleştirme ve akış kontrolünü yönetir
│
├── extract_text.py      <-- [Sunum / Giriş Noktası] CLI arayüzü ve uygulamayı başlatan kök betik
└── README.md             <-- [Dökümantasyon] Proje kullanım dökümanı
```

---

## Nasıl Çalıştırılır?

1. Kaynak HTML, XHTML veya HTM dosyalarınızı `html_source` isimli klasörün içine yerleştirin (klasör yoksa ilk çalıştırmada otomatik oluşacaktır).
2. Betiğin bulunduğu kök dizinde bir terminal açın.
3. Aşağıdaki komutu çalıştırın:

```bash
python extract_text.py
```

İşlem tamamlandığında, `outputs/` klasörü içinde yeni metin dosyanız hazır olacaktır.
