"""Print batch/serial numbers for connected PicoLog TC-08 devices."""

import ctypes

from picosdk.functions import assert_pico2000_ok
from picosdk.usbtc08 import usbtc08 as tc08


# Line 4 is USBTC08LINE_BATCH_AND_SERIAL in the Pico TC-08 programmer guide.
USBTC08LINE_BATCH_AND_SERIAL = 4


def get_tc08_sn(handle: int) -> str:
    """Return the batch/serial string for an opened TC-08 device handle."""
    buffer = ctypes.create_string_buffer(80)
    status = tc08.usb_tc08_get_unit_info2(
        handle,
        ctypes.byref(buffer),
        ctypes.sizeof(buffer),
        USBTC08LINE_BATCH_AND_SERIAL,
    )
    assert_pico2000_ok(status)
    return buffer.value.decode("ascii", errors="replace").strip()


def main() -> None:
    """Open each available TC-08, print its serial number, then close it."""
    handles = []

    try:
        # Keep handles open while scanning so the same device is not reopened.
        while True:
            handle = tc08.usb_tc08_open_unit()
            if handle <= 0:
                break

            handles.append(handle)
            print(f"TC-08 #{len(handles)}: {get_tc08_sn(handle)}")

        if not handles:
            print("No TC-08 loggers found.")

    finally:
        # Close every device opened by this script before exiting.
        for handle in handles:
            status = tc08.usb_tc08_close_unit(handle)
            assert_pico2000_ok(status)


if __name__ == "__main__":
    main()
