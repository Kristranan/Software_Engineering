// Unit test script for Story 002-1 validation logic

const clinics = [
    { clinic_id: 'CLK-001', clinic_name: 'Salaya Health Center', is_registered: true },
    { clinic_id: 'CLK-002', clinic_name: 'Nakhon Pathom Rural Clinic', is_registered: true },
    { clinic_id: 'CLK-003', clinic_name: 'Unregistered Test Site', is_registered: false }
];

function validateAndAssign(shipmentId, clinicId) {
    const clinic = clinics.find(c => c.clinic_id === clinicId);
    
    if (!clinic || !clinic.is_registered) {
        return { success: false, error: 'Invalid Destination: Only registered clinics can be assigned.' };
    }
    
    return { success: true, shipmentId, destinationClinicId: clinicId };
}

// Run Test Cases
console.log("\n===============================================");
console.log(" RUNNING ACCEPTANCE TESTS FOR STORY 002-1 ");
console.log("===============================================\n");

// Test 1: Valid registered clinic
const test1 = validateAndAssign('SHP-1001', 'CLK-001');
if (test1.success) {
    console.log("✅ TEST 1 PASSED: Registered clinic successfully assigned.");
} else {
    console.error("❌ TEST 1 FAILED:", test1.error);
}

// Test 2: Unregistered clinic rejection
const test2 = validateAndAssign('SHP-1001', 'CLK-003');
if (!test2.success && test2.error.includes("Only registered clinics can be assigned")) {
    console.log("✅ TEST 2 PASSED: Unregistered clinic correctly rejected.");
} else {
    console.error("❌ TEST 2 FAILED: Failed to reject unregistered clinic.");
}

console.log("\n===============================================\n");