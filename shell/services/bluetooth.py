from fabric.bluetooth import BluetoothClient, BluetoothDevice
from fabric.core import Property
from util.singleton import Singleton


class BluetoothService(BluetoothClient, Singleton):
    @Property(bool, default_value=False, flags="readable")
    def is_device_connected(self) -> bool:
        return self.connected_devices != []

    @Property(BluetoothDevice | None, flags="readable")
    def current_device(self) -> BluetoothDevice | None:
        if self.is_device_connected:
            return self.connected_devices[0]
        else:
            return None
