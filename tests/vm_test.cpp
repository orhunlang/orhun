#include "../Memory.h"
#include "../VM.h"

#include <cassert>
#include <string>

int main() {
  // Value boxing / unboxing testi.
  {
    const Value bos = Value::bos();
    const Value sayi = Value::sayi(42.5);
    const Value mantik = Value::mantik(true);
    assert(bos.type == ValueType::BOS);
    assert(sayi.type == ValueType::SAYI && sayi.as.sayi == 42.5);
    assert(mantik.type == ValueType::MANTIK && mantik.as.mantik);
  }

  // GC testi: kok yoksa tum nesneler toplanmali.
  {
    MemoryManager mem;
    for (int i = 0; i < 5000; ++i) {
      (void)mem.allocate<ObjString>(std::to_string(i));
    }
    assert(mem.objectCount() >= 5000);
    mem.collectGarbage([](MemoryManager&) {
      // Bilerek bos root set
    });
    assert(mem.objectCount() == 0);
  }

  // Basit VM smoke testi.
  {
    BytecodeChunk chunk;
    const std::uint16_t c1 = chunk.sabitEkle(SabitDeger(2.0));
    const std::uint16_t c2 = chunk.sabitEkle(SabitDeger(3.0));
    chunk.yazOpCode(OpCode::OP_SABIT, 1);
    chunk.yazU16(c1, 1);
    chunk.yazOpCode(OpCode::OP_SABIT, 1);
    chunk.yazU16(c2, 1);
    chunk.yazOpCode(OpCode::OP_TOPLA, 1);
    chunk.yazOpCode(OpCode::OP_POP, 1);
    chunk.yazOpCode(OpCode::OP_BOS, 1);
    chunk.yazOpCode(OpCode::OP_DON, 1);

    VM vm;
    vm.calistir(chunk);
  }

  return 0;
}
