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

### Login

Anda dapat menjalankan proses login mandiri dengan opsi `--login` dan parameter terkait. Kredensial juga dapat disimpan dalam berkas konfigurasi JSON dengan opsi `--config`:

```bash
python src/scraper.py --login \
  --url https://contoh.com/login \
  --username nama_pengguna \
  --password kata_sandi \
  --username-selector nama-class \
  --password-selector sandi-class \
  --submit-selector tombol-id
```

Atau simpan kredensial ke dalam berkas `config.json`:

```json
{
  "username": "nama_pengguna",
  "password": "kata_sandi"
}
```

Kemudian jalankan:

```bash
python src/scraper.py --login \
  --url https://contoh.com/login \
  --config config.json \
  --username-selector nama-class \
  --password-selector sandi-class \
  --submit-selector tombol-id
```

Perintah di atas hanya menguji proses login dan akan menampilkan pesan `Login berhasil` atau `Login gagal`.

### Pencarian Lanjutan

Anda dapat menjalankan proses login kemudian langsung melakukan pencarian lanjutan pada Bugzilla dengan opsi `--advanced-search`:

```bash
python src/scraper.py --advanced-search \
  --url https://contoh.com/ \
  --username nama_pengguna \
  --password kata_sandi \
  --username-selector nama-class \
  --password-selector sandi-class \
  --submit-selector tombol-id \
  --csv-output hasil.csv \
  --download-dir unduhan
```

Anda juga dapat menggunakan berkas konfigurasi dengan opsi `--config`.

Skrip akan masuk ke aplikasi kemudian membuka halaman **Advanced Search**,
memilih produk *Company*, memilih seluruh komponen serta semua nilai pada
**Status** dan **Resolution**, lalu menekan tombol **Search**.
Jika opsi `--csv-output` diberikan, hasil pencarian akan disimpan ke berkas
CSV tersebut. Bila tidak, berkas `download.csv` akan dibuat di direktori yang
dapat diatur dengan opsi `--download-dir` (default `.`).


## Docker

Anda dapat menjalankan aplikasi ini di dalam container. Bangun image dengan:

```bash
docker build -t rpabuddy .
```

Kemudian jalankan:

```bash
docker run --rm rpabuddy --url https://contoh.com --selector "h1"
```

Untuk menjalankan proses login di dalam container, Anda perlu me-*mount* berkas
`config.json` karena berkas tersebut tidak termasuk di dalam image:

```bash
  docker run --rm \
    -v "$(pwd)/config.json:/app/config.json" \
    rpabuddy --login \
      --url https://contoh.com/login \
      --config /app/config.json \
      --username-selector nama-class \
      --password-selector sandi-class \
      --submit-selector tombol-id
```

Jika Anda menyimpan hasil dengan opsi `--csv-output`, path yang diberikan
adalah relatif terhadap direktori kerja `/app` di dalam container. *Mount*
direktori pada host agar berkas dapat diakses:

```bash
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  rpabuddy --advanced-search \
    --url https://contoh.com/ \
    --username nama_pengguna \
    --password kata_sandi \
    --username-selector nama-class \
    --password-selector sandi-class \
    --submit-selector tombol-id \
    --csv-output /app/output/hasil.csv
```

Browser Chromium dalam container memerlukan flag `--no-sandbox`. Skrip sudah
menambahkan flag ini secara otomatis, tetapi pastikan Anda tetap
menggunakannya bila menyesuaikan konfigurasi.

## Docker Compose

Jika Anda lebih suka menggunakan Docker Compose, file `docker-compose.yml`
disediakan. Bangun image dan jalankan skrip dengan:

```bash
docker compose build
docker compose run rpabuddy --url https://contoh.com --selector "h1"
```

Untuk login menggunakan Docker Compose, *mount* berkas konfigurasi yang sama
dengan contoh di atas:

```bash
docker compose build
docker compose run -v "$(pwd)/config.json:/app/config.json" rpabuddy --login \
    --url https://contoh.com/login \
    --config /app/config.json \
    --username-selector nama-class \
    --password-selector sandi-class \
    --submit-selector tombol-id
```

Sama halnya, ketika menggunakan opsi `--csv-output`, path tujuan berada di
direktori `/app`. Mount direktori pada host agar hasil CSV dapat tersimpan:

```bash
docker compose run \
  -v "$(pwd)/output:/app/output" \
  rpabuddy --advanced-search \
    --url https://contoh.com/ \
    --username nama_pengguna \
    --password kata_sandi \
    --username-selector nama-class \
    --password-selector sandi-class \
    --submit-selector tombol-id \
    --csv-output /app/output/hasil.csv
```


