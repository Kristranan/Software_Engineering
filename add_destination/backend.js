const express = require('express');
const app = express();
app.use(express.json());

app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});
// In-Memory Database for registered clinics
const clinics = [
    { clinic_id: 'CLK-001', clinic_name: 'Salaya Health Center', district: 'Phutthamonthon', province: 'Nakhon Pathom', is_registered: true },
    { clinic_id: 'CLK-002', clinic_name: 'Nakhon Pathom Rural Clinic', district: 'Bang Len', province: 'Nakhon Pathom', is_registered: true },
    { clinic_id: 'CLK-003', clinic_name: 'Unregistered Test Site', district: 'Muang', province: 'Nakhon Pathom', is_registered: false }
];

// In-Memory Database for shipments
const shipments = [
    { shipment_id: 'SHP-1001', vaccine_type: 'Measles', destination_clinic_id: null, status: 'DRAFT' }
];

// Endpoint 1: Get registered clinics
app.get('/api/clinics/registered', (req, res) => {
    const registeredOnly = clinics.filter(c => c.is_registered);
    res.json(registeredOnly);
});

// Endpoint 2: Assign destination (Story 002-1)
app.post('/api/shipments/assign-destination', (req, res) => {
    const { shipment_id, destination_clinic_id } = req.body;

    // Check if clinic exists and is registered
    const clinic = clinics.find(c => c.clinic_id === destination_clinic_id);
    if (!clinic || !clinic.is_registered) {
        return res.status(400).json({ error: 'Invalid destination: Only registered clinics can be assigned.' });
    }

    // Assign destination to shipment
    const shipment = shipments.find(s => s.shipment_id === shipment_id);
    if (shipment) {
        shipment.destination_clinic_id = destination_clinic_id;
        shipment.status = 'READY_FOR_DISPATCH';
        return res.json({ message: 'Destination assigned successfully!', shipment });
    }

    res.status(404).json({ error: 'Shipment not found.' });
});


app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});