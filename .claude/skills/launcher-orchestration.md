# Skill: Launcher Orchestration

## Amaç
Projenin çalıştırılma, durdurulma ve ortam kurulum adımlarını yönetmek. Geliştirme ortamı, build ve çalıştırma komutlarının doğruluğunu sağlamak.

## Neyi Yapar
- Projeyi başlatma / durdurma komutlarını yönetir
- Ortam değişkenlerinin eksiksizliğini kontrol eder
- Build ve run sürecini raporlar
- Port çakışması, eksik bağımlılık gibi başlatma hatalarını tespit eder
- Başlatma adımlarını belgelenmiş halde tutar

## Neyi Yapmaz
- Uygulama kodu yazmaz
- Ortam değişkenlerinin içeriğini belirlemez — kullanıcı belirler
- Deployment yapmaz (CI/CD scope'u dışında)
- Servislerin iç mantığına müdahale etmez
- Kullanıcı onayı olmadan script değiştirmez

## Bu Projeye Özel Çalışma Kuralları
- Başlatma komutu her zaman tek bir entry point üzerinden çalışır
- Her ortam (dev / test / prod) için ayrı başlatma talimatı tutulur
- Ortam dosyası (.env gibi) eksikse kullanıcıyı bilgilendirir, kendisi doldurmaz
- Başlatma başarısız olursa hata çıktısı ve olası neden raporlanır

## Scope Dışına Çıkmama Kuralları
- Deployment veya infra provisioning yapmaz
- Yeni servis veya bileşen eklemez
- "Daha iyi bir başlatma sistemi" önerisi yapabilir ama uygulamaz

## Raporlama Beklentileri

```
LAUNCHER RAPORU
───────────────
Ortam: [dev / test / prod]
Komut: [çalıştırılan komut]
Durum: BAŞARILI / BAŞARISIZ
Çıktı özeti: [ilk / son N satır]
Hatalar:
  - [varsa]
Olası neden:
  - [varsa]
```
