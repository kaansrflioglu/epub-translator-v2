# HTML Metin Ayıklayıcı, Birleştirici ve Çevirici (HTML Text Extractor, Merger & Translator)

Bu proje, bir klasör içerisindeki çoklu HTML/XHTML/HTM dosyalarının içindeki metinleri HTML etiketlerinden arındırarak, düzgün paragraflarla ve sıralı biçimde tek bir `.txt` dosyasında birleştiren ve ardından bu dosyaları yerel yapay zeka (Ollama) kullanarak çevirebilen yardımcı bir Python aracıdır. Katmanlı mimariye uygun şekilde tasarlanmıştır.

## Özellikler

1. **Akıllı Satır Birleştirme (Smart Sentence Merging):** 
   E-kitap veya PDF dönüştürme işlemlerinden kaynaklanan ve cümleleri ortasından bölen hatalı satır sonlarını (line-breaks) otomatik olarak algılar ve birleştirir.
2. **Çıktı Sürümleme (Outputs Naming):**
   Birleştirilen dosyalar `outputs/` klasörüne kaydedilir. Eğer klasörde halihazırda bir dosya varsa, üzerine yazmak yerine sırasıyla `combined_text_2.txt`, `combined_text_3.txt` şeklinde devam eder.
3. **Katmanlı Mimari:**
   Proje; veri erişimi, iş mantığı, ayrıştırma ve sunum (arayüz) katmanlarına bölünmüştür. Bu sayede genişletilebilir ve bakımı kolaydır.
4. **UTF-8 Desteği:**
   Türkçe ve diğer özel karakterlerin bozulmasını önlemek için tüm okuma ve yazma işlemlerinde UTF-8 kodlaması kullanır.
5. **Yerel Yapay Zeka Çevirisi (Local AI Translation):**
   Oluşturulan metin dosyalarını yerel olarak çalışan Ollama modellerini (örneğin `llama3`) kullanarak istediğiniz herhangi bir dile çevirir. Büyük dosyalar, modelin bağlam penceresini aşmamak için akıllıca paragraflara ve bölümlere ayrılarak çevrilir.

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
├── outputs/              <-- [Veri Katmanı Çıkış] Birleştirilen ve çevrilen .txt dosyaları buraya kaydedilir
│   ├── combined_text.txt
│   ├── combined_text_translated_english.txt
│   └── ...
│
├── src/                  <-- [Uygulama Mantığı Klasörü]
│   ├── __init__.py
│   ├── parser.py         <-- [Ayrıştırma Katmanı] HTML etiketlerini ve özel boşlukları temizler
│   ├── file_handler.py   <-- [Veri Erişim Katmanı] Dosya okuma/yazma ve listeleme işlemlerini yürütür
│   ├── processor.py      <-- [İş Mantığı Katmanı] Cümle birleştirme ve akış kontrolünü yönetir
│   └── translator.py     <-- [Çeviri Mantığı Katmanı] Ollama API'si ile dosya çevirisini yönetir
│
├── extract_text.py      <-- [Sunum / Giriş Noktası] Metin ayıklamayı başlatan CLI betiği
├── translate.py         <-- [Sunum / Giriş Noktası] Yerel yapay zeka çevirisini başlatan CLI betiği
└── README.md             <-- [Dökümantasyon] Proje kullanım dökümanı
```

---

## Kurulum ve Hazırlık

Yerel yapay zeka çevirisini kullanabilmek için bilgisayarınızda **Ollama** kurulu olmalı ve ilgili model indirilmiş olmalıdır.

1. **Ollama Kurulumu:**
   - [Ollama Web Sitesi](https://ollama.com/download) üzerinden işletim sisteminize uygun sürümü indirin ve kurun.
2. **Gerekli Python Paketleri:**
   - Çeviri modülünün Ollama API'si ile haberleşebilmesi için `requests` paketinin kurulu olması gerekir:
     ```bash
     pip install requests
     ```
3. **Yapay Zeka Modeli İndirme:**
   - Ollama çalışır durumdayken terminale şu komutu yazarak kullanmak istediğiniz modeli indirin (Varsayılan olarak `llama3` kullanılmaktadır):
     ```bash
     ollama pull llama3
     ```

---

## Nasıl Çalıştırılır?

### 1. Metin Ayıklama ve Birleştirme

1. Kaynak HTML, XHTML veya HTM dosyalarınızı `html_source` isimli klasörün içine yerleştirin (klasör yoksa ilk çalıştırmada otomatik oluşacaktır).
2. Betiğin bulunduğu kök dizinde bir terminal açın ve aşağıdaki komutu çalıştırın:
   ```bash
   python extract_text.py
   ```
3. İşlem tamamlandığında, `outputs/` klasörü içinde birleştirilmiş metin dosyanız hazır olacaktır.

### 2. Yerel Yapay Zeka ile Çeviri Yapma

1. Terminalde şu komutu çalıştırın:
   ```bash
   python translate.py
   ```
2. Çıkan menüde `outputs/` klasöründeki TXT dosyalarınız listelenecektir. Çevirmek istediğiniz dosyanın numarasını seçin.
3. Çevirmek istediğiniz hedef dili girin (Örn: `English`, `Turkish`, vb. Varsayılan: `English`).
4. Kullanmak istediğiniz Ollama modelini girin (Varsayılan: `llama3`).
5. Çeviri işlemi başlayacak ve ilerleme durumu konsoldan takip edilebilecektir.
6. Çeviri tamamlandığında çıktı dosyanız `outputs/` klasörü altına `<orijinal_isim>_translated_<hedef_dil>.txt` adıyla kaydedilecektir.

