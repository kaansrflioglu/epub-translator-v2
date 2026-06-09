# HTML Text Extractor, Merger & Translator

Choose Language / Dil Seçin:
- [English](#english-html-text-extractor-merger-translator)
- [Türkçe](#türkçe-html-metin-ayıklayıcı-birleştirici-ve-çevirici)

---

# English: HTML Text Extractor, Merger & Translator

This project is a helper Python tool designed in a layered architecture that extracts text from multiple HTML/XHTML/HTM files within a folder, strips HTML tags, merges sentences cleanly, outputs them in order into a single `.txt` file, and then translates these files using a local AI (Ollama).

## Features

1. **Smart Sentence Merging:**
   Automatically detects and merges incorrect line breaks that split sentences in half, which often result from ebook or PDF conversion processes.
2. **Outputs Versioning:**
   Merged files are saved in the `outputs/` directory. If a file already exists in the folder, instead of overwriting it, it appends a counter, e.g., `combined_text_2.txt`, `combined_text_3.txt`.
3. **Layered Architecture:**
   The project is divided into data access, business logic, parsing, and presentation (interface) layers. This makes it extensible and easy to maintain.
4. **UTF-8 Support:**
   Uses UTF-8 encoding for all read and write operations to prevent corruption of special characters.
5. **Local AI Translation:**
   Translates generated text files into any target language using locally running Ollama models (e.g., `llama3`). Large files are smartly split into paragraphs and sections to stay within the model's context window.

---

## Project Structure

The project structure is designed according to a layered architecture:

```text
OEBPS/
│
├── html_source/          <-- [Data Layer Input] Source HTML/XHTML files are placed here
│   ├── text00000.html
│   └── ...
│
├── outputs/              <-- [Data Layer Output] Merged and translated .txt files are saved here
│   ├── combined_text.txt
│   ├── combined_text_translated_english.txt
│   └── ...
│
├── src/                  <-- [Application Logic Directory]
│   ├── __init__.py
│   ├── parser.py         <-- [Parsing Layer] Cleans HTML tags and redundant whitespace
│   ├── file_handler.py   <-- [Data Access Layer] Manages file read/write and listing processes
│   ├── processor.py      <-- [Business Logic Layer] Manages sentence merging and flow control
│   └── translator.py     <-- [Translation Logic Layer] Manages file translation using the Ollama API
│
├── extract_text.py      <-- [Presentation / Entry Point] CLI script starting text extraction
├── translate.py         <-- [Presentation / Entry Point] CLI script starting local AI translation
└── README.md             <-- [Documentation] Project documentation and user guide
```

---

## Installation & Setup

To use the local AI translation feature, you must have **Ollama** installed on your machine and have the corresponding model downloaded.

1. **Ollama Installation:**
   - Download and install the version appropriate for your operating system via the [Ollama Website](https://ollama.com/download).
2. **Required Python Packages:**
   - The translation module requires the `requests` package to communicate with the Ollama API:
     ```bash
     pip install requests
     ```
3. **Download AI Model:**
   - While Ollama is running, open a terminal and download the model you want to use (Default is `llama3`):
     ```bash
     ollama pull llama3
     ```

---

## How to Run

### 1. Text Extraction and Merging

1. Place your source HTML, XHTML, or HTM files in the folder named `html_source` (if the directory does not exist, it will be automatically created on first run).
2. Open a terminal in the root directory where the script is located and run:
   ```bash
   python extract_text.py
   ```
3. Once completed, your merged text file will be ready in the `outputs/` folder.

### 2. Translating with Local AI

1. Run the following command in your terminal:
   ```bash
   python translate.py
   ```
2. The interactive menu will list your TXT files located in the `outputs/` folder. Choose the number of the file you wish to translate.
3. Enter your target language (e.g. `English`, `Turkish`, etc. Default: `English`).
4. Enter the Ollama model you want to use (Default: `llama3`).
5. The translation process will start, and the progress can be tracked in the console.
6. Once the translation is complete, the output file will be saved under the `outputs/` folder with the name `<original_name>_translated_<target_lang>.txt`.

### 3. Genre-Specific Prompt Customization
To improve translation quality for different book types, you can customize or add new prompt templates in `config.json`.
By default, the following genres are available:
- **Fiction / Novel (`fiction`)**: Tailored for literary prose and dialogue authenticity.
- **Fantasy / Sci-Fi (`fantasy_scifi`)**: Keeps invented proper nouns and jargon intact.
- **Mystery / Thriller (`mystery_thriller`)**: Optimizes for suspense and pacing.
- **Non-Fiction (`non_fiction`)**: Keeps argument structures and terms authoritative.
- **Academic / Scientific (`academic`)**: Focuses on precise terminology and formal tone.
- **Children's / YA (`children`)**: Uses clear, age-appropriate language.

You can modify these templates or add your own in `config.json` under `prompt_templates`.


---

# Türkçe: HTML Metin Ayıklayıcı, Birleştirici ve Çevirici

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

### 3. Kitap Türüne Özel Prompt Kişiselleştirme
Farklı kitap türlerinde en iyi çeviri kalitesini elde etmek için `config.json` içerisindeki prompt şablonlarını özelleştirebilir veya yenilerini ekleyebilirsiniz.
Varsayılan olarak aşağıdaki türler mevcuttur:
- **Fiction / Novel (`fiction`)**: Edebi anlatım ve diyalog doğallığına odaklanır.
- **Fantasy / Sci-Fi (`fantasy_scifi`)**: Kurgusal özel adları, terimleri ve büyü isimlerini çevirmeden korur.
- **Mystery / Thriller (`mystery_thriller`)**: Gerilim, tempo ve sürükleyici dile göre optimize edilmiştir.
- **Non-Fiction (`non_fiction`)**: Bilgi verici, otoriter ve argüman odaklı bir dil kullanır.
- **Academic / Scientific (`academic`)**: Resmi akademik jargon, formüller ve atıflar için hassastır.
- **Children's / YA (`children`)**: Yaş grubuna uygun, sıcak ve akıcı bir dil tercih eder.

Bu şablonları `config.json` dosyasındaki `prompt_templates` kısmından değiştirebilir veya kendi şablonlarınızı ekleyebilirsiniz.

