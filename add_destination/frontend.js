import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AssignDestination({ shipmentId }) {
    const [clinics, setClinics] = useState([]);
    const [selectedClinic, setSelectedClinic] = useState('');
    const [statusMessage, setStatusMessage] = useState('');
    const [isError, setIsError] = useState(false);

    // Fetch registered clinics on component mount
    useEffect(() => {
        axios.get('/api/clinics/registered')
            .then(response => setClinics(response.data))
            .catch(err => setStatusMessage('Error loading clinic list'));
    }, []);

    const handleAssign = async () => {
        try {
            const response = await axios.post('/api/shipments/assign-destination', {
                shipment_id: shipmentId,
                destination_clinic_id: selectedClinic
            });
            setIsError(false);
            setStatusMessage(`Successfully assigned to ${response.data.shipment.destination_clinic_id}`);
        } catch (error) {
            setIsError(true);
            setStatusMessage(error.response?.data?.error || 'Failed to assign destination.');
        }
    };

    return (
        <div className="destination-panel">
            <h3>Assign Shipment Destination (Story 002-1)</h3>
            
            <label htmlFor="clinic-select">Select Registered Clinic:</label>
            <select 
                id="clinic-select" 
                value={selectedClinic} 
                onChange={(e) => setSelectedClinic(e.target.value)}
            >
                <option value="">-- Select a Registered Clinic --</option>
                {clinics.map(clinic => (
                    <option key={clinic.clinic_id} value={clinic.clinic_id}>
                        {clinic.clinic_name} ({clinic.district})
                    </option>
                ))}
            </select>

            <button onClick={handleAssign} disabled={!selectedClinic}>
                Assign Destination
            </button>

            {statusMessage && (
                <p style={{ color: isError ? 'red' : 'green' }}>
                    {statusMessage}
                </p>
            )}
        </div>
    );
}

export default AssignDestination;