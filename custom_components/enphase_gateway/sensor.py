"""Home assistant sensors for the Enphase gateway integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfEnergy,
    UnitOfPower,
)

from .const import DOMAIN,  ICON, CONF_INVERTERS, CONF_ENCHARGE_ENTITIES
from .entity import GatewaySensorBaseEntity
from .coordinator import GatewayReaderUpdateCoordinator


INVERTER_SENSORS = (
    SensorEntityDescription(
        key="lastReportWatts",
        name="Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="lastReportDate",
        name="Last reported",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=True,  # TODO: check feature
    ),
)


PRODUCTION_SENSORS = (
    SensorEntityDescription(
        key="production",
        name="Current Power Production",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        suggested_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        # value_fn=lambda production: production.watts_now,
    ),
    SensorEntityDescription(
        key="daily_production",
        name="Today's Energy Production",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
        # value_fn=lambda production: production.watt_hours_today,
    ),
    SensorEntityDescription(
        key="seven_days_production",
        name="Last Seven Days Energy Production",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        suggested_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="lifetime_production",
        name="Lifetime Energy Production",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
    ),
)


CONSUMPTION_SENSORS = (
    SensorEntityDescription(
        key="consumption",
        name="Current Power Consumption",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        suggested_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        # value_fn=lambda consumption: consumption.watts_now,
    ),
    SensorEntityDescription(
        key="daily_consumption",
        name="Today's Energy Consumption",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
        # value_fn=lambda consumption: consumption.watt_hours_today,
    ),
    SensorEntityDescription(
        key="seven_days_consumption",
        name="Last Seven Days Energy Consumption",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        suggested_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="lifetime_consumption",
        name="Lifetime Energy Consumption",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
    ),
)


AC_BATTERY_SENSORS = (
    SensorEntityDescription(
        key="whNow",
        name="AC-Battery Capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE
    ),
    SensorEntityDescription(
        key="percentFull",
        name="AC-Battery Soc",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY
    ),
    SensorEntityDescription(
        key="wNow",
        name="AC-Battery power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
    SensorEntityDescription(
        key="charge",
        name="AC-Battery charging power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
    SensorEntityDescription(
        key="discharge",
        name="AC-Battery discharging power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
)


ENCHARGE_AGG_SENSORS = (
    SensorEntityDescription(
        key="Enc_max_available_capacity",
        name="ENCHARGE capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE
    ),
    SensorEntityDescription(
        key="ENC_agg_avail_energy",
        name="ENCHARGE energy availiable",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE
    ),
    SensorEntityDescription(
        key="ENC_agg_backup_energy",
        name="ENCHARGE backup capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE
    ),
    SensorEntityDescription(
        key="ENC_agg_soc",
        name="ENCHARGE SoC",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY
    ),
    SensorEntityDescription(
        key="ENC_agg_soh",
        name="ENCHARGE SoH",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


ENCHARGE_AGG_POWER_SENSORS = (
    SensorEntityDescription(
        key="real_power_mw",
        name="ENCHARGE power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
    SensorEntityDescription(
        key="apparent_power_mva",
        name="ENCHARGE apparent power",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.APPARENT_POWER
    ),
    SensorEntityDescription(
        key="charge",
        name="ENCHARGE charging power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
    SensorEntityDescription(
        key="discharge",
        name="ENCHARGE discharging power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
)


ENCHARGE_INVENTORY_SENSORS = (
    SensorEntityDescription(
        key="encharge_capacity",
        name="Capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="calculated_capacity",
        name="Calculated energy availiable",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
    )
)


ENCHARGE_POWER_SENSORS = (
    SensorEntityDescription(
        key="soc",
        name="SoC",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY
    ),
    SensorEntityDescription(
        key="real_power_mw",
        name="Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
    SensorEntityDescription(
        key="apparent_power_mva",
        name="Apparent power",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.APPARENT_POWER
    ),
    SensorEntityDescription(
        key="charge",
        name="Charging power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
    SensorEntityDescription(
        key="discharge",
        name="Discharging power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up envoy sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    options = config_entry.options
    get_inverters = options.get(CONF_INVERTERS, False)
    encharge_device = options.get(CONF_ENCHARGE_ENTITIES, False)
    entities = []

    for sensor_description in (PRODUCTION_SENSORS + CONSUMPTION_SENSORS):
        if getattr(coordinator.data, sensor_description.key):
            entities.append(
                GatewaySensorEntity(coordinator, sensor_description)
            )

    if (data := coordinator.data.inverters_production) and get_inverters:
        if get_inverters == "gateway_sensor":
            entities.extend(
                GatewaySensorInverterEntity(coordinator, description, inverter)
                for description in INVERTER_SENSORS[:1]
                for inverter in data
            )
        if get_inverters == "device":
            entities.extend(
                GatewayInverterEntity(coordinator, description, inverter)
                for description in INVERTER_SENSORS
                for inverter in data
            )

    if coordinator.data.ensemble_secctrl:
        entities.extend(
            EnchargeAggregatedEntity(coordinator, description)
            for description in ENCHARGE_AGG_SENSORS
        )

    if coordinator.data.ensemble_power:
        entities.extend(
            EnchargeAggregatedPowerEntity(coordinator, description)
            for description in ENCHARGE_AGG_POWER_SENSORS
        )

    if data := coordinator.data.encharge_inventory and encharge_device:
        entities.extend(
            EnchargeInventoryEntity(coordinator, description, encharge)
            for description in ENCHARGE_INVENTORY_SENSORS
            for encharge in data
        )

    if data := coordinator.data.encharge_power and encharge_device:
        entities.extend(
            EnchargePowerEntity(coordinator, description, encharge)
            for description in ENCHARGE_POWER_SENSORS
            for encharge in data
        )

    async_add_entities(entities)


class GatewaySystemSensorEntity(GatewaySensorBaseEntity):
    """Gateway system base entity."""

    _attr_icon = ICON

    def __init__(
        self,
        coordinator: GatewayReaderUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize Envoy entity."""
        super().__init__(coordinator, description)
        self._attr_unique_id = f"{self.gateway_serial_num}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.gateway_serial_num))},
            name=self.coordinator.name,
            manufacturer="Enphase",
            model=self.coordinator.gateway_reader.name,
            sw_version=str(self.coordinator.gateway_reader.firmware_version),
        )


