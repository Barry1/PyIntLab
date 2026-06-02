# AGENTS.md - Learnings für Grok / AI-Assistenten bei der Optimierung von PyIntLab

## Architecture Decisions

### Interval Representation

- **ScalarInterval**: The core reference implementation. Handles rigorous outward rounding for single intervals.
- **ArrayInterval**: Implemented using a NumPy structured dtype `[("lowerbound", "<f8"), ("upperbound", "<f8")]`. 
  - **Why**: Memory efficiency and potential for vectorization.
  - **Rounding**: Implemented via `RoundingContext` which interfaces with C-level rounding modes (`fesetround` on Unix, `_controlfp` on Windows).
  - **Thread Safety**: `fesetround` is thread-local but may be affected by NumPy's internal multi-threaded BLAS. Rigorous use should be paired with `OMP_NUM_THREADS=1`.

### Linear Algebra

- **Matrix Multiplication**: Implemented in `ArrayInterval.__matmul__`. Currently utilizes a hybrid approach: NumPy for storage and C-level rounding for the summation of interval products.

## Current Status

- `scalar_interval.py`: Stable.
- `array_interval.py`: Implemented basic arithmetic and matrix multiplication with platform-agnostic rounding control.

## Wichtige Prinzipien aus dem Dialog (Stand Mai 2026)

### 1. Korrektheit hat absolute Priorität

- **Outward Rounding** muss bei **jeder** arithmetischen Operation garantiert werden (nicht nur in `__init__` und Inplace-Methoden).
- Jede nicht-inplace Operation (`__add__`, `__mul__`, `__sub__`, `__truediv__`, `log`, `exp`, `__pow__` etc.) muss am Ende `_downward` / `_upward` oder `_orderguaranteed=True` verwenden.
- "Als würden Menschenleben davon abhängen" → Keine Kompromisse bei der mathematischen Korrektheit von Intervall-Arithmetik.
- Fehler bei Rounding können zu falschen Ergebnissen in sensiblen Anwendungen führen.
- Der pylint-Score darf nicht geringer werden.
- pytest muss erfolgreich durchlaufen.

### 2. Performance-Optimierungen (bei erhaltener Semantik)

- Direkter Zugriff auf `_lowerbound` und `_upperbound` in allen Hot-Path-Methoden (statt Properties).
- `_orderguaranteed=True` als schneller, sicherer Konstruktor-Pfad.
- Schnelle Skalar-Pfade: `isinstance(other, ScalarInterval)` zuerst, dann `float(other)`.
- Optimierte `_mulbounds` mit speziellen Vorzeichen-Fällen.
- Inplace-Methoden (`__iadd__` etc.) weiterhin nutzen, wo möglich.

### 3. Vollständigkeit der Klasse

- **Niemals** Methoden weglassen.
- Alle ursprünglichen Methoden müssen in optimierter Form erhalten bleiben.
- Öffentliche API und Semantik müssen 100% identisch bleiben.

### 4. Code-Qualität & Struktur

- Reine Python (keine Cython-Abhängigkeit im Hauptcode, solange nicht explizit gewünscht).
- Statische Helper-Methoden: `_downward`, `_upward`, `_outward`, `_mulbounds`.
- Gute Typ-Hints und Dokumentation beibehalten.
- `__slots__` weiterhin nutzen.
- `__init__` sauber mit `_orderguaranteed`-Flag.

### 5. Arbeitsweise des Assistenten (Lessons Learned)

- Immer den **aktuellen Stand der Datei** im Repository prüfen, bevor Optimierungen vorgeschlagen werden.
- Bei umfangreichen Refactorings die **komplette Datei** liefern, nicht nur Fragmente.
- Bei Veränderungen explizit bestätigen, dass Rounding-Regeln eingehalten werden.
- Wenn Unsicherheit besteht: Nachfragen, bevor Code geliefert wird.
- Entschuldigung und Korrektur bei Fehlern (z.B. fehlende Methoden) sofort und gründlich.

### 6. Nächste Schritte / Empfehlungen

- Nach jedem größeren Refactoring: ASV-Benchmarks laufen lassen (besonders `TimeScalarIntervalLarge`).
- Bei gutem Speedup: Cython-Version als optionale Erweiterung erwägen (`.pyx`).
- Object-Pooling für sehr viele temporäre Intervalle als weiteres Performance-Level.

**Ziel:** Schnellere Interval-Arithmetik ohne Kompromisse bei der mathematischen Korrektheit.

---

_Letztes Update: 02. Juni 2026_
