"""Spotify multiroom switch."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import RaumfeldApiClient
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Spotify multiroom switch."""
    client: RaumfeldApiClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RaumfeldSpotifyMultiroomSwitch(client, entry.entry_id)])


class RaumfeldSpotifyMultiroomSwitch(SwitchEntity):
    """Control Raumfeld Spotify multiroom mode."""

    _attr_name = "Spotify Multiroom"
    _attr_icon = "mdi:spotify"
    _attr_should_poll = False

    def __init__(self, client: RaumfeldApiClient, entry_id: str) -> None:
        self._client = client
        self._attr_unique_id = f"{entry_id}_spotify_multiroom"
        self._attr_is_on = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._client.register_listener(self._handle_update)
        if self._client.connected:
            await self._client.get_state()

    async def async_will_remove_from_hass(self) -> None:
        self._client.unregister_listener(self._handle_update)
        await super().async_will_remove_from_hass()

    @callback
    def _handle_update(self, data: dict[str, Any]) -> None:
        if data.get("type") != "fullStateUpdate":
            return

        mode = data.get("payload", {}).get("spotifyMode")
        if mode not in ("multiRoom", "singleRoom"):
            return

        self._attr_is_on = mode == "multiRoom"
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._client.set_spotify_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.set_spotify_mode(False)
