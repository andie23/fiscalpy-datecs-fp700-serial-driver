const NATIVE_PORT = 'com.fiscalpy.fp700'

const ACTION_WHITE_LIST = [ 
    'print-receipt',
    'play-sound'
]

chrome.runtime.onMessage.addListener((message, sender) => {
    if (!ACTION_WHITE_LIST.includes(message.action)) return

    port = chrome.runtime.connectNative(NATIVE_PORT);

    port.onMessage.addListener(nativeMessage => {
        // Send the response back to the originating extension context
        if (sender.tab) {
            // If the message came from a tab, send the response to the specific tab
            chrome.tabs.sendMessage(sender.tab.id, {...nativeMessage, origin: message});
        } 
    });

    port.onDisconnect.addListener(() => {
        const error = chrome.runtime.lastError.message
        console.error("Failed to connect: " + error);
        if (/host not found/i.test(error)) {
            chrome.tabs.sendMessage(
                sender.tab.id, { 
                    origin: message, 
                    error: "Printer driver not found on your computer!!"
                }
            )   
        }
    });

    console.log('Sending message to port')
    chrome.storage.local.get(['port', 'baudrate'], (conf) => {
        const payload = {
            printer_config: {
                port: conf?.port,
                baudrate: conf?.baudrate ? Number(conf.baudrate) : undefined
            },
            ...message
        }
        console.log("Sending payload ", payload)
        port.postMessage(payload)
    })
})