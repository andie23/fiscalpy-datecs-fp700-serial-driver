const RECEIPT_SCREEN_CLASS = 'pos-receipt'
const FISCALPY_PRINT_UI_ID = 'fiscalpy-print-ui'
const FISCALPY_PRINT_BTN_ID = 'fiscalpy-print-btn'
const LOCAL_STORAGE_PAYMENT_FISCALPY = 'paymentTypes'
const LOCAL_STORAGE_CAN_PRINT_ONLOAD = 'printOnload'
const LOCAL_STORAGE_PRINT_COPY = 'printCopy'
const LOCAL_STORAGE_PRINTED_ORDER_NUMBERS = 'com.fiscalpy.odoo.extension.printed_order_numbers'

/**
 * Listen for messages from the background script
 */
chrome.runtime.onMessage.addListener((message) => {
    if (message.origin.action === 'print-receipt') {
        // Print went through successfully
        if (message.ok) updateOrderNumber(message.origin.receipt.order_number)

        // Print failed
        if (message.error) alert(message.error)
    }
})

function injectDownloadOption(params) {
    // if it's there, don't add it again
    if (document.getElementById(FISCALPY_PRINT_UI_ID)) return
    const htmlDownload = `
        <div id="${FISCALPY_PRINT_UI_ID}" class='d-flex gap-1'>
            <button
                disabled
                id="${FISCALPY_PRINT_BTN_ID}"
                class='button print btn btn-lg w-100 py-3'
                style='color: white; background-color: #115027;'>
                Print Fiscal Receipt (MRA)
            </button>
        </div>`;
    const receiptSpaceNode = document.getElementsByClassName('buttons')[0];
    receiptSpaceNode.insertAdjacentHTML('afterbegin', htmlDownload);
    setTimeout(() => {
        document.getElementById(FISCALPY_PRINT_BTN_ID).removeAttribute('disabled');
        document.getElementById(FISCALPY_PRINT_BTN_ID).addEventListener('click', () => {
            if (typeof params.onPrint === 'function') params.onPrint()
        });
    }, 500)
}

function isCurrentDate(date) {
    try {
        const [day, month, year] = date.split('/')
        const today = new Date()
        const receiptDate = new Date(`${year.split(' ')[0]}-${month}-${day}`)
        receiptDate.setHours(0,0,0,0)
        today.setHours(0,0,0,0)
        return receiptDate >= today
    } catch (e) {
        console.error(e)
        return false
    }
}

function toFloat(val) {
    return parseFloat(val.replace(',','')).toFixed(2)
}

function extractText(text, pattern, defaultValue='', index=1) {
    return `${text??''}`.match(new RegExp(pattern, 'i'))?.[index] ?? defaultValue
}

function extractMoney(text, extraPattern='') {
    const moneyPattern = '(([1-9]\\d{0,2}(,\\d{3})*)|0)?\\.\\d{2}'
    const val = extractText(text, `${extraPattern}(${moneyPattern})`)
    return new RegExp(moneyPattern, 'i').test(`${val}`) ? toFloat(val) : ''
}


function extractInt(text, pattern, defaultValue=0, index=1) { 
    const val = extractText(text, pattern, defaultValue, index)
    return /^\d+$/i.test(`${val}`) ?  parseInt(`${val}`) : defaultValue
}

