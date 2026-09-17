# Runtime Pack Portable Conformance Profile

## Status

Draft — normative profile for Kristal v5 conformance testing

## Profile identifier

```text
kristal.v5:runtime-pack-portable-conformance@1
```

## Purpose

This profile fixes the byte-level semantics needed to make Runtime Pack acceptance tests **RP-2 through RP-5 executable and portable**. It does not require every production Runtime Pack to use these fixture encodings. A production implementation MAY use another declared storage profile, but it MUST provide equivalent deterministic byte-level rules and vectors before claiming full Runtime Pack compiler conformance for that profile.

The profile covers four reproducibility surfaces:

- deterministic record ordering (`RP-2`);
- deterministic fixed-row group boundaries (`RP-3`);
- deterministic Bloom-filter bytes and false-positive pruning (`RP-4`);
- deterministic 32-bit Roaring portable serialization (`RP-5`).

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative requirements.

---

## 1. Common byte rules

1. Text is UTF-8 without a byte-order mark.
2. Integer fields in binary fixture formats are unsigned unless explicitly stated otherwise.
3. Multi-byte integers in Kristal-defined binary fixture formats are little-endian.
4. SHA-256 digests are lowercase hexadecimal.
5. A JSON Lines payload is a sequence of RFC 8785/JCS canonical JSON objects, each followed by one LF byte (`0x0a`).
6. Source row order MUST NOT affect output when an ordering policy other than `none` is selected.
7. Locale, host collation, filesystem order, CPU count, and thread scheduling MUST NOT affect bytes.

---

## 2. RP-2 — ordered triples fixture

### 2.1 Supported ordering policy

The profile's required RP-2 vector uses:

```text
qid_pid_statement_id_asc
```

Rows MUST contain string fields:

```text
subject
predicate
object
statement_id
```

### 2.2 Comparison

Rows are ordered by this tuple:

1. `subject` UTF-8 bytes;
2. `predicate` UTF-8 bytes;
3. `statement_id` UTF-8 bytes;
4. JCS bytes of the complete row as a final deterministic tie-breaker.

Each tuple component is compared as an unsigned byte sequence. No locale collation or Unicode normalization is applied by this profile.

### 2.3 Output

The ordered fixture payload is `data/triples.jsonl` encoded according to the common JSON Lines rule above.

Two builds given the same row set MUST emit byte-identical output and the published golden SHA-256.

---

## 3. RP-3 — fixed-row grouping fixture

The required profile vector uses:

```text
fixed_rows_100k
```

Let `N` be the total ordered row count. Group `i`, zero-based, is:

```text
start_row = i * 100000
row_count = min(100000, N - start_row)
```

Groups with `row_count <= 0` do not exist.

The portable fixture representation is the JCS object:

```json
{
  "policy": "fixed_rows_100k",
  "row_count": 200005,
  "groups": [
    {"index": 0, "start_row": 0, "row_count": 100000},
    {"index": 1, "start_row": 100000, "row_count": 100000},
    {"index": 2, "start_row": 200000, "row_count": 5}
  ]
}
```

followed by LF and stored as `metadata/row-groups.json` for the TCK fixture.

The fixture representation proves the row-to-group assignment rule without requiring a 200,005-row payload in the repository.

---

## 4. RP-4 — deterministic Bloom filter fixture

### 4.1 Policy

The required vector uses:

```text
kind = bloom
```

and MUST declare:

- `seed`;
- `bits_per_key`;
- `hash_functions`.

### 4.2 Bit count

For `n` keys:

```text
bit_count = max(8, ceil(n * bits_per_key / 8) * 8)
```

The bitset therefore always occupies a whole number of bytes.

### 4.3 Key hashing

For each UTF-8 key, compute:

```text
SHA-256(
  UTF8("kristal-bloom-v1\0") ||
  uint32_le(seed) ||
  uint32_le(key_byte_length) ||
  key_bytes
)
```

Interpret digest bytes `0..7` as unsigned `h1` little-endian and bytes `8..15` as unsigned `h2` little-endian. If `h2 == 0`, use `h2 = 1`.

For `i = 0 .. hash_functions-1`:

