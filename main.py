import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

# ==========================================
# PART 1: Join and Filter
# ==========================================

# 1. Boston employees
df_boston = pd.read_sql(
    """
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""",
    conn,
)

# 2. Offices with zero employees
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

df_employee = pd.read_sql(
    """
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""",
    conn,
)

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

# Close connection
conn.close()