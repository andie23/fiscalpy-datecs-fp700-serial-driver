const K_PAYMENT_TYPES = 'paymentTypes'
const K_PRINT_ON_LOAD = 'printOnload'
const K_PRINT_COPY = 'printCopy'
const K_PORT = 'port'
const K_BAUDRATE = 'baudrate'
const K_NEW_ORDER_ON_PRINT = 'newOrderOnPrint'

const printCopiesToggle = document.getElementById("printCopies");
const printOnLoadToggle = document.getElementById("printOnLoad");
const paymentKeySelect = document.getElementById("paymentKey");
const paymentNameInput = document.getElementById("paymentName");
const addPaymentButton = document.getElementById("addPayment");
const paymentList = document.getElementById("paymentList");
const baudRateSelect = document.getElementById("baudrate")
const portSelect = document.getElementById("port")
const testPrinterButton = document.getElementById("testPrinter")
const newOrderAfterPrintingToggle = document.getElementById("newOrderAfterPrinting")

// Load saved settings
chrome.storage.local.get([K_NEW_ORDER_ON_PRINT, K_PORT, K_BAUDRATE, K_PRINT_ON_LOAD, K_PAYMENT_TYPES, K_PRINT_COPY], (data) => {
    printCopiesToggle.checked = data[K_PRINT_COPY] || false;
    printOnLoadToggle.checked = data[K_PRINT_ON_LOAD] || false;
    newOrderAfterPrintingToggle.checked = data[K_NEW_ORDER_ON_PRINT] || false;
    portSelect.value = data.port
    baudRateSelect.value = data.baudrate

    if (data[K_PAYMENT_TYPES]) {
        for (const [key, name] of Object.entries(data[K_PAYMENT_TYPES])) {
            addPaymentToList(key, name);
        }
    }
});

baudRateSelect.addEventListener("change", (event) => {
    chrome.storage.local.set({ [K_BAUDRATE]: event.target.value })
})

portSelect.addEventListener("change", (event) => {
    chrome.storage.local.set({ [K_PORT]: event.target.value })
})

testPrinterButton.addEventListener("click", () => {
    alert("Listen, The fiscal Printer will beep 4 times. Please confirm")
    chrome.runtime.sendMessage({ action: 'play-sound', playCount: 4 })
})

newOrderAfterPrintingToggle.addEventListener("change", () => {
    chrome.storage.local.set({ [K_NEW_ORDER_ON_PRINT]: newOrderAfterPrintingToggle.checked })
}) 

// Save print copies toggle
printCopiesToggle.addEventListener("change", () => {
    chrome.storage.local.set({ [K_PRINT_COPY]: printCopiesToggle.checked });
});

// Save print on load setting
printOnLoadToggle.addEventListener("change", () => {
    chrome.storage.local.set({ [K_PRINT_ON_LOAD]: printOnLoadToggle.checked });
});

// Add new payment method
addPaymentButton.addEventListener("click", () => {
    const key = paymentKeySelect.value;
    const name = paymentNameInput.value.trim();

    if (!name) return alert("Please enter payment type name");

    chrome.storage.local.get([K_PAYMENT_TYPES], (data) => {
        if (data?.[K_PAYMENT_TYPES]?.[name]) {
            return alert("Payment type already exists");
        }
        chrome.storage.local.set({ 
            [K_PAYMENT_TYPES]: {
                ...data[K_PAYMENT_TYPES], 
                [name]: key 
            } 
        })
        .then(() => {
            addPaymentToList(name, key)
            paymentNameInput.value = ""
        })
        .catch((err) => console.error(err))
    });
});

// Helper function to add to UI
function addPaymentToList(key, name) {
    const li = document.createElement("li");
    li.onclick = () => {
        if (!confirm(`Are you sure you want to delete payment type: ${key}`)) {
            return
        }
        chrome.storage.local.get([K_PAYMENT_TYPES], (conf) => {
            const paymentTypes = conf?.[K_PAYMENT_TYPES] ?? {}
            delete paymentTypes[key]
            chrome.storage.local.set({ [K_PAYMENT_TYPES]: paymentTypes })
                .then(() => li.remove())
                .catch((e) => {
                    alert("Error deleting payment type")
                    console.error(e)
                })
        })
    }
    li.textContent = `❌ ${key}: ${name}`;
    paymentList.appendChild(li);
}

