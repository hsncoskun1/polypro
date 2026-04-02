# Skill: Documentation Ledger

## Amaç
Projeye ait kararların, değişikliklerin ve teknik bilginin yaşayan bir ledger'da tutulmasını sağlamak. Geliştirici belleği değil, denetlenebilir kayıt sistemi.

## Neyi Yapar
- Her teslimde önemli kararları changelog formatında kaydeder
- Mimari kararları (ADR) kayıt altına alır
- Kurulum ve çalıştırma talimatlarını güncel tutar
- Yeniden üretilebilirlik için kritik bilgiyi yazar
- Geçici çözümleri (workaround) açıkça işaretler

## Neyi Yapmaz
- Kullanıcı onayı olmadan API spec veya sözleşme yazmaz
- Kodu dökümante etmez (kod kendi konuşur ilkesi)
- Speculative/gelecek planı yazmaz
- Teslim edilmemiş özelliği dökümante etmez

## Bu Projeye Özel Çalışma Kuralları
- CHANGELOG.md projenin kökünde tutulur
- Her teslim sonrası CHANGELOG.md güncellenir
- Format: `## [tarih] [görev adı]` başlığı altında madde listesi
- Workaround varsa: `> [!WARNING] Geçici çözüm: ...` formatıyla işaretlenir
- ADR gerektiren kararlar `docs/decisions/` altında tutulur (klasör kullanıcı onayıyla açılır)

## Scope Dışına Çıkmama Kuralları
- Sadece gerçekleşen değişiklikleri yazar
- "Yapılacaklar" veya "plan" yazmaz (bu task tracker'ın işi)
- Kod örnekleri dokümanı şişirirse link verir, kopyalamaz

## Raporlama Beklentileri

```
DOKÜMANTASYON RAPORU
────────────────────
Güncellenen dosyalar:
  - [dosya]: [ne eklendi / değişti]
ADR oluşturuldu: EVET / HAYIR
Workaround işaretlendi: EVET / HAYIR
```
