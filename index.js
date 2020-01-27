const AsciiTable = require('ascii-table');
const log = require('single-line-log').stdout;
const BeaconScanner = require('node-beacon-scanner');
const scanner = new BeaconScanner();

const beacons = {};

// Source: https://evothings.com/doc/lib-doc/evothings-libraries_libs_evothings_eddystone_eddystone.js.html#source-line-174
function calculateAccuracy(txPower, rssi) {
    if (!rssi || rssi >= 0 || !txPower) {
        return null
    }
    // Algorithm
    // http://developer.radiusnetworks.com/2014/12/04/fundamentals-of-beacon-ranging.html
    // http://stackoverflow.com/questions/21338031/radius-networks-ibeacon-ranging-fluctuation
    // The beacon distance formula uses txPower at 1 meters, but the Eddystone
    // protocol reports the value at 0 meters. 41dBm is the signal loss that
    // occurs over 1 meter, so we subtract that from the reported txPower.
    var ratio = rssi * 1.0 / (txPower - 41)
    if (ratio < 1.0) {
        return Math.pow(ratio, 10)
    }
    else {
        var accuracy = (0.89976) * Math.pow(ratio, 7.7095) + 0.111
        return accuracy
    }
}

function printBeacons() {
    var table = new AsciiTable();
    table.setHeading('Beacon ID', 'Last RSSI', 'Estimated distance');
    for (b in beacons) {
        let distance = calculateAccuracy(beacons[b].txPower, beacons[b].rssi)
        table.addRow(b, beacons[b].rssi, `${distance.toFixed(2)}m`)
    }
    log(table.toString());
}

// Set an Event handler for becons
scanner.onadvertisement = (ad) => {
    if (ad.id in beacons) {
        beacons[ad.id].rssi = ad.rssi

    } else if (ad.beaconType == "eddystoneUrl") {
        beacons[ad.id] = {
            'txPower': ad.eddystoneUrl.txPower,
            'rssi': ad.rssi
        }
    }
    printBeacons();
};

// Start scanning
scanner.startScan().then(() => {
    console.log('Started to scan.');
}).catch((error) => {
    console.error(error);
});