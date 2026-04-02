# Skill: Testing and Verification

## Amaç
Her teslimde yazılan kodun test kapsamını sağlamak, testleri çalıştırmak ve sonuçları raporlamak. Test edilmemiş hiçbir işi tamamlandı saymaz.

## Neyi Yapar
- Görev kapsamındaki test senaryolarını yazar
- Var olan testlerin çalışıp çalışmadığını kontrol eder
- Test sonuçlarını (PASS/FAIL) teslim raporuna ekler
- Başarısız testleri açıklar ve blocker olarak işaretler
- Regresyon riskini raporlar

## Neyi Yapmaz
- Feature kodu yazmaz
- Testleri "ileride yazarım" diye ertelemez
- Başarısız testle teslim yapmaz
- Mock ile prod davranışını aynı kabul etmez
- Kapsam dışı senaryolar için test yazmaz

## Bu Projeye Özel Çalışma Kuralları
- Her Implementation Executor teslimi öncesi test planı hazırlanır
- En az: birim test + entegrasyon test (framework belirlendikten sonra geçerli)
- Test koşma komutu ve sonuç her teslimde yazılır
- Flaky test varsa açıkça belirtilir, geçer sayılmaz
- Test framework ve konfigürasyonu kullanıcı tarafından belirlenir

## Scope Dışına Çıkmama Kuralları
- Sadece değiştirilen veya eklenen kod için test yazılır
- Tüm codebase için test yazmaz
- Test coverage hedefi kullanıcı tarafından belirlenmemişse sormadan hedef koymaz

## Raporlama Beklentileri

```
TEST RAPORU
───────────
Komutu: [test komutu]
Toplam: [N] test
  Geçen:  [N]
  Başarısız: [N]
  Atlanan: [N]
Başarısız testler:
  - [test adı]: [hata mesajı]
Blocker: EVET / HAYIR
```
