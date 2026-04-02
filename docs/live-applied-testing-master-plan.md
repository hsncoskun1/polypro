# Live Applied Testing Master Plan — POLYPRO

**Hazırlık tarihi:** 2026-04-02
**Sistem durumu:** v0.8.6 main'de, completion_ready=True, 0 blocker
**Yetki:** Gerçek canlı emir — yalnızca kullanıcı onayıyla

---

## 1. Mevcut Sistemin Canlı Test Öncesi Durumu

| Alan | Durum |
|------|-------|
| Backend | Tümü main'de (v0.1.1–v0.8.6) |
| Market discovery | Tamamlandı (v0.2–v0.3) |
| Trading decision / rule governance | Tamamlandı (v0.4) |
| Simulation execution / exit policy / force sell | Tamamlandı (v0.5) |
| Risk engine / control plane / admin reporting | Tamamlandı (v0.6) |
| Live readiness foundation / credentials | Tamamlandı (v0.7.0–v0.7.1) |
| Preflight / outbound guard | Tamamlandı (v0.7.2) |
| Order submission seam | Tamamlandı (v0.7.3) |
| Fill confirmation | Tamamlandı (v0.7.4) |
| Cancel/replace seam | Tamamlandı (v0.7.5) |
| Event stream reconciliation | Tamamlandı (v0.7.6) |
| Execution orchestrator | Tamamlandı (v0.7.7) |
| Exchange client adapter | Tamamlandı (v0.7.8) |
| Production client wiring / dry-run | Tamamlandı (v0.7.9) |
| Concrete integration / operational hardening | Tamamlandı (v0.8.0–v0.8.1) |
| Backend readiness chain | Tamamlandı (v0.8.2) |
| Final validation / non-live modes | Tamamlandı (v0.8.3) |
| Release readiness / live test gate | Tamamlandı (v0.8.4) |
| Frontend/launcher surface wiring | Tamamlandı (v0.8.5) |
| Completion audit | Tamamlandı (v0.8.6) |
| **Test suite** | **1228 passed, 1 skipped, 0 failed** |
| **live_applied_testing_ready** | **False — henüz yetkilendirilmedi** |

### Kesin ön koşullar (canlı teste geçmeden önce)
- [ ] Gerçek API credential'ları `.env` dosyasında doğru yapılandırılmış
- [ ] `explicit_live_enable=True` açıkça set edilmiş
- [ ] `live_test_gate_enabled=True` ve `live_test_gate_passed=True` kullanıcı tarafından onaylanmış
- [ ] Tek market / tek event seçilmiş
- [ ] Maksimum emir boyutu en küçük izin verilen değere set edilmiş
- [ ] Stop koşulları tanımlanmış ve bilinir durumda

---

## 2. Faz Bazlı Canlı Uygulamalı Test Planı

### Phase 1 — Read-Only / No Outbound Verification

**Amaç:** Sistemin canlı ortama bağlanabildiğini, market verisi çekebildiğini doğrulamak. Hiçbir emir gönderilmez.

**Giriş koşulları:**
- Credential'lar yapılandırılmış
- `outbound_allowed=False` (kesin)
- Backend readiness chain: tüm bayraklar True (outbound hariç)

**Yapılacak adımlar:**
1. Discovery trigger'ı başlat, market verisi çekildiğini doğrula
2. Normalization pipeline'ın çıktısını gözlemle
3. Trading decision katmanının kuralları değerlendirdiğini kontrol et
4. Preflight check'in geçtiğini (outbound_allowed=False olarak) doğrula
5. Admin surface'te scheduler ve control plane durumunu gözlemle

**Beklenen sonuç:** Market verisi çekilir, karar katmanı çalışır, sıfır outbound istek.

**Fail criteria:**
- Market verisi gelmiyor
- Discovery pipeline exception veriyor
- Admin surface'te görünmez hata

**Rollback/Stop:** Herhangi bir exception'da scheduler'ı durdur, log incele.

---

### Phase 2 — Dry-Run Verification

**Amaç:** Tüm execution pathinin dry-run modunda uçtan uca çalıştığını doğrulamak. Gerçek emir gönderilmez.

**Giriş koşulları:**
- Phase 1 sorunsuz tamamlandı
- `client_mode=DRY_RUN`
- `outbound_allowed=False`
- `validation_mode=DRY_RUN`

**Yapılacak adımlar:**
1. Trading decision üret
2. Order sizing hesaplamasını gözlemle
3. Risk engine'in emir onayladığını doğrula
4. Execution orchestrator'ın dry-run path'e yönlendirdiğini doğrula
5. Dry-run fill simulation'ın PnL ve balance güncellemelerini doğru ürettiğini kontrol et
6. Position lifecycle kaydını doğrula
7. Admin report'ta dry-run sonuçlarını gözlemle

**Beklenen sonuç:** Tüm execution path çalışır, sıfır gerçek outbound, position ve PnL dry-run kayıtları oluşur.

**Fail criteria:**
- Execution orchestrator yanlış path'e yönleniyor
- PnL / balance hesabı hatalı
- Position lifecycle kaydı oluşmuyor

