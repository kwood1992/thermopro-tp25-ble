"""BLE client for TP25 thermometer devices."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Final

from bleak import BleakClient, BleakError

import .constants

def _decode_bcd(pair: bytes) -> int | None:
    """Decode a 2-byte BCD value."""
    if len(pair) != 2:
        return None

    nibbles = (
        (pair[0] >> 4) & 0xF,
        pair[0] & 0xF,
        (pair[1] >> 4) & 0xF,
        pair[1] & 0xF,
    )

    if any(n > 9 for n in nibbles):
        return None

    return nibbles[0] * 1000 + nibbles[1] * 100 + nibbles[2] * 10 + nibbles[3]


def decode_packet(data: bytes) -> tuple[list[int | None], int | None]:
    """Decode a TP25 notification packet."""
    offset = 5
    temps: list[int | None] = []

    for _ in range(constants.NUM_PROBES):
        raw = _decode_bcd(data[offset : offset + 2])
        offset += 2

        if raw is None or raw == 0:
            temps.append(None)
        else:
            temps.append(round(raw / 10))

    battery = data[-3] if len(data) >= 3 else None
    return temps, battery


class TP25Client:
    """Async BLE client for TP25 thermometers."""

    def __init__(self, address: str) -> None:
        """Initialize the client."""
        self._address = address
        self._client = BleakClient(address)
        self._callback: Callable[[list[int | None], int | None], None] | None = None

    def set_callback(
        self,
        callback: Callable[[list[int | None], int | None], None],
    ) -> None:
        """Register a data callback."""
        self._callback = callback

    async def connect(self) -> None:
        """Connect and start notifications."""
        try:
            await self._client.connect(timeout=20.0)
        except BleakError as err:
            msg = "BLE connection failed"
            raise RuntimeError(msg) from err

        for cmd in constants.HANDSHAKE_COMMANDS:
            try:
                await self._client.write_gatt_char(
                    constants.CMD_CHAR_UUID,
                    cmd,
                    response=False,
                )
            except BleakError:
                pass

            await asyncio.sleep(0.05)

        await self._client.start_notify(constants.DATA_CHAR_UUID, self._notification_handler)

    async def disconnect(self) -> None:
        """Disconnect the BLE client."""
        if self._client.is_connected:
            await self._client.disconnect()

    def _notification_handler(self, _: int, data: bytearray) -> None:
        """Handle BLE notifications."""
        if self._callback is None:
            return

        temps, battery = decode_packet(bytes(data))
        self._callback(temps, battery)
