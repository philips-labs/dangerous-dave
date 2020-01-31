const AsciiTable = require('ascii-table');
const hex2ascii = require('hex2ascii');
const log = require('single-line-log').stdout;
const trilateration = require('node-trilateration');
const BeaconScanner = require('node-beacon-scanner');
const CircularBuffer = require("circular-buffer");
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
    table.setHeading('Beacon ID', 'Instance', 'Average RSSI', 'RSSI', 'TxPower', 'Estimated distance');
    if (Object.keys(beacons).length >= 3) {
        let trilaterationBeacons = [];
        for (b in beacons) {
            if (beacons[b].txPower === 0) continue;
            let rssiArray = beacons[b].rssi.toarray();
            let averageRssi = rssiArray.reduce((a, b) => a + b, 0) / rssiArray.length;
            let distance = calculateAccuracy(beacons[b].txPower, averageRssi)
            if (beacons[b].instance.startsWith('(')) {
                let beaconXY = beacons[b].instance.substr(1, beacons[b].instance.length - 2).split(',');
                // console.log(beaconXY)
                trilaterationBeacons.push({
                    x: parseFloat(beaconXY[0]),
                    y: parseFloat(beaconXY[1]),
                    distance: distance
                });
            }
            table.addRow(b, beacons[b].instance, `${averageRssi.toFixed(2)}`, beacons[b].rssi.toarray(), beacons[b].txPower, `${distance.toFixed(2)}m`)
        }
        let logLine = table.toString();
        // console.log(trilaterationBeacons);
        let pos = trilateration.calculate(trilaterationBeacons);
        logLine += `\nMy Position: ${pos.x}, ${pos.y}`;
        log(logLine);
    } else {
        console.log(`Not enough beacons!`);
    }
}

// Set an Event handler for becons
scanner.onadvertisement = (ad) => {
    // Only pick up the 
    if (!(ad.id in beacons)) {
        beacons[ad.id] = {
            'rssi': new CircularBuffer(10),
            'txPower': 0,
            'instance': '??'
        };
    }
    if (ad.beaconType == "eddystoneUrl") {
        beacons[ad.id].txPower = ad.eddystoneUrl.txPower;
        beacons[ad.id].rssi.push(ad.rssi);
    } else
        if (ad.beaconType == "eddystoneUid") {
            // if (!ad.eddystoneUid.instance.startsWith("0028")) return;
            // console.log(ad)
            // if (!(ad.id in beacons)) {
            //     beacons[ad.id] = { 'rssi': new CircularBuffer(10) };
            // }
            beacons[ad.id].txPower = ad.eddystoneUid.txPower;
            beacons[ad.id].rssi.push(ad.rssi);
            beacons[ad.id].instance = hex2ascii(ad.eddystoneUid.instance);
        } else {
            return;
        }
    printBeacons();
};

// Start scanning
scanner.startScan().then(() => {
    console.log('Started to scan.');
}).catch((error) => {
    console.error(error);
});

// var s = '0028362C3029';
// console.log(hex2ascii(s));