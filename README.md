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


## Docker

Anda dapat menjalankan aplikasi ini di dalam container. Bangun image dengan:

```bash
docker build -t rpabuddy .
```

Kemudian jalankan:

```bash
docker run --rm rpabuddy --url https://contoh.com --selector "h1"
```

## Docker Compose

Jika Anda lebih suka menggunakan Docker Compose, file `docker-compose.yml`
disediakan. Bangun image dan jalankan skrip dengan:

```bash
docker compose build
docker compose run rpabuddy --url https://contoh.com --selector "h1"
```


