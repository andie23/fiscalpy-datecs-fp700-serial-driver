const LOCAL_STORAGE_PAYMENT_FISCALPY = 'paymentTypes'
const LOCAL_STORAGE_CAN_PRINT_ONLOAD = 'printOnload'
const LOCAL_STORAGE_PRINT_COPY = 'printCopy'

const printCopiesToggle = document.getElementById("printCopies");
const printOnLoadToggle = document.getElementById("printOnLoad");
const paymentKeySelect = document.getElementById("paymentKey");
const paymentNameInput = document.getElementById("paymentName");
const addPaymentButton = document.getElementById("addPayment");
const paymentList = document.getElementById("paymentList");

// Load saved settings
chrome.storage.local.get([LOCAL_STORAGE_CAN_PRINT_ONLOAD, LOCAL_STORAGE_PAYMENT_FISCALPY, LOCAL_STORAGE_PRINT_COPY], (data) => {
    printCopiesToggle.checked = data[LOCAL_STORAGE_PRINT_COPY] || false;
    printOnLoadToggle.checked = data[LOCAL_STORAGE_CAN_PRINT_ONLOAD] || false;
    if (data[LOCAL_STORAGE_PAYMENT_FISCALPY]) {
        for (const [key, name] of Object.entries(data[LOCAL_STORAGE_PAYMENT_FISCALPY])) {
            addPaymentToList(key, name);
        }
    }
});

// Save print copies toggle
printCopiesToggle.addEventListener("change", () => {
    chrome.storage.local.set({ [LOCAL_STORAGE_PRINT_COPY]: printCopiesToggle.checked });
});

// Save print on load setting
printOnLoadToggle.addEventListener("change", () => {
    chrome.storage.local.set({ [LOCAL_STORAGE_CAN_PRINT_ONLOAD]: printOnLoadToggle.checked });
});

// Add new payment method
addPaymentButton.addEventListener("click", () => {
    const key = paymentKeySelect.value;
    const name = paymentNameInput.value.trim();

    if (!name) return alert("Please enter payment type name");

    chrome.storage.local.get([LOCAL_STORAGE_PAYMENT_FISCALPY], (data) => {
        if (data?.[LOCAL_STORAGE_PAYMENT_FISCALPY]?.[name]) {
            return alert("Key already exists");
        }
        chrome.storage.local.set({ 
            [LOCAL_STORAGE_PAYMENT_FISCALPY]: {
                ...data[LOCAL_STORAGE_PAYMENT_FISCALPY], [name]: key 
            } 
        }).then(() => {
            addPaymentToList(key, name);
            paymentNameInput.value = "";
        }).catch((err) => {
            console.error(err);
        })
    });
});

// Helper function to add to UI
function addPaymentToList(key, name) {
    const li = document.createElement("li");
    li.textContent = `🔑 ${key}: ${name}`;
    paymentList.appendChild(li);
}

