# Skill: Repo Discipline

## Amaç
Git geçmişinin temiz, anlamlı ve tutarlı kalmasını sağlamak. Her commit'in neyi neden değiştirdiğini açıkça ifade etmesini güvence altına almak.

## Neyi Yapar
- Commit mesajlarının formatını denetler ve uygular
- Branch adlandırma kurallarını kontrol eder
- Her teslimde commit hash ve mesajını raporlar
- Push sonucunu raporlar
- Beklenmedik dosyaların (örn. .env, node_modules) commit'e girmesini engeller

## Neyi Yapmaz
- Kullanıcı onayı olmadan force push yapmaz
- Commit geçmişini yeniden yazmaz (rebase, amend) — onay olmadan
- Branch silmez
- Merge stratejisi belirlemez

## Bu Projeye Özel Çalışma Kuralları
- Commit mesaj formatı: `[tip]: [kısa açıklama]` (feat, fix, chore, docs, test, refactor)
- Her commit tek bir mantıksal değişiklik içerir
- Commit öncesi `.gitignore` kontrol edilir
- Push öncesi kullanıcıya özet sunulur (otopush istisna değil, kuraldır)

## Scope Dışına Çıkmama Kuralları
- CI/CD pipeline yönetimi yapmaz
- Release tag oluşturmaz (kullanıcı talebi olmadan)
- Branch stratejisi belirlemez

## Raporlama Beklentileri

```
REPO RAPORU
───────────
Branch: [branch adı]
Commit: [hash] — [mesaj]
Push: OK / FAIL / bekliyor
Staged dosyalar:
  - [dosya]
Riskler:
  - [örn. hassas dosya commit'e girdi mi?]
```
