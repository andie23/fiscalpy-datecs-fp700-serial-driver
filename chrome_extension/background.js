const NATIVE_PORT = 'com.fiscalpy.fp700'

const ACTION_WHITE_LIST = [ 
    'print-receipt'
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
        console.error("Failed to connect: " + chrome.runtime.lastError.message);
    });

    console.log('Sending message to port')
    port.postMessage(message)
})