**Rollback/Stop:** Dry-run modundan çık, log incele.

---

### Phase 3 — Minimal Real Outbound with Strict Guard

**Amaç:** Gerçek outbound bağlantısını doğrulamak. **Tek, en küçük boyutlu, tek market.**

**Giriş koşulları:**
- Phase 2 sorunsuz tamamlandı
- `outbound_allowed=True` — **kullanıcı açıkça onayladı**
- `client_mode=PRODUCTION_WIRING`
- Maksimum emir boyutu en küçük değerde
- Tek market / tek event seçilmiş
- `live_test_gate_enabled=True`, `live_test_gate_passed=True`

**Yapılacak adımlar:**
1. Preflight check'i çalıştır, tüm bayrakları doğrula
2. Outbound guard'ın açık olduğunu teyit et
3. **Kullanıcı manuel onayı alındıktan sonra** tek emir gönder
4. Exchange'in isteği kabul ettiğini doğrula (HTTP 200 / ack)
5. Response classifier'ın doğru sonuç ürettiğini doğrula
6. Beklenmedik durum → anında safe_stop

**Beklenen sonuç:** Emir exchange'e ulaşır, ack alınır, sonraki faza geçiş için temel oluşur.

**Fail criteria:**
- Auth hatası (credential sorunu)
- Exchange reject (rate limit, format hatası)
- Response classifier UNKNOWN döndürüyor
- Connection timeout

**Rollback/Stop:**
- Auth hatası → outbound_allowed=False, credential kontrol et
- Reject → safe_stop aktif et, log incele
- Timeout → retry policy devreye giriyor mu doğrula, timeout sonrası safe_stop

---

### Phase 4 — Submit / Response / Fill Observation

**Amaç:** Emir gönderimi, response classification ve fill confirmation pathinin doğruluğunu doğrulamak.

**Giriş koşulları:**
- Phase 3 başarıyla tamamlandı
- Exchange bağlantısı doğrulandı

**Yapılacak adımlar:**
1. Emir gönder
2. Response'u gözlemle — classifier doğru etiketliyor mu?
3. Fill confirmation event'ini bekle
4. Fill event'in position lifecycle'ı güncellediğini doğrula
5. PnL accounting'in fill sonrası doğru hesaplandığını doğrula
6. Balance summary'nin güncellendiğini doğrula
7. User ve admin surface'te pozisyon görünür mü?

**Beklenen sonuç:** Submit → response → fill → position + PnL + balance güncelleme zinciri eksiksiz çalışır.

**Fail criteria:**
- Fill event gelmiyor
- Position güncellenmiyor
- PnL / balance yanlış
- Surface'te pozisyon görünmüyor

**Rollback/Stop:** Fill gelmediyse belirli süre sonra safe_stop, manuel pozisyon kontrolü.

---

### Phase 5 — Cancel / Replace Observation

**Amaç:** Cancel ve replace emirlerinin doğru işlendiğini doğrulamak.

**Giriş koşulları:**
- Phase 4 sorunsuz tamamlandı
- Açık pozisyon veya bekleyen emir mevcut

**Yapılacak adımlar:**
1. Cancel isteği gönder
2. Cancel response'u gözlemle
3. Position lifecycle'ın iptal durumunu yansıttığını doğrula
4. Replace senaryosu: aynı market'te yeni parametre ile replace isteği gönder
5. Replace response ve sonraki fill'i gözlemle
6. Reconciliation'ın cancel/replace eventlerini doğru işlediğini doğrula

**Beklenen sonuç:** Cancel ve replace emirleri exchange'e ulaşır, position lifecycle doğru güncellenir, reconciliation tutarlı.

**Fail criteria:**
- Cancel reject
- Replace sonrası çift pozisyon kaydı
- Reconciliation uyuşmazlığı

**Rollback/Stop:** Uyuşmazlıkta safe_stop, manuel reconciliation.

---

### Phase 6 — Reconciliation / Accounting / Surface Verification

**Amaç:** Tüm accounting, PnL, balance, claim settlement ve admin reporting'in uçtan uca doğruluğunu doğrulamak.

**Giriş koşulları:**
- Phase 4 ve 5 sorunsuz tamamlandı
- En az bir fill ve bir cancel/replace cycle tamamlandı

**Yapılacak adımlar:**
1. Reconciliation pipeline'ını çalıştır
2. Exchange event stream ile iç kayıtların eşleştiğini doğrula
3. PnL summary doğruluğunu kontrol et
4. Balance summary doğruluğunu kontrol et
5. Claim settlement pipeline'ını kontrol et (eğer settle edilmiş event varsa)
6. Admin report snapshot'ının tüm alanları doğru yansıttığını kontrol et
7. User surface'te görünen verinin backend truth ile tutarlı olduğunu doğrula
8. Launcher surface'in launcher_blocked durumunu doğru gösterdiğini doğrula

**Beklenen sonuç:** Tüm sayısal değerler, event kayıtları ve surface gösterimleri tutarlı ve doğru.