class GatewaySensorEntity(GatewaySystemSensorEntity):
    """Gateway sensor entity."""

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)


class GatewaySensorInverterEntity(GatewaySystemSensorEntity):
    """Gateway sensor inverter entity."""

    _attr_icon = ICON

    def __init__(
            self,
            coordinator,
            description,
            serial_number: str,
    ) -> None:
        """Initialize Gateway inverter entity."""
        super().__init__(coordinator, description)
        self._serial_number = serial_number
        self._attr_unique_id = serial_number

    @property
    def name(self):
        """Return the entity name."""
        return f"Inverter {self._serial_number}"
        # return f"{self.entity_description.name} {self._serial_number}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.data.get("inverters_production")
        if data is not None:
            inv = data.get(self._serial_number)
            return inv.get(self.entity_description.key) if inv else None

        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.data.get("inverters_production")
        if data is not None:
            inv = data.get(self._serial_number)
            if last_reported := inv.get("lastReportDate"):
                dt = dt_util.utc_from_timestamp(last_reported)
                return {"last_reported": dt}

        return None


class GatewayInverterEntity(GatewaySensorInverterEntity):
    """Gateway inverter entity.

    Add inverters as seperate devices.

    """

    @property
    def name(self):
        """Return the entity's name."""
        # override the parent inverter class name
        return super(GatewaySensorInverterEntity, self).name
        #return self.entity_description.name

    @property
    def unique_id(self) -> str:
        """Return the entity's unique_id."""
        # TODO: improve unique ids
        # Originally there was only one inverter sensor, so we don't want to
        # break existing installations by changing the unique_id.
        if self.entity_description.key == "lastReportWatts":
            return self._serial_number
        else:
            return f"{self._serial_number}_{self.entity_description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device_info of the device."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._serial_number))},
            name=f"Inverter {self._serial_number}",
            manufacturer="Enphase",
            model="Inverter",
            via_device=(DOMAIN, self.gateway_serial_num),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        _key = self.entity_description.key
        if (data := self.data.get("inverters_production")) is not None:
            value = data.get(self._serial_number, {}).get(_key)
            if value is not None and _key == "lastReportDate":
                return dt_util.utc_from_timestamp(value)
            return value

        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return None


