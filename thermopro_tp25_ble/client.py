"""BLE hub for ThermoPro TP25 thermometer devices."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from bleak import BleakClient, BleakError

from .constants import HANDSHAKE_COMMANDS, CMD_CHAR_UUID, DATA_CHAR_UUID, NUM_PROBES

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class ProbeReading:
    probe_id: str
    temperature: int | None


@dataclass(frozen=True)
class BatteryReading:
    level: int | None

class ProbeInfo:
    """Probes info."""

    def __init__(self, probe_id: str, name: str, hub: ThermoProTP25):
        """Init probe."""
        self.probe_id = probe_id
        self.name = name
        self.hub = hub

class BatteryInfo:
    """Battery info."""

    def __init__(self, battery_id: str, name: str, hub: ThermoProTP25):
        """Init battery."""
        self.battery_id = battery_id
        self.name = name
        self.hub = hub

def _decode_bcd(pair: bytes) -> int | None:
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
    offset = 5
    temps: list[int | None] = []

    for _ in range(NUM_PROBES):
        raw = _decode_bcd(data[offset : offset + 2])
        offset += 2
        temps.append(round(raw / 10) if raw else None)

    battery = data[-3] if len(data) >= 3 else None
    return temps, battery

class ThermoProTP25:
    """Async BLE client for ThermoPro TP25 BBQ Thermometers."""

    def __init__(self, address: str, reconnect_interval: float = 5.0) -> None:
        self.address = address
        self._client = BleakClient(
            address,
            disconnected_callback = self._disconnected_callback,
        )
        self._connected = False
        self._reconnect_interval = reconnect_interval
        self._retry_task: asyncio.Task | None = None
        self.probes: list[ProbeInfo] = [
            ProbeInfo(
                probe_id=f"{address}_probe_{i}",
                name=f"Probe {i + 1}",
                hub=self
            )
            for i in range(NUM_PROBES)
        ]

        self.battery = BatteryInfo(
            battery_id=f"{address}_battery",
            name="Battery",
            hub=self
        )
        self._callbacks = set()

    @property
    def device_id(self) -> str:
        """Use the MAC address for the device ID"""
        return self.address
    
    @property
    def connected(self) -> bool:
        """Return device connection status."""
        return self._connected

    def _disconnected_callback(self, client: BleakClient) -> None:
        """Set device connected state to False to handle in HA."""
        if self._connected:
            _LOGGER.info(f"ThermoPro TP25 {self.address} disconnected")
            self._connected = False
    
            for callback in set(self._callbacks):
                callback(self._connected, None, None)
    
            if not self._retry_task or self._retry_task.done():
                self._retry_task = asyncio.create_task(self._retry_connect_loop())

    def register_callback(
        self,
        callback: Callable[[bool, list[ProbeReading], BatteryReading], None],
    ) -> Callable[[], None]:
        """Register update callback."""
        self._callbacks.add(callback)

    def remove_callback(
        self,
        callback: Callable[[bool, list[ProbeReading], BatteryReading], None],
    ) -> None:
        """Register update callback."""
        self._callbacks.discard(callback)

    def _notification_handler(self, _: int, data: bytearray) -> None:
        temps, battery_level = decode_packet(bytes(data))

        probe_readings = [
            ProbeReading(info.probe_id, temp)
            for info, temp in zip(self.probes, temps, strict=False)
        ]

        battery_reading = BatteryReading(battery_level)

        for callback in set(self._callbacks):
            callback(self._connected, probe_readings, battery_reading)

    async def connect(self) -> None:
        """Connect and start notifications."""
        try:
            await self._client.connect(timeout=20.0)
            self._connected = True
        except Exception:
            self._connected = False
            raise

        for cmd in HANDSHAKE_COMMANDS:
            try:
                await self._client.write_gatt_char(
                    CMD_CHAR_UUID,
                    cmd,
                    response=False,
                )
            except BleakError:
                pass

            await asyncio.sleep(0.05)

        await self._client.start_notify(DATA_CHAR_UUID, self._notification_handler)

    async def disconnect(self) -> None:
        """Disconnect the BLE client."""
        if self._client.is_connected:
            await self._client.disconnect()

    async def _retry_connect_loop(self) -> None:
        """Automatically retry connecting."""
        while not self._connected:
            try:
                await self.connect()
                _LOGGER.info(f"Reconnected to ThermoPro TP25 device {self.address}")
            except (BleakError, asyncio.TimeoutError) as ex:
                await asyncio.sleep(self._reconnect_interval)
