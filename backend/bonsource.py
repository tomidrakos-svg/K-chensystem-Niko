"""Bon-Quellen (Handoff §2 Datenabgriff).

Kapselt WOHER die Rohbons kommen, damit Service und UI davon unberuehrt bleiben.
V1 nutzt `SimulatorSource`. Die reale Anbindung steckt in `PrinterTcpSource` als
dokumentierter Stub.

WICHTIG (Recherche-Korrektur): "Passives Mithoeren" auf TCP 9100 ist in der Praxis
KEIN passiver Wire-Tap — der Pi ist der Drucker-*Endpunkt* (Impersonation) und
muss Epson-APG-Statusabfragen (DLE EOT / DLE ENQ / DLE DC4) beantworten, sonst
haelt die Kasse den "Drucker" fuer offline und sendet nicht. Das kollidiert mit
der Nicht-verhandelbar-Regel "faellt der Pi aus, druckt die Kueche weiter"
(Handoff §1/§2). Robuste Anschluss-Optionen (siehe scripts/kiosk/README.md):
  (a) Kasse druckt den Kuechenbon auf ZWEI Ziele (echter Drucker + Pi),
  (b) SPAN/Mirror-Port am Switch (echtes passives Mithoeren, Pi nie im Pfad),
  (c) Inline-Proxy Kasse->Pi->Drucker (Notloesung, Single Point of Failure).
Mit Port 9100 beginnen; LPD 515 nur falls die konkrete Kasse es nutzt.
"""
from __future__ import annotations

import asyncio
from typing import AsyncIterator, Awaitable, Callable, Optional

from simulator import generate_bon


class BonSource:
    """Interface: liefert Rohbon-Strings, sobald sie eintreffen."""

    async def stream(self) -> AsyncIterator[str]:  # pragma: no cover - Interface
        raise NotImplementedError
        yield ""  # markiert die Methode als AsyncGenerator


class SimulatorSource(BonSource):
    """Erzeugt in Intervallen Zufallsbons. Zusaetzlich kann `inject()` einen Bon
    sofort einspeisen (fuer den Dev-Endpunkt / Tests)."""

    def __init__(self, intervall_sek: float | None = None):
        self.intervall_sek = intervall_sek
        self._queue: asyncio.Queue[str] = asyncio.Queue()

    async def inject(self, roh_text: Optional[str] = None) -> str:
        bon = roh_text if roh_text is not None else generate_bon()
        await self._queue.put(bon)
        return bon

    async def stream(self) -> AsyncIterator[str]:
        auto_task: Optional[asyncio.Task] = None
        if self.intervall_sek:
            auto_task = asyncio.create_task(self._auto_generate())
        try:
            while True:
                yield await self._queue.get()
        finally:
            if auto_task:
                auto_task.cancel()

    async def _auto_generate(self) -> None:
        while True:
            await asyncio.sleep(self.intervall_sek)
            await self._queue.put(generate_bon())


class PrinterTcpSource(BonSource):
    """STUB fuer die reale Anbindung. Lauscht auf TCP 9100, nimmt den ESC/POS-
    Bytestrom entgegen und muss Epson-APG-Statusabfragen beantworten. Wird erst
    nach dem echten Bon-Foto (Format-Eichung) implementiert; hier nur als
    einhaengbarer Platzhalter, damit Service/UI stabil bleiben."""

    def __init__(self, host: str = "0.0.0.0", port: int = 9100,
                 decode: Optional[Callable[[bytes], Awaitable[str]]] = None):
        self.host = host
        self.port = port
        self.decode = decode

    async def stream(self) -> AsyncIterator[str]:  # pragma: no cover - Stub
        raise NotImplementedError(
            "PrinterTcpSource ist bis zur Bon-Foto-Eichung nicht implementiert. "
            "Siehe scripts/kiosk/README.md fuer die Anschluss-Optionen."
        )
        yield ""
