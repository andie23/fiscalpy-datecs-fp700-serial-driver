# Datecs Fp700 driver
Python library/SDK for talking to Fp700 devices via Serial connection

# Compiling into EXE
`pyinstaller --onefile fp700.py`

# Raw commands
## Format
`<code: int>[::<data: string>]`

## Example commands
1. `49::Chocololate E1000.0*1`
2. `80`
3. `42:: Hello world!`

## Printing commands from file example
### Test file
`C:\mra\test.fp`
```text
48::2,0000,12
84::3;123456789012
49::bread \tA1
53::P	
56
```
### Running the file
```bash
fp700.exe -p cf "c:\mra\test.fp"
```

## Running direct printer command in terminal
```bash
fp700.exe -p c "42::Hello world!"
```

# Printing json sales receipt
## Sales object template
```json
 {
    "tpin": 00000,
    "order_number": "0000-0000-000",
    "user": "test123",
    "buyer": "Test Buyer",
    "buyer_tin": 0000,
    "print_copy": false,
    "payment_modes": {
        "P": 1.0
    },
    "products": [
        {
            "tax_code": "A",
            "name": "Bread",
            "price": 1.0,
            "quantity": 1,
            "abs_discount": "20.00",
            "perc_discount": -1800
        }
    ]
  }
```

## Command
```bash
fp700.exe -p jf "c:\mra\sales.json"
```