**Fail criteria:**
- Reconciliation uyuşmazlığı
- PnL / balance sapması
- Admin report eksik alan
- Surface ile backend arasında veri farkı

**Rollback/Stop:** Herhangi bir uyuşmazlıkta scheduler'ı durdur, safe_stop aktif et, manuel audit.

---

## 3. İzlenecek Kritik Alanlar

| Alan | İzlenecek |
|------|-----------|
| Preflight / Outbound Guard | outbound_allowed, preflight_passed, guard bypass girişimi yok |
| Submission Outcome | HTTP status, exchange ack, order_id dönüşü |
| Response Classification | Classifier doğru label veriyor mu, UNKNOWN sıfır |
| Fill Confirmation | Fill event geliyor mu, fill_quantity / fill_price doğru |
| Cancel / Replace | Cancel ack, replace sonrası tek pozisyon kaydı |
| Reconciliation | Event stream ile iç kayıt uyumu |
| Accounting / PnL / Balances | Her fill sonrası güncelleniyor, sapma yok |
| Control Plane | scheduler durumu, safe_stop aktif mi, blocked_trades |
| Admin Reporting | Snapshot doğru, operational_alerts görünür |
| Launcher Surface | launcher_blocked doğru yansıtılıyor, visible_panels tutarlı |

---

## 4. Stop / Rollback Koşulları

| Durum | Eylem |
|-------|-------|
| Auth hatası | outbound_allowed=False, credential kontrol, canlıya devam etme |
| Exchange connection timeout | Retry policy çalıştı mı kontrol et, sonra safe_stop |
| Unexpected reject (format/limit) | safe_stop, log incele, Phase 3'e geri dön |
| Fill gelmedi (timeout) | safe_stop, manuel pozisyon kontrolü, exchange UI'dan doğrula |
| Reconciliation uyuşmazlığı | Scheduler durdur, manuel audit, düzeltilmeden Phase 6 tamamlanmaz |
| PnL / balance sapması | safe_stop, accounting katmanını debug et |
| Beklenmeyen exception (herhangi bir fazda) | Anında safe_stop, log kaydet, kullanıcıya bildir |
| Çift pozisyon kaydı | safe_stop, manuel temizleme, sebebi tespit et |

---

## 5. Kullanıcı Checklist'i

### Başlamadan önce
- [ ] `.env` içinde gerçek API credential'ları doğru yapılandırıldı
- [ ] `explicit_live_enable=True` onaylandı
- [ ] `live_test_gate_enabled=True` ve `live_test_gate_passed=True` ayarlandı
- [ ] Test edilecek tek market / tek event belirlendi
- [ ] Maksimum emir boyutu en küçük değere set edildi
- [ ] Admin panel erişimi hazır
- [ ] Stop koşulları bilinir durumda

### Phase 1 (Read-Only)
- [ ] Discovery trigger çalıştı
- [ ] Market verisi geldi
- [ ] Sıfır outbound istek doğrulandı
- [ ] Admin surface normal görünüyor

### Phase 2 (Dry-Run)
- [ ] Tüm execution path dry-run'da çalıştı
- [ ] Dry-run fill simülasyonu doğru
- [ ] PnL / balance dry-run kaydı oluştu
- [ ] Admin report dry-run sonuçlarını gösteriyor

### Phase 3 (İlk Gerçek Outbound)
- [ ] Preflight tüm bayraklar geçti
- [ ] **Manuel onay verildi**
- [ ] Tek emir gönderildi
- [ ] Exchange ack alındı
- [ ] Response classifier doğru sonuç verdi

### Phase 4 (Fill Observation)
- [ ] Fill event alındı
- [ ] Pozisyon güncellendi
- [ ] PnL / balance doğru
- [ ] Surface'te pozisyon görünür

### Phase 5 (Cancel/Replace)
- [ ] Cancel başarılı
- [ ] Replace başarılı, tek pozisyon kaydı
- [ ] Reconciliation tutarlı

### Phase 6 (Final Verification)
- [ ] Reconciliation uyumsuzluk yok
- [ ] Tüm sayısal değerler tutarlı
- [ ] Admin report eksiksiz
- [ ] Surface gösterimi doğru

---

## 6. Son Riskler ve Notlar

| Risk | Açıklama |
|------|----------|
| Credential yapılandırma | Gerçek API key'lerin doğru formatta olması kritik. Yanlış format → Phase 3'te auth hatası |
| Exchange rate limiting | Phase 3/4/5'te çok sık test edilirse rate limit devreye girebilir. Fazlar arası bekleme süresi bırak |
| live_applied_testing_ready | Hâlâ False — bu plan yetkilendirme değil, hazırlık + yürütme rehberidir. Her fazda kullanıcı manuel onayı zorunlu |
| Beklenmeyen exchange davranışı | Exchange API'si değişmiş olabilir. Phase 3'te response format check öncelikli |
| Fail-closed korundu | Tüm fazlarda safe_stop ve outbound guard korumaları aktif kalır |