```text
position_i = (h1 + i * h2) mod bit_count
```

Bit numbering inside each byte is least-significant-bit first.

Input keys MUST be de-duplicated by exact UTF-8 byte equality and then sorted by UTF-8 bytes before insertion. Duplicate input keys therefore do not alter the filter.

### 4.4 KBF1 serialization

The TCK serializes the filter as:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | ASCII `KBF1` |
| 4 | 1 | format version = `1` |
| 5 | 1 | hash method = `1` (SHA-256 double-hash defined above) |
| 6 | 2 | reserved = `0` |
| 8 | 4 | seed |
| 12 | 4 | bit_count |
| 16 | 2 | hash_functions |
| 18 | 2 | reserved = `0` |
| 20 | 4 | unique key count |
| 24 | variable | bitset bytes |

The file role is `membership_filter`.

### 4.5 Semantic pruning

A Bloom hit is only a prefilter result. Final membership MUST be computed as:

```text
bloom_maybe_contains(key) AND authoritative_store_contains(key)
```

The RP-4 vector includes an absent key that is a deterministic Bloom false positive. The profile requires that its final semantic result be `false`.

---

## 5. RP-5 — deterministic Roaring bitmap fixture

### 5.1 External wire format

The wire format is the standard **32-bit Roaring portable serialization** defined by the Roaring Format Specification. Multi-byte words are little-endian. The TCK uses the standard cookies:

```text
SERIAL_COOKIE_NO_RUNCONTAINER = 12346
SERIAL_COOKIE = 12347
NO_OFFSET_THRESHOLD = 4
```

Reference specification:

```text
https://github.com/RoaringBitmap/RoaringFormatSpec
```

### 5.2 Canonical container selection

Input values are unsigned 32-bit integers, de-duplicated and sorted ascending.

Values are partitioned by their high 16 bits. Containers are emitted in ascending high-key order.

When `run_optimize = false`:

- run containers MUST NOT be emitted;
- cardinality `<= 4096` uses an array container;
- cardinality `> 4096` uses a bitset container;
- serialization MUST use `SERIAL_COOKIE_NO_RUNCONTAINER`.

When `run_optimize = true`:

1. Compute the base container size:
   - array: `2 * cardinality` bytes when cardinality `<= 4096`;
   - bitset: `8192` bytes when cardinality `> 4096`.
2. Compute maximal contiguous runs of low-16 values.
3. Run-container size is `2 + 4 * run_count` bytes.
4. Use a run container only when its size is **strictly smaller** than the base container size. Ties use the base container.
5. If at least one run container is selected, serialize with `SERIAL_COOKIE`; otherwise serialize canonically with `SERIAL_COOKIE_NO_RUNCONTAINER`.

This rule removes implementation-specific run-optimization heuristics from the reproducibility surface.

### 5.3 Standard portable serialization

After canonical container selection, headers, offsets, array containers, bitset containers, and run containers MUST follow the Roaring portable format specification exactly.

The profile intentionally forbids alternate but semantically equivalent Roaring serializations for RP-5 conformance. A conforming build MUST match the published golden bytes.

---

## 6. Conformance fixtures

Golden vectors are published in:

```text
09-test-vectors/runtime-pack/portable-vectors.json
```

The framework TCK MUST verify exact output bytes and SHA-256 for RP-2 through RP-5.

A compiler/verifier implementation claiming this profile MUST independently reproduce those bytes. Merely reading the expected bytes from the vector file is not conformance.

---

## 7. Relationship to Runtime Pack identity

This profile tests byte-producing materializations. The resulting payload hashes MAY participate in `kristal.v5:runtime-pack-id-core@1` through the manifest `files` inventory.

The profile does not change the Runtime Pack identity exclusions defined by `kristal.v5:runtime-pack-id-core@1`.

---

## 8. Portability claim

A PASS of RP-2 through RP-5 under this profile establishes deterministic byte production for these portable fixture surfaces. It does not by itself prove that arbitrary Parquet encoders, third-party Bloom implementations, or every Roaring library emit identical bytes unless they are constrained by this profile or another declared byte-level profile.