// Parse the receipt screen and extract the necessary data
async function parseReceipt(node) {
    const paymentTypes = await getPaymentModes();
    const canPrintCopy = (await chrome.storage.local.get(LOCAL_STORAGE_PRINT_COPY))?.[LOCAL_STORAGE_PRINT_COPY] ?? false
    const receiptText = (node?.innerText ?? '').replace(/\s+/g, ' ')
    const contactSectionText = node.querySelector('.pos-receipt-contact')?.innerText ?? ''
    const receiptDate = node.querySelector('.pos-receipt-order-data')?.innerText ?? ''

    // We need to track the following aggregates for validation purposes..
    const aggregates = {
        "without_tax_code": 0,
        "calculated_total_quantity": 0,
        "calculated_total_products": 0,
        "calculated_sub_total_by_product": 0,
        "calculated_sub_total_by_payment_modes": 0,
        "sub_total": extractMoney(receiptText, 'Sub\\s+Total\\s+'),
        "total_quantity": extractInt(receiptText, 'Total\\s+Product\\s+Qty\\s+(\\d+)'),
        "total_products": extractInt(receiptText, 'Total\\s+No.\\s+of\\s+Products\\s+(\\d+)')
    }
    // Final receipt object that will be printed
    const receiptObj = {
        "print_copy": canPrintCopy,
        "user": extractText(contactSectionText, "Served\\s+by\\s+(\\w+\\s*(?:\\w+))", "N/A"),
        "order_number": extractText(contactSectionText, "order (\\d{5}-\\d{3}-\\d{4})", "N/A"),
        "payment_modes": Object.keys(paymentTypes).reduce((acc, key) => { 
            const amount = extractMoney(receiptText, `${key}\\s+`)
            if (amount) {
                acc[paymentTypes[key]] = amount
                if (aggregates.calculated_sub_total_by_payment_modes === 0) {
                    aggregates.calculated_sub_total_by_payment_modes = acc[paymentTypes[key]]
                } else {
                    aggregates.calculated_sub_total_by_payment_modes += acc[paymentTypes[key]]
                }
            }
            return acc
        }, {}),
        "products": (() => {
            const orders = []
            let taxCode = ''
            let productName = ''
            let productPrice = 0
            let productQuantity = 0
            const orderNodes = node.querySelector('.orderlines')

            for(let i=0;i < orderNodes.children.length; ++i) {
                child = orderNodes.children[i]
                if (child.classList.contains('responsive-price')) {
                    productName = `${child.innerText}`.trim()
                } else if(child.tagName === 'DIV' && !productName && /^[\w\s]+$/i.test(child.innerHTML)) {
                    productName = `${child.innerText}`.trim()
                } else if (child.tagName === 'SPAN' && productName && !(productPrice && productQuantity)) {
                    productName = `${productName} ${child.innerText}`.trim()
                } else if (/price_display/i.test(child.innerHTML) && productName && !(productPrice && productQuantity)) {
                    const [priceQuantity, priceAndTaxCode] = child.innerText.split('\n')
                    const [quantity, price] = priceQuantity.split(' x ')
                    taxCode = extractText(priceAndTaxCode, '([ABE]{1})$', '', 0)
                    productQuantity = parseInt(quantity)
                    productPrice = toFloat(price)
                    orders.push({
                        "quantity": productQuantity,
                        "price": productPrice,
                        "name": productName,
                        "tax_code": taxCode
                    })
                    // Update aggregates after successfully identifying all product attributes
                    aggregates.calculated_sub_total_by_product += productPrice * productQuantity
                    aggregates.calculated_total_quantity += productQuantity
                    aggregates.calculated_total_products += 1
                    if (productPrice && !taxCode) aggregates.without_tax_code += 1
                    // Clear for next products to be iterated on
                    taxCode = ''
                    productPrice = 0
                    productQuantity = 0
                    productName = ''
                }
            }
            return orders
        })()
    }
    let validations = {}
    try {
        validations = {
            "Missing products": receiptObj.products.length === 0,
            "Missing total quantity": aggregates.total_quantity === 0,
            "Missing Order Number": !receiptObj.order_number,
            "Missing sub total": !aggregates.sub_total || !aggregates.sub_total || isNaN(aggregates.sub_total) || aggregates.sub_total === 0,
            "Tax Code Missing": aggregates.without_tax_code > 0,
            "Invalid Sub Total": parseInt(aggregates.sub_total) !== parseInt(aggregates.calculated_sub_total_by_product),
            "Invalid Total Quantity": aggregates.total_quantity !== aggregates.calculated_total_quantity,
            "Invalid/ Unknown payment method used": parseInt(aggregates.calculated_sub_total_by_payment_modes) < parseInt(aggregates.sub_total),
            "Invalid Total Products": parseInt(aggregates.total_products) !== parseInt(aggregates.calculated_total_products)
        }
    } catch (e) {
        validations = {
            "Receipt validation has crashed!": true
        }
        console.error(e)
    }
    return {
        aggregates,
        receiptDate,
        receiptData: receiptObj,
        isCurrentDate: isCurrentDate(receiptDate),
        errors: Object.keys(validations).filter(key => validations[key])
    }
}

function isOrderNumberPrinted(orderNumber) {
    const orderNumbers = JSON.parse(localStorage.getItem(LOCAL_STORAGE_PRINTED_ORDER_NUMBERS) ?? '[]')
    return orderNumbers && orderNumbers.includes(orderNumber)
}

function updateOrderNumber(orderNumber) {
    const orderNumbers = JSON.parse(localStorage.getItem(LOCAL_STORAGE_PRINTED_ORDER_NUMBERS) ?? '[]')
    orderNumbers.push(orderNumber)
    localStorage.setItem(LOCAL_STORAGE_PRINTED_ORDER_NUMBERS, JSON.stringify(orderNumbers))
}

async function getPaymentModes() {
    return (await chrome.storage.local.get([LOCAL_STORAGE_PAYMENT_FISCALPY]))?.[LOCAL_STORAGE_PAYMENT_FISCALPY] ?? { "Cash": "P" }
}

function init(node) {
    const sendPrintMessage = async () => {
        const receipt = await parseReceipt(node)
        console.log(receipt)
        if (receipt.errors.length > 0) {
            return alert(`Receipt Extraction Failed: ${receipt.errors.join(', ')}`)
        }
        if (receipt.receiptDate && 
            !receipt.isCurrentDate && 
            !confirm('The receipt date is not today. Are you sure you want to print?')) {
            return
        }
        if (isOrderNumberPrinted(receipt.receiptData.order_number)) {
            if (!confirm(`Order number ${receipt.receiptData.order_number} was already processed. YOU MAY INCUR DOUBLE TAXATION IF YOU PRINT AGAIN...`)) {
                return
            }
        }
        chrome.runtime.sendMessage({ receipt: receipt.receiptData, action: "print-receipt" })
    }

    chrome.storage.local.get([LOCAL_STORAGE_CAN_PRINT_ONLOAD]).then((data) => { 
        if (data[LOCAL_STORAGE_CAN_PRINT_ONLOAD]) {
            sendPrintMessage()
        }
    })

    injectDownloadOption({
        onPrint: () => sendPrintMessage()
    })
}

/*
* Entry point
*/
window.addEventListener('load', () => {
    const container = document.getElementsByClassName(RECEIPT_SCREEN_CLASS)[0]
    if (container) init(container)
    // Observe for new receipt screens
    const observer = new MutationObserver((mutationsList) => {
        for (const mutation of mutationsList) {
            // A new receipt screen has been added
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains(RECEIPT_SCREEN_CLASS)) {
                        init(node)
                    }
                });
            }
        }
    });
    // Start observing the target node for configured mutations
    observer.observe(document.body, {
        childList: true, // Observe direct children
        attributes: true, // Observe attribute changes (like class)
        subtree: true, // Observe all descendants
    });
})