class ACBatteryEntity(GatewaySystemSensorEntity):
    """AC battery entity."""

    @property
    def native_value(self):
        """Return the state of the sensor."""
        storage = self.data.acb_storage
        if self.entity_description.key in {"charge", "discharge"}:
            if (power := storage.get("wNow")) is not None:
                if self.entity_description.key == "charge":
                    return (power * -1) if power < 0 else 0
                elif self.entity_description.key == "discharge":
                    return power if power > 0 else 0
        else:
            return storage.get(self.entity_description.key)

        return None


class EnchargeAggregatedEntity(GatewaySystemSensorEntity):
    """Aggregated Encharge entity."""

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        data = self.data.ensemble_secctrl
        if data is not None:
            return data.get(self.entity_description.key)

        return None


class EnchargeAggregatedPowerEntity(GatewaySystemSensorEntity):
    """Aggregated Encharge entity.

    # FIXME
    At the moment all devices of the power enpoint are aggregated.
    There is no check if the device is an actual encharge device.
    """

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        data = self.data.ensemble_power
        if isinstance(data, list) and len(data) > 0:
            real_power_agg = 0
            apparent_power_agg = 0
            for device in data:
                real_power_agg += device["real_power_mw"]
                apparent_power_agg += device["apparent_power_mva"]

            if self.entity_description.key == "real_power_mw":
                return round(real_power_agg * 0.001)
            elif self.entity_description.key == "apparent_power_mva":
                return round(apparent_power_agg * 0.001)
            elif self.entity_description.key == "charge":
                power = round(real_power_agg * 0.001)
                return (power * -1) if power < 0 else 0
            elif self.entity_description.key == "discharge":
                power = round(real_power_agg * 0.001)
                return power if power > 0 else 0

        return None


class EnchargeEntity(GatewaySensorBaseEntity):
    """Encharge base entity."""

    def __init__(
            self,
            coordinator,
            description,
            serial_number: str,
    ) -> None:
        """Initialize Gateway inverter entity."""
        super().__init__(coordinator, description)
        self._serial_number = serial_number
        self._attr_unique_id = f"{serial_number}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._serial_number))},
            name=f"Encharge {self._serial_number}",
            manufacturer="Enphase",
            model="Encharge",
            via_device=(DOMAIN, self.gateway_serial_num)
        )


class EnchargeInventoryEntity(EnchargeEntity):
    """Ensemble inventory encharge data."""

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        inventory = self.data.encharge_inventory.get(self._serial_number)
        if inventory:
            if self.entity_description.key == "calculated_capacity":
                percentage = inventory.get("percentFull")
                capacity = inventory.get("encharge_capacity")
                if percentage and capacity:
                    return round(capacity * (percentage * 0.01))
            else:
                return inventory.get(self.entity_description.key)

        return None


class EnchargePowerEntity(EnchargeEntity):
    """Ensemble power encharge data."""

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        storage = self.data.encharge_power.get(self._serial_number)
        if storage:
            if self.entity_description.key == "real_power_mw":
                if (real_power := storage.get("real_power_mw")) is not None:
                    return round(real_power * 0.001)

            elif self.entity_description.key == "apparent_power_mva":
                if (va := storage.get("apparent_power_mva")) is not None:
                    return round(va * 0.001)

            elif self.entity_description.key == "charge":
                if (real_power := storage.get("real_power_mw")) is not None:
                    real_power = round(real_power * 0.001)
                    return (real_power * -1) if real_power < 0 else 0

            elif self.entity_description.key == "discharge":
                if (real_power := storage.get("real_power_mw")) is not None:
                    real_power = round(real_power * 0.001)
                    return real_power if real_power > 0 else 0

            else:
                return storage.get(self.entity_description.key)

        return None
