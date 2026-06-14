INVOICE_1 = """
From: ABC Office Supplies <billing@abcoffice.com>
Date: March 15, 2024

Thank you for your order!

Invoice #: INV-2024-0315
Customer: TechCorp Inc.

Items:
- 50x Ballpoint Pens (Blue) @ $0.50 = $25.00
- 20x Legal Pads @ $3.00 = $60.00
- 5x Desk Organizers @ $15.00 = $75.00

Subtotal: $160.00
Tax (8%): $12.80
TOTAL: $172.80

Payment due within 30 days.
"""

INVOICE_2 = """
ACME Catering Services
Invoice Date: 03/20/2024
Invoice Number: AC-2024-782

Bill To: TechCorp Inc.

Corporate lunch service for March 18, 2024
Attendees: 45 people

Menu items at $22 per person: $990
Delivery fee: $50
Service charge (15%): $148.50

Amount Due: $1,188.50

Terms: Net 15
"""

INVOICE_3 = """
Hey team,

Quick note - we had the IT consultant onsite last week.
The total came to $3,500 for 20 hours of work.
I think we need to get this paid soon.

- Mike
"""

NOISY_INVOICE = """
1NV01CE N0: 2024-XYZ-789    (Note: OCR errors)
Vend0r: Qu1ckSupply C0rp

1tems:
- 0ff1ce Cha1rs x 5 @ $150 = $750
- Desktop C0mputers x 3 @ $800 = $2400

T0TAL AM0UNT: $3,150.00

Due: March 25th 2024
"""

PROBLEMATIC_INVOICE = """
Subject: returned-shipment credit memo

This document references a credit/refund of -$500 against an
unspecified invoice number. Original invoice details — including the
issuing party, line items, and any identifying header — are not
recoverable from this excerpt.

Date: ??/??/????
Amount Due: -$500
"""
