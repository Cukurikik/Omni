package dev.omniframework.interface.android

import android.bluetooth.BluetoothAdapter
import android.bluetooth.le.BluetoothLeScanner
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult

sealed class OmniBleResult {
    data class Success(val deviceAddress: String, val rssi: Int) : OmniBleResult()
    data class Error(val message: String) : OmniBleResult()
}

class OmniBleScanner(private val adapter: BluetoothAdapter?) {
    private val scanner: BluetoothLeScanner? = adapter?.bluetoothLeScanner
    private var scanCallback: ScanCallback? = null

    fun startScan(onResult: (OmniBleResult) -> Unit) {
        if (scanner == null) {
            onResult(OmniBleResult.Error("BLE not supported"))
            return
        }

        scanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                onResult(OmniBleResult.Success(result.device.address, result.rssi))
            }
            override fun onScanFailed(errorCode: Int) {
                onResult(OmniBleResult.Error("Scan failed with code: $errorCode"))
            }
        }
        
        scanner.startScan(scanCallback)
    }

    fun stopScan() {
        scanCallback?.let { scanner?.stopScan(it) }
    }
}
