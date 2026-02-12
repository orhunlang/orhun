#pragma once

#include "AST.h"

#include <functional>
#include <map>
#include <memory>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>

// Orhun çalışma zamanı değeri.
// v0.6: sayı(int/double), metin, liste ve sözlük desteklenir.
struct OrhunDegeri {
  // Recursive variant problemi için konteynerler shared_ptr ile taşınır.
  using ListeVeri = std::vector<OrhunDegeri>;
  using SozlukVeri = std::map<std::string, OrhunDegeri>;
  using ListeTipi = std::shared_ptr<ListeVeri>;
  using SozlukTipi = std::shared_ptr<SozlukVeri>;

  std::variant<int, double, std::string, ListeTipi, SozlukTipi> veri;

  OrhunDegeri() : veri(0) {}
  explicit OrhunDegeri(int v) : veri(v) {}
  explicit OrhunDegeri(double v) : veri(v) {}
  explicit OrhunDegeri(std::string v) : veri(std::move(v)) {}
  explicit OrhunDegeri(const char *v) : veri(std::string(v)) {}
  explicit OrhunDegeri(ListeTipi v)
      : veri(v ? std::move(v) : std::make_shared<ListeVeri>()) {}
  explicit OrhunDegeri(SozlukTipi v)
      : veri(v ? std::move(v) : std::make_shared<SozlukVeri>()) {}
  explicit OrhunDegeri(ListeVeri v)
      : veri(std::make_shared<ListeVeri>(std::move(v))) {}
  explicit OrhunDegeri(SozlukVeri v)
      : veri(std::make_shared<SozlukVeri>(std::move(v))) {}

  bool operator==(const OrhunDegeri &diger) const {
    if (veri.index() != diger.veri.index()) {
      return false;
    }

    if (const auto *v = std::get_if<int>(&veri)) {
      return *v == std::get<int>(diger.veri);
    }
    if (const auto *v = std::get_if<double>(&veri)) {
      return *v == std::get<double>(diger.veri);
    }
    if (const auto *v = std::get_if<std::string>(&veri)) {
      return *v == std::get<std::string>(diger.veri);
    }
    if (const auto *v = std::get_if<ListeTipi>(&veri)) {
      const auto &digerListe = std::get<ListeTipi>(diger.veri);
      if (!(*v) || !digerListe) {
        return !(*v) && !digerListe;
      }
      return **v == *digerListe;
    }

    const auto *v = std::get_if<SozlukTipi>(&veri);
    const auto &digerSozluk = std::get<SozlukTipi>(diger.veri);
    if (!(*v) || !digerSozluk) {
      return !(*v) && !digerSozluk;
    }
    return **v == *digerSozluk;
  }
};

class Interpreter {
public:
  Interpreter();

  // Program veya herhangi bir komut düğümünü çalıştırır.
  void calistir(const ASTNode *dugum);

private:
  using DegiskenTablosu = std::unordered_map<std::string, OrhunDegeri>;
  using GomuluIslev =
      std::function<OrhunDegeri(const std::vector<OrhunDegeri> &, std::size_t)>;

  DegiskenTablosu globalHafiza_;
  std::vector<DegiskenTablosu> yerelKapsamYigini_;

  std::unordered_map<std::string, const IslevTanimNode *> islevTablosu_;
  std::unordered_map<std::string, GomuluIslev> gomuluIslevler_;
  std::vector<std::unique_ptr<ProgramNode>> yukluModuller_;

  void gomuluIslevleriYukle();
  void yerlesikModulleriYukle();

  void calistirBlock(const BlockNode *block);
  void calistirAtama(const AtamaNode *dugum);
  void calistirYazdir(const YazdirNode *dugum);
  void calistirEger(const EgerNode *dugum);
  void calistirTekrarla(const TekrarlaNode *dugum);
  void calistirSurece(const SureceNode *dugum);
  void calistirIslevTanim(const IslevTanimNode *dugum);
  void calistirDondur(const DondurNode *dugum);
  void calistirDahilEt(const DahilEtNode *dugum);
  void calistirIfadeKomut(const IfadeKomutNode *dugum);

  OrhunDegeri ifadeHesapla(const ASTNode *dugum);
  OrhunDegeri tekliIslemHesapla(const TekliIslemNode *dugum);
  OrhunDegeri ikiliIslemHesapla(const IkiliIslemNode *dugum);
  OrhunDegeri listeIslemi(const OrhunDegeri &sol, const OrhunDegeri &sag,
                          const std::string &op, std::size_t satir);
  OrhunDegeri sorCalistir(const SorNode *dugum);
  OrhunDegeri listeOlustur(const ListeNode *dugum);
  OrhunDegeri sozlukOlustur(const SozlukNode *dugum);
  OrhunDegeri indeksErisim(const IndeksErisimNode *dugum);
  OrhunDegeri alanErisim(const AlanErisimNode *dugum);
  OrhunDegeri islevCagir(const IslevCagriNode *dugum);
  OrhunDegeri dahilEtDegerlendir(const DahilEtNode *dugum);
  OrhunDegeri islevCagirAdaGore(const std::string &ad,
                                const std::vector<OrhunDegeri> &argumanlar,
                                std::size_t satir);
  OrhunDegeri nesneMetoduCagir(const OrhunDegeri &hedef,
                               const std::string &metodAdi,
                               const std::vector<OrhunDegeri> &argumanlar,
                               std::size_t satir);
  OrhunDegeri noktaYoluDegeri(const std::string &yol, std::size_t satir) const;
  bool islevReferansiCoz(const OrhunDegeri &deger,
                         std::string &gercekAd) const;

  DegiskenTablosu &aktifKapsam();
  const OrhunDegeri &degiskenBul(const std::string &ad,
                                 std::size_t satir) const;

  bool dogruMu(const OrhunDegeri &deger) const;
  bool esittir(const OrhunDegeri &sol, const OrhunDegeri &sag) const;
  std::string metneCevir(const OrhunDegeri &deger) const;

  // Sayı yardımcıları: int/double birlikte işlenir.
  bool sayiMi(const OrhunDegeri &deger) const;
  double sayiDegeri(const OrhunDegeri &deger, std::size_t satir,
                    const std::string &baglam) const;
  bool tamSayiMi(const OrhunDegeri &deger) const;
  bool tamSayiMi(double deger) const;
  std::size_t listeIndeksiCevir(const OrhunDegeri &deger, std::size_t satir,
                                const std::string &baglam) const;

  [[noreturn]] void hataFirlat(std::size_t satir,
                               const std::string &mesaj) const;
};
