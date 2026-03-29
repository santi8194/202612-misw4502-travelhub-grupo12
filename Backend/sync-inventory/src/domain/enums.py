from enum import Enum


class ResourceType(str, Enum):
    PROPERTY = "property"
    ROOM_TYPE = "room-type"
    AVAILABILITY = "availability"
    RATE = "rate"

    @property
    def inventory_sync_path(self) -> str:
        mapping = {
            ResourceType.PROPERTY: "/inventory/sync/property",
            ResourceType.ROOM_TYPE: "/inventory/sync/room-type",
            ResourceType.AVAILABILITY: "/inventory/sync/availability",
            ResourceType.RATE: "/inventory/sync/rate",
        }
        return mapping[self]
