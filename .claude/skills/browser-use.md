# Skill: Browser Use

## Amaç
Çalışan uygulamanın tarayıcı üzerinde görsel ve işlevsel olarak doğrulanması. Frontend Design ve Testing & Verification skill'lerinin tarayıcı kanadı.

## Neyi Yapar
- Çalışan uygulamayı tarayıcıda açar ve ekran görüntüsü alır
- Tıklama, form doldurma, navigasyon senaryolarını çalıştırır
- Görsel kırılmaları (layout bozulması, overflow, beyaz ekran) tespit eder
- Console hata ve uyarılarını raporlar
- Network isteklerinin başarılı / başarısız olduğunu kontrol eder

## Neyi Yapmaz
- Uygulama kodu değiştirmez
- Test senaryosu yazmaz (Testing & Verification'ın işi)
- Tarayıcı dışı ortam sorunlarını debug etmez
- Kullanıcı onayı olmadan form gönderimi veya veri değişikliği yapmaz (prod ortam riski)
- Otomatik tarama veya crawl yapmaz

## Bu Projeye Özel Çalışma Kuralları
- Her Frontend Design teslimi sonrası doğrulama çalışır
- En az: sayfa yükleniyor mu? Console'da hata var mı? Layout kırık mı?
- Ekran görüntüsü alınır ve raporlanır
- Hata tespit edilirse teslim raporuna blocker olarak işaretlenir
- Sadece localhost / test ortamında çalışır; prod'a otomatik bağlanmaz

## Scope Dışına Çıkmama Kuralları
- End-to-end test suite yazmaz
- Performance profiling yapmaz (task'ta yoksa)
- Accessibility audit yapmaz (task'ta yoksa)

## Raporlama Beklentileri

```
BROWSER USE RAPORU
──────────────────
URL: [test edilen URL]
Ortam: [localhost / test]
Sayfa yüklendi: EVET / HAYIR
Console hataları:
  - [varsa]
Görsel sorunlar:
  - [varsa]
Network hataları:
  - [varsa]
Ekran görüntüsü: ALINDI / ALINAMADI
Genel durum: OK / BLOCKER VAR
```
