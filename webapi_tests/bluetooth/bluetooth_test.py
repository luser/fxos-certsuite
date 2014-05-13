# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette.wait import Wait


class BluetoothTestCommon(object):
    def is_bt_enabled(self):
        return self.marionette.execute_script("return window.navigator.mozBluetooth.enabled;")

    def set_bt_enabled(self, enable):
        self.marionette.execute_async_script("""
        var enable = arguments[0];
        window.wrappedJSObject.rcvd_enabled_event = false;
        window.wrappedJSObject.rcvd_disabled_event = false;       
        window.wrappedJSObject.rcvd_error = false;
        var mozBT = window.navigator.mozBluetooth;
        
        mozBT.onenabled = function() {
           console.log("Recieved mozBluetooth.onenabled event");
           window.wrappedJSObject.rcvd_enabled_vent = true;
        }

        mozBT.ondisabled = function() {
           console.log("Recieved mozBluetooth.ondisabled event");
           window.wrappedJSObject.rcvd_disabled_event = true;
        }

        if (enable) {
            console.log("Turning on bluetooth via settings");
        } else {
            console.log("Turning off bluetooth via settings");
        }
        var lock = window.navigator.mozSettings.createLock();

        var result = lock.set({
            'bluetooth.enabled': enable
        });

        result.onerror = function() {
            console.log("Failed to changed Bluetooth setting to ON");
            window.wrappedJSObject.rcvd_error = true;
        }
        marionetteScriptFinished(1);
        """, script_args=[enable])

        # wait for enabled/disabled event
        wait = Wait(self.marionette, timeout=30, interval=0.5)
        try:
            if enable:
                wait.until(lambda x: x.execute_script("return window.wrappedJSObject.rcvd_enabled_vent;"))
            else:
                wait.until(lambda x: x.execute_script("return window.wrappedJSObject.rcvd_disabled_event;"))
        except:
            if self.marionette.execute_script("return window.wrappedJSObject.rcvd_error;"):
                self.fail("Error received while changing the bluetooth enabled setting;")
            else:
                if enable:
                    self.fail("Failed to enable bluetooth via mozSettings")
                else:
                    self.fail("Failed to disable bluetooth via mozSettings")

    def get_default_bt_adapter(self):
        self.marionette.execute_async_script("""
        window.wrappedJSObject.rcvd_success = false;
        window.wrappedJSObject.rcvd_error = false;
        window.wrappedJSObject.bt_adapter = null;
        var mozBt = window.navigator.mozBluetooth;
        window.wrappedJSObject.bluetooth_adapter = null;

        console.log("Getting default bluetooth adaptor");
        var request = mozBt.getDefaultAdapter();

        request.onsuccess = function() {
            console.log("mozBluetooth.getDefaultAdapter request success");
            window.wrappedJSObject.rcvd_success = true;
            window.wrappedJSObject.bt_adapter = request.result;
            window.wrappedJSObject.bluetooth_adapter = request.result;       
        }

        request.onerror = function() {
            console.log("mozBluetooth.getDefaultAdapter request returned error");
            window.wrappedJSObject.rcvd_error = true;
        }
        marionetteScriptFinished(1);
        """)

        # wait for adapter to be found
        wait = Wait(self.marionette, timeout=30, interval=0.5)
        try:
            wait.until(lambda x: x.execute_script("return window.wrappedJSObject.rcvd_success"))
        except:
            if self.marionette.execute_script("return window.wrappedJSObject.rcvd_error"):
                self.fail("mozBluetooth.getDefaultAdapter returned error")
            else:
                self.fail("mozBluetooth.getDefaultAdapter failed")

        adapter = self.marionette.execute_script("return window.wrappedJSObject.bt_adapter")
        self.assertNotEqual(adapter, None, "mozBluetooth.getDefaultAdapter returned none")
        return adapter

    def set_bt_discoverable_timeout(self, timeout):
        self.marionette.execute_async_script("""
        window.wrappedJSObject.rcvd_success = false;
        window.wrappedJSObject.rcvd_error = false;
        window.wrappedJSObject.discoverable_timeout = null;
        var mozBt = window.navigator.mozBluetooth;
        var mozBtAdapter = window.wrappedJSObject.bluetooth_adapter;

        console.log("Setting bluetooth discoverable timeout");
        var request = mozBtAdapter.setDiscoverableTimeout(10);

        request.onsuccess = function() {
            console.log("BluetoothAdapter.setDiscoverableTimeout request success");
            window.wrappedJSObject.rcvd_success = true;
            window.wrappedJSObject.discoverable_timeout = mozBtAdapter.discoverableTimeout;
        }

        request.onerror = function() {
            console.log("BluetoothAdapter.setDiscoverableTimeout returned error");
            window.wrappedJSObject.rcvd_error = true;
        }
        marionetteScriptFinished(1);
        """, script_args=[timeout])

        # wait for adapter to be found
        wait = Wait(self.marionette, timeout=30, interval=0.5)
        try:
            wait.until(lambda x: x.execute_script("return window.wrappedJSObject.rcvd_success"))
        except:
            if self.marionette.execute_script("return window.wrappedJSObject.rcvd_error"):
                self.fail("BluetoothAdapter.setDiscoverableTimeout returned error")
            else:
                self.fail("BluetoothAdapter.setDiscoverableTimeout failed")

        set_timeout = self.marionette.execute_script("return window.wrappedJSObject.discoverable_timeout")
        self.assertEqual(set_timeout, timeout, "BluetoothAdapter.discoverableTimeout value was not set correctly")
