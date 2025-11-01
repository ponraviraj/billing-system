# Billing System

A production-ready Flask-based billing system that handles product management, invoice generation, and customer purchase tracking.

## Features

1. **Product Management**
   - Database schema for products with fields: name, product ID, available stocks, price per unit, and tax percentage
   - Pre-seeded sample products for testing

2. **Billing Calculation (Page 1)**
   - Customer email input
   - Dynamic product addition with Product ID and Quantity fields
   - Shop denominations tracking (500, 50, 20, 10, 5, 2, 1)
   - Cash paid by customer input
   - Generate Bill functionality

3. **Invoice Display (Page 2)**
   - Detailed bill table with all product information
   - Billing summary with calculations:
     - Total price without tax
     - Total tax payable
     - Net price of purchased items
     - Rounded down value (as per requirement)
     - Balance payable to customer
   - Balance denomination breakdown

4. **Purchase History**
   - View all previous purchases by customer email
   - Display purchase details including items purchased
   - Link to view detailed bill for each purchase

5. **Product Management (Admin)**
   - CRUD operations for products
   - Add, edit, and delete products
   - View all products with their details

## Project Structure

```
Billing System/
├── app.py                 # Main Flask application
├── billing.db            # SQLite database (created on first run)
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── templates/
    ├── page1.html       # Billing calculation page
    ├── page2.html       # Invoice display page
    └── purchases.html   # Customer purchase history page
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "Billing System"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser and navigate to: `http://localhost:5000`
   - The database will be automatically initialized on first run with sample data

## Usage

### Generating a Bill

1. Navigate to the home page (Page 1)
2. Enter the customer's email address
3. Add products by:
   - Entering Product ID (e.g., P001, P002)
   - Entering Quantity
   - Clicking "Add New" to add more products
4. Enter the count for each denomination available in the shop
5. Enter the cash amount paid by the customer
6. Click "Generate Bill"
7. You will be redirected to Page 2 showing the complete invoice

### Viewing Purchase History

1. On Page 1, scroll to the "View Previous Purchases" section
2. Enter the customer's email address
3. Click "View Purchases"
4. You will see a list of all purchases made by that customer
5. Click "View Bill" on any purchase to see the detailed invoice

### Managing Products (Admin)

1. Navigate to `/admin/products` or click "Manage Products (Admin)" link on Page 1
2. View all existing products in a table
3. To add a new product:
   - Fill in the form at the bottom (Product ID, Name, Price, Tax %, Available Stocks)
   - Click "Save Product"
4. To edit a product:
   - Click "Edit" button on any product row
   - Modify the fields in the form
   - Click "Save Product"
5. To delete a product:
   - Click "Delete" button on any product row
   - Confirm the deletion

## Database Schema

### Products Table
- `id`: Primary key
- `name`: Product name
- `product_id`: Unique product identifier
- `available_stocks`: Available quantity
- `price`: Price per unit (float)
- `tax_percentage`: Tax percentage (float)

### Purchases Table
- `id`: Primary key
- `customer_email`: Customer email address
- `purchase_date`: Purchase timestamp
- `total_amount`: Total amount (rounded down)
- `tax_amount`: Total tax amount
- `paid_amount`: Amount paid by customer
- `balance_amount`: Balance to be returned
- `items_json`: JSON string of purchased items
- `balance_denominations`: JSON string of balance denomination breakdown

### Shop Denominations Table
- `id`: Primary key
- `value`: Denomination value (500, 50, 20, 10, 5, 2, 1)
- `count`: Available count of this denomination

## Sample Data

The system comes pre-loaded with the following products:

- Laptop (P001): ₹50,000, 18% tax, Stock: 10
- Mouse (P002): ₹500, 12% tax, Stock: 50
- Keyboard (P003): ₹1,500, 12% tax, Stock: 30
- Monitor (P004): ₹15,000, 18% tax, Stock: 15
- USB Cable (P005): ₹200, 5% tax, Stock: 100

Shop denominations are initialized with 50 of each: 500, 50, 20, 10, 5, 2, 1

## Key Features Implementation

### Rounded Down Calculation
The system rounds down the net price to the nearest integer before calculating the balance payable to the customer, as shown in Page 2.

### Balance Denomination Calculation
The system automatically calculates the optimal combination of denominations to return as change, based on available denominations in the shop.

### Stock Management
Stock levels are automatically updated when a bill is generated. The system validates stock availability before processing the bill.


## Testing the Application

### Test Scenario 1: Generate a Simple Bill
1. Go to Page 1
2. Enter email: `test@example.com`
3. Add Product ID: `P002`, Quantity: `2` (Mouse)
4. Enter paid amount: `1500`
5. Click Generate Bill
6. Verify Page 2 shows correct calculations

### Test Scenario 2: View Purchase History
1. Generate a bill as above
2. Scroll to "View Previous Purchases" section
3. Enter email: `test@example.com`
4. Click "View Purchases"
5. Verify the purchase appears in the list

### Test Scenario 3: Multiple Products
1. Generate a bill with multiple products
2. Verify all products appear in the bill table
3. Verify tax calculations are correct for each item

## Assumptions

1. **Denominations**: The system uses denominations as shown in the image (500, 50, 20, 10, 5, 2, 1). Higher denominations can be added if needed.

2. **Currency**: The system uses ₹ (Indian Rupee) symbol for display. This can be changed in templates.


4. **Stock Validation**: The system validates stock availability before bill generation. If stock is insufficient, an error is returned.

5. **Change Calculation**: The system ensures exact change can be given. If exact change cannot be provided with available denominations, an error is returned.

6. **Database**: Uses SQLite for simplicity. For production, consider PostgreSQL or MySQL.

## Production Considerations

1. **Database**: Migrate to PostgreSQL or MySQL for better performance and scalability
2. **Security**: Implement proper authentication and authorization
4. **Error Handling**: Add comprehensive error logging
5. **Validation**: Add client-side and server-side validation
6. **Testing**: Add unit tests and integration tests
7. **Deployment**: Use WSGI server (Gunicorn) for production deployment

## Troubleshooting

### Database Issues
- If database errors occur, delete `billing.db` and restart the application
- The database will be recreated with sample data

### Port Already in Use
- If port 5000 is in use, modify the last line in `app.py`:
  ```python
  app.run(debug=True, port=5001)
  ```


## Support

For issues or questions, please refer to the code comments or contact the development team.

---

**Note**: This application follows best practices for Flask development with proper separation of concerns, database management, and template rendering.

