import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

# ==========================================
# PART 1: Join and Filter
# ==========================================

# 1. Return the first and last names and the job titles for all employees in Boston.
df_boston = pd.read_sql(
    """
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""",
    conn,
)

# 2. Are there any offices that have zero employees?
df_zero_emp = pd.read_sql(
    """
    SELECT o.officeCode, o.city
    FROM offices o
    LEFT JOIN employees e ON o.officeCode = e.officeCode
    WHERE e.employeeNumber IS NULL;
""",
    conn,
)


# ==========================================
# PART 2: Type of Join
# ==========================================

# 3. Return employees' first name, last name, city, and state. Order by first name, then last name.
df_employee = pd.read_sql(
    """
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""",
    conn,
)

# 4. Customer contact info and sales rep employee number for customers who haven't placed an order, sorted by last name.
df_contacts = pd.read_sql(
    """
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM customers c
    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""",
    conn,
)


# ==========================================
# PART 3: Built-In Function
# ==========================================

# 5. Customer contacts with payment amounts and dates, sorted descending by payment amount.
df_payment = pd.read_sql(
    """
    SELECT c.contactFirstName, c.contactLastName, p.amount, p.paymentDate
    FROM customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""",
    conn,
)


# ==========================================
# PART 4: Joining and Grouping
# ==========================================

# 6. Employee number, first name, last name, and number of customers for employees whose customers have avg credit limit > 90k.
df_credit = pd.read_sql(
    """
    SELECT e.employeeNumber, e.firstName, e.lastName, COUNT(c.customerNumber) AS n_customers
    FROM employees e
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY n_customers DESC;
""",
    conn,
)

# 7. Product name, count of orders (numorders), and total quantity ordered (totalunits), sorted by totalunits high to low.
df_product_sold = pd.read_sql(
    """
    SELECT p.productName, COUNT(od.orderNumber) AS numorders, SUM(od.quantityOrdered) AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productCode
    ORDER BY totalunits DESC;
""",
    conn,
)


# ==========================================
# PART 5: Multiple Joins
# ==========================================

# 8. Product name, code, and total number of unique customers (numpurchasers), sorted by highest purchasers.
df_total_customers = pd.read_sql(
    """
    SELECT p.productName, p.productCode, COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode
    ORDER BY numpurchasers DESC;
""",
    conn,
)

# 9. Count of customers (n_customers), office code, and city per office.
df_customers = pd.read_sql(
    """
    SELECT COUNT(c.customerNumber) AS n_customers, o.officeCode, o.city
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode
    ORDER BY n_customers DESC;
""",
    conn,
)


# ==========================================
# PART 6: Subquery
# ==========================================

# 10. Employee number, first name, last name, city, and office code for employees who sold products ordered by fewer than 20 customers.
df_subquery = pd.read_sql(
    """
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName, o.city, o.officeCode
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders ord ON c.customerNumber = ord.customerNumber
    JOIN orderdetails od ON ord.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od_sub.productCode
        FROM orderdetails od_sub
        JOIN orders ord_sub ON od_sub.orderNumber = ord_sub.orderNumber
        JOIN customers c_sub ON ord_sub.customerNumber = c_sub.customerNumber
        GROUP BY od_sub.productCode
        HAVING COUNT(DISTINCT c_sub.customerNumber) < 20
    );
""",
    conn,
)

# 11. Close the connection
conn.close()