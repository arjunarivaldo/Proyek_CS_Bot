## 🧠 Fasha AI — Role-Based Commerce Assistant

Fasha AI adalah sistem **AI Customer Service berbasis Retrieval-Augmented Generation (RAG)** yang dirancang untuk mensimulasikan perilaku customer service manusia dalam konteks e-commerce fashion.

Berbeda dari chatbot berbasis prompt biasa, Fasha AI tidak hanya menjawab, tetapi memahami konteks, niat pengguna, dan batasan data, lalu menyesuaikan perannya secara dinamis.

---

## 🎯 Tujuan Proyek

Proyek ini bertujuan untuk membangun AI yang:

- Memberikan jawaban berbasis data nyata, bukan asumsi
- Tidak mengarang ketika informasi tidak tersedia
- Mampu berperilaku berbeda sesuai konteks interaksi
- Aman untuk digunakan dalam alur bisnis nyata (bukan sekadar demo AI)

---

## 🧩 Konsep Utama

Fasha AI dibangun dengan pendekatan Role-Based AI, di mana satu sistem dapat beroperasi dalam tiga peran berbeda:

### 🧑‍💼 Employee Mode

Berperan sebagai Customer Service internal toko, memprioritaskan produk milik brand sendiri dan memberikan rekomendasi berbasis data produk internal.

### 🤝 Affiliate Mode

Aktif ketika produk yang dicari tidak tersedia secara internal. AI memberikan alternatif dari pihak ketiga tanpa memaksakan penjualan.

### 🎓 Advisor Mode

Berperan sebagai fashion advisor non-komersial, memberikan saran dan edukasi tanpa mengarahkan ke pembelian.

Semua mode ini menggunakan **LLM yang sama**, namun dibedakan melalui **engineering decision, data routing, dan metadata**, bukan dengan mengganti model.

---

## 🧠 Arsitektur Singkat

Sistem ini mengadopsi arsitektur RAG (Retrieval-Augmented Generation):

- Data produk disusun dalam format terstruktur (CSV)
- Data diubah menjadi knowledge chunks dan disimpan sebagai embedding di vector database
- Setiap pertanyaan user melalui tahap:

1. Intent detection
2. Semantic retrieval
3. Role & mode determination
4. Controlled response generation

Keputusan kritikal seperti state order, validasi transaksi, dan perhitungan harga ditangani oleh logika Python, bukan oleh LLM, untuk menghindari hallucination.

---

🧪 Filosofi Engineering

Beberapa prinsip utama yang diterapkan dalam proyek ini:

- Data over prompt — kualitas jawaban ditentukan oleh data dan struktur, bukan prompt panjang
- LLM is not trusted by default — LLM dibatasi perannya dan tidak memegang logika kritikal
- Fail honestly — lebih baik tidak menjawab daripada mengarang
- Pragmatic over fancy — fokus pada sistem yang stabil dan dapat dipercaya

---

🚀 Status Proyek

Proyek ini dikembangkan sebagai bagian dari Final Project Bootcamp NLP, dengan fokus pada:

- Eksplorasi arsitektur AI berbasis data
- Simulasi use-case dunia nyata (customer service & commerce)
- Fondasi yang siap dikembangkan ke skala produksi

---

📌 Catatan

Proyek ini **tidak bertujuan untuk melatih atau fine-tuning model bahasa**, melainkan mengeksplorasi bagaimana **engineering decisions** dapat membuat AI lebih berguna, jujur, dan relevan dalam konteks bisnis.
