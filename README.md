# RPABuddy

Contoh aplikasi scraping informasi berbasis RPA. Skrip ini menggunakan `selenium` untuk membuka halaman web secara otomatis, kemudian mengekstrak informasi yang dibutuhkan.

## Prasyarat

- Python 3.8+
- Driver browser (misalnya `chromedriver` untuk Google Chrome)
- Paket dependensi pada `requirements.txt`

Install dependensi dengan:

```bash
pip install -r requirements.txt
```

## Menjalankan

```
python src/scraper.py --url https://contoh.com --selector "h1"
```

Skrip akan membuka halaman menggunakan Selenium dan menampilkan teks dari elemen yang sesuai dengan selector.

