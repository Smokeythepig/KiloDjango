# KiloDjango
Kilo Teams, Django Website!!!!

 1. Project Overview
This application is the final evolution of the Personal Expense Tracker, transitioning from a desktop GUI to a robust, multi-user Django web application [cite: 1, 4]. It allows users to manage expenses through a browser, view summaries and category totals, filter expenses, and convert totals into other currencies using a live API [cite: 13]. The system preserves the core business logic from previous checkpoints—including manual entry, file loading, and aggregation—while redesigning it for a modern web environment with a relational database.

 2. Team Members and Contributions
Our team divided responsibilities based on the core logic each member developed during the desktop GUI phase to ensure architectural continuity [cite: 92].

Michael McCarty: Initialized the Django project structure and URL configuration. He implemented the User Authentication system, including login and logout functionality to ensure expenses belong to specific users.

Claire Nguyen: Developed the `Expense` model and integrated it with Django. She created the web forms and views for managing expenses (Create, View, Edit, Delete)

Brinton Mucher: Developed the aggregation logic for the Dashboard to display overall and per-category totals. He also implemented the filtering system to narrow expenses by category and date range.

Connor Beasley: Refactored the file-loading logic to support web-based CSV and JSON imports. He also integrated the Currency Conversion API, ensuring the application handles API failures gracefully.

3. How to Run the Program

    1.  Prerequisites: Ensure Python 3.x is installed.
    2.  Dependencies: Install required packages (e.g., `pip install django requests`).
    3.  Database Setup: Run `python manage.py makemigrations` and `python manage.py migrate` to initialize the    database.
    4.  Launch: Run the command `python manage.py runserver` [cite: 96].
    5.  Access: Navigate to `http://127.0.0.1:8000/` in your web browser.

4. Django Architecture
The application follows the Django MVT (Model-View-Template) pattern to ensure a clean separation of concerns:
Models: Uses the `Expense` model tied to the built-in `User` model via the Django ORM [cite: 72, 78].
Forms: Utilizes `ExpenseForm` and `ImportForm` for secure and validated user input [cite: 53, 54, 79].
Views: Separate views handle the Dashboard (summaries), Expense List, Management (CRUD), and Data Imports.
Templates: A base template provides shared navigation, with specific templates for the dashboard, forms, and reports.

5. Feature Evolution
Checkpoint 1: Established core data handling via console-based manual entry and flat-file loading.
Checkpoint 2: Refactored logic into an object-oriented desktop GUI with API-based currency conversion.
Checkpoint 3: Moved the system into Django, replacing in-memory structures with a relational database and enabling multi-user support.

6. API Integration
The application integrates a live currency API to convert spending totals [cite: 33]. The logic is designed to be robust; if the API fails or the network is unavailable, the application provides a user-friendly error message rather than crashing.

7. Data Import Strategy
Users can upload CSV or JSON files through the web interface. The application validates the uploaded data to ensure required fields (Date, Amount, Category, Description) are present. Malformed rows or invalid formats are skipped or flagged without interrupting the rest of the import process.

8. Error Handling and Edge Cases
Form Validation: Invalid inputs trigger clear, inline error messages.
Defensive Design: The application handles empty datasets and invalid numeric values gracefully.
Authentication: Protected views ensure users can only view or edit their own data.

9. Known Limitations
(Example: User registration is optional and may not be implemented if only pre-created accounts are supported.)
(Example: Data is not permanently stored after an import unless specifically saved to the database)

10. Reflection
This project highlighted the importance of modular design. By separating our business logic from the interface in earlier checkpoints, we were able to refactor our core calculations and file-parsing logic for the web.

11. Academic Integrity Statement
We reaffirm that our team understands and can explain all submitted work, and we have adhered to all academic integrity policies throughout the development of this project.